#!/usr/bin/env python3
"""Detect already-configured BYOK custom models the user can reuse for the
TEE agent's LLM. The agent inside the CVM speaks OpenAI-compatible HTTP, so
only `wire: openai` entries with a present api_key_env are compatible.

Usage:  python3 detect-byok.py
Output: JSON list to stdout — empty list = no compatible BYOK, run the popup.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

WORKSPACE = Path(os.environ.get("WORKSPACE_DIR", "/data/workspace"))
CONFIG = WORKSPACE / "config" / "custom_models.yaml"
ENVFILE = WORKSPACE / ".env"


def load_env_keys() -> set[str]:
    keys: set[str] = set()
    if not ENVFILE.exists():
        return keys
    for ln in ENVFILE.read_text().splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#") or "=" not in ln:
            continue
        keys.add(ln.split("=", 1)[0].strip())
    return keys


def load_models() -> list[dict]:
    if not CONFIG.exists():
        return []
    try:
        import yaml  # type: ignore
    except ImportError:
        # Fall back to a minimal parser — custom_models.yaml is a flat list of dicts.
        return _parse_minimal_yaml(CONFIG.read_text())
    data = yaml.safe_load(CONFIG.read_text()) or {}
    return data.get("custom_models", []) or []


def _parse_minimal_yaml(text: str) -> list[dict]:
    """Tolerant fallback when PyYAML is missing. Only handles the shape this file
    actually has: top-level `custom_models:` then list of `- key: val` entries
    with 2-space indented scalars. Good enough for filtering by wire/id."""
    out: list[dict] = []
    cur: dict | None = None
    in_list = False
    for raw in text.splitlines():
        if raw.strip() == "custom_models:":
            in_list = True
            continue
        if not in_list:
            continue
        if raw.startswith("- "):
            if cur is not None:
                out.append(cur)
            cur = {}
            k, _, v = raw[2:].partition(":")
            if v.strip():
                cur[k.strip()] = v.strip()
            continue
        if cur is None:
            continue
        # Only capture top-level scalars on the entry (skip nested dicts).
        if raw.startswith("  ") and not raw.startswith("    "):
            line = raw[2:]
            if ":" in line:
                k, _, v = line.partition(":")
                v = v.strip()
                if v and not v.startswith(("{", "[")):
                    cur[k.strip()] = v
    if cur is not None:
        out.append(cur)
    return out


def main() -> int:
    env_keys = load_env_keys()
    models = load_models()
    out = []
    for m in models:
        wire = (m.get("wire") or "").lower()
        if wire != "openai":  # agent app.py is OpenAI-compatible only
            continue
        key_env = m.get("api_key_env")
        if not key_env or key_env not in env_keys:
            continue
        base_url = (m.get("base_url") or "").rstrip("/")
        if not base_url:
            continue
        out.append({
            "id": m.get("id", ""),
            "label": m.get("name", m.get("id", "")),
            "base_url": base_url,
            "model": m.get("upstream_model", ""),
            "key_env": key_env,
        })
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
