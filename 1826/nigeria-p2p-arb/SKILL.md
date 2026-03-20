---
name: "@1826/nigeria-p2p-arb"
version: 1.6.0
description: Real-time Binance P2P Naira rates vs USDT/USDC spot scanner + instant arbitrage alerts, plus live CBN/SEC/NIN policy & local crypto news watch. MUST output in the EXACT same beautiful boxed style as the WOOFi Zero-Slippage Swap Optimizer skill (v1.1), including the final ACT NOW? CTA box.
category: Trading
tags:
  - ngn
  - p2p
  - arbitrage
  - binance
  - cbn
  - nigeria
  - local
  - fiat
  - naira
  - contest
  - StarchildContest
author: "@1826"
requires:
  - web search
  - wallet
  - premium data
---

# 🇳🇬 Nigeria P2P Arbitrage + Local Reg Watcher

## Overview

Real-time NGN P2P arbitrage scanner + CBN/SEC/NIN regulatory watcher.  
Outputs a fully formatted report in the **exact same boxed style** as the WOOFi Zero-Slippage Swap Optimizer v1.1 — including the final ACT NOW? CTA box.

---

## How to Use This Skill

When user says **"check ngn p2p"** or calls this skill, execute ALL steps and output ONLY the full report below — no extra text, no model names, no signatures, no explanations.

### Step 1 — Fetch Live P2P Rates
- Fetch `https://p2p.army/en/p2p/prices/binance?fiatUnit=NGN` for USDT/USDC buy/sell NGN rates
- Also check Quidax live USDT/NGN sell rate via monierate or web search

### Step 2 — Fetch Consistent Live Spot
- Call `coin_price(coin_ids="tether")` → get USDT price in USD
- Fetch CBN official USD/NGN rate OR use forex search for current rate
- Calculate: `spot_ngn = usdt_usd_price × usd_ngn_rate`
- Use this SAME spot_ngn for ALL spread calculations — no parity shortcuts

### Step 3 — Calculate Spreads & Profits
- Spread % = `((p2p_rate − spot_ngn) / spot_ngn) × 100`
- ₦500K Profit = `((p2p_rate − spot_ngn) / spot_ngn) × 500000`
- Color: 🟢 for SELL spreads (positive arb), 🔴 for BUY costs (you pay premium)

### Step 4 — Regulatory Scan
- `web_search("CBN SEC Nigeria crypto P2P regulation news [today's date]", max_results=3)`
- Summarise top 3–4 bullet points for REG WATCH section

### Step 5 — Generate Full Formatted Report

Output EXACTLY this structure (copy separators, boxes, emojis verbatim):

```
╔══════════════════════════════════════════════════════╗
║     🇳🇬 NGN P2P ARBITRAGE REPORT  v1.6              ║
║     📅 [Day DD Mon YYYY · HH:MM WAT]                 ║
╚══════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💡 BOTTOM LINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📌 Spot: USDT $[price] × [USD/NGN] = ₦[spot_ngn]
 📌 Best SELL: ₦[best_sell]/USDT ([exchange])
 🟢 Premium over spot: +[X.XX]% — [verdict]
 ⚠️  [Key risk or platform note]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📊 LIVE RATES TABLE  (NGN · [Date])
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Asset │ Side │ Local Rate   │ Spot (₦)   │ Spread       │ ₦500K Profit
 ──────┼──────┼──────────────┼────────────┼──────────────┼─────────────
 USDT  │ BUY  │ ₦[rate]      │ ₦[spot]    │ 🔴 +[X.XX]%  │      —
 USDT  │ SELL │ ₦[rate] ✅   │ ₦[spot]    │ 🟢 +[X.XX]%  │ ~₦[profit] 💰
 USDC  │ BUY  │ ₦[rate]      │ ₦[spot]    │ 🔴 +[X.XX]%  │      —
 USDC  │ SELL │ ₦[rate]      │ ₦[spot]    │ 🟢 +[X.XX]%  │ ~₦[profit] 💰

 Spot basis: CoinGecko $[usdt_price] × [source] ₦[usd_ngn]
 Profit: ((P2P − Spot) / Spot) × ₦500,000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚠️  RISK FLAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🔴 [Platform/regulatory risk]
 🔴 [SEC/CBN enforcement risk]
 ⚠️  [KYC requirement]
 ⚠️  [Scam/chargeback risk]
 ⚠️  [Time-of-day liquidity note]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📰 REG WATCH  (CBN / SEC / NIN · Last 48h)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 • 🏦 [CBN update]
 • 📋 [SEC update]
 • 📋 [Platform/licensing update]
 • 💸 [Tax/FIRS update]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💼 WALLET SUGGESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Optimal path:
 WOOFi/DEX → USDT → [Exchange] SELL → NGN bank
 Best rate:       ₦[best_rate]/USDT 🟢
 Gross vs spot:   +[X.XX]%
 Est. net (fees): ~[X–X]% ✅ [verdict]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🎯 ACT NOW?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [✅ YES — Execute now / ⏳ WAIT — Timing only]:
  ✅ [Green flag 1]
  ✅ [Green flag 2]
  ✅ [Green flag 3]
  ❌ [Red flag 1]
  ❌ [Red flag 2]

 🕘 [Timing recommendation + target rate]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚡ Powered by Starchild · @1826/nigeria-p2p-arb
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Safety & Rules

- **NEVER** output any model name, token counts, LLM commentary, or extra text
- **NEVER** use ₦1,000 parity — always derive spot from CoinGecko × live USD/NGN
- Always flag KYC requirements and platform risks
- Always end report with the **ACT NOW?** box — this is mandatory
- Log every scan internally

---

## Changelog

| Version | Changes |
|---------|---------|
| v1.6.0 | Full WOOFi v1.1 structural parity; ACT NOW? box mandatory; output template locked verbatim; StarchildContest tag |
| v1.5.0 | ACT NOW? CTA added; strict no-commentary output |
| v1.4.0 | Consistent live spot rate; accurate spread/profit formulas |
| v1.3.0 | Full template rewrite; contest tag added |
| v1.2.0 | Reg watch section expanded |
| v1.1.0 | Boxed WOOFi-style output introduced |
| v1.0.0 | Initial release |
