#!/usr/bin/env python3
"""
Meta DEX Aggregator — Multi-source quote comparison CLI.
Queries ParaSwap, Odos, KyberSwap, Matcha/0x, and 1inch for the best swap route.

Usage:
  python3 skills/meta-dex-aggregator/scripts/meta_dex.py search --chain ethereum --query USDC
  python3 skills/meta-dex-aggregator/scripts/meta_dex.py quote --chain ethereum --from ETH --to USDC --amount 1.0
  python3 skills/meta-dex-aggregator/scripts/meta_dex.py swap --chain base --from ETH --to USDC --amount 0.5 --aggregator odos --wallet 0x...
  python3 skills/meta-dex-aggregator/scripts/meta_dex.py xquote --src-chain arbitrum --dst-chain polygon --from ETH --to USDC --amount 0.5 --wallet 0x...
  python3 skills/meta-dex-aggregator/scripts/meta_dex.py execute --chain base --from ETH --to USDC --amount 0.5 --aggregator kyberswap --wallet 0x... --verify
  python3 skills/meta-dex-aggregator/scripts/meta_dex.py monitor --chain arbitrum --from ETH --to USDC --amount 1.0 --interval 60 --target-net-out 2050
"""

import argparse, json, sys, os, time, hashlib
from datetime import datetime
from time import monotonic
from concurrent.futures import ThreadPoolExecutor, as_completed
from chains import CHAINS
from tokens import search_tokens, resolve_token, to_wei, from_wei
from aggregators import AGGREGATORS, ZERO_ADDR
from safety import full_safety_check
from crosschain import get_crosschain_quotes, LIFI_CHAIN_IDS
from quote_logger import log_quote

# Quote deadline: stop waiting after this many seconds and return what we have.
# Prevents one slow upstream from blocking the entire quote.
QUOTE_DEADLINE_SECONDS = 6.0


