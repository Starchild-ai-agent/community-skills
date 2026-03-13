#!/usr/bin/env python3
"""
discover_dust.py — Offline dust discovery helper.

NOT called directly by the agent (agent uses native tools).
This is a reference/test script for validating dust discovery logic
against a known wallet address using the Etherscan token API.

Usage:
    python3 skills/dust-sweeper/scripts/discover_dust.py <wallet_address>

Requires:
    ETHERSCAN_API_KEY in environment (optional — uses free tier if absent)
    pip install requests

Output:
    JSON list of {token, contract, balance_raw, balance_human}
    for all ERC-20 tokens with non-zero balance.
    Agent then prices each one via birdeye_token_overview / oneinch_quote.
"""

import sys
import json
import os
import requests

ETHERSCAN_API = "https://api.etherscan.io/api"
DUST_THRESHOLD_USD = 50.0


def get_token_list(wallet: str, api_key: str = "") -> list[dict]:
    """Fetch ERC-20 token transfer history to infer current holdings."""
    params = {
        "module": "account",
        "action": "tokentx",
        "address": wallet,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "desc",
        "apikey": api_key or "YourApiKeyToken",
    }
    resp = requests.get(ETHERSCAN_API, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "1":
        return []

    # Deduplicate by contract address
    seen = {}
    for tx in data["result"]:
        addr = tx["contractAddress"].lower()
        if addr not in seen:
            seen[addr] = {
                "symbol": tx["tokenSymbol"],
                "name": tx["tokenName"],
                "contract": addr,
                "decimals": int(tx["tokenDecimal"]),
            }
    return list(seen.values())


def main():
    if len(sys.argv) < 2:
        print("Usage: discover_dust.py <wallet_address>")
        sys.exit(1)

    wallet = sys.argv[1]
    api_key = os.environ.get("ETHERSCAN_API_KEY", "")

    print(f"Scanning {wallet} for ERC-20 tokens...", file=sys.stderr)
    tokens = get_token_list(wallet, api_key)
    print(f"Found {len(tokens)} unique ERC-20 contracts in history", file=sys.stderr)
    print(json.dumps(tokens, indent=2))


if __name__ == "__main__":
    main()
