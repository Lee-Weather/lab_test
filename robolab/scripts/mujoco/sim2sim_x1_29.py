#!/usr/bin/env python3
# Copyright (c) 2025-2026, The RoboLab Project Developers.
# SPDX-License-Identifier: BSD-3-Clause
"""Sim2Sim for X1_29 (29-DOF) humanoid robot.

Usage:
    python sim2sim_x1_29.py --load_model policy_300.pt --headless
"""
import numpy as np
import mujoco
from tqdm import tqdm
from scipy.spatial.transform import Rotation as R
import torch
import os
import csv
import cv2
import matplotlib.pyplot as plt
from datetime import datetime

# X1_29 assets root
X1_29_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "czy", "data", "x1_29")
X1_29_DATA_DIR = os.path.abspath(X1_29_DATA_DIR)


class cmd:
    vx = 0.0
    vy = 0.0
    dyaw = 0.0


def get_obs(data):
    """Extract observation from MuJoCo data."""
    q = data.qpos.astype(np.double)
    dq = data.qvel.astype(np.double)
    quat = data.sensor('body-orientation').data[[1, 2, 3, 0]].astype(np.double)
    r = R.from_quat(quat)
    v = r.apply(data.qvel[:3], inverse=True).astype(np.double)
    omega = data.sensor('body-angular-velocity').data.astype(np.double)
    gvec = r.apply(np.array([0., 0., -1.]), inverse=True).astype(np.double)
    return (q, dq, quat, v, omega, gvec)


def pd_control(target_q, q, kp, target_dq, dq, kd):
    return (target_q - q) * kp + (target_dq - dq) * kd


