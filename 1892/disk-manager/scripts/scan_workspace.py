#!/usr/bin/env python3
"""
Workspace disk scanner for disk-manager skill.

Outputs JSON with categorized cleanup opportunities.
Human mode includes ASCII visualization bars.
"""

import argparse
import json
import os
import time
from pathlib import Path

WORKSPACE = Path('/data/workspace')

SAFE_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache"}
RECREATABLE_DIR_NAMES = {"node_modules", "dist", "build", ".next", "target"}


def dir_size_bytes(path: Path) -> int:
    total = 0
    try:
        for root, _, files in os.walk(path, onerror=lambda e: None):
            for f in files:
                fp = Path(root) / f
                try:
                    total += fp.stat().st_size
                except Exception:
                    pass
    except Exception:
        pass
    return total


def top_level_usage(workspace: Path):
    items = []
    for p in workspace.iterdir():
        if p.name.startswith('.'):
            continue
        try:
            size = dir_size_bytes(p) if p.is_dir() else p.stat().st_size
            items.append({"path": str(p), "size_bytes": size})
        except Exception:
            continue
    items.sort(key=lambda x: x["size_bytes"], reverse=True)
    return items


def find_dirs_by_name(workspace: Path, names):
    found = []
    for root, dirs, _ in os.walk(workspace, onerror=lambda e: None):
        root_path = Path(root)
        for d in list(dirs):
            if d in names:
                dp = root_path / d
                size = dir_size_bytes(dp)
                try:
                    mtime = int(dp.stat().st_mtime)
                except Exception:
                    mtime = 0
                found.append({"path": str(dp), "size_bytes": size, "mtime": mtime})
    found.sort(key=lambda x: x["size_bytes"], reverse=True)
    return found


def find_large_files(workspace: Path, min_mb: int):
    threshold = min_mb * 1024 * 1024
    found = []
    for root, _, files in os.walk(workspace, onerror=lambda e: None):
        for f in files:
            fp = Path(root) / f
            try:
                st = fp.stat()
            except Exception:
                continue
            if st.st_size >= threshold:
                found.append({
                    "path": str(fp),
                    "size_bytes": st.st_size,
                    "mtime": int(st.st_mtime),
                })
    found.sort(key=lambda x: x["size_bytes"], reverse=True)
    return found


def find_old_files(root: Path, older_than_days: int):
    cutoff = time.time() - older_than_days * 86400
    if not root.exists():
        return []
    found = []
    for r, _, files in os.walk(root, onerror=lambda e: None):
        for f in files:
            fp = Path(r) / f
            try:
                st = fp.stat()
            except Exception:
                continue
            if st.st_mtime < cutoff:
                found.append({
                    "path": str(fp),
                    "size_bytes": st.st_size,
                    "mtime": int(st.st_mtime),
                })
    found.sort(key=lambda x: x["size_bytes"], reverse=True)
    return found


def summarize_size(items):
    return sum(i.get("size_bytes", 0) for i in items)


def fmt_bytes(n: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    v = float(max(0, n))
    for u in units:
        if v < 1024 or u == units[-1]:
            return f"{v:.1f} {u}" if u != "B" else f"{int(v)} B"
        v /= 1024
    return f"{n} B"


def bar(part: int, whole: int, width: int = 24) -> str:
    if whole <= 0:
        filled = 0
    else:
        filled = int(round((part / whole) * width))
    filled = max(0, min(width, filled))
    return "█" * filled + "░" * (width - filled)


def print_human(report: dict, top_n: int = 8):
    totals = report["totals"]
    total = totals["top_level_total_bytes"]
    safe = totals["safe_clean_bytes"]
    rec = totals["recreatable_bytes"]
    large = totals["large_files_bytes"]
    old = totals["old_output_bytes"]

    print("DISK MANAGER SCAN")
    print(f"Workspace: {report['workspace']}")
    print(f"Total scanned: {fmt_bytes(total)} ({total} bytes)")
    print()

    rows = [
        ("Safe to clean", safe),
        ("Recreatable", rec),
        ("Large files", large),
        ("Old output", old),
    ]

    print("Category view")
    for label, value in rows:
        pct = (value / total * 100) if total else 0
        print(f"- {label:<13} [{bar(value, total)}] {pct:5.1f}%  {fmt_bytes(value)}")
    print()

    print(f"Top {top_n} heavy paths")
    for item in report["top_level"][:top_n]:
        value = item["size_bytes"]
        pct = (value / total * 100) if total else 0
        print(f"- [{bar(value, total, width=18)}] {pct:5.1f}%  {fmt_bytes(value):>9}  {item['path']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', default=str(WORKSPACE))
    parser.add_argument('--large-file-mb', type=int, default=100)
    parser.add_argument('--old-days', type=int, default=30)
    parser.add_argument('--json', action='store_true', help='print JSON only')
    args = parser.parse_args()

    workspace = Path(args.workspace)

    top = top_level_usage(workspace)
    safe_dirs = find_dirs_by_name(workspace, SAFE_DIR_NAMES)
    recreatable_dirs = find_dirs_by_name(workspace, RECREATABLE_DIR_NAMES)
    large_files = find_large_files(workspace, args.large_file_mb)
    old_output = find_old_files(workspace / 'output', args.old_days)

    report = {
        "workspace": str(workspace),
        "generated_at": int(time.time()),
        "totals": {
            "top_level_total_bytes": summarize_size(top),
            "safe_clean_bytes": summarize_size(safe_dirs),
            "recreatable_bytes": summarize_size(recreatable_dirs),
            "large_files_bytes": summarize_size(large_files),
            "old_output_bytes": summarize_size(old_output),
        },
        "top_level": top[:25],
        "safe_to_clean": safe_dirs,
        "recreatable": recreatable_dirs,
        "large_files": large_files,
        "old_output": old_output,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)


if __name__ == '__main__':
    main()
