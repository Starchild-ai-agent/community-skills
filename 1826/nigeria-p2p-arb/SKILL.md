---
name: "@1826/nigeria-p2p-arb"
version: 1.2.0
description: Real-time Binance P2P Naira rates vs USDT/USDC spot scanner + instant arbitrage alerts, plus live CBN/SEC/NIN policy & local crypto news watch. Beautiful formatted reports like WOOFi skill. Now with explicit spot comparison and visual spreads.
category: Trading
tags: [ngn, p2p, arbitrage, binance, cbn, nigeria, local, fiat, naira, contest, StarchildContest]
author: "@1826"
requires: [api.binance, web search, wallet, premium data]
---

## How to use this skill

When user says **"check ngn p2p"** or calls this skill, follow these steps exactly and output in the same beautiful boxed style as the WOOFi Zero-Slippage Swap Optimizer skill:

### Step 1 — Pull Live P2P Rates
- Primary: Query Binance P2P API for USDT/USDC NGN buy/sell orders
- Fallback: Use p2p.army tracker (https://p2p.army/en/p2p/prices/binance?fiatUnit=NGN)
- Fetch all popular payment methods: Bank Transfer, OPay, PalmPay, Moniepoint
- Data must be fresh — nothing older than 5 minutes

### Step 2 — Pull Spot Reference Price
- Fetch current USDT/USD spot price from CoinGecko or WOOFi sPMM
- Convert to NGN using CBN/parallel rate (web search for latest)
- This becomes your "Spot Price" column baseline

### Step 3 — Calculate Spreads & Profit
- Spread vs Spot = ((P2P Rate − Spot Rate) / Spot Rate) × 100
- Profit example = ₦500,000 notional × spread %
- Flag spreads >1.5% as ✅ ARB OPPORTUNITY
- Flag spreads <0.5% as ❌ NOT WORTH IT after fees

### Step 4 — Regulatory & News Scan
- web_search: "CBN crypto Nigeria [today's date]"
- web_search: "SEC Nigeria crypto [today's date]"
- web_search: "Binance Nigeria [today's date]"
- Summarise top 3–4 results into clean bullets

### Step 5 — Generate Full Report
Output exactly this structure using ━━━ separators, ╔═══╗ box headers, full tables, and emoji-rich formatting:

```
╔══════════════════════════════════════════════════╗
║     🇳🇬 NGN P2P ARBITRAGE REPORT                ║
║     📅 [Day Date Month Year · HH:MM WAT]         ║
╚══════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💡 BOTTOM LINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[One-line verdict: arb available or not, best platform, best time]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📊 LIVE P2P RATES vs SPOT  (NGN)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Asset | Side | P2P Rate(₦) | Spot(₦) | Spread vs Spot | Min Amt | Profit ₦500K |
|-------|------|------------|---------|---------------|---------|-------------|
| USDT  | BUY  | X,XXX.XX   | X,XXX   | 🔴 +X.XX%     | ₦X,XXX  | ₦X,XXX      |
| USDT  | SELL | X,XXX.XX   | X,XXX   | 🟢 +X.XX%     | ₦X,XXX  | ₦X,XXX      |
| USDC  | BUY  | X,XXX.XX   | X,XXX   | 🔴 +X.XX%     | ₦X,XXX  | ₦X,XXX      |
| USDC  | SELL | X,XXX.XX   | X,XXX   | 🟢 +X.XX%     | ₦X,XXX  | ₦X,XXX      |

🟢 = premium above spot (SELL profit) | 🔴 = cost above spot (BUY premium)
Bold spreads >1.5% = actionable arb. <0.5% = skip after fees.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚠️  RISK FLAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• [Platform suspension status]
• [KYC/NIN/BVN requirements]
• [Chargeback/scam warning]
• [Spread viability after fees]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📰 LOCAL NEWS & REGULATORY WATCH (Last 48h)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 🏦 [CBN update]
• 📋 [SEC Nigeria update]
• 💸 [Tax/FIRS update]
• 🔐 [KYC enforcement update]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💼 WALLET SUGGESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Specific platform recommendation based on current spread + suspension status]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🎯 ACT NOW?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ YES / ❌ WAIT — [reason + best window if waiting]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚡ Powered by Starchild · @1826/nigeria-p2p-arb@1.2.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Safety & Rules
- NEVER suggest illegal, unlicensed, or unregulated activity
- Always note P2P counterparty & scam risks explicitly
- Warn about current Nigerian KYC/AML/NIN requirements on every report
- Use only fresh data — nothing older than 5 minutes
- NEVER show any model name or AI footer credit
- Log every scan to memory

## Changelog
- v1.2.0 — Added Spot Price column, Spread vs Spot column, visual 🟢🔴 spread indicators, profit emojis, enhanced wallet suggestion section, p2p.army fallback as primary data source
- v1.1.0 — WOOFi-style boxed report format, risk flags, regulatory news watch, ACT NOW CTA
- v1.0.0 — Initial release
