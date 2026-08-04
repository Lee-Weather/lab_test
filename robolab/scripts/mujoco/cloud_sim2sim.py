#!/usr/bin/env python3
"""Cloud sim2sim orchestration for GM platform.

Runs MuJoCo sim2sim with video recording in a GM container (no local
MuJoCo / RTX renderer needed). Packages the output video as a model_*.pt
so the GM SDK auto-uploads it and we can download it back locally.

Usage (GM startScript, single command constraint):
  gm-run lab_test/robolab/scripts/mujoco/cloud_sim2sim.py --checkpoint /personal/model_loaded.pt
"""
import os
import sys
import re
import glob
import shutil
import subprocess

# this file: <repo>/robolab/scripts/mujoco/cloud_sim2sim.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", ".."))

MUJOCO_SCRIPT = os.path.join(SCRIPT_DIR, "sim2sim_x1_29.py")
CONVERT_SCRIPT = os.path.join(SCRIPT_DIR, "convert_x1_29_checkpoint.py")
MJCF_SRC = os.path.join(REPO_ROOT, "czy", "data", "x1_29", "mjcf",
                        "mjmodel_x1_29dof_perfect_mirrored_sim_flat.xml")
MESHES_DIR = os.path.join(REPO_ROOT, "czy", "data", "x1_29", "meshes")
CLEAN_DIR = "/tmp/x1_29_mjcf_clean"


def run(cmd, **kw):
    print(f"[cloud_sim2sim] RUN: {' '.join(cmd)}", flush=True)
    subprocess.check_call(cmd, **kw)


def install_deps():
    run([sys.executable, "-m", "pip", "install", "--quiet",
         "mujoco", "scipy", "opencv-python-headless", "tqdm", "matplotlib"])


def clean_mjcf():
    os.makedirs(CLEAN_DIR, exist_ok=True)
    out = os.path.join(CLEAN_DIR, "mjmodel_x1_29dof_perfect_mirrored_sim_flat.xml")
    with open(MJCF_SRC, "r") as f:
        text = f.read()
    text = text.replace(' content_type="model/stl"', "")
    text = re.sub(r' actuatorfrcrange="[^"]*"', "", text)
    text = re.sub(r'meshdir="[^"]*"', f'meshdir="{CLEAN_DIR}/meshes/"', text)
    text = text.replace("<compiler ", '<compiler autolimits="true" ', 1)
    text = text.replace(
        "<visual>",
        '<visual><headlight diffuse="0.6 0.6 0.6" ambient="0.3 0.3 0.3" specular="0 0 0"/>',
        1,
    )
    text = text.replace("<option ", '<option offwidth="1920" offheight="1080" ', 1)
    with open(out, "w") as f:
        f.write(text)
    mesh_link = os.path.join(CLEAN_DIR, "meshes")
    if os.path.islink(mesh_link) or os.path.exists(mesh_link):
        shutil.rmtree(mesh_link)
    os.symlink(MESHES_DIR, mesh_link)
    print(f"[cloud_sim2sim] cleaned MJCF -> {out}", flush=True)
    return out


def convert_ckpt(ckpt_path, out_path):
    run([sys.executable, CONVERT_SCRIPT, "--checkpoint", ckpt_path, "--output", out_path])


def run_sim2sim(policy_path, mjcf_path, workdir):
    os.makedirs(workdir, exist_ok=True)
    env = dict(os.environ)
    env["X1_29_MJCF"] = mjcf_path
    env["MUJOCO_GL"] = "egl"
    env["__EGL_VENDOR_LIBRARY_FILENAMES"] = "/usr/share/glvnd/egl_vendor.d/10_nvidia.json"
    run([sys.executable, MUJOCO_SCRIPT, "--load_model", policy_path, "--headless"],
        cwd=workdir, env=env)
    video = os.path.join(workdir, "simulation.mp4")
    if not os.path.exists(video):
        raise RuntimeError("simulation.mp4 not generated")
    return video


def package_video(video_path):
    import numpy as np
    import torch
    with open(video_path, "rb") as f:
        raw = f.read()
    data = {
        "format": "mp4",
        "filename": os.path.basename(video_path),
        "bytes": np.frombuffer(raw, dtype=np.uint8),
    }
    tmp = "/tmp/model_sim2sim_video.pt"
    torch.save(data, tmp)
    print(f"[cloud_sim2sim] packaged {len(raw)} bytes -> model_sim2sim_video.pt", flush=True)
    candidates = []
    if os.path.isdir("/personal"):
        candidates.append("/personal/model_sim2sim_video.pt")
    candidates.append(os.path.join(os.getcwd(), "model_sim2sim_video.pt"))
    candidates.append(os.path.join(os.getcwd(), "logs", "rsl_rl", "x1_29_flat",
                                   "model_sim2sim_video.pt"))
    for c in candidates:
        try:
            os.makedirs(os.path.dirname(c), exist_ok=True)
            shutil.copy2(tmp, c)
            print(f"[cloud_sim2sim] packaged to {c}", flush=True)
        except Exception as e:
            print(f"[cloud_sim2sim] package {c} failed: {e}", flush=True)


def resolve_checkpoint(ckpt):
    if ckpt and os.path.exists(ckpt):
        return ckpt
    for d in ["/personal", os.getcwd()]:
        for pt in sorted(glob.glob(os.path.join(d, "**", "*.pt"), recursive=True)):
            b = os.path.basename(pt)
            if "model_" in b and "deploy" not in b and "sim2sim_video" not in b:
                return pt
    return None


def print_diag(workdir):
    """Print condensed rows from isaac_diag CSV to stdout as fallback data."""
    import csv as _csv
    files = glob.glob(os.path.join(workdir, "isaac_diag_*.csv"))
    if not files:
        print("[cloud_sim2sim] no isaac_diag CSV found", flush=True)
        return
    path = files[0]
    with open(path, "r") as f:
        rows = list(_csv.reader(f))
    print(f"[cloud_sim2sim] DIAG_CSV_BEGIN {path} rows={len(rows)-1}", flush=True)
    for i, row in enumerate(rows):
        if i == 0 or i % 10 == 0:
            print("|".join(row), flush=True)
    print("[cloud_sim2sim] DIAG_CSV_END", flush=True)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="")
    parser.add_argument("--workdir", default="/tmp/sim2sim_out")
    parser.add_argument("--skip-install", action="store_true")
    args = parser.parse_args()

    ckpt = resolve_checkpoint(args.checkpoint)
    if ckpt is None:
        print("[cloud_sim2sim] ERROR: checkpoint not found", file=sys.stderr)
        sys.exit(1)
    print(f"[cloud_sim2sim] checkpoint: {ckpt}", flush=True)

    if not args.skip_install:
        install_deps()

    os.makedirs(args.workdir, exist_ok=True)
    mjcf = clean_mjcf()
    policy = os.path.join(args.workdir, "policy_3000.pt")
    convert_ckpt(ckpt, policy)
    video = run_sim2sim(policy, mjcf, args.workdir)
    print_diag(args.workdir)
    package_video(video)
    print("[cloud_sim2sim] DONE", flush=True)


if __name__ == "__main__":
    main()
