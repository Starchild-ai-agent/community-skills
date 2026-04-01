#!/usr/bin/env python3
"""
SOL 15M Scalping Signal Monitor
Strategy: 9/21 EMA cross + 50 EMA bias + RSI filter + volume spike
Enhanced: Funding rate check + Order Block detection
"""

import requests
import json
import time
import sys
import numpy as np

JOB_ID = "interval_14b08cb274ef"

# ── Fetch candles from Hyperliquid ──────────────────────────────────────────
def fetch_candles(coin="SOL", interval="15m", lookback_hours=20):
    now_ms = int(time.time() * 1000)
    start_ms = now_ms - (lookback_hours * 60 * 60 * 1000)
    payload = {
        "type": "candleSnapshot",
        "req": {"coin": coin, "interval": interval, "startTime": start_ms, "endTime": now_ms}
    }
    resp = requests.post("https://api.hyperliquid.xyz/info", json=payload, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    if not data or len(data) < 60:
        return None
    opens   = [float(c["o"]) for c in data]
    closes  = [float(c["c"]) for c in data]
    highs   = [float(c["h"]) for c in data]
    lows    = [float(c["l"]) for c in data]
    volumes = [float(c["v"]) for c in data]
    return opens, closes, highs, lows, volumes

# ── EMA helper ───────────────────────────────────────────────────────────────
def ema(series, period):
    k = 2 / (period + 1)
    result = [series[0]]
    for v in series[1:]:
        result.append(v * k + result[-1] * (1 - k))
    return result

# ── RSI helper ───────────────────────────────────────────────────────────────
def rsi(closes, period=14):
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains  = [max(d, 0) for d in deltas]
    losses = [max(-d, 0) for d in deltas]
    avg_g  = sum(gains[:period]) / period
    avg_l  = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_g = (avg_g * (period - 1) + gains[i]) / period
        avg_l = (avg_l * (period - 1) + losses[i]) / period
    if avg_l == 0:
        return 100.0
    return 100 - (100 / (1 + avg_g / avg_l))

# ── Funding rate ─────────────────────────────────────────────────────────────
def get_funding(coin="SOL"):
    try:
        payload = {"type": "metaAndAssetCtxs"}
        resp = requests.post("https://api.hyperliquid.xyz/info", json=payload, timeout=10)
        meta, ctx = resp.json()
        for asset, c in zip(meta["universe"], ctx):
            if asset["name"] == coin:
                fr = float(c.get("funding", 0)) * 100
                oi = float(c.get("openInterest", 0))
                return fr, oi
    except Exception:
        pass
    return None, None

# ── Order Block Detection ─────────────────────────────────────────────────────
# An order block is:
#   Bullish OB  — last bearish (down) candle before a strong bullish impulse
#   Bearish OB  — last bullish (up) candle before a strong bearish impulse
# "Strong impulse" = body size >= 1.5x average body size in the lookback window
# We scan the last N candles and return the most recent valid OBs still "alive"
# (price hasn't fully traded through them)

def detect_order_blocks(opens, closes, highs, lows, lookback=60, min_impulse_mult=1.5):
    n = len(closes)
    if n < lookback + 3:
        return [], []

    candles = list(zip(opens[-lookback:], closes[-lookback:],
                       highs[-lookback:], lows[-lookback:]))
    bodies = [abs(c[1] - c[0]) for c in candles]
    avg_body = sum(bodies) / len(bodies) if bodies else 0

    bullish_obs = []  # (zone_high, zone_low, idx_in_window, age_candles)
    bearish_obs = []

    cur_price = closes[-1]

    for i in range(1, len(candles) - 2):
        o, c, h, l = candles[i]
        # Check next 2 candles for impulse
        impulse_body = max(abs(candles[i+1][1] - candles[i+1][0]),
                           abs(candles[i+2][1] - candles[i+2][0]))

        if impulse_body < avg_body * min_impulse_mult:
            continue

        age = len(candles) - 1 - i  # candles ago

        # Bullish OB: bearish candle (c < o) followed by bullish impulse
        if c < o:
            next_bullish = candles[i+1][1] > candles[i+1][0]
            if next_bullish:
                ob_high = h
                ob_low  = l
                # Still valid if current price is above the OB low (not taken out below)
                if cur_price > ob_low:
                    bullish_obs.append({
                        "high": ob_high,
                        "low":  ob_low,
                        "mid":  (ob_high + ob_low) / 2,
                        "age":  age,
                        "dist_pct": (cur_price - ob_high) / cur_price * 100
                    })

        # Bearish OB: bullish candle (c > o) followed by bearish impulse
        if c > o:
            next_bearish = candles[i+1][1] < candles[i+1][0]
            if next_bearish:
                ob_high = h
                ob_low  = l
                # Still valid if current price is below the OB high (not taken out above)
                if cur_price < ob_high:
                    bearish_obs.append({
                        "high": ob_high,
                        "low":  ob_low,
                        "mid":  (ob_high + ob_low) / 2,
                        "age":  age,
                        "dist_pct": (ob_low - cur_price) / cur_price * 100
                    })

    # Sort by proximity to current price
    bullish_obs.sort(key=lambda x: abs(x["dist_pct"]))
    bearish_obs.sort(key=lambda x: abs(x["dist_pct"]))

    return bullish_obs[:3], bearish_obs[:3]  # top 3 nearest each side

# ── Check if price is near an order block ───────────────────────────────────
def ob_proximity(cur_price, bullish_obs, bearish_obs, threshold_pct=0.5):
    """Returns (near_bullish_ob, near_bearish_ob, ob_note)"""
    near_bull = None
    near_bear = None

    for ob in bullish_obs:
        if abs(ob["dist_pct"]) <= threshold_pct:
            near_bull = ob
            break

    for ob in bearish_obs:
        if abs(ob["dist_pct"]) <= threshold_pct:
            near_bear = ob
            break

    return near_bull, near_bear


# ── Format OB section for alert ─────────────────────────────────────────────
def format_ob_section(bullish_obs, bearish_obs, cur_price):
    lines = []

    if bullish_obs:
        ob = bullish_obs[0]
        tag = " ← PRICE HERE" if abs(ob["dist_pct"]) < 0.5 else ""
        lines.append(f"  Bull OB: ${ob['low']:.3f}–${ob['high']:.3f}  "
                     f"({ob['dist_pct']:+.2f}% away, {ob['age']}c ago){tag}")
    else:
        lines.append("  Bull OB: none detected")

    if bearish_obs:
        ob = bearish_obs[0]
        tag = " ← PRICE HERE" if abs(ob["dist_pct"]) < 0.5 else ""
        lines.append(f"  Bear OB: ${ob['low']:.3f}–${ob['high']:.3f}  "
                     f"({ob['dist_pct']:+.2f}% away, {ob['age']}c ago){tag}")
    else:
        lines.append("  Bear OB: none detected")

    # Show 2nd nearest if exists
    if len(bullish_obs) > 1:
        ob = bullish_obs[1]
        lines.append(f"  Bull OB2: ${ob['low']:.3f}–${ob['high']:.3f}  "
                     f"({ob['dist_pct']:+.2f}%)")
    if len(bearish_obs) > 1:
        ob = bearish_obs[1]
        lines.append(f"  Bear OB2: ${ob['low']:.3f}–${ob['high']:.3f}  "
                     f"({ob['dist_pct']:+.2f}%)")

    return "\n".join(lines)


# ── Main signal check ─────────────────────────────────────────────────────────
def check_signal():
    result = fetch_candles("SOL", "15m", lookback_hours=20)
    if not result:
        print("Not enough candle data.", file=sys.stderr)
        return

    opens, closes, highs, lows, volumes = result

    if len(closes) < 60:
        print("Not enough candle data.", file=sys.stderr)
        return

    # Use last 60 candles for indicator calc
    o = opens[-60:]
    c = closes[-60:]
    h = highs[-60:]
    l = lows[-60:]
    v = volumes[-60:]

    e9   = ema(c, 9)
    e21  = ema(c, 21)
    e50  = ema(c, 50)
    rsi_raw = rsi(c, 14)
    # RSI Smoothed (5-period MA) — reduces noise, improves signal quality
    rsi_arr = np.array(rsi_raw)
    rsi_smooth = np.convolve(rsi_arr, np.ones(5)/5, mode='same')
    rsi_val = rsi_smooth[-1]

    # ── 1H EMA (50) — use 4x span since 4x 15M = 1H ────────────────────────
    e50_1h = ema(closes[-240:] if len(closes) >= 240 else closes, 200)
    cur_e50_1h = e50_1h[-1]

    # ── 200 EMA Regime Gate (macro trend filter) ────────────────────────────
    e200 = ema(np.array(closes), 200)
    cur_e200 = e200[-1]
    macro_bull = closes[-1] > cur_e200
    macro_bear = closes[-1] < cur_e200

    # ── VWAP (daily reset, approximate over available candles) ───────────────
    tp  = [(highs[i] + lows[i] + closes[i]) / 3 for i in range(len(closes))]
    tp_vol = [tp[i] * volumes[i] for i in range(len(closes))]
    # Use last 96 candles (~1 day) as rolling VWAP proxy
    window = 96
    cum_tpv = sum(tp_vol[-window:])
    cum_v   = sum(volumes[-window:]) if sum(volumes[-window:]) > 0 else 1
    vwap_val = cum_tpv / cum_v

    cur_e9    = e9[-1];   prev_e9   = e9[-2]
    cur_e21   = e21[-1];  prev_e21  = e21[-2]
    cur_e50   = e50[-1]
    cur_price = c[-1]
    cur_high  = h[-1]
    cur_low   = l[-1]
    cur_vol   = v[-1]
    vol_avg5  = sum(v[-6:-1]) / 5

    # ── Order blocks (use full candle history) ──────────────────────────────
    bullish_obs, bearish_obs = detect_order_blocks(
        opens, closes, highs, lows, lookback=60
    )
    near_bull_ob, near_bear_ob = ob_proximity(
        cur_price, bullish_obs, bearish_obs, threshold_pct=0.5
    )

    # ── Crossover detection ─────────────────────────────────────────────────
    long_cross  = (cur_e9 > cur_e21) and (prev_e9 <= prev_e21)
    short_cross = (cur_e9 < cur_e21) and (prev_e9 >= prev_e21)

    # ── OB confluence bonus: near a bullish OB = stronger long, near bearish = stronger short
    ob_long_confluence  = near_bull_ob is not None
    ob_short_confluence = near_bear_ob is not None

    # ── Signal conditions ───────────────────────────────────────────────────
    long_signal  = (
        long_cross
        and cur_price > cur_e50
        and 45 <= rsi_val <= 65         # RSI Smoothed gate
        and cur_vol >= vol_avg5 * 1.3
        and cur_price > cur_e50_1h      # 1H EMA filter
        and cur_price > vwap_val        # VWAP filter
        and macro_bull                  # 200 EMA Regime Gate — no longs in downtrend
    )
    short_signal = (
        short_cross
        and cur_price < cur_e50
        and 35 <= rsi_val <= 55         # RSI Smoothed gate
        and cur_vol >= vol_avg5 * 1.3
        and cur_price < cur_e50_1h      # 1H EMA filter
        and cur_price < vwap_val        # VWAP filter
        and macro_bear                  # 200 EMA Regime Gate — no shorts in uptrend
    )

    # ── Always-on OB proximity alert (no crossover needed) ─────────────────
    # Fire an alert if price is sitting right on a key OB even without a cross
    ob_only_long  = (not long_signal and not short_signal
                     and ob_long_confluence
                     and cur_price > cur_e50
                     and 40 <= rsi_val <= 70)
    ob_only_short = (not long_signal and not short_signal
                     and ob_short_confluence
                     and cur_price < cur_e50
                     and 30 <= rsi_val <= 60)

    if not long_signal and not short_signal and not ob_only_long and not ob_only_short:
        return  # silent — no signal

    # ── Funding rate ────────────────────────────────────────────────────────
    funding, oi = get_funding("SOL")
    funding_str = f"{funding:+.4f}%" if funding is not None else "N/A"
    oi_str      = f"{oi:,.0f}" if oi is not None else "N/A"

    funding_warn = ""
    if funding is not None:
        if (long_signal or ob_only_long) and funding > 0.03:
            funding_warn = " ⚠️ longs paying — reduce size"
        elif (short_signal or ob_only_short) and funding < -0.03:
            funding_warn = " ⚠️ shorts paying — reduce size"
        elif abs(funding) < 0.005:
            funding_warn = " ✅ neutral — clean entry env"

    # ── Levels ──────────────────────────────────────────────────────────────
    if long_signal or ob_only_long:
        direction = "LONG 🟢" if long_signal else "LONG 🟢 (OB only — no cross yet)"
        sl   = cur_low * 0.999
        risk = cur_price - sl
        tp1  = cur_price + 1.5 * risk
        tp2  = cur_price + 2.5 * risk
    else:
        direction = "SHORT 🔴" if short_signal else "SHORT 🔴 (OB only — no cross yet)"
        sl   = cur_high * 1.001
        risk = sl - cur_price
        tp1  = cur_price - 1.5 * risk
        tp2  = cur_price - 2.5 * risk

    # ── OB confluence note ──────────────────────────────────────────────────
    conf_note = ""
    if long_signal and ob_long_confluence:
        conf_note = "  🔥 OB CONFLUENCE — signal + bullish OB = high conviction\n"
    elif short_signal and ob_short_confluence:
        conf_note = "  🔥 OB CONFLUENCE — signal + bearish OB = high conviction\n"

    # ── OB section ──────────────────────────────────────────────────────────
    ob_section = format_ob_section(bullish_obs, bearish_obs, cur_price)

    # ── Signal type label ───────────────────────────────────────────────────
    if long_signal or short_signal:
        sig_type = "FULL SIGNAL ✅"
    else:
        sig_type = "OB WATCH ZONE ⚡ (no crossover yet)"

    msg = (
        f"📡 SOL 15M SCALP — {sig_type}\n"
        f"─────────────────────────────\n"
        f"Direction : {direction}\n"
        f"Price     : ${cur_price:.3f}\n"
        f"{conf_note}"
        f"─────────────────────────────\n"
        f"Stop Loss       : ${sl:.3f}  ({abs(cur_price-sl)/cur_price*100:.2f}%)\n"
        f"Take Profit 1   : ${tp1:.3f}  (1.5R)\n"
        f"Take Profit 2   : ${tp2:.3f}  (2.5R)\n"
        f"─────────────────────────────\n"
        f"RSI       : {rsi_val:.1f}\n"
        f"EMA 9/21  : ${cur_e9:.3f} / ${cur_e21:.3f}\n"
        f"EMA 50    : ${cur_e50:.3f}\n"
        f"1H EMA50  : ${cur_e50_1h:.3f} ({'✅ above' if cur_price > cur_e50_1h else '❌ below'})\n"
        f"200 EMA   : ${cur_e200:.3f} ({'✅ BULL regime' if macro_bull else '🔴 BEAR regime — longs blocked'})\n"
        f"VWAP      : ${vwap_val:.3f} ({'✅ above' if cur_price > vwap_val else '❌ below'})\n"
        f"RSI (raw) : {rsi_raw[-1]:.1f} | RSI (smooth): {rsi_val:.1f}\n"
        f"Volume    : {cur_vol:,.0f} ({cur_vol/vol_avg5:.1f}x avg)\n"
        f"Funding   : {funding_str}{funding_warn}\n"
        f"Open Int  : {oi_str} SOL\n"
        f"─────────────────────────────\n"
        f"Order Blocks (15M):\n{ob_section}\n"
        f"─────────────────────────────\n"
        f"Risk: 1% of account | Leverage: 1–2x max\n"
        f"Position $: risk_dollars / sl_pct × leverage\n"
        f"  e.g. $10k acct → $100 risk / 0.4% SL × 2x = $50k notional\n"
        f"Sizing rule: NEVER risk >1% per trade. Compound winnings, not risk.\n"
        f"Close 50% @ TP1, move SL to breakeven\n"
        f"Full exit @ TP2 or EMA cross reversal"
    )
    print(msg)

if __name__ == "__main__":
    check_signal()
