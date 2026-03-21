#!/usr/bin/env python3
"""Verify skills.json fully covers all SKILL.md files in repo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "skills.json"


def list_skill_files() -> set[str]:
    found: set[str] = set()
    for p in ROOT.rglob("SKILL.md"):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith(".git/") or rel.startswith(".github/"):
            continue
        found.add(rel)
    return found


def main() -> int:
    if not INDEX_PATH.exists():
        print("ERROR: skills.json does not exist")
        return 1

    with INDEX_PATH.open("r", encoding="utf-8") as f:
        data = json.load(f)

    skills = data.get("skills", [])
    indexed_paths = {s.get("path", "") for s in skills if isinstance(s, dict)}
    actual_paths = list_skill_files()

    missing = sorted(actual_paths - indexed_paths)
    stale = sorted(indexed_paths - actual_paths)

    print(f"actual SKILL.md files: {len(actual_paths)}")
    print(f"indexed skills:        {len(indexed_paths)}")

    if missing:
        print("\nMISSING paths (in repo but not in skills.json):")
        for p in missing:
            print(f"  - {p}")

    if stale:
        print("\nSTALE paths (in skills.json but not in repo):")
        for p in stale:
            print(f"  - {p}")

    if missing or stale:
        print("\nFAIL: skills.json is out of sync")
        return 1

    print("\nPASS: skills.json fully covers all community skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
