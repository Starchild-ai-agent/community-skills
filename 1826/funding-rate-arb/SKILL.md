---
name: "@1826/funding-rate-arb"
version: 1.0.0
description: Real-time funding rate scanner across Hyperliquid, Binance Futures, Bybit, OKX and more. Highlights biggest long/short arb gaps and gives wallet-sized entry/exit suggestions. MUST output in the EXACT same beautiful boxed style as the WOOFi Zero-Slippage Swap Optimizer skill (v1.1), including the final "Ready to open position?" CTA box.
category: Trading
tags:
  - funding rate
  - arbitrage
  - hyperliquid
  - binance
  - bybit
  - okx
  - perp
  - contest
  - StarchildContest
author: "@1826"
requires: premium data apis, wallet
---

# Cross-Exchange Funding Rate Arbitrage Scanner

## Purpose
Real-time funding rate scanner across Hyperliquid, Binance Futures, Bybit, OKX and more. Identifies top long/short arb gaps, calculates annualized yield, and suggests wallet-sized entries with concrete profit projections — all in the WOOFi v1.1 boxed report style.

## When to Use
- User says **"scan funding rates"** or **"check funding arb"**
- User asks **"where are the best funding rates?"**
- User asks **"which perp has highest funding?"**
- Any request involving cross-exchange funding rate comparison

---

## Step-by-Step Execution

### Step 1 — Pull Live Funding Rates
Use `funding_rate()` tool for each major exchange and Coinglass API for cross-exchange data:
- **Hyperliquid**: `funding_rate(symbol="BTC")`, `funding_rate(symbol="ETH")`, `funding_rate(symbol="SOL")`
- **Binance**: `funding_rate(symbol="BTC", exchange="Binance")`, etc.
- **Bybit**: `funding_rate(symbol="BTC", exchange="Bybit")`, etc.
- **OKX**: `funding_rate(symbol="BTC", exchange="OKX")`, etc.
- Also scan: `cg_coins_market_data()` for broad funding snapshot across all coins

Pull top 10 coins by open interest minimum. Focus on BTC, ETH, SOL, BNB, XRP, DOGE, AVAX, ARB.

### Step 2 — Calculate Annualized Rates
Formula:
```
8h_rate → Daily: rate × 3
Daily → Annualized: daily × 365
```
Example: 0.01% per 8h → 0.03% daily → 10.95% APR

### Step 3 — Identify Top Arb Gaps
Long/short arb = open LONG on exchange with lowest (or negative) funding + SHORT on exchange with highest funding for same coin.

Gap formula:
```
arb_gap = high_exchange_rate - low_exchange_rate (per 8h)
annualized_gap = arb_gap × 3 × 365
```

Rank top 3 by annualized gap. Flag any gap > 20% APR as 🔥 HOT.

### Step 4 — Wallet-Sized Suggestions
Check wallet balance via `hl_account()` or use user-stated size. Suggest:
- Position size: 10–25% of available margin per leg
- Leverage: max 3x (delta-neutral arb)
- Entry: market order (IoC)
- Exit trigger: when funding flips or gap narrows below 5% APR

### Step 5 — Generate Full Report
Output ONLY the boxed report below. No extra text, no model names, no commentary.

---

## Output Template (copy exactly — fill in live data)

