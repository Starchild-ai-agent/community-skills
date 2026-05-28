#!/usr/bin/env python3
"""
OpenSea market surface for a collection.

Usage:
  python3 skills/opensea/scripts/get_market_surface.py doodles-official
"""

import json
import sys

sys.path.insert(0, "/data/workspace/skills/opensea")
from exports import os_listings_best, os_listings_all, os_offers_all


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: get_market_surface.py <collection_slug>")
        return 1

    slug = sys.argv[1]

    out = {
        "slug": slug,
        "best_listings": os_listings_best(slug, limit=20),
        "all_listings": os_listings_all(slug, limit=50),
        "all_offers": os_offers_all(slug, limit=50),
    }

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
