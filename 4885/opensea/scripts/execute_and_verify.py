#!/usr/bin/env python3
"""
Execute OpenSea swap transactions with wallet_transfer and verify via OpenSea receipt API.

Usage:
  python3 skills/opensea/scripts/execute_and_verify.py \
    --from-chain arbitrum \
    --from-token 0xaf88d065e77c8cc2239327c5edb3a432268e5831 \
    --from-amount 1000000 \
    --to-chain arbitrum \
    --to-token 0x82af49447d8a07e3bd95bd0d56f35241523fbab1 \
    --wallet 0xYourWallet \
    --chain-id 42161

Notes:
- Requires OPENSEA_API_KEY in env.
- This script signs + broadcasts on-chain transactions.
- wallet_transfer endpoint must be available in current environment.
"""

import argparse
import json
import sys
import uuid
from urllib.request import Request, urlopen
from urllib.error import HTTPError

sys.path.insert(0, "/data/workspace/skills/opensea")
from exports import os_swap_execute, os_transaction_receipt

WALLET_TOOL_URL = "http://localhost:8000/api/wallet/transfer"


def wallet_transfer_http(to: str, data: str, chain_id: int, amount: str = "0"):
    payload = {
        "to": to,
        "amount": amount,
        "chain_id": chain_id,
        "data": data,
    }
    req = Request(
        WALLET_TOOL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"wallet_transfer HTTP {e.code}: {body}")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--from-chain", required=True)
    p.add_argument("--from-token", required=True)
    p.add_argument("--from-amount", required=True)
    p.add_argument("--to-chain", required=True)
    p.add_argument("--to-token", required=True)
    p.add_argument("--wallet", required=True)
    p.add_argument("--chain-id", type=int, required=True)
    p.add_argument("--slippage", type=float, default=0.01)
    args = p.parse_args()

    execute_payload = {
        "address": args.wallet,
        "from_assets": [{
            "chain": args.from_chain,
            "contract": args.from_token,
            "amount": args.from_amount,
        }],
        "to_assets": [{
            "chain": args.to_chain,
            "contract": args.to_token,
            "amount": "0",
        }],
        "slippage_tolerance": args.slippage,
    }

    execute_resp = os_swap_execute(execute_payload)
    quote = execute_resp.get("quote", {})
    txs = execute_resp.get("transactions", [])
    if not txs:
        raise RuntimeError("No transactions returned by OpenSea execute endpoint")

    transfer_results = []
    tx_identifiers = []
    for i, tx in enumerate(txs, 1):
        result = wallet_transfer_http(
            to=tx.get("to"),
            data=tx.get("data", ""),
            chain_id=args.chain_id,
            amount=tx.get("value", "0"),
        )
        transfer_results.append({"index": i, "tx": tx, "wallet_result": result})

        # best-effort tx hash extraction
        tx_hash = (
            result.get("tx_hash")
            or result.get("transaction_hash")
            or result.get("hash")
            or result.get("txHash")
        )
        if tx_hash:
            tx_identifiers.append({
                "transaction_hash": tx_hash,
                "chain": args.from_chain,
                "swap_provider": quote.get("swap_provider"),
            })

    request_id = str(uuid.uuid4())
    swap_quote_for_receipt = {
        "from_assets": execute_payload["from_assets"],
        "to_assets": execute_payload["to_assets"],
    }

    receipt = os_transaction_receipt(
        swap_quote=swap_quote_for_receipt,
        transaction_identifiers=tx_identifiers if tx_identifiers else None,
        request_id=request_id,
    )

    out = {
        "execute_payload": execute_payload,
        "execute_quote": quote,
        "transactions_count": len(txs),
        "transfer_results": transfer_results,
        "transaction_identifiers": tx_identifiers,
        "receipt_request_id": request_id,
        "receipt": receipt,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
