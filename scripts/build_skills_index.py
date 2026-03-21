#!/usr/bin/env python3
"""Rebuild community skills.json from all SKILL.md files in the repo.

- Discovers SKILL.md recursively (any depth)
- Reads YAML-like frontmatter fields: name, version, description
- Falls back to path-derived defaults when missing
- Writes deterministic, path-sorted output
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "skills.json"

FRONTMATTER_RE = re.compile(r"^---\s*\n([\s\S]*?)\n---", re.MULTILINE)
FIELD_RE_TEMPLATE = r"^{}:\s*[\"']?(.*?)[\"']?\s*$"


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    fm = match.group(1)
    data: dict[str, str] = {}
    for key in ("name", "version", "description"):
        field_re = re.compile(FIELD_RE_TEMPLATE.format(re.escape(key)), re.MULTILINE)
        m = field_re.search(fm)
        if m:
            data[key] = m.group(1).strip().strip('"').strip("'")
    return data


def iter_skill_files(root: Path):
    for path in sorted(root.rglob("SKILL.md")):
        rel = path.relative_to(root)
        rel_str = rel.as_posix()
        if rel_str.startswith(".git/") or rel_str.startswith(".github/"):
            continue
        yield path, rel


def fallback_name(rel: Path) -> str:
    parts = rel.parts
    # Expected: namespace/.../SKILL.md
    namespace = parts[0] if len(parts) >= 2 else "unknown"
    slug = parts[-2] if len(parts) >= 2 else "unknown"
    return f"@{namespace}/{slug}"


def build_index(root: Path) -> dict:
    skills = []

    for path, rel in iter_skill_files(root):
        content = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)

        skills.append(
            {
                "name": fm.get("name") or fallback_name(rel),
                "path": rel.as_posix(),
                "version": fm.get("version") or "1.0.0",
                "description": fm.get("description") or "",
            }
        )

    skills.sort(key=lambda x: x["path"])
    return {"registry": "starchild-community", "skills": skills}


def main() -> None:
    index = build_index(ROOT)
    OUTPUT.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Rebuilt {OUTPUT.name}: {len(index['skills'])} skills")


if __name__ == "__main__":
    main()
