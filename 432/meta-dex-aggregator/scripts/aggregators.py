"""DEX aggregator adapters for Meta DEX Aggregator."""

import os, requests
from chains import (CHAINS, ZERO_ADDR, NATIVE_PLACEHOLDER, DEFILLAMA_REFERRER)

# ── ParaSwap ──────────────────────────────────────────────────────────────────
PARASWAP_CHAINS = {"ethereum","bsc","polygon","avax","arbitrum","fantom","optimism","base","gnosis","sonic","unichain"}

def paraswap_quote(chain, chain_id, from_tok, to_tok, amount_wei, wallet, slippage):
    if chain not in PARASWAP_CHAINS:
        return None
    from_addr = NATIVE_PLACEHOLDER if from_tok["address"] == ZERO_ADDR else from_tok["address"]
    to_addr = NATIVE_PLACEHOLDER if to_tok["address"] == ZERO_ADDR else to_tok["address"]

    url = (
        f"https://apiv5.paraswap.io/prices/?srcToken={from_addr}&destToken={to_addr}"
        f"&amount={amount_wei}&srcDecimals={from_tok['decimals']}&destDecimals={to_tok['decimals']}"
        f"&partner=llamaswap&side=SELL&network={chain_id}"
        f"&excludeDEXS=ParaSwapPool,ParaSwapLimitOrders&version=6.2"
    )
    data = requests.get(url, timeout=15).json()
    if "error" in data:
        return None

    result = {
        "aggregator": "ParaSwap",
        "amountOut": data["priceRoute"]["destAmount"],
        "amountIn": data["priceRoute"]["srcAmount"],
        "gas": data["priceRoute"].get("gasCost", "0"),
        "tokenApprovalAddress": data["priceRoute"].get("tokenTransferProxy"),
    }

    if wallet and wallet != ZERO_ADDR:
        slippage_bps = int(float(slippage) * 100) if slippage else 100
        tx_resp = requests.post(
            f"https://apiv5.paraswap.io/transactions/{chain_id}?ignoreChecks=true",
            json={
                "srcToken": data["priceRoute"]["srcToken"],
                "srcDecimals": data["priceRoute"]["srcDecimals"],
                "destToken": data["priceRoute"]["destToken"],
                "destDecimals": data["priceRoute"]["destDecimals"],
                "slippage": slippage_bps,
                "userAddress": wallet,
                "partner": "llamaswap",
                "partnerAddress": DEFILLAMA_REFERRER,
                "takeSurplus": True,
                "priceRoute": data["priceRoute"],
                "isCapSurplus": True,
                "srcAmount": data["priceRoute"]["srcAmount"],
            },
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        tx_data = tx_resp.json()
        if "error" not in tx_data:
            result["tx"] = {
                "to": tx_data["to"], "data": tx_data["data"],
                "value": tx_data.get("value", "0"),
                "gas": tx_data.get("gas", data["priceRoute"].get("gasCost", "0")),
                "from": tx_data["from"],
            }
    return result


# ── Odos ──────────────────────────────────────────────────────────────────────
ODOS_CHAINS = {"ethereum","arbitrum","optimism","base","polygon","avax","bsc","fantom","zksync","linea","scroll","sonic","unichain"}
ODOS_ROUTERS = {
    "ethereum": "0xcf5540fffcdc3d510b18bfca6d2b9987b0772559",
    "arbitrum": "0xa669e7a0d4b3e4fa48af2de86bd4cd7126be4e13",
    "optimism": "0xca423977156bb05b13a2ba3b76bc5419e2fe9680",
    "base": "0x19ceead7105607cd444f5ad10dd51356436095a1",
    "polygon": "0x4e3288c9ca110bcc82bf38f09a7b425c095d92bf",
    "avax": "0x88de50b233052e4fb783d4f6db78cc34fea3e9fc",
    "bsc": "0x89b8aa89fdd0507a99d334cbe3c808fafc7d850e",
    "fantom": "0xd0c22a5435f4e8e5770c1fafb5374015fc12f7cd",
    "zksync": "0x4bBa932E9792A2b917D47830C93a9BC79320E4f7",
    "linea": "0x2d8879046f1559E53eb052E949e9544bCB72f414",
    "scroll": "0xbFe03C9E20a9Fc0b37de01A172F207004935E0b1",
    "sonic": "0xac041df48df9791b0654f1dbbf2cc8450c5f2e9d",
    "unichain": "0x6409722F3a1C4486A3b1FE566cBDd5e9D946A1f3",
}

def odos_quote(chain, chain_id, from_tok, to_tok, amount_wei, wallet, slippage):
    if chain not in ODOS_CHAINS:
        return None
    from_addr = from_tok["address"]
    to_addr = to_tok["address"]

    quote = requests.post(
        "https://api.odos.xyz/sor/quote/v2",
        json={
            "chainId": chain_id,
            "inputTokens": [{"tokenAddress": from_addr, "amount": amount_wei}],
            "outputTokens": [{"tokenAddress": to_addr, "proportion": 1}],
            "userAddr": wallet or ZERO_ADDR,
            "slippageLimitPercent": float(slippage) if slippage else 1.0,
            "referralCode": 2101375859,
            "disableRFQs": True, "compact": True,
        },
        headers={"Content-Type": "application/json"},
        timeout=15,
    ).json()

    if "pathId" not in quote:
        return None

    result = {
        "aggregator": "Odos",
        "amountOut": str(quote.get("outAmounts", ["0"])[0]),
        "amountIn": amount_wei,
        "gas": str(quote.get("gasEstimate", 0)),
        "tokenApprovalAddress": ODOS_ROUTERS.get(chain),
    }

    if wallet and wallet != ZERO_ADDR:
        swap_data = requests.post(
            "https://api.odos.xyz/sor/assemble",
            json={"userAddr": wallet, "pathId": quote["pathId"]},
            headers={"Content-Type": "application/json"},
            timeout=15,
        ).json()

        if "transaction" in swap_data:
            tx = swap_data["transaction"]
            if tx["to"].lower() == ODOS_ROUTERS.get(chain, "").lower():
                result["tx"] = {
                    "to": tx["to"], "data": tx["data"],
                    "value": str(tx.get("value", "0")),
                    "gas": str(tx.get("gas") or swap_data.get("gasEstimate", 0)),
                    "from": tx["from"],
                }
                if swap_data.get("outputTokens"):
                    result["amountOut"] = str(swap_data["outputTokens"][0]["amount"])
            else:
                result["error"] = f"Router mismatch: {tx['to']} != {ODOS_ROUTERS.get(chain)}"
    return result


# ── KyberSwap ─────────────────────────────────────────────────────────────────
KYBER_CHAIN_MAP = {
    "ethereum": "ethereum", "bsc": "bsc", "polygon": "polygon",
    "arbitrum": "arbitrum", "optimism": "optimism", "avax": "avalanche",
    "fantom": "fantom", "base": "base", "linea": "linea",
    "scroll": "scroll", "zksync": "zksync", "sonic": "sonic",
}

def kyberswap_quote(chain, chain_id, from_tok, to_tok, amount_wei, wallet, slippage):
    kyber_chain = KYBER_CHAIN_MAP.get(chain)
    if not kyber_chain:
        return None
    from_addr = NATIVE_PLACEHOLDER if from_tok["address"] == ZERO_ADDR else from_tok["address"]
    to_addr = NATIVE_PLACEHOLDER if to_tok["address"] == ZERO_ADDR else to_tok["address"]

    url = (
        f"https://aggregator-api.kyberswap.com/{kyber_chain}/api/v1/routes?"
        f"tokenIn={from_addr}&tokenOut={to_addr}&amountIn={amount_wei}"
        f"&saveGas=false&gasInclude=true"
    )
    data = requests.get(url, timeout=15).json()
    if data.get("code") != 0 or not data.get("data", {}).get("routeSummary"):
        return None

    summary = data["data"]["routeSummary"]
    result = {
        "aggregator": "KyberSwap",
        "amountOut": summary.get("amountOut", "0"),
        "amountIn": summary.get("amountIn", amount_wei),
        "gas": summary.get("gasUsd", "0"),
        "tokenApprovalAddress": summary.get("routerAddress"),
    }

    if wallet and wallet != ZERO_ADDR:
        slippage_bps = int(float(slippage) * 100) if slippage else 100
        build_data = requests.post(
            f"https://aggregator-api.kyberswap.com/{kyber_chain}/api/v1/route/build",
            json={
                "routeSummary": summary,
                "sender": wallet, "recipient": wallet,
                "slippageTolerance": slippage_bps,
            },
            headers={"Content-Type": "application/json"},
            timeout=15,
        ).json()

        if build_data.get("code") == 0 and build_data.get("data"):
            tx_data = build_data["data"]
            result["tx"] = {
                "to": tx_data["routerAddress"], "data": tx_data["data"],
                "value": tx_data.get("value", "0"),
                "gas": tx_data.get("gas", "0"),
                "from": wallet,
            }
    return result


# ============================================================
# 0x / Matcha (requires OX_API_KEY env var - free at 0x.org/pricing)
# ============================================================

ZEROX_CHAIN_IDS = {
    "ethereum": "1", "bsc": "56", "polygon": "137", "optimism": "10",
    "arbitrum": "42161", "avalanche": "43114", "base": "8453",
    "linea": "59144", "scroll": "534352", "unichain": "130"
}

ZEROX_PERMIT2_ADDRESS = "0x000000000022d473030f116ddee9f6b43ac78ba3"

def zerox_quote(chain, chain_id, from_tok, to_tok, amount_wei, wallet, slippage):
    """Get quote from 0x/Matcha v2 (permit2) API."""
    api_key = os.environ.get("OX_API_KEY", "")
    if not api_key:
        return None  # silently skip if no key configured

    zx_chain_id = ZEROX_CHAIN_IDS.get(chain)
    if not zx_chain_id:
        return None

    native = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    from_addr = from_tok["address"] if isinstance(from_tok, dict) else from_tok
    to_addr = to_tok["address"] if isinstance(to_tok, dict) else to_tok
    token_from = native if from_addr == ZERO_ADDR else from_addr
    token_to = native if to_addr == ZERO_ADDR else to_addr
    # 0x requires taker > 0x...ffff; use a real address as fallback for quotes
    taker = wallet or "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

    slippage_bps = int(float(slippage) * 100) if slippage else 100

    try:
        r = requests.get(
            "https://api.0x.org/swap/permit2/quote",
            params={
                "chainId": zx_chain_id,
                "buyToken": token_to,
                "sellToken": token_from,
                "sellAmount": amount_wei,
                "slippageBps": str(slippage_bps),
                "taker": taker,
            },
            headers={
                "0x-api-key": api_key,
                "0x-version": "v2"
            },
            timeout=15,
        )
        if r.status_code != 200:
            return None

        data = r.json()
        buy_amount = data.get("buyAmount") or data.get("minBuyAmount", "0")
        tx = data.get("transaction")
        return {
            "aggregator": "Matcha/0x",
            "amountOut": buy_amount,
            "gas": data.get("gas", tx.get("gas", "0") if tx else "0"),
            "tx": tx,
            "tokenApprovalAddress": ZEROX_PERMIT2_ADDRESS,
        }
    except Exception:
        return None


# ── 1inch ─────────────────────────────────────────────────────────────────────
# 1inch is NOT called from this script. It uses the platform's native
# oneinch_quote / oneinch_swap tools (proxied, no user API key needed).
# The agent merges the 1inch result into the comparison table.
# See SKILL.md for the workflow.


# ── Dispatch ──────────────────────────────────────────────────────────────────
AGGREGATORS = {
    "paraswap": paraswap_quote,
    "odos": odos_quote,
    "kyberswap": kyberswap_quote,
    "matcha/0x": zerox_quote,
    # "1inch" — handled via native oneinch_quote tool, not in this script
}
