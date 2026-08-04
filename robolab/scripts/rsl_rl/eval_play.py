#!/usr/bin/env python3
"""Cloud play evaluation wrapper for GM platform.

Runs play.py with checkpoint copied to /personal/ so that recorded videos
automatically land in /personal/videos/play/ (downloadable via gm task storage).

Usage (in GM startScript):
  gm-run lab_test/robolab/scripts/rsl_rl/eval_play.py \
      --task=RPO-Flat --video --video_length=500 --num_envs=1 --headless
"""
import os
import sys
import glob
import shutil
import subprocess

PERSONAL_DIR = "/personal"


def resolve_checkpoint():
    """Find checkpoint: explicit --checkpoint, or search /personal/ and cwd."""
    if "--checkpoint" in sys.argv:
        idx = sys.argv.index("--checkpoint")
        ckpt = sys.argv[idx + 1]
        if os.path.exists(ckpt):
            return ckpt
    # GM resume mounts checkpoint; search likely locations
    search_dirs = [PERSONAL_DIR, os.getcwd()]
    for d in search_dirs:
        for pt in sorted(glob.glob(os.path.join(d, "**", "*.pt"), recursive=True)):
            bname = os.path.basename(pt)
            if "model_" in bname and "deploy" not in bname:
                return pt
    return None


def main():
    ckpt = resolve_checkpoint()
    if ckpt is None:
        print("[eval_play] ERROR: No checkpoint found in /personal/ or cwd", file=sys.stderr)
        sys.exit(1)

    # Copy checkpoint to /personal/ so play.py writes video to /personal/videos/play/
    os.makedirs(PERSONAL_DIR, exist_ok=True)
    dst = os.path.join(PERSONAL_DIR, "model_loaded.pt")
    if os.path.abspath(ckpt) != os.path.abspath(dst):
        shutil.copy2(ckpt, dst)
    print(f"[eval_play] Checkpoint ready: {dst}")

    # Set --checkpoint to /personal copy
    if "--checkpoint" in sys.argv:
        idx = sys.argv.index("--checkpoint")
        sys.argv[idx + 1] = dst
    else:
        sys.argv.extend(["--checkpoint", dst])

    print(f"[eval_play] Video will save to: {PERSONAL_DIR}/videos/play/")

    # Delegate to play.py (must be separate process for AppLauncher)
    play_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "play.py")
    result = subprocess.run([sys.executable, play_script] + sys.argv[1:])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
