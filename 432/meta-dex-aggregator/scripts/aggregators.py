"""DEX aggregator adapters for Meta DEX Aggregator.

Every adapter returns a NORMALIZED schema:
  aggregator: str           — display name
  amount_out: str           — output amount in wei
  amount_in: str            — input amount in wei
  gas_units: int | None     — estimated gas consumption (units, NOT USD)
  gas_usd: float | None     — gas cost in USD (if upstream provides it directly)
  token_approval_address: str | None
  is_mev_safe: bool
  tx: dict | None           — transaction payload for execution
  raw: dict                 — original upstream response for debugging

The safety engine uses gas_usd if present, otherwise derives from gas_units.
This prevents the KyberSwap bug where gasUsd was stuffed into the gas_units field.
"""

import os
import http_client as http
from chains import (CHAINS, ZERO_ADDR, NATIVE_PLACEHOLDER, DEFILLAMA_REFERRER,
                    COWSWAP_CHAINS, COWSWAP_CHAIN_PREFIX, COWSWAP_WRAPPED_NATIVE, COWSWAP_NATIVE_TOKEN)


def _norm(aggregator, amount_out, amount_in="0", gas_units=None, gas_usd=None,
          token_approval_address=None, is_mev_safe=False, tx=None, raw=None, **extra):
    """Build a normalized quote dict. All adapters must go through this."""
    r = {
        "aggregator": aggregator,
        "amount_out": str(amount_out),
        "amount_in": str(amount_in),
        "gas_units": int(gas_units) if gas_units else None,
        "gas_usd": float(gas_usd) if gas_usd else None,
        "token_approval_address": token_approval_address,
        "is_mev_safe": is_mev_safe,
        "tx": tx,
        "raw": raw or {},
    }
    r.update(extra)
    return r


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
    data = http.get(url).json()
    if "error" in data:
        return None

    pr = data["priceRoute"]
    tx = None
    if wallet and wallet != ZERO_ADDR:
        slippage_bps = int(float(slippage) * 100) if slippage else 100
        tx_resp = http.post(
            f"https://apiv5.paraswap.io/transactions/{chain_id}?ignoreChecks=true",
            json={
                "srcToken": pr["srcToken"], "srcDecimals": pr["srcDecimals"],
                "destToken": pr["destToken"], "destDecimals": pr["destDecimals"],
                "slippage": slippage_bps, "userAddress": wallet,
                "partner": "llamaswap", "partnerAddress": DEFILLAMA_REFERRER,
                "takeSurplus": True, "priceRoute": pr, "isCapSurplus": True,
                "srcAmount": pr["srcAmount"],
            },
            headers={"Content-Type": "application/json"},
        )
        tx_data = tx_resp.json()
        if "error" not in tx_data:
            tx = {
                "to": tx_data["to"], "data": tx_data["data"],
                "value": tx_data.get("value", "0"),
                "gas": tx_data.get("gas", pr.get("gasCost", "0")),
                "from": tx_data["from"],
            }

    return _norm("ParaSwap",
                 amount_out=pr["destAmount"], amount_in=pr["srcAmount"],
                 gas_units=pr.get("gasCost", 0),
                 token_approval_address=pr.get("tokenTransferProxy"),
                 tx=tx, raw=pr)


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

    quote = http.post(
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
    ).json()

    if "pathId" not in quote:
        return None

    gas_est = quote.get("gasEstimate", 0)
    amount_out = str(quote.get("outAmounts", ["0"])[0])
    tx = None

    if wallet and wallet != ZERO_ADDR:
        swap_data = http.post(
            "https://api.odos.xyz/sor/assemble",
            json={"userAddr": wallet, "pathId": quote["pathId"]},
            headers={"Content-Type": "application/json"},
        ).json()

        if "transaction" in swap_data:
            tx_raw = swap_data["transaction"]
            if tx_raw["to"].lower() == ODOS_ROUTERS.get(chain, "").lower():
                tx = {
                    "to": tx_raw["to"], "data": tx_raw["data"],
                    "value": str(tx_raw.get("value", "0")),
                    "gas": str(tx_raw.get("gas") or gas_est),
                    "from": tx_raw["from"],
                }
                if swap_data.get("outputTokens"):
                    amount_out = str(swap_data["outputTokens"][0]["amount"])

    return _norm("Odos",
                 amount_out=amount_out, amount_in=amount_wei,
                 gas_units=gas_est,
                 token_approval_address=ODOS_ROUTERS.get(chain),
                 tx=tx, raw=quote)


