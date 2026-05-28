#!/usr/bin/env python3
"""
Poll OpenSea transaction receipt endpoint until a terminal state or timeout.

Usage:
  python3 skills/opensea/scripts/poll_tx_receipt.py '<swap_quote_json>' --tx-hash 0xabc... --chain ethereum --swap-provider LIFI --interval 3 --max-attempts 40
"""

import argparse
import json
import sys
import time

sys.path.insert(0, "/data/workspace/skills/opensea")
from exports import os_transaction_receipt


def _is_terminal(receipt: dict) -> bool:
    # API schema may evolve; use defensive checks.
    status = str(receipt.get("status", "")).lower()
    tx_status = str(receipt.get("transaction_status", "")).lower()
    state = str(receipt.get("state", "")).lower()

    terminal_markers = {
        "confirmed", "success", "succeeded", "failed", "reverted", "dropped", "not_found"
    }
    return (
        status in terminal_markers
        or tx_status in terminal_markers
        or state in terminal_markers
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("swap_quote_json", help="Inline JSON string for swap_quote, or @/path/to/quote.json")
    parser.add_argument("--tx-hash", default=None)
    parser.add_argument("--chain", default=None)
    parser.add_argument("--swap-provider", default=None)
    parser.add_argument("--relay-request-id", default=None)
    parser.add_argument("--request-id", default=None)
    parser.add_argument("--interval", type=int, default=3)
    parser.add_argument("--max-attempts", type=int, default=40)
    args = parser.parse_args()

    if args.swap_quote_json.startswith("@"):
        with open(args.swap_quote_json[1:], "r", encoding="utf-8") as f:
            swap_quote = json.load(f)
    else:
        swap_quote = json.loads(args.swap_quote_json)

    tx_identifiers = None
    if args.tx_hash:
        if not args.chain:
            raise SystemExit("--chain is required when --tx-hash is provided")
        tx_entry = {"transaction_hash": args.tx_hash, "chain": args.chain}
        if args.swap_provider:
            tx_entry["swap_provider"] = args.swap_provider
        tx_identifiers = [tx_entry]

    last = None
    for i in range(1, args.max_attempts + 1):
        last = os_transaction_receipt(
            swap_quote=swap_quote,
            transaction_identifiers=tx_identifiers,
            relay_request_id=args.relay_request_id,
            request_id=args.request_id,
        )
        print(json.dumps({"attempt": i, "receipt": last}, indent=2))
        if _is_terminal(last):
            return 0
        time.sleep(args.interval)

    print(json.dumps({"warning": "timeout without terminal status", "last": last}, indent=2))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
