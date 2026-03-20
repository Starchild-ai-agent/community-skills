---
name: "@1826/funding-rate-arb"
version: 1.3.0
description: Real-time funding rate scanner across Hyperliquid, Binance Futures, Bybit, OKX and more. Highlights biggest long/short arb gaps and gives wallet-sized entry/exit suggestions. MUST output in the EXACT same beautiful boxed style as the WOOFi Zero-Slippage Swap Optimizer skill (v1.1) and Nigeria P2P skill, with every section.
category: Trading
tags: [funding rate, arbitrage, hyperliquid, binance, bybit, okx, perp, contest, StarchildContest]
author: "@1826"
requires: premium data apis, wallet
---

## How to use this skill

When user says "scan funding rates" or calls this skill, follow these steps exactly and output ONLY the full beautiful report — no extra text, no model names, no signatures, no explanations:

### Step 1 — Pull Live Funding Rates
Fetch current 8h/1h funding rates for BTC, ETH, SOL, DOGE, XRP from:
- Hyperliquid (1h intervals)
- Binance Futures (8h)
- Bybit (8h)
- OKX (8h)
- HTX, KuCoin, Gate, MEXC, BingX, Bitget, WhiteBIT, Bitunix, CoinEx, LBank, Aster, dYdX, Coinbase Intl, Lighter

Use `funding_rate(symbol=BTC)` etc. via Coinglass premium API.

### Step 2 — Annualize & Rank
- 8h rate: `rate × 3 × 365` = annualized
- 1h rate: `rate × 24 × 365` = annualized
- Gap formula: `best_positive_rate − best_negative_rate` on the same coin
- Rank top 3 gaps by size (biggest gap = best arb)
- Flag any exchange at rate cap (usually ±1.000%)

### Step 3 — Size Recommendations
- Default leg size: $500–$1,000 per leg unless wallet data available
- Max leverage: 3x for majors (BTC/ETH), 2x for alts (DOGE/XRP/SOL)
- Must be delta-neutral: equal notional on each leg
- Daily profit estimate: `gap_per_8h × 3 × notional`

### Step 4 — Generate Report (EXACT STRUCTURE — NO DEVIATIONS)

Output the following sections in this exact order using the exact same boxes, separators, and emojis as WOOFi v1.1 and Nigeria P2P skills:

```
╔══════════════════════════════════════════════════════════╗
║  💸 CROSS-EXCHANGE FUNDING RATE ARB SCANNER  v1.3       ║
║  📅 {Day Date} · {HH:MM WAT}  |  {N} Coins · {N} CEXs  ║
╚══════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💡 BOTTOM LINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🏆 Top gap:  {COIN}  {ExchA} {rateA}/8h ↔ {ExchB} {rateB}/8h
              Gap: +{gap}%/8h = 🔥 +{annualized}% annualized
 🥈 Runner:   {COIN}  ...
 🥉 Third:    {COIN}  ...
 ⚠️  {Key risk note about rate caps or market regime}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📊 FULL RATES TABLE  (USDT-margined · live {HH:MM WAT})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 {coin_emoji} {COIN}  ${price}  ·  Next funding: ~{Xh}
 Exchange      │ 8h Rate    │ Annualized   │ Side
 ──────────────┼────────────┼──────────────┼──────────────
 {exchange}    │ {rate}%    │ 🔴/🟢 {ann}% │ SHORT/LONG pays
 ...
 Best gap: {ExchA}(long) ↔ {ExchB}(short) = +{gap}%/8h

[Repeat per coin — BTC, ETH, SOL, DOGE, XRP]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🏆 TOP 3 ARB OPPORTUNITIES  (Delta-Neutral Pairs)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 #1  🔥 {COIN}  |  Gap: +{gap}%/8h  |  +{ann}% annualized
 ┌────────────────────────────────────────────────────────┐
 │ LEG A: LONG  {COIN} on {ExchA}  (earns +{rateA}%/8h)  │
 │ LEG B: SHORT {COIN} on {ExchB}  (earns +{rateB}%/8h)  │
 │ Net collect:  +{gap}% per 8h  (~+{daily}% per day)     │
 │ Size: ${amount} each leg · {X}x leverage max           │
 │ Entry: {COIN} ${price}                                  │
 │ Est. daily: ~${profit} gross on ${notional} notional    │
 │ ⚠️  {Risk note}                                        │
 └────────────────────────────────────────────────────────┘

[Repeat for #2 and #3]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💼 WALLET SUGGESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Cleanest leg available right now:
 → {COIN} delta-neutral: LONG {ExchA} + SHORT {ExchB}
   Gross yield:  +{gap}%/8h
   Est. net:     ~+{net}%/8h after fees (~+{monthly}% monthly)
   Capital req:  ~${capital} total (${leg} each leg)
   Max leverage: {X}x · use cross margin
   Risk level:   ⚠️ {LOW/MEDIUM/HIGH} ({reason})

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚠️  RISK FLAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🔴 {Exchange} rate at cap — likely to flip, verify live
 🔴 {Market condition — e.g. ETH bearish, crowded shorts}
 ⚠️  Rates reset every 8h — gap can close before collect
 ⚠️  Capital required on BOTH legs simultaneously
 ⚠️  Maker/taker fees: ~0.02–0.05% per trade per leg
 ⚠️  Delta-neutral positions still carry liquidation risk
    if price swings >10% and margin isn't topped up

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🎯 ACT NOW?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⏳ REVIEW FIRST — then say YES to open:
  ✅ {Top gap confirmed live with exchange names}
  ✅ {Second gap confirmed — clean pair}
  ✅ {Third gap — note on quality}
  ❌ {Rate cap / flip risk — must verify live}
  ❌ {Market timing note — e.g. enter after next reset}
  ❌ {Capital placement note}

 📌 Best first trade if YES:
    {COIN}: LONG ${amount} {ExchA} + SHORT ${amount} {ExchB}
    {X}x leverage · cross margin · verify {ExchB} rate live

 👉 Reply YES to open position · NO to rescan later

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚡ Powered by Starchild · @1826/funding-rate-arb
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Safety & Rules
- NEVER execute any trade without explicit "YES" from the user.
- NEVER output any model name, token counts, or extra commentary.
- Always warn on liquidation risk and funding flip potential.
- Use only live data fetched in the current session (nothing older than 60s).
- Report opens at the header box, closes at the `⚡ Powered by` line — nothing else.
- Log every scan timestamp for trading journal reference.

## Example

User input: `Scan funding rates now`
Your output: [full formatted report in the exact structure above — all 6 sections in order, ACT NOW? box at the very end, ⚡ Powered by footer as the final line]

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.3.0 | Full section ordering locked: BOTTOM LINE → TABLE → TOP 3 → WALLET → RISK FLAGS → ACT NOW?. Verbatim template embedded. Complete WOOFi/Nigeria structural parity. |
| 1.2.0 | Added WALLET SUGGESTION + ACT NOW? CTA. Full WOOFi/Nigeria style parity. StarchildContest tag. |
| 1.0.0 | Initial release. Cross-exchange funding scanner. 5 coins, 9+ exchanges. |