```
╔══════════════════════════════════════════════════════╗
║   💸 FUNDING RATE ARB SCANNER  v1.0                 ║
║   📅 {Date} · {Time} UTC                            ║
╚══════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💡 BOTTOM LINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🔥 Top arb: {COIN} — {ExchangeA} vs {ExchangeB}
 📌 Gap: {gap_8h}% per 8h → {annualized}% APR
 📌 $10K position → est. ~${daily_profit}/day gross
 ⚠️  {Risk note — e.g. funding can flip, liq risk}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📊 FUNDING RATES TABLE  ({Date} · {Time} UTC)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Coin  │ Exchange   │ 8h Rate  │ APR      │ Long/Short
 ──────┼────────────┼──────────┼──────────┼───────────
 BTC   │ Binance    │ +0.01%   │ +10.95%  │ Longs pay
 BTC   │ Bybit      │ +0.01%   │ +10.95%  │ Longs pay
 BTC   │ OKX        │ +0.008%  │  +8.76%  │ Longs pay
 BTC   │ Hyperliquid│ +0.0125% │ +13.69%  │ Longs pay
 ETH   │ Binance    │ +0.012%  │ +13.14%  │ Longs pay
 ETH   │ Bybit      │ +0.011%  │ +12.05%  │ Longs pay
 ETH   │ OKX        │ +0.009%  │  +9.86%  │ Longs pay
 ETH   │ Hyperliquid│ +0.015%  │ +16.43%  │ Longs pay
 SOL   │ Binance    │ -0.005%  │  -5.48%  │ Shorts pay
 SOL   │ Hyperliquid│ +0.02%   │ +21.90%  │ 🔥 Longs pay

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🔝 TOP 3 ARB OPPORTUNITIES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 #1 🔥 {COIN}: {ExchangeA} SHORT vs {ExchangeB} LONG
    Gap: {gap}% per 8h | APR: {annualized}%
    $10K each leg → ~${profit}/day | Risk: {risk}

 #2 ⚡ {COIN}: {ExchangeA} SHORT vs {ExchangeB} LONG
    Gap: {gap}% per 8h | APR: {annualized}%
    $10K each leg → ~${profit}/day | Risk: {risk}

 #3 📌 {COIN}: {ExchangeA} SHORT vs {ExchangeB} LONG
    Gap: {gap}% per 8h | APR: {annualized}%
    $10K each leg → ~${profit}/day | Risk: {risk}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚠️  RISK FLAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🔴 Funding rates reset every 8h — can flip sign
    at any time. Monitor closely.
 🔴 Delta-neutral requires BOTH legs open — if one
    leg fails, you carry directional exposure
 ⚠️  Liquidation risk: use max 3x leverage per leg
 ⚠️  Exchange withdrawal delays can trap capital
 ⚠️  Slippage on entry/exit eats into arb spread
 ⚠️  Tax event on each funding payment received

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💼 WALLET SUGGESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Suggested allocation (delta-neutral):
 LONG:  {ExchangeB} {COIN} — {size} at {leverage}x
 SHORT: {ExchangeA} {COIN} — {size} at {leverage}x
 Max drawdown buffer: 20% margin each leg
 Exit trigger: gap < 5% APR or funding flip

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🎯 READY TO OPEN POSITION?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 {YES / WAIT / NO} — {reason}:
  ✅ {green bullet 1}
  ✅ {green bullet 2}
  ❌ {red flag 1}
  ❌ {red flag 2}

 Say "YES open #{1/2/3}" to execute the arb.
 NEVER executes without your explicit YES.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚡ Powered by Starchild · @1826/funding-rate-arb
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Safety & Rules
- **NEVER execute** any trade without explicit user "YES"
- **NEVER output** model names, token counts, or extra commentary
- Always use **live data only** — nothing older than 60 seconds
- Always warn on **liquidation risk** and **funding flip potential**
- Always confirm **both legs** before suggesting delta-neutral entry
- Log every scan timestamp for trading journal
- Rate formulas: `APR = 8h_rate × 3 × 365`
- Profit estimate: `daily_profit = notional × daily_rate`

## Tools Required
- `funding_rate(symbol, exchange)` — per-exchange funding rates
- `cg_coins_market_data()` — broad funding snapshot
- `cg_open_interest(symbol)` — filter by OI size
- `hl_account()` — check wallet balance for sizing
- `hl_order()` — execute Hyperliquid leg (on user YES only)

## Changelog
- **v1.0.0** — Initial release. Cross-exchange scanner (HL, Binance, Bybit, OKX). Delta-neutral arb suggestions. WOOFi v1.1 boxed style. StarchildContest tag.