# ── KyberSwap ─────────────────────────────────────────────────────────────────
# KEY FIX: KyberSwap returns gasUsd (dollars), NOT gas units.
# Previous code stored gasUsd into the generic "gas" field, which safety.py
# treated as gas units and multiplied by gwei*tokenPrice — double-counting.
# Now we correctly store it as gas_usd (dollars) and leave gas_units as None.
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
    data = http.get(url).json()
    if data.get("code") != 0 or not data.get("data", {}).get("routeSummary"):
        return None

    summary = data["data"]["routeSummary"]

    # IMPORTANT: summary["gasUsd"] is already in USD (e.g. "0.45").
    # Do NOT put this in gas_units — that would cause double-conversion.
    kyber_gas_usd = None
    try:
        kyber_gas_usd = float(summary.get("gasUsd", "0"))
        if kyber_gas_usd == 0:
            kyber_gas_usd = None
    except (ValueError, TypeError):
        pass

    tx = None
    if wallet and wallet != ZERO_ADDR:
        slippage_bps = int(float(slippage) * 100) if slippage else 100
        build_data = http.post(
            f"https://aggregator-api.kyberswap.com/{kyber_chain}/api/v1/route/build",
            json={
                "routeSummary": summary,
                "sender": wallet, "recipient": wallet,
                "slippageTolerance": slippage_bps,
            },
            headers={"Content-Type": "application/json"},
        ).json()

        if build_data.get("code") == 0 and build_data.get("data"):
            tx_data = build_data["data"]
            tx = {
                "to": tx_data["routerAddress"], "data": tx_data["data"],
                "value": tx_data.get("value", "0"),
                "gas": tx_data.get("gas", "0"),
                "from": wallet,
            }

    return _norm("KyberSwap",
                 amount_out=summary.get("amountOut", "0"),
                 amount_in=summary.get("amountIn", amount_wei),
                 gas_units=None,  # KyberSwap doesn't give gas units
                 gas_usd=kyber_gas_usd,  # Already in USD — use directly
                 token_approval_address=summary.get("routerAddress"),
                 tx=tx, raw=summary)


# ── 0x / Matcha ───────────────────────────────────────────────────────────────
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
        return None

    zx_chain_id = ZEROX_CHAIN_IDS.get(chain)
    if not zx_chain_id:
        return None

    native = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
    from_addr = from_tok["address"] if isinstance(from_tok, dict) else from_tok
    to_addr = to_tok["address"] if isinstance(to_tok, dict) else to_tok
    token_from = native if from_addr == ZERO_ADDR else from_addr
    token_to = native if to_addr == ZERO_ADDR else to_addr
    taker = wallet or "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
    slippage_bps = int(float(slippage) * 100) if slippage else 100

    try:
        r = http.get(
            "https://api.0x.org/swap/permit2/quote",
            params={
                "chainId": zx_chain_id, "buyToken": token_to, "sellToken": token_from,
                "sellAmount": amount_wei, "slippageBps": str(slippage_bps), "taker": taker,
            },
            headers={"0x-api-key": api_key, "0x-version": "v2"},
        )
        if r.status_code != 200:
            return None

        data = r.json()
        buy_amount = data.get("buyAmount") or data.get("minBuyAmount", "0")
        tx_data = data.get("transaction")
        gas_est = data.get("gas") or (tx_data.get("gas", "0") if tx_data else "0")

        return _norm("Matcha/0x",
                     amount_out=buy_amount, amount_in=amount_wei,
                     gas_units=gas_est,
                     token_approval_address=ZEROX_PERMIT2_ADDRESS,
                     tx=tx_data, raw=data)
    except Exception:
        return None


