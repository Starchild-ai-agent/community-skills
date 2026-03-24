"""Cross-chain aggregator adapters for Meta DEX Aggregator.

Queries LI.FI (multi-bridge) and 1inch Fusion+ for cross-chain quotes.
Returns standardized results compatible with the same-chain pipeline.
"""

import os, json
import http_client as http
from chains import CHAINS

# ── Proxy Configuration ─────────────────────────────────────────────────────
# Platform uses transparent proxy (sc-proxy) for billing on whitelisted APIs.
# LI.FI is NOT whitelisted — use direct connection.
# Configure proxies from environment if available (used for other APIs if needed).
PROXIES = {}  # LI.FI uses direct connection (no proxy)
_proxy_host = os.environ.get("PROXY_HOST", "")
_proxy_port = os.environ.get("PROXY_PORT", "")
if _proxy_host and _proxy_port:
    # Handle IPv6 addresses by wrapping in brackets
    if ":" in _proxy_host and not _proxy_host.startswith("["):
        _proxy_host = f"[{_proxy_host}]"
    PROXY_URL = f"http://{_proxy_host}:{_proxy_port}"
    # Store for potential use by other APIs, but LI.FI calls use PROXIES = {}
    _PLATFORM_PROXIES = {"http": PROXY_URL, "https": PROXY_URL}
else:
    _PLATFORM_PROXIES = {}

# ── Chain ID mappings ────────────────────────────────────────────────────────

LIFI_CHAIN_IDS = {
    "ethereum": 1, "arbitrum": 42161, "optimism": 10, "base": 8453,
    "polygon": 137, "bsc": 56, "avax": 43114, "fantom": 250,
    "gnosis": 100, "zksync": 324, "scroll": 534352, "linea": 59144,
    "blast": 81457, "sonic": 146,
}

# 1inch Fusion+ supported chains (chain name -> 1inch chain identifier)
ONEINCH_XCHAIN = {
    "ethereum", "arbitrum", "optimism", "base", "polygon", "bsc", "avax", "gnosis",
}

LIFI_NATIVE = "0x0000000000000000000000000000000000000000"
ONEINCH_NATIVE = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


# ── LI.FI ────────────────────────────────────────────────────────────────────

def lifi_resolve_token(chain_id, symbol_or_addr):
    """Resolve token via LI.FI's own token endpoint."""
    if symbol_or_addr.startswith("0x") and len(symbol_or_addr) == 42:
        return symbol_or_addr
    try:
        r = http.get(
            f"https://li.quest/v1/token",
            params={"chain": chain_id, "token": symbol_or_addr},
            timeout=10,

        )
        if r.status_code == 200:
            data = r.json()
            return data.get("address", symbol_or_addr)
    except Exception:
        pass
    return symbol_or_addr