def get_all_quotes(chain, from_tok, to_tok, amount_wei, wallet=None, slippage=None, deadline=None):
    chain_id = CHAINS[chain]
    budget = deadline or QUOTE_DEADLINE_SECONDS
    results = []
    start = monotonic()
    with ThreadPoolExecutor(max_workers=len(AGGREGATORS)) as pool:
        futures = {
            pool.submit(func, chain, chain_id, from_tok, to_tok, amount_wei, wallet, slippage): name
            for name, func in AGGREGATORS.items()
        }
        for f in as_completed(futures, timeout=budget):
            remaining = budget - (monotonic() - start)
            if remaining <= 0:
                break
            try:
                r = f.result(timeout=max(remaining, 0.1))
                if r:
                    results.append(r)
            except Exception:
                pass
    results.sort(key=lambda r: int(r.get("amount_out", "0")), reverse=True)
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
    # Build quote list for safety check (normalized schema)
    quote_data = []
    for q in quotes:
        human_out = from_wei(q["amount_out"], to_tok["decimals"])
        quote_data.append({
            "name": q["aggregator"], "outputAmount": float(human_out),
            "gas_units": q.get("gas_units"),
            "gas_usd": q.get("gas_usd"),
            "is_mev_safe": q.get("is_mev_safe", False),
            "amountOut": q["amount_out"],
            "tokenApprovalAddress": q.get("token_approval_address"),
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
    
    best_aggregator = None
    best_net_out = 0
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
        
        # Track best for logging
        if r.get("netOut") and float(r["netOut"]) > best_net_out:
            best_net_out = float(r["netOut"])
            best_aggregator = r["name"]
    
    # Log this quote for historical analysis
    if best_aggregator and best_net_out > 0:
        try:
            log_id = log_quote(
                chain=args.chain,
                from_token=from_tok,
                to_token=to_tok,
                amount_in=args.amount,
                quotes=output["quotes"],
                best_aggregator=best_aggregator,
                net_out_usd=best_net_out
            )
            output["_logId"] = log_id
        except Exception:
            pass  # Logging is optional, don't fail the quote
    
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
        "amountOut": result["amount_out"],
        "amountOutHuman": from_wei(result["amount_out"], to_tok["decimals"]),
        "tokenApprovalAddress": result.get("token_approval_address"),
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
            human_out = from_wei(q.get("amount_out", "0"), to_tok["decimals"])
            human_min = from_wei(q.get("amountOutMin", q.get("amount_out", "0")), to_tok["decimals"])
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


def cmd_execute(args):
    """
    Execute a swap with built-in verification.
    
    Workflow:
    1. Get quote from specified aggregator
    2. Print pre-swap balances (requires wallet_balance tool call by agent)
    3. Return tx data for execution
    4. Agent executes via wallet_transfer
    5. Agent calls this again with --verify to check post-swap balances
    
    v3.1.0: Added --market-order flag for instant execution via 1inch
    v3.1.0: Added --auto-verify to auto-fetch balances (no manual args needed)
    """
    if not args.wallet:
        print(json.dumps({"error": "Wallet address required. Use --wallet 0x..."}))
        sys.exit(1)
    
    chain = args.chain
    from_tok = resolve_token(chain, getattr(args, "from"))
    to_tok = resolve_token(chain, args.to)
    amount_wei = to_wei(args.amount, from_tok["decimals"])
    
    # Check if using market order mode
    use_market_order = getattr(args, "market_order", False)
    
    # Market order mode: use 1inch directly for instant execution (no aggregator needed)
    if use_market_order:
        # Get 1inch quote via native tool
        from aggregators import ZERO_ADDR
        from_tok_addr = from_tok["address"] if from_tok["address"] != ZERO_ADDR else "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
        to_tok_addr = to_tok["address"]
        
        # Return marker for agent to call oneinch_swap
        result = {
            "step": "market_order_ready",
            "mode": "market_order",
            "chain": chain,
            "fromToken": from_tok,
            "toToken": to_tok,
            "amountIn": args.amount,
            "amountInWei": amount_wei,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "instruction": "Execute via oneinch_swap(chain='{chain}', src='{from_addr}', dst='{to_addr}', amount='{amount_wei}', slippage={slippage})",
            "fromAddr": from_tok_addr,
            "toAddr": to_tok_addr,
            "slippage": getattr(args, "slippage", "2.0"),  # Default 2% for market orders
        }
        print(json.dumps(result, indent=2))
        return
    
    # Normal limit order mode requires aggregator
    if not args.aggregator:
        print(json.dumps({"error": "Aggregator required for limit orders. Use --aggregator kyberswap, or use --market-order for 1inch market order"}))
        sys.exit(1)
    
    agg = args.aggregator.lower()
    
    # Normal limit order mode
    chain_id = CHAINS[chain]
    if agg not in AGGREGATORS:
        print(json.dumps({"error": f"Unknown aggregator: {agg}. Available: {list(AGGREGATORS.keys())}"}))
        sys.exit(1)
    
    quote = AGGREGATORS[agg](chain, chain_id, from_tok, to_tok, amount_wei, args.wallet, args.slippage)
    if not quote:
        print(json.dumps({"error": f"{agg} returned no quote for this pair on {chain}"}))
        sys.exit(1)
    
    if "tx" not in quote and agg != "cowswap":
        print(json.dumps({"error": f"{agg} returned a quote but no swap tx data."}))
        sys.exit(1)
    
    # Build execution package
    result = {
        "step": "pre_execution",
        "chain": chain,
        "chainId": chain_id,
        "aggregator": quote["aggregator"],
        "fromToken": from_tok,
        "toToken": to_tok,
        "amountIn": args.amount,
        "amountInWei": amount_wei,
        "expectedOut": quote["amount_out"],
        "expectedOutHuman": from_wei(quote["amount_out"], to_tok["decimals"]),
        "slippage": args.slippage,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    # CowSwap order handling
    if agg == "cowswap":
        result["orderType"] = "cowswap_order"
        result["orderUid"] = quote.get("orderUid")
        result["eip712Data"] = quote.get("eip712Data")
        result["note"] = "CowSwap order - sign EIP-712 and poll for fulfillment"
        result["pollEndpoint"] = f"https://api.cow.fi/{chain}/api/v1/orders/{quote.get('orderUid')}"
    else:
        result["tx"] = quote["tx"]
        result["needsApproval"] = from_tok["address"] != ZERO_ADDR
        result["tokenApprovalAddress"] = quote.get("token_approval_address")
    
    # Verification instructions
    result["verification"] = {
        "instruction": "After execution, call: python3 meta_dex.py execute --chain {chain} --from {from_tok} --to {to_tok} --amount {amount} --aggregator {agg} --wallet {wallet} --verify --expected-out {expected_out}",
        "expectedOutWei": quote["amount_out"],
        "maxDeviationPct": args.max_deviation if hasattr(args, "max_deviation") else 2.0,
    }
    
    print(json.dumps(result, indent=2))


def cmd_monitor(args):
    """
    Monitor for target net output. Polls quotes at interval until target is met.
    
    Use case: "Alert me when ETH→USDC on Arbitrum nets >$2050 after gas"
    """
    chain = args.chain
    from_tok = resolve_token(chain, getattr(args, "from"))
    to_tok = resolve_token(chain, args.to)
    amount_wei = to_wei(args.amount, from_tok["decimals"])
    interval = args.interval
    target_net_out = float(args.target_net_out)
    max_runs = args.max_runs if hasattr(args, "max_runs") and args.max_runs else 0
    
    print(json.dumps({
        "mode": "monitor",
        "chain": chain,
        "fromToken": from_tok["symbol"],
        "toToken": to_tok["symbol"],
        "amount": args.amount,
        "targetNetOutUsd": target_net_out,
        "intervalSeconds": interval,
        "maxRuns": max_runs if max_runs else "unlimited",
        "startedAt": datetime.utcnow().isoformat() + "Z",
    }, indent=2), file=sys.stderr)
    
    run_count = 0
    while True:
        run_count += 1
        if max_runs and run_count > max_runs:
            print(json.dumps({"status": "max_runs_reached", "runs": run_count}))
            break
        
        # Get all quotes
        quotes = get_all_quotes(chain, from_tok, to_tok, amount_wei, getattr(args, "wallet", None), "1.0")
        
        # Find best net out
        best_quote = None
        best_net_out = 0
        for q in quotes:
            net_out = float(q.get("netOut", 0))
            if net_out > best_net_out:
                best_net_out = net_out
                best_quote = q
        
        # Check if target met
        if best_net_out >= target_net_out:
            print(json.dumps({
                "status": "TARGET_MET",
                "run": run_count,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "bestAggregator": best_quote["aggregator"],
                "netOutUsd": best_net_out,
                "targetNetOutUsd": target_net_out,
                "excessUsd": best_net_out - target_net_out,
                "quote": best_quote,
            }))
            break
        
        # Log progress
        print(json.dumps({
            "status": "waiting",
            "run": run_count,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "bestNetOutUsd": best_net_out,
            "targetNetOutUsd": target_net_out,
            "gapUsd": target_net_out - best_net_out,
            "bestAggregator": best_quote["aggregator"] if best_quote else None,
        }), file=sys.stderr)
        
        time.sleep(interval)


def cowswap_poll_order(chain, order_uid, timeout_sec=180, poll_interval=5):
    """
    Poll CowSwap order until fulfilled or timeout.
    
    Returns: {"status": "fulfilled"|"expired"|"cancelled"|"timeout", "orderData": {...}}
    """
    import http_client as http
    
    endpoint = f"https://api.cow.fi/{chain}/api/v1/orders/{order_uid}"
    start_time = time.time()
    
    while time.time() - start_time < timeout_sec:
        try:
            r = http.get(endpoint, timeout=(2, 10))
            if r.status_code == 200:
                data = r.json()
                status = data.get("status")
                if status == "fulfilled":
                    return {"status": "fulfilled", "orderData": data}
                elif status in ["expired", "cancelled"]:
                    return {"status": status, "orderData": data}
        except Exception as e:
            pass
        
        time.sleep(poll_interval)
    
    return {"status": "timeout", "orderData": None, "error": f"Did not fulfill within {timeout_sec}s"}


def get_fallback_aggregators(chain, from_tok, to_tok, amount_wei, wallet, slippage, exclude=None):
    """
    Get ranked list of fallback aggregators for retry logic.
    
    Returns: List of (aggregator_name, quote) tuples sorted by netOut
    """
    exclude = exclude or []
    quotes = get_all_quotes(chain, from_tok, to_tok, amount_wei, wallet, slippage)
    
    # Filter out excluded and sort by netOut
    valid = []
    for q in quotes:
        if q["aggregator"].lower() not in exclude and not q.get("isOutlier", False):
            valid.append(q)
    
    valid.sort(key=lambda x: float(x.get("netOut", 0)), reverse=True)
    return valid


def cmd_stats(args):
    """Show historical winner statistics for a trading pair."""
    from quote_logger import get_winner_stats
    result = get_winner_stats(args.chain, getattr(args, "from"), args.to, getattr(args, "days", 7))
    print(json.dumps(result, indent=2))


def cmd_trend(args):
    """Show price trend (net output over time) for a trading pair."""
    from quote_logger import get_price_trend
    result = get_price_trend(
        args.chain, getattr(args, "from"), args.to,
        getattr(args, "days", 7), getattr(args, "bucket_hours", 1)
    )
    print(json.dumps(result, indent=2))


def cmd_slippage(args):
    """Show slippage analysis for a trading pair."""
    from quote_logger import get_slippage_analysis
    result = get_slippage_analysis(args.chain, getattr(args, "from"), args.to, getattr(args, "days", 7))
    print(json.dumps(result, indent=2))


def cmd_export(args):
    """Export historical quotes to CSV."""
    from quote_logger import export_to_csv
    output_file = getattr(args, "output", None)
    result = export_to_csv(args.chain, getattr(args, "from"), args.to, getattr(args, "days", 30), output_file)
    if output_file:
        print(json.dumps({"status": "exported", "file": output_file, "message": result}))
    else:
        print(result)


def verify_swap(args):
    """
    Verify a swap was executed correctly by comparing expected vs actual.
    
    v3.1.0: Added --auto-verify mode that auto-fetches balances from wallet
    v3.1.1: Fixed RPC endpoints to use reliable public providers (Ankr, Cloudflare)
    """
    chain = args.chain
    from_tok = resolve_token(chain, getattr(args, "from"))
    to_tok = resolve_token(chain, args.to)
    from_decimals = from_tok["decimals"]
    to_decimals = to_tok["decimals"]
    
    # Auto-verify mode: fetch balances from wallet
    if getattr(args, "auto_verify", False):
        import http_client as http
        from gas_oracle import _RPC_ENDPOINTS
        wallet = args.wallet
        from aggregators import CHAINS
        chain_id = CHAINS[chain]
        
        # Fetch current balances via RPC (reuses gas_oracle's RPC map + http_client session)
        def get_token_balance(token_addr, decimals):
            rpc = _RPC_ENDPOINTS.get(chain)
            if not rpc:
                print(json.dumps({"error": f"No RPC URL for chain {chain}"}))
                sys.exit(1)
            if token_addr == "0x0000000000000000000000000000000000000000":
                payload = {"jsonrpc": "2.0", "method": "eth_getBalance", "params": [wallet, "latest"], "id": 1}
            else:
                data = f"0x70a08231000000000000000000000000{wallet[2:]}"
                payload = {"jsonrpc": "2.0", "method": "eth_call", "params": [{"to": token_addr, "data": data}, "latest"], "id": 1}
            r = http.post(rpc, json=payload, timeout=(2, 10))
            if r.status_code == 200:
                return int(r.json().get("result", "0x0"), 16)
            return 0
        
        # Try to fetch balances with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                post_from_wei = get_token_balance(from_tok["address"], from_decimals)
                post_to_wei = get_token_balance(to_tok["address"], to_decimals)
                break  # Success
            except Exception as e:
                if attempt == max_retries - 1:
                    print(json.dumps({"error": f"Auto-verify failed after {max_retries} attempts: {str(e)}"}))
                    sys.exit(1)
                time.sleep(1)  # Wait before retry
        
        # For auto-verify, we need pre-balances from args or estimate from expected
        if args.pre_from_balance:
            pre_from_wei = to_wei(float(args.pre_from_balance), from_decimals)
        else:
            pre_from_wei = post_from_wei + to_wei(float(args.amount), from_decimals)
        
        if args.pre_to_balance:
            pre_to_wei = to_wei(float(args.pre_to_balance), to_decimals)
        else:
            pre_to_wei = post_to_wei - (args.expected_out if args.expected_out else 0)
    else:
        # Manual mode (v3.0.0)
        if not args.pre_from_balance or not args.pre_to_balance:
            print(json.dumps({"error": "Pre-swap balances required. Use --pre-from-balance and --pre-to-balance, or use --auto-verify"}))
            sys.exit(1)
        if not args.post_from_balance or not args.post_to_balance:
            print(json.dumps({"error": "Post-swap balances required. Use --post-from-balance and --post-to-balance, or use --auto-verify"}))
            sys.exit(1)
        
        pre_from_wei = to_wei(float(args.pre_from_balance), from_decimals)
        post_from_wei = to_wei(float(args.post_from_balance), from_decimals)
        pre_to_wei = to_wei(float(args.pre_to_balance), to_decimals)
        post_to_wei = to_wei(float(args.post_to_balance), to_decimals)
    
    # Calculate actual amounts
    actual_spent_wei = pre_from_wei - post_from_wei
    actual_received_wei = post_to_wei - pre_to_wei
    
    actual_spent = from_wei(actual_spent_wei, from_decimals)
    actual_received = from_wei(actual_received_wei, to_decimals)
    
    expected_received_wei = args.expected_out if args.expected_out else "0"
    expected_received = from_wei(expected_received_wei, to_decimals)
    
    # Calculate deviation
    if float(expected_received) > 0:
        deviation_pct = ((float(actual_received) - float(expected_received)) / float(expected_received)) * 100
    else:
        deviation_pct = 0
    
    max_deviation = args.max_deviation if hasattr(args, "max_deviation") else 2.0
    passed = abs(deviation_pct) <= max_deviation
    
    result = {
        "verification": "PASSED" if passed else "FAILED",
        "chain": args.chain,
        "aggregator": args.aggregator,
        "expectedSpent": args.amount,
        "expectedReceived": expected_received,
        "actualSpent": actual_spent,
        "actualReceived": actual_received,
        "deviationPct": round(deviation_pct, 3),
        "maxDeviationPct": max_deviation,
        "priceAchieved": float(actual_received) / float(actual_spent) if float(actual_spent) > 0 else 0,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
    
    if not passed:
        result["warning"] = f"Deviation {deviation_pct:.2f}% exceeds threshold {max_deviation}% — check for slippage, MEV, or partial fill"
    
    print(json.dumps(result, indent=2))


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
    xq.add_argument("--wallet", required=True, help="Your wallet address (required for LI.FI quotes)")
    xq.add_argument("--slippage", default="3")

    # New: execute with verification
    ex = sub.add_parser("execute")
    ex.add_argument("--chain", required=True, choices=list(CHAINS.keys()))
    ex.add_argument("--from", required=True)
    ex.add_argument("--to", required=True)
    ex.add_argument("--amount", required=True)
    ex.add_argument("--aggregator", required=False, help="Aggregator for limit orders (not needed with --market-order)")
    ex.add_argument("--wallet", required=True)
    ex.add_argument("--slippage", default="2.0", help="Slippage tolerance %% (default 2.0%% for market orders)")
    ex.add_argument("--max-deviation", type=float, default=2.0, help="Max deviation %% for verification")
    ex.add_argument("--verify", action="store_true", help="Run verification mode (requires balance args)")
    ex.add_argument("--auto-verify", action="store_true", help="Auto-fetch balances from wallet (no manual args needed)")
    ex.add_argument("--market-order", action="store_true", help="Use 1inch market order for instant execution")
    ex.add_argument("--pre-from-balance", type=float, help="Pre-swap from-token balance")
    ex.add_argument("--pre-to-balance", type=float, help="Pre-swap to-token balance")
    ex.add_argument("--post-from-balance", type=float, help="Post-swap from-token balance")
    ex.add_argument("--post-to-balance", type=float, help="Post-swap to-token balance")
    ex.add_argument("--expected-out", type=str, help="Expected output amount in wei (for verification)")

    # New: monitor for target net output
    m = sub.add_parser("monitor")
    m.add_argument("--chain", required=True, choices=list(CHAINS.keys()))
    m.add_argument("--from", required=True)
    m.add_argument("--to", required=True)
    m.add_argument("--amount", required=True)
    m.add_argument("--wallet", default=None)
    m.add_argument("--interval", type=int, default=60, help="Poll interval in seconds")
    m.add_argument("--target-net-out", type=float, required=True, help="Target net output in USD")
    m.add_argument("--max-runs", type=int, default=0, help="Max poll attempts (0=unlimited)")

    # New: analytics commands
    stats = sub.add_parser("stats")
    stats.add_argument("--chain", required=True, choices=list(CHAINS.keys()))
    stats.add_argument("--from", required=True)
    stats.add_argument("--to", required=True)
    stats.add_argument("--days", type=int, default=7, help="Analysis period in days")
    
    trend = sub.add_parser("trend")
    trend.add_argument("--chain", required=True, choices=list(CHAINS.keys()))
    trend.add_argument("--from", required=True)
    trend.add_argument("--to", required=True)
    trend.add_argument("--days", type=int, default=7, help="Analysis period in days")
    trend.add_argument("--bucket-hours", type=int, default=1, help="Data bucket size in hours")
    
    slippage = sub.add_parser("slippage")
    slippage.add_argument("--chain", required=True, choices=list(CHAINS.keys()))
    slippage.add_argument("--from", required=True)
    slippage.add_argument("--to", required=True)
    slippage.add_argument("--days", type=int, default=7, help="Analysis period in days")
    
    export = sub.add_parser("export")
    export.add_argument("--chain", required=True, choices=list(CHAINS.keys()))
    export.add_argument("--from", required=True)
    export.add_argument("--to", required=True)
    export.add_argument("--days", type=int, default=30, help="Export period in days")
    export.add_argument("--output", default=None, help="Output CSV file path")

    args = p.parse_args()
    
    if args.command == "execute":
        if args.verify:
            verify_swap(args)
        else:
            cmd_execute(args)
    elif args.command == "monitor":
        cmd_monitor(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "trend":
        cmd_trend(args)
    elif args.command == "slippage":
        cmd_slippage(args)
    elif args.command == "export":
        cmd_export(args)
    else:
        {"search": cmd_search, "quote": cmd_quote, "swap": cmd_swap, "xquote": cmd_xquote}[args.command](args)

if __name__ == "__main__":
    main()
