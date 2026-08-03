# Copyright (c) 2022-2025, The Isaac Lab Project Developers.
# Copyright (c) 2025-2026, The RoboLab Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import isaaclab.sim as sim_utils
from isaaclab.actuators import DelayedPDActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg

from robolab.assets import ISAAC_DATA_DIR, CZY_DATA_DIR

RPO_CFG = ArticulationCfg(
    spawn=sim_utils.UrdfFileCfg(
        asset_path=f"{ISAAC_DATA_DIR}/robots/roboparty/rpo/urdf/rpo.urdf",
        fix_base=False,
        activate_contact_sensors=True,
        replace_cylinders_with_capsules=True,
        joint_drive = sim_utils.UrdfConverterCfg.JointDriveCfg(
            gains=sim_utils.UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=0, damping=0)
        ),
        articulation_props = sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True,
            solver_position_iteration_count=8,
            solver_velocity_iteration_count=4,
        ),
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.75),
        joint_pos={
            "left_thigh_pitch_joint": -0.1,
            "left_knee_joint": 0.3,
            "left_ankle_pitch_joint": -0.2,
            "left_arm_pitch_joint": 0.18,
            "left_arm_roll_joint": 0.06,
            "left_elbow_pitch_joint": 0.78,
            "right_thigh_pitch_joint": -0.1,
            "right_knee_joint": 0.3,
            "right_ankle_pitch_joint": -0.2,
            "right_arm_pitch_joint": 0.18,
            "right_arm_roll_joint": -0.06,
            "right_elbow_pitch_joint": 0.78,
        },
        joint_vel={".*": 0.0},
    ),
    soft_joint_pos_limit_factor=0.90,
    actuators={
        "legs": DelayedPDActuatorCfg(
            joint_names_expr=[
                ".*_thigh_yaw_joint",
                ".*_thigh_roll_joint",
                ".*_thigh_pitch_joint",
                ".*_knee_joint",
                ".*torso.*",
            ],
            effort_limit_sim=120.0,
            velocity_limit_sim=25.0,
            stiffness={
                ".*_thigh_yaw_joint": 100.0,
                ".*_thigh_roll_joint": 100.0,
                ".*_thigh_pitch_joint": 100.0,
                ".*_knee_joint": 150.0,
                ".*torso.*": 150.0,
            },
            damping={
                ".*_thigh_yaw_joint": 3.3,
                ".*_thigh_roll_joint": 3.3,
                ".*_thigh_pitch_joint": 3.3,
                ".*_knee_joint": 5.0,
                ".*torso.*": 5.0,
            },
            armature=0.01,
            min_delay=0,
            max_delay=2,
        ),
        "feet": DelayedPDActuatorCfg(
            joint_names_expr=[".*_ankle_pitch_joint", ".*_ankle_roll_joint"],
            effort_limit_sim=27.0,
            velocity_limit_sim=8.0,
            stiffness=40.0,
            damping=2.0,
            armature=0.01,
            min_delay=0,
            max_delay=2,
        ),
        "shoulders": DelayedPDActuatorCfg(
            joint_names_expr=[
                ".*_arm_pitch_joint",
                ".*_arm_roll_joint",
                ".*_arm_yaw_joint",
            ],
            effort_limit_sim=27.0,
            velocity_limit_sim=8.0,
            stiffness=40.0,
            damping=2.0,
            armature=0.01,
            min_delay=0,
            max_delay=2,
        ),
        "arms": DelayedPDActuatorCfg(
            joint_names_expr=[
                ".*_elbow_pitch_joint",
                ".*_elbow_yaw_joint",
            ],
            stiffness={
                ".*_elbow_pitch_joint": 30.0,
                ".*_elbow_yaw_joint": 20.0,
            },
            damping={
                ".*_elbow_pitch_joint": 1.5,
                ".*_elbow_yaw_joint": 1.0,
            },
            effort_limit_sim=27.0,
            velocity_limit_sim=8.0,
            armature=0.01,
            min_delay=0,
            max_delay=2,
        ),
    },
)


RPO_LINKS = [
    "base_link",
    "left_thigh_yaw_link",
    "left_thigh_roll_link",
    "left_thigh_pitch_link",
    "left_knee_link",
    "left_ankle_pitch_link",
    "left_ankle_roll_link",
    "right_thigh_yaw_link",
    "right_thigh_roll_link",
    "right_thigh_pitch_link",
    "right_knee_link",
    "right_ankle_pitch_link",
    "right_ankle_roll_link",
    "torso_link",
    "left_arm_pitch_link",
    "left_arm_roll_link",
    "left_arm_yaw_link",
    "left_elbow_pitch_link",
    "left_elbow_yaw_link",
    "right_arm_pitch_link",
    "right_arm_roll_link",
    "right_arm_yaw_link",
    "right_elbow_pitch_link",
    "right_elbow_yaw_link",
]