def lifi_quote(src_chain, dst_chain, from_tok, to_tok, amount_wei, wallet, slippage):
    """Get cross-chain quotes from LI.FI advanced routes API.
    
    Returns list of route options (LI.FI often returns multiple bridge paths).
    """
    src_chain_id = LIFI_CHAIN_IDS.get(src_chain)
    dst_chain_id = LIFI_CHAIN_IDS.get(dst_chain)
    if not src_chain_id or not dst_chain_id:
        return []

    from_addr = from_tok["address"]
    to_addr = to_tok["address"]
    # LI.FI uses 0x000...000 for native tokens
    if from_addr.lower() == ONEINCH_NATIVE.lower():
        from_addr = LIFI_NATIVE
    if to_addr.lower() == ONEINCH_NATIVE.lower():
        to_addr = LIFI_NATIVE

    slip = float(slippage) / 100 if float(slippage) > 1 else float(slippage)

    try:
        r = http.post(
            "https://li.quest/v1/advanced/routes",
            json={
                "fromChainId": src_chain_id,
                "toChainId": dst_chain_id,
                "fromTokenAddress": from_addr,
                "toTokenAddress": to_addr,
                "fromAmount": str(amount_wei),
                "fromAddress": wallet,
                "options": {
                    "slippage": slip,
                    "order": "RECOMMENDED",
                    "maxPriceImpact": 0.5,  # 50% max — cross-chain routes can have higher impact
                },
            },
            headers={"Content-Type": "application/json"},
            timeout=30,

        )
        data = r.json()
    except Exception as e:
        return [{"aggregator": "LI.FI", "error": str(e)}]

    routes = data.get("routes", [])
    results = []
    for route in routes[:5]:  # cap at 5 routes
        steps = route.get("steps", [])
        bridge_names = [s.get("toolDetails", {}).get("name", "?") for s in steps]
        route_label = " → ".join(bridge_names)

        est_time = sum(s.get("estimate", {}).get("executionDuration", 0) for s in steps)
        gas_usd = float(route.get("gasCostUSD", "0"))

        # Collect all fee costs
        total_fees_usd = gas_usd
        fee_breakdown = []
        for s in steps:
            for fc in s.get("estimate", {}).get("feeCosts", []):
                fee_usd = float(fc.get("amountUSD", "0"))
                total_fees_usd += fee_usd
                fee_breakdown.append({"name": fc.get("name", "fee"), "usd": fee_usd})

        to_amount = route.get("toAmount", "0")
        to_amount_min = route.get("toAmountMin", "0")

        result = {
            "aggregator": f"LI.FI ({route_label})",
            "amountOut": to_amount,
            "amountOutMin": to_amount_min,
            "amountIn": str(amount_wei),
            "gasUsd": gas_usd,
            "totalFeesUsd": total_fees_usd,
            "feeBreakdown": fee_breakdown,
            "estimatedTimeSeconds": est_time,
            "tags": route.get("tags", []),
            "crosschain": True,
            "execution": "lifi",
        }

        # Include transaction data for execution
        if steps and steps[0].get("transactionRequest"):
            tx_req = steps[0]["transactionRequest"]
            result["tx"] = {
                "to": tx_req.get("to"),
                "data": tx_req.get("data"),
                "value": tx_req.get("value", "0"),
                "gas": tx_req.get("gasLimit", "0"),
                "from": tx_req.get("from", wallet),
                "chainId": src_chain_id,
            }
        # Store full route for step-by-step execution if needed
        result["_lifi_route"] = route

        results.append(result)

    return results


# ── 1inch Fusion+ ────────────────────────────────────────────────────────────

def oneinch_fusion_quote(src_chain, dst_chain, from_tok, to_tok, amount_wei, wallet, slippage):
    """Get cross-chain quote from 1inch Fusion+.
    
    NOTE: This returns quote data. Actual execution uses the oneinch_cross_chain_swap
    tool (intent-based, handled by the agent, not raw tx).
    """
    if src_chain not in ONEINCH_XCHAIN or dst_chain not in ONEINCH_XCHAIN:
        return []

    from_addr = from_tok["address"]
    to_addr = to_tok["address"]
    # 1inch native = 0xEeee...
    if from_addr == "0x0000000000000000000000000000000000000000":
        from_addr = ONEINCH_NATIVE
    if to_addr == "0x0000000000000000000000000000000000000000":
        to_addr = ONEINCH_NATIVE

    # We can't call the proxied 1inch API directly from scripts.
    # Instead, return a marker that the agent should use oneinch_cross_chain_quote tool.
    return [{
        "aggregator": "1inch Fusion+",
        "srcChain": src_chain,
        "dstChain": dst_chain,
        "srcToken": from_addr,
        "dstToken": to_addr,
        "amountIn": str(amount_wei),
        "crosschain": True,
        "execution": "oneinch_fusion",
        "_needs_tool_call": True,
        "note": "Quote requires agent tool call (oneinch_cross_chain_quote)",
    }]


# ── Dispatch ─────────────────────────────────────────────────────────────────

def get_crosschain_quotes(src_chain, dst_chain, from_tok, to_tok, amount_wei, wallet, slippage="1"):
    """Get quotes from all cross-chain aggregators.
    
    Returns list of quote results from LI.FI and 1inch Fusion+.
    """
    results = []

    # LI.FI — returns ready-to-execute tx data
    lifi_results = lifi_quote(src_chain, dst_chain, from_tok, to_tok, amount_wei, wallet, slippage)
    results.extend(lifi_results)

    # 1inch Fusion+ — returns marker for agent tool call
    oneinch_results = oneinch_fusion_quote(src_chain, dst_chain, from_tok, to_tok, amount_wei, wallet, slippage)
    results.extend(oneinch_results)

    return results
