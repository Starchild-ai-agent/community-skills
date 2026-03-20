"""
Meta DEX Aggregator Safety Layer — Price impact, slippage, gas-adjusted ranking, MEV flags.
Implements protective checks: price impact detection, gas-adjusted ranking, and outlier rejection.

Thresholds from constants.ts:
  PRICE_IMPACT_WARNING = 3%, MEDIUM = 5%, HIGH = 10%
"""

import requests, json, sys

PRICE_IMPACT_WARNING = 3.0
PRICE_IMPACT_MEDIUM  = 5.0
PRICE_IMPACT_HIGH    = 10.0
SLIPPAGE_SANDWICH_RISK = 1.0
STABLECOIN_SLIPPAGE_MAX = 0.05
LOW_SLIPPAGE_THRESHOLD  = 0.05

STABLECOINS = {
    "USDT", "USDC", "BUSD", "DAI", "FRAX", "TUSD", "USDD", "USDP", "GUSD",
    "LUSD", "sUSD", "FPI", "MIM", "DOLA", "USP", "USDX", "MAI", "EURS",
    "EURT", "alUSD", "PAX", "USDS", "GHO", "crvUSD", "pyUSD", "USDe"
}
MEV_SAFE_AGGREGATORS = {"CowSwap", "0x Gasless", "Hashflow"}
DEFILLAMA_CHAIN_MAP = {
    "ethereum": "ethereum", "bsc": "bsc", "polygon": "polygon",
    "optimism": "optimism", "arbitrum": "arbitrum", "avax": "avax",
    "avalanche": "avax", "gnosis": "xdai", "fantom": "fantom",
    "zksync": "era", "base": "base", "linea": "linea",
    "scroll": "scroll", "sonic": "sonic", "unichain": "unichain",
}
ZERO_ADDR = "0x0000000000000000000000000000000000000000"


def _dexscreener_price(chain, token_addr):
    """Liquidity-weighted price from DexScreener (experimental price fallback)."""
    try:
        resp = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{token_addr}", timeout=2)
        if resp.status_code != 200:
            return None
        pairs = resp.json().get("pairs", [])
        wp, tl = 0.0, 0.0
        for pair in pairs:
            liq = (pair.get("liquidity") or {}).get("usd", 0)
            pu = pair.get("priceUsd")
            ba = (pair.get("baseToken") or {}).get("address", "")
            if liq > 10000 and pu and ba.lower() == token_addr.lower():
                p = float(pu)
                if tl > 0:
                    avg = wp / tl
                    if abs(p - avg) / avg > 0.1:
                        continue
                wp += p * liq
                tl += liq
        return wp / tl if tl > 0 else None
    except Exception:
        return None


def get_fair_market_prices(chain, from_addr, to_addr):
    """Fetch fair market prices from DefiLlama coins API + DexScreener fallback."""
    llama_chain = DEFILLAMA_CHAIN_MAP.get(chain, chain)
    coin_ids = [f"{llama_chain}:{ZERO_ADDR}"]
    if from_addr != ZERO_ADDR:
        coin_ids.append(f"{llama_chain}:{from_addr}")
    if to_addr != ZERO_ADDR:
        coin_ids.append(f"{llama_chain}:{to_addr}")

    prices = {}
    try:
        resp = requests.get(f"https://coins.llama.fi/prices/current/{','.join(coin_ids)}", timeout=5)
        if resp.status_code == 200:
            for cid, data in resp.json().get("coins", {}).items():
                prices[cid.split(":")[-1].lower()] = data.get("price")
    except Exception:
        pass

    for addr in [from_addr, to_addr]:
        if addr != ZERO_ADDR and (addr.lower() not in prices or prices.get(addr.lower()) is None):
            p = _dexscreener_price(chain, addr)
            if p:
                prices[addr.lower()] = p

    return {
        "gas_token_price": prices.get(ZERO_ADDR),
        "from_token_price": prices.get(ZERO_ADDR if from_addr == ZERO_ADDR else from_addr.lower()),
        "to_token_price": prices.get(ZERO_ADDR if to_addr == ZERO_ADDR else to_addr.lower()),
    }


def calculate_price_impact(amount_in, amount_out, from_price, to_price):
    if not all([from_price, to_price, amount_in, amount_out]):
        return None
    val_in = float(amount_in) * float(from_price)
    val_out = float(amount_out) * float(to_price)
    if val_in <= 0:
        return None
    return round(((val_in - val_out) / val_in) * 100, 4)


def classify_price_impact(impact):
    if impact is None: return "unknown"
    if impact < PRICE_IMPACT_WARNING: return "ok"
    if impact < PRICE_IMPACT_MEDIUM: return "warning"
    if impact < PRICE_IMPACT_HIGH: return "high"
    return "critical"


def slippage_warnings(slippage, from_sym, to_sym):
    warnings = []
    s = float(slippage)
    is_stable = from_sym in STABLECOINS and to_sym in STABLECOINS
    if s > SLIPPAGE_SANDWICH_RISK:
        warnings.append({"level": "warning", "msg": f"High slippage ({s}%)! You might get sandwiched."})
    if is_stable and s > STABLECOIN_SLIPPAGE_MAX:
        warnings.append({"level": "warning", "msg": f"Stablecoin pair but slippage is {s}% — recommend ≤0.05%."})
    if not is_stable and s < LOW_SLIPPAGE_THRESHOLD:
        warnings.append({"level": "warning", "msg": f"Slippage very low ({s}%) — tx likely to revert."})
    return warnings


