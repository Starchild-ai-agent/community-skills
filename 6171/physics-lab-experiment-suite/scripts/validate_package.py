#!/usr/bin/env python3
"""Validate an unpacked experiment package has all required files."""
import sys, os

REQUIRED = {
    "固件": [".ino"],
    "图纸": [".png"],
    "文档": ["采购清单", "材料尺寸清单", "调试与使用手册", "视频分镜脚本", "视频文字讲稿"],
    "教学文稿": [".docx", ".pptx"],
}

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <experiment_dir>")
        sys.exit(1)

    root = sys.argv[1]
    if not os.path.isdir(root):
        print(f"ERROR: Not a directory: {root}")
        sys.exit(1)

    missing = []
    for folder, patterns in REQUIRED.items():
        path = os.path.join(root, folder)
        if not os.path.isdir(path):
            missing.append(f"❌ Missing folder: {folder}/")
            continue
        files = os.listdir(path)
        for pat in patterns:
            if pat.startswith("."):
                if not any(f.endswith(pat) for f in files):
                    missing.append(f"❌ {folder}/: no file ending with {pat}")
            else:
                if not any(pat in f for f in files):
                    missing.append(f"❌ {folder}/: no file containing '{pat}'")

    if missing:
        print("Validation FAILED:")
        for m in missing:
            print(f"  {m}")
        sys.exit(1)
    else:
        total = sum(len(files) for _, _, files in os.walk(root))
        print(f"✅ Package validated: {root} ({total} files, all required components present)")


if __name__ == "__main__":
    main()