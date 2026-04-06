#!/usr/bin/env python3
"""
Archive a project folder while excluding recreatable heavy directories.
"""

import argparse
import json
import tarfile
import time
from pathlib import Path

EXCLUDES = {"node_modules", ".next", "dist", "build", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def should_exclude(path: Path) -> bool:
    return any(part in EXCLUDES for part in path.parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', default='/data/workspace')
    parser.add_argument('--project', required=True, help='project folder relative to workspace')
    parser.add_argument('--output-dir', default='/data/workspace/output/archives')
    args = parser.parse_args()

    workspace = Path(args.workspace)
    project = workspace / args.project
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not project.exists() or not project.is_dir():
        raise SystemExit(f'Project not found: {project}')

    ts = time.strftime('%Y%m%d-%H%M%S')
    archive_path = output_dir / f'{project.name}-{ts}.tar.gz'

    with tarfile.open(archive_path, 'w:gz') as tf:
        for item in project.rglob('*'):
            rel = item.relative_to(workspace)
            if should_exclude(rel):
                continue
            tf.add(item, arcname=str(rel), recursive=False)

    print(json.dumps({
        "status": "ok",
        "project": str(project),
        "archive": str(archive_path),
        "excluded_names": sorted(list(EXCLUDES)),
    }, indent=2))


if __name__ == '__main__':
    main()