def run_mujoco(policy, cfg, headless=False):
    model = mujoco.MjModel.from_xml_path(cfg.sim_config.mujoco_model_path)
    model.opt.timestep = cfg.sim_config.dt
    if getattr(cfg.sim_config, 'use_implicit', False):
        model.opt.integrator = mujoco.mjtIntegrator.mjINT_IMPLICIT
        model.dof_damping[6:] = cfg.robot_config.kds
        print(f"Using mjINT_IMPLICIT integrator with dof_damping (kd implicit)")
    data = mujoco.MjData(model)
    data.qpos[2] = 0.65
    data.qpos[-cfg.robot_config.num_actions:] = cfg.robot_config.default_pos
    mujoco.mj_forward(model, data)

    # No settle phase: start policy immediately from z=0.65 (matches Isaac Lab training init)
    # Settle phase was found harmful in deployment diagnostics (robot drops to unstable position)

    os.environ['__GLX_VENDOR_LIBRARY_NAME'] = 'nvidia'
    if headless:
        renderer = mujoco.Renderer(model, width=1920, height=1080)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        cam = mujoco.MjvCamera()
        cam.distance = 4.0
        cam.azimuth = 45.0
        cam.elevation = -20.0
        cam.lookat = [0, 0, 1]
        out = cv2.VideoWriter('simulation.mp4', fourcc, 1.0 / cfg.sim_config.dt / cfg.sim_config.decimation, (1920, 1080))
    else:
        import mujoco_viewer
        viewer = mujoco_viewer.MujocoViewer(model, data, mode='window', width=1920, height=1080)
        viewer.cam.distance = 4.0
        viewer.cam.azimuth = 45.0
        viewer.cam.elevation = -20.0
        viewer.cam.lookat = [0, 0, 1]

    target_pos = np.zeros((cfg.robot_config.num_actions), dtype=np.double)
    action = np.zeros((cfg.robot_config.num_actions), dtype=np.double)
    hist_obs = np.zeros((cfg.robot_config.frame_stack, cfg.robot_config.num_single_obs), dtype=np.double)
    hist_obs.fill(0.0)
    count_lowlevel = 0

    # Data collection
    time_data, commanded_joint_pos_data, actual_joint_pos_data = [], [], []
    tau_data, commanded_lin_vel_x_data, commanded_lin_vel_y_data = [], [], []
    commanded_ang_vel_z_data, actual_lin_vel_data, actual_ang_vel_data = [], [], []
    tau = np.zeros((cfg.robot_config.num_actions), dtype=np.double)
    is_first_frame = True

    # CSV diagnostic logging setup
    joint_names_csv = [
        'lumbar_yaw', 'lumbar_roll', 'lumbar_pitch',
        'L_shoulder_pitch', 'L_shoulder_roll', 'L_shoulder_yaw',
        'L_elbow_pitch', 'L_elbow_yaw', 'L_wrist_pitch', 'L_wrist_roll',
        'R_shoulder_pitch', 'R_shoulder_roll', 'R_shoulder_yaw',
        'R_elbow_pitch', 'R_elbow_yaw', 'R_wrist_pitch', 'R_wrist_roll',
        'L_hip_pitch', 'L_hip_roll', 'L_hip_yaw', 'L_knee_pitch', 'L_ankle_pitch', 'L_ankle_roll',
        'R_hip_pitch', 'R_hip_roll', 'R_hip_yaw', 'R_knee_pitch', 'R_ankle_pitch', 'R_ankle_roll',
    ]
    csv_header = ['timestamp_ns',
                  'cmd_linear_x', 'cmd_linear_y', 'cmd_angular_z',
                  'base_euler_x', 'base_euler_y', 'base_euler_z',
                  'base_ang_vel_x', 'base_ang_vel_y', 'base_ang_vel_z',
                  'base_lin_vel_x', 'base_lin_vel_y', 'base_lin_vel_z',
                  'imu_quat_w', 'imu_quat_x', 'imu_quat_y', 'imu_quat_z',
                  'left_contact', 'right_contact',
                  'left_foot_force_z', 'right_foot_force_z',
                  'left_foot_force_mag', 'right_foot_force_mag']
    for _jn in joint_names_csv:
        csv_header += [f'action_{_jn}', f'pos_{_jn}', f'vel_{_jn}', f'effort_{_jn}', f'pos_des_{_jn}']
    csv_path = f'isaac_diag_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    csv_file = open(csv_path, 'w', newline='')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(csv_header)
    print(f'CSV diagnostic logging to: {csv_path}')

    # Foot body IDs for contact force extraction
    left_foot_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, 'left_ankle_roll_link')
    right_foot_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, 'right_ankle_roll_link')
    print(f'Foot body IDs: left={left_foot_id}, right={right_foot_id}')
    _step_dt_ns = int(cfg.sim_config.dt * cfg.sim_config.decimation * 1e9)
    _t0_ns = 0  # relative timestamp from sim start

    for step in tqdm(range(int(cfg.sim_config.sim_duration / cfg.sim_config.dt)), desc="Simulating..."):
        q, dq, quat, v, omega, gvec = get_obs(data)
        q = q[-cfg.robot_config.num_actions:]
        dq = dq[-cfg.robot_config.num_actions:]

        if count_lowlevel % cfg.sim_config.decimation == 0:
            q_obs = np.zeros((cfg.robot_config.num_actions), dtype=np.double)
            dq_obs = np.zeros((cfg.robot_config.num_actions), dtype=np.double)
            q_ = q - cfg.robot_config.default_pos
            for i in range(len(cfg.robot_config.usd2urdf)):
                q_obs[i] = q_[cfg.robot_config.usd2urdf[i]]
                dq_obs[i] = dq[cfg.robot_config.usd2urdf[i]]

            # Obs layout: [omega(3), gvec(3), cmd(3), q(29), dq(29), action(29)] = 96
            obs = np.zeros([1, cfg.robot_config.num_single_obs], dtype=np.float32)
            obs[0, 0:3] = omega
            obs[0, 3:6] = gvec
            obs[0, 6] = cmd.vx
            obs[0, 7] = cmd.vy
            obs[0, 8] = cmd.dyaw
            obs[0, 9:38] = q_obs
            obs[0, 38:67] = dq_obs
            obs[0, 67:96] = action

            if is_first_frame:
                hist_obs = np.tile(obs, (cfg.robot_config.frame_stack, 1))
                is_first_frame = False
            else:
                hist_obs = np.concatenate((hist_obs[1:], obs.reshape(1, -1)), axis=0)

            policy_input = hist_obs.reshape(1, -1).astype(np.float32)
            with torch.inference_mode():
                action[:] = policy(torch.tensor(policy_input))[0].detach().numpy()

            target_q = action * cfg.robot_config.action_scale
            for i in range(len(cfg.robot_config.usd2urdf)):
                target_pos[cfg.robot_config.usd2urdf[i]] = target_q[i]
            target_pos = target_pos + cfg.robot_config.default_pos

            q_low_freq = q.copy()
            v_low_freq = v[:2].copy()
            omega_low_freq = omega[2].copy()

            time_data.append(step * cfg.sim_config.dt)
            commanded_joint_pos_data.append(target_pos.copy())
            actual_joint_pos_data.append(q_low_freq)
            tau_data.append(tau.copy())
            commanded_lin_vel_x_data.append(cmd.vx)
            commanded_lin_vel_y_data.append(cmd.vy)
            commanded_ang_vel_z_data.append(cmd.dyaw)
            actual_lin_vel_data.append(v_low_freq)
            actual_ang_vel_data.append(omega_low_freq)

            # CSV diagnostic row
            _euler = R.from_quat(quat).as_euler('xyz', degrees=False)
            _lf_force = data.cfrc_ext[left_foot_id][:3].copy()
            _rf_force = data.cfrc_ext[right_foot_id][:3].copy()
            _lf_fz = float(_lf_force[2])
            _rf_fz = float(_rf_force[2])
            _lf_fmag = float(np.linalg.norm(_lf_force))
            _rf_fmag = float(np.linalg.norm(_rf_force))
            _csv_row = [_t0_ns + (count_lowlevel // cfg.sim_config.decimation) * _step_dt_ns,
                        cmd.vx, cmd.vy, cmd.dyaw,
                        _euler[0], _euler[1], _euler[2],
                        omega[0], omega[1], omega[2],
                        v[0], v[1], v[2],
                        quat[3], quat[0], quat[1], quat[2],
                        int(_lf_fz > 5.0), int(_rf_fz > 5.0),
                        _lf_fz, _rf_fz, _lf_fmag, _rf_fmag]
            for _j in range(cfg.robot_config.num_actions):
                _csv_row += [action[_j], q[_j], dq[_j], tau[_j], target_pos[_j]]
            csv_writer.writerow(_csv_row)

            if headless:
                renderer.update_scene(data, camera=cam)
                img = renderer.render()
                out.write(img)
            else:
                viewer.render()

        target_vel = np.zeros((cfg.robot_config.num_actions), dtype=np.double)
        if getattr(cfg.sim_config, 'use_implicit', False):
            # kd handled implicitly via dof_damping; only apply kp explicitly
            tau = pd_control(target_pos, q, cfg.robot_config.kps, target_vel, dq * 0, cfg.robot_config.kds * 0)
        else:
            tau = pd_control(target_pos, q, cfg.robot_config.kps, target_vel, dq, cfg.robot_config.kds)
        tau = np.clip(tau, -cfg.robot_config.tau_limit, cfg.robot_config.tau_limit)
        # Use qfrc_applied (qpos order) instead of data.ctrl (actuator order)
        data.qfrc_applied[6:] = tau
        mujoco.mj_step(model, data)
        count_lowlevel += 1

    if headless:
        out.release()
    else:
        viewer.close()

    csv_file.close()
    print(f'CSV diagnostic saved to: {csv_path}')

    print("Simulation finished. Generating plots...")
    time_data = np.array(time_data)
    commanded_joint_pos_data = np.array(commanded_joint_pos_data)
    actual_joint_pos_data = np.array(actual_joint_pos_data)
    tau_data = np.array(tau_data)
    commanded_lin_vel_x_data = np.array(commanded_lin_vel_x_data)
    commanded_lin_vel_y_data = np.array(commanded_lin_vel_y_data)
    commanded_ang_vel_z_data = np.array(commanded_ang_vel_z_data)
    actual_lin_vel_data = np.array(actual_lin_vel_data)
    actual_ang_vel_data = np.array(actual_ang_vel_data)

    # Plot joint positions
    num_joints = cfg.robot_config.num_actions
    n_cols = 6
    n_rows = (num_joints + n_cols - 1) // n_cols
    fig1, axes1 = plt.subplots(n_rows, n_cols, figsize=(20, 3 * n_rows), sharex=True)
    axes1 = axes1.flatten()
    joint_names = [
        'lumbar_yaw', 'lumbar_roll', 'lumbar_pitch',
        'L_shoulder_pitch', 'L_shoulder_roll', 'L_shoulder_yaw',
        'L_elbow_pitch', 'L_elbow_yaw', 'L_wrist_pitch', 'L_wrist_roll',
        'R_shoulder_pitch', 'R_shoulder_roll', 'R_shoulder_yaw',
        'R_elbow_pitch', 'R_elbow_yaw', 'R_wrist_pitch', 'R_wrist_roll',
        'L_hip_pitch', 'L_hip_roll', 'L_hip_yaw', 'L_knee_pitch', 'L_ankle_pitch', 'L_ankle_roll',
        'R_hip_pitch', 'R_hip_roll', 'R_hip_yaw', 'R_knee_pitch', 'R_ankle_pitch', 'R_ankle_roll',
    ]
    for i in range(num_joints):
        ax = axes1[i]
        ax.plot(time_data, commanded_joint_pos_data[:, i], label='Cmd', linestyle='--')
        ax.plot(time_data, actual_joint_pos_data[:, i], label='Act')
        ax.set_title(joint_names[i], fontsize=8)
        ax.set_xlabel("Time [s]")
        ax.legend(fontsize=6)
        ax.grid(True)
    for i in range(num_joints, len(axes1)):
        fig1.delaxes(axes1[i])
    fig1.suptitle("X1_29 Joint Positions: Commanded vs Actual", fontsize=14)
    plt.tight_layout()
    fig1.savefig("joint_positions.png", dpi=150)

    # Plot base velocities
    fig2, axes2 = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    axes2[0].plot(time_data, commanded_lin_vel_x_data, label='Cmd Vx', linestyle='--')
    axes2[0].plot(time_data, actual_lin_vel_data[:, 0], label='Act Vx')
    axes2[0].set_title("Base Linear Velocity X")
    axes2[0].set_ylabel("[m/s]")
    axes2[0].legend()
    axes2[0].grid(True)

    axes2[1].plot(time_data, commanded_lin_vel_y_data, label='Cmd Vy', linestyle='--')
    axes2[1].plot(time_data, actual_lin_vel_data[:, 1], label='Act Vy')
    axes2[1].set_title("Base Linear Velocity Y")
    axes2[1].set_ylabel("[m/s]")
    axes2[1].legend()
    axes2[1].grid(True)

    axes2[2].plot(time_data, commanded_ang_vel_z_data, label='Cmd Dyaw', linestyle='--')
    axes2[2].plot(time_data, actual_ang_vel_data, label='Act Dyaw')
    axes2[2].set_title("Base Angular Velocity Z")
    axes2[2].set_xlabel("Time [s]")
    axes2[2].set_ylabel("[rad/s]")
    axes2[2].legend()
    axes2[2].grid(True)

    fig2.suptitle("X1_29 Base Velocities", fontsize=14)
    plt.tight_layout()
    fig2.savefig("base_velocities.png", dpi=150)
    print("Plots saved: joint_positions.png, base_velocities.png")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='X1_29 Sim2Sim Deployment.')
    parser.add_argument('--load_model', type=str, required=True, help='Path to JIT policy.')
    parser.add_argument('--headless', action='store_true', help='Run without GUI and save video.')
    args = parser.parse_args()

    class Sim2simCfg():
        class sim_config:
            mujoco_model_path = os.environ.get('X1_29_MJCF', os.path.join(X1_29_DATA_DIR, 'mjcf', 'mjmodel_x1_29dof_perfect_mirrored_sim_flat.xml'))
            sim_duration = 20.0
            dt = 0.005
            decimation = 4
            use_implicit = True  # mjINT_IMPLICIT + dof_damping for kd (best deployment config)

        class robot_config:
            # URDF/Isaac joint order: lumbar(3), L_arm(7), R_arm(7), L_leg(6), R_leg(6)
            kps = np.array([
                150, 150, 150,          # lumbar yaw/roll/pitch
                40, 40, 40, 30, 20, 15, 15,  # L shoulder/shoulder/shoulder/elbow/elbow/wrist/wrist
                40, 40, 40, 30, 20, 15, 15,  # R shoulder/shoulder/shoulder/elbow/elbow/wrist/wrist
                120, 100, 100, 180, 50, 50,  # L hip/hip/hip/knee/ankle/ankle
                120, 100, 100, 180, 50, 50,  # R hip/hip/hip/knee/ankle/ankle
            ], dtype=np.double)
            kds = np.array([
                5, 5, 5,                # lumbar
                2, 2, 2, 1.5, 1, 1, 1,  # L arm
                2, 2, 2, 1.5, 1, 1, 1,  # R arm
                4, 3.3, 3.3, 6, 2.5, 2.5,  # L leg
                4, 3.3, 3.3, 6, 2.5, 2.5,  # R leg
            ], dtype=np.double)
            default_pos = np.array([
                0, 0, 0,                          # lumbar
                0.2, 0, 0, 0.5, 0, 0, 0,          # L arm (shoulder_pitch=0.2, elbow_pitch=0.5)
                0.2, 0, 0, 0.5, 0, 0, 0,          # R arm
                0.4, 0.05, -0.31, 0.49, -0.21, 0, # L leg: 镜像对称 hip_pitch/roll/yaw
                -0.4, -0.05, 0.31, 0.49, -0.21, 0,# R leg: hip_pitch=-0.4 (镜像)
            ], dtype=np.double)
            tau_limit = np.array([
                120, 120, 120,          # lumbar
                20, 20, 20, 20, 20, 10, 10,  # L arm
                20, 20, 20, 20, 20, 10, 10,  # R arm
                150, 150, 150, 150, 60, 60,  # L leg
                150, 150, 150, 150, 60, 60,  # R leg
            ], dtype=np.double)
            frame_stack = 10
            num_single_obs = 96
            num_observations = 960
            num_actions = 29
            action_scale = 0.25
            # Isaac DOF = URDF = MuJoCo qpos order -> identity mapping
            usd2urdf = list(range(29))

    policy = torch.jit.load(args.load_model)
    run_mujoco(policy, Sim2simCfg(), args.headless)
