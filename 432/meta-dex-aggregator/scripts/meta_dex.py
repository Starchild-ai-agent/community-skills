#!/usr/bin/env python3
"""
Meta DEX Aggregator — Multi-source quote comparison CLI.
Queries ParaSwap, Odos, KyberSwap, Matcha/0x, and 1inch for the best swap route.

Usage:
  python3 skills/meta-dex-aggregator/scripts/meta_dex.py search --chain ethereum --query USDC
  python3 skills/meta-dex-aggregator/scripts/meta_dex.py quote --chain ethereum --from ETH --to USDC --amount 1.0
  python3 skills/meta-dex-aggregator/scripts/meta_dex.py swap --chain base --from ETH --to USDC --amount 0.5 --aggregator odos --wallet 0x...
  python3 skills/meta-dex-aggregator/scripts/meta_dex.py xquote --src-chain arbitrum --dst-chain polygon --from ETH --to USDC --amount 0.5 --wallet 0x...
"""

import argparse, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from concurrent.futures import ThreadPoolExecutor, as_completed
from chains import CHAINS
from tokens import search_tokens, resolve_token, to_wei, from_wei
from aggregators import AGGREGATORS, ZERO_ADDR
from safety import full_safety_check
from crosschain import get_crosschain_quotes, LIFI_CHAIN_IDS


def get_all_quotes(chain, from_tok, to_tok, amount_wei, wallet=None, slippage=None):
    chain_id = CHAINS[chain]
    results = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {
            pool.submit(func, chain, chain_id, from_tok, to_tok, amount_wei, wallet, slippage): name
            for name, func in AGGREGATORS.items()
        }
        for f in as_completed(futures):
            try:
                r = f.result()
                if r:
                    results.append(r)
            except Exception:
                pass
    results.sort(key=lambda r: int(r.get("amountOut", "0")), reverse=True)
    return results


def cmd_search(args):
    results = search_tokens(args.chain, args.query, limit=args.limit)
    out = [{"symbol": t["symbol"], "name": t["name"], "address": t["address"],
            "decimals": t["decimals"], "volume24h": t.get("volume24h")} for t in results]
    print(json.dumps(out, indent=2))


def cmd_quote(args):
    from_tok = resolve_token(args.chain, getattr(args, "from"))
    to_tok = resolve_token(args.chain, args.to)
    amount_wei = to_wei(args.amount, from_tok["decimals"])
    quotes = get_all_quotes(args.chain, from_tok, to_tok, amount_wei,
                            getattr(args, "wallet", None), getattr(args, "slippage", "1.0"))
    # Build quote list for safety check
    quote_data = []
    for q in quotes:
        human_out = from_wei(q["amountOut"], to_tok["decimals"])
        quote_data.append({
            "name": q["aggregator"], "outputAmount": float(human_out),
            "estimatedGas": int(float(q.get("gas", "0") or 0)),
            "amountOut": q["amountOut"],
            "tokenApprovalAddress": q.get("tokenApprovalAddress"),
        })

    slippage = getattr(args, "slippage", "0.5")
    safety = full_safety_check(
        quote_data, args.chain, from_tok["address"], to_tok["address"],
        from_tok["symbol"], to_tok["symbol"], float(args.amount), slippage
    )

    output = {"chain": args.chain, "fromToken": from_tok, "toToken": to_tok,
              "amountIn": args.amount, "amountInWei": amount_wei,
              "safety": {
                  "recommendation": safety["recommendation"],
                  "priceImpact": safety["price_impact"],
                  "slippageWarnings": safety["slippage_warnings"],
                  "marketPrices": safety["prices"],
              },
              "quotes": []}
    for r in safety["ranked_quotes"]:
        entry = {"aggregator": r["name"],
                 "amountOutHuman": r["outputAmount"],
                 "amountUsd": r.get("amountUsd"),
                 "gasUsd": r.get("gasUsd"),
                 "netOut": r.get("netOut"),
                 "vsbestPct": r.get("vsbestPct"),
                 "isMEVSafe": r.get("isMEVSafe", False),
                 "isOutlier": r.get("isOutlier", False)}
        output["quotes"].append(entry)
    print(json.dumps(output, indent=2))


