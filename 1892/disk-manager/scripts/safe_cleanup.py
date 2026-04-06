#!/usr/bin/env python3
"""
Safe cleanup runner for disk-manager skill.

Removes cache/recreatable artifacts from workspace with dry-run support.
Human mode includes ASCII summary bars.
"""

import argparse
import json
import os
import shutil
import time
from pathlib import Path

SAFE_REMOVE_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SAFE_FILE_SUFFIXES = {".pyc", ".pyo"}


def dir_size(path: Path) -> int:
    total = 0
    for root, _, files in os.walk(path, onerror=lambda e: None):
        for f in files:
            fp = Path(root) / f
            try:
                total += fp.stat().st_size
            except Exception:
                pass
    return total


def collect_targets(workspace: Path):
    targets = []
    for root, dirs, files in os.walk(workspace, onerror=lambda e: None):
        root_path = Path(root)

        for d in list(dirs):
            if d in SAFE_REMOVE_NAMES:
                p = root_path / d
                targets.append({
                    "path": str(p),
                    "kind": "dir",
                    "reason": f"safe-cache:{d}",
                    "size_bytes": dir_size(p),
                })

        for f in files:
            p = root_path / f
            if p.suffix in SAFE_FILE_SUFFIXES:
                try:
                    size = p.stat().st_size
                except Exception:
                    size = 0
                targets.append({
                    "path": str(p),
                    "kind": "file",
                    "reason": f"bytecode:{p.suffix}",
                    "size_bytes": size,
                })

    targets.sort(key=lambda x: x["size_bytes"], reverse=True)
    return targets


def apply_cleanup(targets, dry_run: bool):
    cleaned = []
    errors = []
    for t in targets:
        p = Path(t["path"])
        if not p.exists():
            continue

        if dry_run:
            cleaned.append({**t, "status": "would_remove"})
            continue

        try:
            if t["kind"] == "dir":
                shutil.rmtree(p)
            else:
                p.unlink(missing_ok=True)
            cleaned.append({**t, "status": "removed"})
        except Exception as e:
            errors.append({**t, "status": "error", "error": str(e)})

    return cleaned, errors


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


def print_human(report: dict):
    before = report["before_bytes"]
    freed = report["freed_bytes"]
    mode = "DRY RUN" if report["dry_run"] else "EXECUTED"

    print(f"SAFE CLEANUP ({mode})")
    print(f"Workspace: {report['workspace']}")
    print(f"Before: {fmt_bytes(before)}")
    if report["dry_run"]:
        print(f"Estimated freed: {fmt_bytes(freed)}")
    else:
        print(f"After:  {fmt_bytes(report['after_bytes'])}")
        print(f"Freed:  {fmt_bytes(freed)}")

    pct = (freed / before * 100) if before else 0
    print(f"Impact: [{bar(freed, before)}] {pct:5.2f}%")
    print(f"Targets: {report['targets_count']} | Cleaned: {report['cleaned_count']} | Errors: {report['errors_count']}")

    top = report.get("cleaned", [])[:10]
    if top:
        print("Top cleaned targets")
        for t in top:
            print(f"- {fmt_bytes(t.get('size_bytes', 0)):>9}  {t.get('path')}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', default='/data/workspace')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--json', action='store_true', help='print JSON report')
    args = parser.parse_args()

    workspace = Path(args.workspace)
    before = dir_size(workspace)

    targets = collect_targets(workspace)
    cleaned, errors = apply_cleanup(targets, args.dry_run)

    after = dir_size(workspace)
    freed = max(0, before - after) if not args.dry_run else sum(t["size_bytes"] for t in targets)

    report = {
        "workspace": str(workspace),
        "generated_at": int(time.time()),
        "dry_run": args.dry_run,
        "before_bytes": before,
        "after_bytes": after,
        "freed_bytes": freed,
        "targets_count": len(targets),
        "cleaned_count": len(cleaned),
        "errors_count": len(errors),
        "cleaned": cleaned,
        "errors": errors,
    }

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human(report)


if __name__ == '__main__':
    main()
