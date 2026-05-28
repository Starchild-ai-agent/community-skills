#!/usr/bin/env python3
"""
OpenSea NFT snapshot.

Usage:
  python3 skills/opensea/scripts/get_nft_snapshot.py ethereum 0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d 1 boredapeyachtclub
"""

import json
import sys

sys.path.insert(0, "/data/workspace/skills/opensea")
from exports import os_nft, os_events_by_nft, os_best_offer_for_nft, os_listings_best


def main() -> int:
    if len(sys.argv) < 5:
        print("Usage: get_nft_snapshot.py <chain> <contract> <identifier> <collection_slug>")
        return 1

    chain = sys.argv[1]
    contract = sys.argv[2]
    identifier = sys.argv[3]
    slug = sys.argv[4]

    out = {
        "chain": chain,
        "contract": contract,
        "identifier": identifier,
        "nft": os_nft(chain, contract, identifier),
        "events": os_events_by_nft(chain, contract, identifier, limit=20),
        "best_offer": os_best_offer_for_nft(slug, identifier),
        "best_listings_on_collection": os_listings_best(slug, limit=10),
    }

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