def cmd_swap(args):
    if not args.wallet:
        print(json.dumps({"error": "Wallet address required. Use --wallet 0x..."}))
        sys.exit(1)
    from_tok = resolve_token(args.chain, getattr(args, "from"))
    to_tok = resolve_token(args.chain, args.to)
    amount_wei = to_wei(args.amount, from_tok["decimals"])
    agg = args.aggregator.lower()
    if agg not in AGGREGATORS:
        print(json.dumps({"error": f"Unknown aggregator: {agg}. Available: {list(AGGREGATORS.keys())}"}))
        sys.exit(1)
    chain_id = CHAINS[args.chain]
    result = AGGREGATORS[agg](args.chain, chain_id, from_tok, to_tok, amount_wei, args.wallet, args.slippage)
    if not result:
        print(json.dumps({"error": f"{agg} returned no quote for this pair on {args.chain}"}))
        sys.exit(1)
    if "tx" not in result:
        print(json.dumps({"error": f"{agg} returned a quote but no swap tx data."}))
        sys.exit(1)
    print(json.dumps({
        "chain": args.chain, "chainId": chain_id, "aggregator": result["aggregator"],
        "fromToken": from_tok, "toToken": to_tok,
        "amountIn": args.amount, "amountInWei": amount_wei,
        "amountOut": result["amountOut"],
        "amountOutHuman": from_wei(result["amountOut"], to_tok["decimals"]),
        "tokenApprovalAddress": result.get("tokenApprovalAddress"),
        "needsApproval": from_tok["address"] != ZERO_ADDR,
        "tx": result["tx"],
    }, indent=2))


def cmd_xquote(args):
    """Cross-chain quote: compare routes across LI.FI and 1inch Fusion+."""
    src_chain = args.src_chain
    dst_chain = args.dst_chain
    from_tok = resolve_token(src_chain, getattr(args, "from"))
    to_tok = resolve_token(dst_chain, args.to)
    amount_wei = to_wei(args.amount, from_tok["decimals"])
    wallet = getattr(args, "wallet", None) or ZERO_ADDR

    quotes = get_crosschain_quotes(
        src_chain, dst_chain, from_tok, to_tok, amount_wei, wallet,
        getattr(args, "slippage", "3")
    )

    output = {
        "type": "crosschain",
        "srcChain": src_chain,
        "dstChain": dst_chain,
        "fromToken": from_tok,
        "toToken": to_tok,
        "amountIn": args.amount,
        "amountInWei": str(amount_wei),
        "quotes": [],
    }

    for q in quotes:
        if q.get("_needs_tool_call"):
            # 1inch Fusion+ marker — agent needs to call oneinch_cross_chain_quote
            output["quotes"].append({
                "aggregator": q["aggregator"],
                "execution": q["execution"],
                "needsToolCall": True,
                "srcToken": q.get("srcToken"),
                "dstToken": q.get("dstToken"),
                "note": q.get("note"),
            })
        else:
            human_out = from_wei(q.get("amountOut", "0"), to_tok["decimals"])
            human_min = from_wei(q.get("amountOutMin", q.get("amountOut", "0")), to_tok["decimals"])
            entry = {
                "aggregator": q["aggregator"],
                "amountOutHuman": human_out,
                "amountOutMinHuman": human_min,
                "gasUsd": q.get("gasUsd", 0),
                "totalFeesUsd": q.get("totalFeesUsd", 0),
                "feeBreakdown": q.get("feeBreakdown", []),
                "estimatedTimeSeconds": q.get("estimatedTimeSeconds", 0),
                "tags": q.get("tags", []),
                "execution": q.get("execution"),
                "hasTxData": "tx" in q,
            }
            if q.get("error"):
                entry["error"] = q["error"]
            output["quotes"].append(entry)

    print(json.dumps(output, indent=2))


def main():
    p = argparse.ArgumentParser(description="Meta DEX Aggregator")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search")
    s.add_argument("--chain", required=True, choices=list(CHAINS.keys()))
    s.add_argument("--query", required=True)
    s.add_argument("--limit", type=int, default=20)

    q = sub.add_parser("quote")
    q.add_argument("--chain", required=True, choices=list(CHAINS.keys()))
    q.add_argument("--from", required=True)
    q.add_argument("--to", required=True)
    q.add_argument("--amount", required=True)
    q.add_argument("--wallet", default=None)
    q.add_argument("--slippage", default="1.0")

    w = sub.add_parser("swap")
    w.add_argument("--chain", required=True, choices=list(CHAINS.keys()))
    w.add_argument("--from", required=True)
    w.add_argument("--to", required=True)
    w.add_argument("--amount", required=True)
    w.add_argument("--aggregator", required=True)
    w.add_argument("--wallet", required=True)
    w.add_argument("--slippage", default="1.0")

    xq = sub.add_parser("xquote")
    xq.add_argument("--src-chain", required=True)
    xq.add_argument("--dst-chain", required=True)
    xq.add_argument("--from", required=True)
    xq.add_argument("--to", required=True)
    xq.add_argument("--amount", required=True)
    xq.add_argument("--wallet", default=None)
    xq.add_argument("--slippage", default="3")

    args = p.parse_args()
    {"search": cmd_search, "quote": cmd_quote, "swap": cmd_swap, "xquote": cmd_xquote}[args.command](args)

if __name__ == "__main__":
    main()
