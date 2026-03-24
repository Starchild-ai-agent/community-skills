"""
Meta DEX Aggregator Safety Layer - Price impact, gas-adjusted ranking, MEV flags.

v4.1 changes:
  - Uses normalized quote schema (gas_units / gas_usd split)
  - Uses per-chain live gas oracle instead of hardcoded 30 gwei
  - Uses shared HTTP client for connection pooling
"""

import time
import http_client as http
import gas_oracle

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

# ── Price cache (avoids repeated DefiLlama/DexScreener calls) ────────
_price_cache = {}  # key: (chain, addr) -> {"price": float, "ts": float}
_PRICE_CACHE_TTL = 15  # seconds — short enough to stay fresh, long enough to dedupe

def _cached_price(chain, addr):
    key = (chain, addr.lower())
    entry = _price_cache.get(key)
    if entry and time.time() - entry["ts"] < _PRICE_CACHE_TTL:
        return entry["price"]
    return None

def _set_price_cache(chain, addr, price):
    _price_cache[(chain, addr.lower())] = {"price": price, "ts": time.time()}


def _dexscreener_price(chain, token_addr):
    """Liquidity-weighted price from DexScreener (fallback)."""
    try:
        resp = http.get(f"https://api.dexscreener.com/latest/dex/tokens/{token_addr}", timeout=(2, 2))
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
    """Fetch fair market prices from cache → DefiLlama → DexScreener fallback."""
    llama_chain = DEFILLAMA_CHAIN_MAP.get(chain, chain)

    # Check cache first — avoids network calls on repeated quotes
    all_addrs = [ZERO_ADDR]
    if from_addr != ZERO_ADDR:
        all_addrs.append(from_addr)
    if to_addr != ZERO_ADDR:
        all_addrs.append(to_addr)

    prices = {}
    uncached = []
    for addr in all_addrs:
        cp = _cached_price(chain, addr)
        if cp is not None:
            prices[addr.lower()] = cp
        else:
            uncached.append(addr)

    # Fetch only uncached prices from DefiLlama
    if uncached:
        coin_ids = [f"{llama_chain}:{a}" for a in uncached]
        try:
            resp = http.get(f"https://coins.llama.fi/prices/current/{','.join(coin_ids)}", timeout=(2, 5))
            if resp.status_code == 200:
                for cid, data in resp.json().get("coins", {}).items():
                    addr = cid.split(":")[-1].lower()
                    p = data.get("price")
                    if p is not None:
                        prices[addr] = p
                        _set_price_cache(chain, addr, p)
        except Exception:
            pass

    # DexScreener fallback for still-missing tokens
    for addr in [from_addr, to_addr]:
        if addr != ZERO_ADDR and (addr.lower() not in prices or prices.get(addr.lower()) is None):
            p = _dexscreener_price(chain, addr)
            if p:
                prices[addr.lower()] = p
                _set_price_cache(chain, addr, p)

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
        warnings.append({"level": "warning", "msg": f"Stablecoin pair but slippage is {s}% - recommend <=0.05%."})
    if not is_stable and s < LOW_SLIPPAGE_THRESHOLD:
        warnings.append({"level": "warning", "msg": f"Slippage very low ({s}%) - tx likely to revert."})
    return warnings


def gas_adjusted_ranking(quotes, chain, gas_token_price, to_token_price):
    """Rank quotes by net output (amountUsd - gasUsd).

    Uses normalized schema:
      - If quote has gas_usd (e.g. KyberSwap): use it directly
      - If quote has gas_units: derive gas_usd via live gas oracle
      - If neither: penalize with median gas from peers (never treat unknown as zero)
    """
    ranked = []

    # Phase 1: resolve known gas costs across all quotes
    known_gas = []
    for q in quotes:
        g = None
        if q.get("gas_usd") is not None and q["gas_usd"] > 0:
            g = q["gas_usd"]
        elif q.get("gas_units") and gas_token_price:
            g = gas_oracle.estimate_gas_usd(chain, q["gas_units"], gas_token_price)
        if g and g > 0:
            known_gas.append(g)

    # Phase 2: fallback for unknown gas — use median of known peers
    # Unknown gas should NEVER be treated as zero gas (biases ranking)
    median_gas = None
    if known_gas:
        s = sorted(known_gas)
        mid = len(s) // 2
        median_gas = s[mid] if len(s) % 2 else (s[mid - 1] + s[mid]) / 2

    for q in quotes:
        out = float(q.get("outputAmount", 0))
        amt_usd = out * float(to_token_price) if to_token_price else None

        # Resolve gas cost — prefer upstream gas_usd, else derive, else median peer penalty
        final_gas_usd = None
        gas_source = "known"
        if q.get("gas_usd") is not None and q["gas_usd"] > 0:
            final_gas_usd = q["gas_usd"]
        elif q.get("gas_units") and gas_token_price:
            final_gas_usd = gas_oracle.estimate_gas_usd(chain, q["gas_units"], gas_token_price)
        elif median_gas is not None:
            # Penalize unknown gas with median from peers — fair, not free
            final_gas_usd = median_gas
            gas_source = "estimated"

        if amt_usd is not None and final_gas_usd is not None:
            net = amt_usd - final_gas_usd
        elif amt_usd is not None:
            net = amt_usd
        else:
            net = out

        ranked.append({
            **q,
            "amountUsd": round(amt_usd, 2) if amt_usd else None,
            "gasUsd": round(final_gas_usd, 4) if final_gas_usd else None,
            "gasSource": gas_source,
            "netOut": round(net, 4),
            "isMEVSafe": q.get("is_mev_safe", False) or q.get("name", "") in MEV_SAFE_AGGREGATORS,
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
    ranked = gas_adjusted_ranking(quotes, chain, prices["gas_token_price"], prices["to_token_price"])

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

    rec = []
    if severity == "critical":
        rec.append(f"PRICE IMPACT {impact:.1f}% - You will likely lose money.")
    elif severity == "high":
        rec.append(f"HIGH PRICE IMPACT ({impact:.1f}%) - Proceed with extreme caution.")
    elif severity == "warning":
        rec.append(f"Moderate price impact ({impact:.1f}%) - Review carefully.")
    elif severity == "unknown":
        rec.append("Could not determine price impact (no market price available).")

    mev_safe = [r for r in ranked if r.get("isMEVSafe")]
    if mev_safe and ranked and not ranked[0].get("isMEVSafe"):
        bm = mev_safe[0]
        if ranked[0]["netOut"] > 0:
            d = abs(ranked[0]["netOut"] - bm["netOut"]) / ranked[0]["netOut"] * 100
            if d < 0.5:
                rec.append(f"{bm['name']} is MEV-protected and only {d:.2f}% worse - recommended.")
            elif d < 2:
                rec.append(f"{bm['name']} offers MEV protection ({d:.1f}% less output).")

    for w in slip_w:
        rec.append(w["msg"])
    outliers = [r["name"] for r in ranked if r.get("isOutlier")]
    if outliers:
        rec.append(f"Outlier quotes (>5% worse): {', '.join(outliers)} - avoid.")
    if not rec:
        rec.append("All checks passed. Best route looks safe.")

    return {
        "prices": prices,
        "ranked_quotes": ranked,
        "price_impact": {"value": impact, "severity": severity},
        "slippage_warnings": slip_w,
        "recommendation": " | ".join(rec),
    }
