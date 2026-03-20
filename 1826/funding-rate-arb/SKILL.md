---
name: "@1826/funding-rate-arb"
version: 1.1.0
description: Real-time funding rate scanner across Hyperliquid, Binance Futures, Bybit, OKX and more. Highlights biggest long/short arb gaps and gives wallet-sized entry/exit suggestions. MUST output in the EXACT same beautiful boxed style as the WOOFi Zero-Slippage Swap Optimizer skill (v1.1) and Nigeria P2P skill.
category: Trading
tags: [funding rate, arbitrage, hyperliquid, binance, bybit, okx, perp, contest, StarchildContest]
author: "@1826"
requires: premium data apis, wallet
---

# Cross-Exchange Funding Rate Arbitrage Scanner v1.1

## Overview

Scans live 8h/1h perpetual funding rates across Hyperliquid, Binance Futures, Bybit, OKX, HTX, KuCoin, Gate, BingX, MEXC, Bitget, WhiteBIT, and more. Identifies top delta-neutral arb opportunities, annualizes gaps, and outputs a full boxed report with wallet-sized trade suggestions and ACT NOW? CTA — identically styled to the WOOFi v1.1 and Nigeria P2P skills.

---

## How to use this skill

When user says **"scan funding rates"** or calls this skill, follow these steps exactly and output **ONLY** the full beautiful report — no extra text, no model names, no signatures, no commentary:

### Step 1 — Pull Live Funding Rates
Use `funding_rate(symbol=X)` for each coin:
```
funding_rate(symbol="BTC")
funding_rate(symbol="ETH")
funding_rate(symbol="SOL")
funding_rate(symbol="DOGE")
funding_rate(symbol="XRP")
```
Pull ALL exchanges from each response (`uMarginList` array). Note each exchange's rate, interval (8h or 1h), and normalize to 8h-equivalent.

**Normalization:** If exchange uses 1h intervals → multiply by 8 to get 8h equivalent.

### Step 2 — Calculate Annualized Rates
```
Annualized % = (8h_rate × 3 × 365) × 100
```
Flag rates > +0.500%/8h as 🟢 HOT, rates < -0.500%/8h as 🔴 HIGH SHORT PRESSURE.

### Step 3 — Identify Top 3 Arb Gaps
For each coin, rank the gap between:
- The exchange with **lowest (most negative)** rate → LONG leg (LONG here, collect funding)
- The exchange with **highest (most positive)** rate → SHORT leg (SHORT here, collect funding)

Gap = |positive_rate| + |negative_rate|

Sort all coin/pair combos by gap descending. Top 3 = your arb opportunities.

### Step 4 — Pull Current Prices
```
coin_price(coin_ids="bitcoin,ethereum,solana,dogecoin,ripple")
```

### Step 5 — Generate Report

Output ONLY this report structure, no text before or after:

```
╔══════════════════════════════════════════════════════════╗
║  💸 FUNDING RATE ARB SCANNER  v1.1                      ║
║  📅 {Day DD Mon YYYY · HH:MM WAT}  |  {N} Coins · CEXs  ║
╚══════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💡 BOTTOM LINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🏆 Top gap:   {COIN} — {ExchangeA} {rateA}% vs
               {ExchangeB} {rateB}%  per 8h
    Net gap:   +{gap}%/8h = {annualized}% annualized
 🥈 Runner-up: {COIN2 summary}
 🥉 Third:     {COIN3 summary}
 📌 {1-line market sentiment note}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📊 FULL RATES TABLE  (USDT-margined perps)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 {COIN}  ${price}  ·  Next funding: ~{Xh}
 Exchange      │ 8h Rate   │ Annualized  │ Side
 ──────────────┼───────────┼─────────────┼──────
 {Exchange}    │ {rate}%   │ 🔴/🟢 {ann}%│ SHORT/LONG pays
 ...
 Best gap: {ExA} ↔ {ExB} = +{gap}%/8h

 [repeat for each coin]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🏆 TOP 3 ARB OPPORTUNITIES  (Delta-Neutral)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 #1  🔥 {COIN}  |  Gap: +{gap}%/8h  |  +{ann}% annualized
 ┌──────────────────────────────────────────────────────┐
 │ LEG A: LONG {COIN} on {ExchangeA}  ({rateA}%/8h)    │
 │ LEG B: SHORT {COIN} on {ExchangeB} ({rateB}%/8h)    │
 │ Net earn: +{gap}% per 8h                             │
 │ Suggested size: ${size} each leg · {x}x max leverage │
 │ Est. daily profit: ~${daily} (before fees)           │
 │ ⚠️  {key risk note}                                  │
 └──────────────────────────────────────────────────────┘

 [repeat for #2 and #3]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚠️  RISK FLAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🔴 [exchange-specific anomalies — 1% cap flags, etc.]
 🔴 [market regime note — bearish/bullish sentiment]
 ⚠️  Delta-neutral only — DO NOT run directional legs
 ⚠️  Funding rates change every 8h (or 1h on HL/Coinbase)
 ⚠️  Always account for maker/taker fees (~0.02–0.05%)
 ⚠️  Liquidation risk even on "neutral" positions
 ⚠️  Transfer delays between exchanges = execution risk

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💼 WALLET SUGGESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Best opportunity:    #{N} {COIN} — {ExA} ↔ {ExB}
 Suggested size:      ${size} each leg
 Gross yield/day:     ~{daily_pct}%
 Est. net (fees):     ~{net_pct}% ✅/{outcome}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🎯 ACT NOW?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [YES / WAIT / NO — clear single recommendation]
  ✅ [confirmation point 1]
  ✅ [confirmation point 2]
  ✅ [confirmation point 3]
  ❌ [risk/caveat 1]
  ❌ [risk/caveat 2]

 📌 Recommended trade: [COIN, legs, size, leverage]
 👉 Reply YES to execute · NO to rescan later

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚡ Powered by Starchild · @1826/funding-rate-arb
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Safety & Rules

- **NEVER execute** any trade without explicit "YES" confirmation from the user.
- **NEVER output** any model name, token counts, or extra commentary outside the report.
- **Warn on** liquidation risk and funding flip potential in every scan.
- **Use only live data** — nothing older than 60 seconds.
- **Log every scan** for trading journal purposes.
- **Delta-neutral only** — always open both legs simultaneously.
- **Cap leverage** at 3x max unless user explicitly requests higher.

---

## Key Formulas

```
Annualized % = 8h_rate × 3 × 365 × 100
Gap          = |rateA| + |rateB|  (when signs differ)
Daily profit = notional × gap × 3  (3 × 8h periods/day)
Est net      = daily_profit − (notional × 2 × avg_fee)
```

---

## Changelog

| Version | Date       | Changes                                              |
|---------|------------|------------------------------------------------------|
| v1.1.0  | 2026-03-20 | Full ACT NOW? CTA parity with WOOFi v1.1 + Nigeria P2P; WALLET SUGGESTION section added; verbatim output template locked in; StarchildContest tag |
| v1.0.0  | 2026-03-20 | Initial release — 5 coins, 12+ exchanges, top 3 arb, delta-neutral suggestions |