X1_29_CFG = ArticulationCfg(
    spawn=sim_utils.UrdfFileCfg(
        asset_path=f"{CZY_DATA_DIR}/x1_29/urdf/X1_29DOF_perfect_mirrored.urdf",
        fix_base=False,
        activate_contact_sensors=True,
        replace_cylinders_with_capsules=True,
        joint_drive=sim_utils.UrdfConverterCfg.JointDriveCfg(
            gains=sim_utils.UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=0, damping=0)
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=True,
            solver_position_iteration_count=8,
            solver_velocity_iteration_count=4,
        ),
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=False,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.65),
        joint_pos={
            # 左右腿镜像对称 (FK验证: X1部署值, 完美对称 dx=0 dz=0)
            "left_hip_pitch_joint": 0.4,
            "left_hip_roll_joint": 0.05,
            "left_hip_yaw_joint": -0.31,
            "left_knee_pitch_joint": 0.49,
            "left_ankle_pitch_joint": -0.21,
            "right_hip_pitch_joint": -0.4,
            "right_hip_roll_joint": -0.05,
            "right_hip_yaw_joint": 0.31,
            "right_knee_pitch_joint": 0.49,
            "right_ankle_pitch_joint": -0.21,
            "left_shoulder_pitch_joint": 0.2,
            "left_elbow_pitch_joint": 0.5,
            "right_shoulder_pitch_joint": 0.2,
            "right_elbow_pitch_joint": 0.5,
        },
        joint_vel={".*": 0.0},
    ),
    soft_joint_pos_limit_factor=0.90,
    actuators={
        "legs": DelayedPDActuatorCfg(
            joint_names_expr=[
                ".*_hip_pitch_joint",
                ".*_hip_roll_joint",
                ".*_hip_yaw_joint",
                ".*_knee_pitch_joint",
            ],
            effort_limit_sim=150.0,
            velocity_limit_sim=25.0,
            stiffness={
                ".*_hip_pitch_joint": 120.0,
                ".*_hip_roll_joint": 100.0,
                ".*_hip_yaw_joint": 100.0,
                ".*_knee_pitch_joint": 180.0,
            },
            damping={
                ".*_hip_pitch_joint": 4.0,
                ".*_hip_roll_joint": 3.3,
                ".*_hip_yaw_joint": 3.3,
                ".*_knee_pitch_joint": 6.0,
            },
            armature=0.01,
            min_delay=0,
            max_delay=2,
        ),
        "feet": DelayedPDActuatorCfg(
            joint_names_expr=[".*_ankle_pitch_joint", ".*_ankle_roll_joint"],
            effort_limit_sim=60.0,
            velocity_limit_sim=10.0,
            stiffness=50.0,
            damping=2.5,
            armature=0.01,
            min_delay=0,
            max_delay=2,
        ),
        "lumbar": DelayedPDActuatorCfg(
            joint_names_expr=[
                "lumbar_yaw_joint",
                "lumbar_roll_joint",
                "lumbar_pitch_joint",
            ],
            effort_limit_sim=120.0,
            velocity_limit_sim=8.9,
            stiffness=150.0,
            damping=5.0,
            armature=0.01,
            min_delay=0,
            max_delay=2,
        ),
        "shoulders": DelayedPDActuatorCfg(
            joint_names_expr=[
                ".*_shoulder_pitch_joint",
                ".*_shoulder_roll_joint",
                ".*_shoulder_yaw_joint",
            ],
            effort_limit_sim=20.0,
            velocity_limit_sim=13.61,
            stiffness=40.0,
            damping=2.0,
            armature=0.005,
            min_delay=0,
            max_delay=2,
        ),
        "arms": DelayedPDActuatorCfg(
            joint_names_expr=[
                ".*_elbow_pitch_joint",
                ".*_elbow_yaw_joint",
            ],
            stiffness={
                ".*_elbow_pitch_joint": 30.0,
                ".*_elbow_yaw_joint": 20.0,
            },
            damping={
                ".*_elbow_pitch_joint": 1.5,
                ".*_elbow_yaw_joint": 1.0,
            },
            effort_limit_sim=20.0,
            velocity_limit_sim=13.61,
            armature=0.005,
            min_delay=0,
            max_delay=2,
        ),
        "wrists": DelayedPDActuatorCfg(
            joint_names_expr=[
                ".*_wrist_pitch_joint",
                ".*_wrist_roll_joint",
            ],
            effort_limit_sim=10.0,
            velocity_limit_sim=2.5,
            stiffness=15.0,
            damping=1.0,
            armature=0.001,
            min_delay=0,
            max_delay=2,
        ),
    },
)


X1_29_LINKS = [
    "base_link",
    "lumbar_yaw_link",
    "lumbar_roll_link",
    "lumbar_pitch_link",
    "left_shoulder_pitch_link",
    "left_shoulder_roll_link",
    "left_shoulder_yaw_link",
    "left_elbow_pitch_link",
    "left_elbow_yaw_link",
    "left_wrist_pitch_link",
    "left_wrist_roll_link",
    "right_shoulder_pitch_link",
    "right_shoulder_roll_link",
    "right_shoulder_yaw_link",
    "right_elbow_pitch_link",
    "right_elbow_yaw_link",
    "right_wrist_pitch_link",
    "right_wrist_roll_link",
    "left_hip_pitch_link",
    "left_hip_roll_link",
    "left_hip_yaw_link",
    "left_knee_pitch_link",
    "left_ankle_pitch_link",
    "left_ankle_roll_link",
    "right_hip_pitch_link",
    "right_hip_roll_link",
    "right_hip_yaw_link",
    "right_knee_pitch_link",
    "right_ankle_pitch_link",
    "right_ankle_roll_link",
]