# ── CowSwap ───────────────────────────────────────────────────────────────────
# MEV-protected by design — solvers compete off-chain. Gasless for the user.

def cowswap_quote(chain, chain_id, from_tok, to_tok, amount_wei, wallet, slippage):
    """Get a quote from CowSwap (CoW Protocol). MEV-protected batch auctions."""
    if chain not in COWSWAP_CHAINS:
        return None

    prefix = COWSWAP_CHAIN_PREFIX[chain]
    sell_token = from_tok["address"]
    buy_token = to_tok["address"]

    # CowSwap doesn't support native ETH — must use wrapped version
    if sell_token == ZERO_ADDR or sell_token.lower() == COWSWAP_NATIVE_TOKEN.lower():
        sell_token = COWSWAP_WRAPPED_NATIVE.get(chain)
        if not sell_token:
            return None
    if buy_token == ZERO_ADDR or buy_token.lower() == COWSWAP_NATIVE_TOKEN.lower():
        buy_token = COWSWAP_WRAPPED_NATIVE.get(chain)
        if not buy_token:
            return None

    sender = wallet if wallet and wallet != ZERO_ADDR else "0x0000000000000000000000000000000000000001"

    try:
        resp = http.post(
            f"https://api.cow.fi/{prefix}/api/v1/quote",
            json={
                "sellToken": sell_token, "buyToken": buy_token,
                "sellAmountBeforeFee": str(amount_wei),
                "from": sender, "kind": "sell", "receiver": sender,
                "appData": "0x" + "0" * 64, "appDataHash": "0x" + "0" * 64,
                "partiallyFillable": False,
                "sellTokenBalance": "erc20", "buyTokenBalance": "erc20",
                "signingScheme": "eip712",
            },
            headers={"Content-Type": "application/json"},
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
    except Exception:
        return None

    quote = data.get("quote", {})
    buy_amount = quote.get("buyAmount", "0")
    fee_amount = quote.get("feeAmount", "0")
    sell_amount = quote.get("sellAmount", "0")

    tx = None
    if wallet and wallet != ZERO_ADDR:
        tx = {
            "to": f"https://api.cow.fi/{prefix}/api/v1/orders",
            "method": "POST", "type": "cowswap_order",
            "order": {
                "sellToken": sell_token, "buyToken": buy_token,
                "sellAmount": sell_amount, "buyAmount": buy_amount,
                "feeAmount": fee_amount, "kind": "sell",
                "receiver": wallet,
                "validTo": quote.get("validTo", 0),
                "appData": "0x" + "0" * 64,
                "partiallyFillable": False,
            },
            "quoteId": data.get("id"),
        }

    return _norm("CowSwap",
                 amount_out=buy_amount, amount_in=sell_amount,
                 gas_units=None,      # Gasless for the user
                 gas_usd=0.0,         # Solvers pay gas, user pays protocol fee from sell token
                 token_approval_address=quote.get("receiver", "0x40A50cf069e992AA4536211B23F286eF88752187"),
                 is_mev_safe=True,
                 tx=tx, raw=data,
                 fee_amount=fee_amount)


# ── 1inch (placeholder) ──────────────────────────────────────────────────────
# 1inch requires API key. Agent calls oneinch_quote tool separately.
def inch_quote(chain, chain_id, from_tok, to_tok, amount_wei, wallet, slippage):
    """Placeholder - 1inch requires API key. Use oneinch_quote tool instead."""
    return None


# ── Dispatch ──────────────────────────────────────────────────────────────────
AGGREGATORS = {
    "paraswap": paraswap_quote,
    "odos": odos_quote,
    "kyberswap": kyberswap_quote,
    "matcha/0x": zerox_quote,
    "cowswap": cowswap_quote,
}
