#!/usr/bin/env python3
"""
OpenSea smoke test (read-only).

Usage:
  python3 skills/opensea/scripts/smoke_test.py
"""

import json
import sys

sys.path.insert(0, "/data/workspace/skills/opensea")
from exports import os_search, os_collections_top, os_collection_stats


def main() -> int:
    report = {"ok": False, "checks": []}

    try:
        top = os_collections_top(limit=3)
        report["checks"].append({"name": "collections_top", "ok": True, "keys": list(top.keys())})
    except Exception as e:
        report["checks"].append({"name": "collections_top", "ok": False, "error": str(e)})

    try:
        s = os_search("doodles", limit=3)
        report["checks"].append({"name": "search", "ok": True, "keys": list(s.keys())})
    except Exception as e:
        report["checks"].append({"name": "search", "ok": False, "error": str(e)})

    try:
        st = os_collection_stats("doodles-official")
        report["checks"].append({"name": "collection_stats", "ok": True, "keys": list(st.keys())})
    except Exception as e:
        report["checks"].append({"name": "collection_stats", "ok": False, "error": str(e)})

    report["ok"] = all(c["ok"] for c in report["checks"])
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
