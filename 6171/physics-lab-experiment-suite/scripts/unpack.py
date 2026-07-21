#!/usr/bin/env python3
"""Unpack a physics experiment asset to a target directory."""
import sys, os, tarfile, shutil

EXPERIMENTS = {
    "pendulum-g": "pendulum-g.tar.gz",
    "acoustic-levitation": "acoustic-levitation.tar.gz",
    "centripetal-force": "centripetal-force.tar.gz",
    "electromagnetic-damping": "electromagnetic-damping.tar.gz",
}

def main():
    if len(sys.argv) < 2 or sys.argv[1] not in EXPERIMENTS:
        print(f"Usage: {sys.argv[0]} <experiment> [output_dir]")
        print(f"Experiments: {', '.join(EXPERIMENTS.keys())}")
        sys.exit(1)

    name = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else f"output/{name}"
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    archive = os.path.join(skill_dir, "assets", EXPERIMENTS[name])

    if not os.path.exists(archive):
        print(f"ERROR: Archive not found: {archive}")
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    with tarfile.open(archive) as tf:
        tf.extractall(out_dir)

    # Count files
    count = sum(len(files) for _, _, files in os.walk(out_dir))
    print(f"✅ Unpacked {name} → {out_dir}/ ({count} files)")


if __name__ == "__main__":
    main()