def gas_adjusted_ranking(quotes, gas_token_price, to_token_price):
    """Rank quotes by net output (amountUsd - gasUsd) with gas-adjusted comparison."""
    ranked = []
    for q in quotes:
        out = float(q.get("outputAmount", 0))
        gas_est = q.get("estimatedGas", 0)
        amt_usd = out * float(to_token_price) if to_token_price else None
        gas_usd = None
        if gas_est and gas_token_price:
            gas_usd = float(gas_est) * 30 * 1e-9 * float(gas_token_price)
        if amt_usd is not None and gas_usd is not None:
            net = amt_usd - gas_usd
        elif amt_usd is not None:
            net = amt_usd
        else:
            net = out
        ranked.append({
            **q,
            "amountUsd": round(amt_usd, 2) if amt_usd else None,
            "gasUsd": round(gas_usd, 4) if gas_usd else None,
            "netOut": round(net, 4),
            "isMEVSafe": q.get("name", "") in MEV_SAFE_AGGREGATORS,
        })
    ranked.sort(key=lambda x: x["netOut"], reverse=True)
    if ranked:
        best = ranked[0]["netOut"]
        for r in ranked:
            r["vsbestPct"] = round((r["netOut"] / best * 100) if best > 0 else 100, 2)
            r["isOutlier"] = r["vsbestPct"] < 95
    return ranked


def full_safety_check(quotes, chain, from_addr, to_addr, from_sym, to_sym,
                      amount_in_human, slippage="0.5"):
    """Complete safety analysis pipeline."""
    prices = get_fair_market_prices(chain, from_addr, to_addr)
    ranked = gas_adjusted_ranking(quotes, prices["gas_token_price"], prices["to_token_price"])

    best = ranked[0] if ranked else None
    impact = None
    severity = "unknown"
    if best and prices["from_token_price"] and prices["to_token_price"]:
        impact = calculate_price_impact(
            amount_in_human, best.get("outputAmount", 0),
            prices["from_token_price"], prices["to_token_price"]
        )
        severity = classify_price_impact(impact)

    slip_w = slippage_warnings(slippage, from_sym, to_sym)

    # Build recommendation
    rec = []
    if severity == "critical":
        rec.append(f"⛔ PRICE IMPACT {impact:.1f}% — You will likely lose money.")
    elif severity == "high":
        rec.append(f"🔴 HIGH PRICE IMPACT ({impact:.1f}%) — Proceed with extreme caution.")
    elif severity == "warning":
        rec.append(f"🟡 Moderate price impact ({impact:.1f}%) — Review carefully.")
    elif severity == "unknown":
        rec.append("⚠️ Could not determine price impact (no market price available).")

    # MEV recommendation
    mev_safe = [r for r in ranked if r.get("isMEVSafe")]
    if mev_safe and ranked and not ranked[0].get("isMEVSafe"):
        bm = mev_safe[0]
        if ranked[0]["netOut"] > 0:
            d = abs(ranked[0]["netOut"] - bm["netOut"]) / ranked[0]["netOut"] * 100
            if d < 0.5:
                rec.append(f"🛡️ {bm['name']} is MEV-protected and only {d:.2f}% worse — recommended.")
            elif d < 2:
                rec.append(f"🛡️ {bm['name']} offers MEV protection ({d:.1f}% less output).")

    for w in slip_w:
        rec.append(f"⚠️ {w['msg']}")
    outliers = [r["name"] for r in ranked if r.get("isOutlier")]
    if outliers:
        rec.append(f"🚫 Outlier quotes (>5% worse): {', '.join(outliers)} — avoid.")
    if not rec:
        rec.append("✅ All checks passed. Best route looks safe.")

    return {
        "prices": prices,
        "ranked_quotes": ranked,
        "price_impact": {"value": impact, "severity": severity},
        "slippage_warnings": slip_w,
        "recommendation": " | ".join(rec),
    }


if __name__ == "__main__":
    prices = get_fair_market_prices("ethereum", ZERO_ADDR, "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")
    print(f"Gas token (ETH): ${prices['gas_token_price']}")
    print(f"From (ETH): ${prices['from_token_price']}")
    print(f"To (USDC): ${prices['to_token_price']}")
    impact = calculate_price_impact(1.0, 2100, prices["from_token_price"], prices["to_token_price"])
    print(f"\n1 ETH -> 2100 USDC: impact {impact:.2f}% ({classify_price_impact(impact)})")
    impact2 = calculate_price_impact(1.0, 1800, prices["from_token_price"], prices["to_token_price"])
    print(f"1 ETH -> 1800 USDC: impact {impact2:.2f}% ({classify_price_impact(impact2)})")
    print(f"\nSlippage warnings (2% volatile): {slippage_warnings('2', 'ETH', 'USDC')}")
    print(f"Slippage warnings (1% stables): {slippage_warnings('1', 'USDC', 'USDT')}")
