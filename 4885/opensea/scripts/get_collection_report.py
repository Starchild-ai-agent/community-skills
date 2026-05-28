#!/usr/bin/env python3
"""
OpenSea collection report.

Usage:
  python3 skills/opensea/scripts/get_collection_report.py doodles-official
"""

import json
import sys

sys.path.insert(0, "/data/workspace/skills/opensea")
from exports import (
    os_collection,
    os_collection_stats,
    os_collection_floor_prices,
    os_events_by_collection,
)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: get_collection_report.py <collection_slug>")
        return 1

    slug = sys.argv[1]

    out = {
        "slug": slug,
        "collection": os_collection(slug),
        "stats": os_collection_stats(slug),
        "floor_prices": os_collection_floor_prices(slug, interval="1d"),
        "recent_sales_events": os_events_by_collection(slug, event_type="sale", limit=20),
    }

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
