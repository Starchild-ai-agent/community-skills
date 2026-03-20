---
name: "@1826/nigeria-p2p-arb"
version: 1.4.0
description: Real-time Binance P2P Naira rates vs USDT/USDC spot scanner + instant arbitrage alerts, plus live CBN/SEC/NIN policy & local crypto news watch. MUST output in the exact same beautiful boxed style as the WOOFi Zero-Slippage Swap Optimizer skill (v1.1). Uses consistent live spot rate from premium APIs for accurate spreads.
category: Trading
tags: [ngn, p2p, arbitrage, binance, cbn, nigeria, local, fiat, naira, contest, StarchildContest]
author: "@1826"
requires: web search, wallet, premium data
---

## How to use this skill

When user says "check ngn p2p" or calls this skill, follow these steps exactly and output ONLY the full beautiful report — no extra text, no model names, no signatures:

### Step 1 — Fetch Live P2P Rates
- Primary: fetch `https://p2p.army/en/p2p/prices/binance?fiatUnit=NGN` for USDT/USDC buy/sell rates
- Secondary: fetch Quidax live USDT/NGN rate via web search
- Tertiary: Binance P2P API direct (geo-blocked for NG users, try anyway)

### Step 2 — Fetch Consistent Live Spot Rate
- Call `coin_price(coin_ids="tether")` to get USDT USD price
- Fetch current USD/NGN via CBN official rate or web search
- Calculate: `spot_ngn = usdt_usd_price × usd_ngn_rate`
- Use this ONE consistent spot rate for ALL spread calculations
- NEVER use ₦1,000 parity — always use current live spot

### Step 3 — Calculate Spreads
- `spread_pct = ((p2p_rate - spot_ngn) / spot_ngn) × 100`
- Apply to USDT BUY, USDT SELL, USDC BUY, USDC SELL
- Profit example: `profit = (p2p_sell_rate - spot_ngn) × (500000 / spot_ngn)`

### Step 4 — Regulatory Scan
- web_search: "CBN SEC Nigeria crypto regulation news [today's date]"
- web_search: "Nigeria P2P crypto crackdown NIN BVN [today's date]"
- Extract 3–4 fresh bullets (last 48h only)

### Step 5 — Generate Report (EXACT FORMAT BELOW)

```
╔══════════════════════════════════════════════════════╗
║     🇳🇬 NGN P2P ARBITRAGE REPORT  v1.4              ║
║     📅 [Day DD Mon YYYY · HH:MM WAT]                 ║
╚══════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💡 BOTTOM LINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [USDT status line — blocked/live]
 ✅  Best rate: ₦[X]/USDT (Quidax/p2p.army)
 🟢  P2P premium over live spot: +[X]%
     (₦[p2p] vs ₦[spot] live spot)
 📌  [One-line action summary]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📊 LIVE RATES TABLE  (NGN · [Date])
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Asset │ Side │ P2P Rate  │ Spot Rate │ Spread    │ ₦500K Profit
 ──────┼──────┼───────────┼───────────┼───────────┼─────────────
 USDT  │ BUY  │ ₦[X]      │ ₦[spot]   │ 🔴 +[X]%  │     —
 USDT  │ SELL │ ₦[X]      │ ₦[spot]   │ 🟢 +[X]%  │ ~₦[X] 💰
 USDC  │ BUY  │ ₦[X]      │ ₦[spot]   │ 🔴 +[X]%  │     —
 USDC  │ SELL │ ₦[X]      │ ₦[spot]   │ 🟢 +[X]%  │ ~₦[X] 💰

 Spot source: CoinGecko USDT $[X] × CBN ₦[X]/USD = ₦[spot]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚠️  RISK FLAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [4–5 risk bullets with 🔴/⚠️ emojis]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📰 REG WATCH  (CBN / SEC / NIN · Last 48h)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [3–4 fresh regulatory bullets with 🏦📋💸🔐 emojis]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💼 WALLET SUGGESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Optimal path: DEX/WOOFi → USDT → [Exchange] → NGN
 Best rate:    ₦[X]/USDT
 Gross spread: +[X]%
 Est. net after fees: ~[X]% [✅/⚠️]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🎯 ACT NOW?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [✅ GO / ⏳ WAIT / ❌ NO] — [One line reason]
  ✅/❌ [Spread assessment]
  ✅/❌ [Platform status]
  ✅/❌ [Timing/liquidity]

 🕘 [Specific action recommendation with time window]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚡ Powered by Starchild · @1826/nigeria-p2p-arb
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Safety & Rules
- NEVER output any model name, token counts, or extra commentary after the report.
- NEVER use ₦1,000 as spot parity — always fetch and use current live spot rate.
- Always use ONE consistent spot rate for all spread calculations in the same report.
- Always note P2P counterparty, scam, and KYC risks.
- Use only fresh data (nothing older than 5 minutes).
- Log every scan.

## Changelog
- v1.4.0: Fixed spot rate consistency (live API only, no parity). Embedded full report template. Strict no-commentary output mode.
- v1.3.0: Strict output-only mode. Full format template added.
- v1.2.0: Added spot comparison column and visual spread indicators.
- v1.1.0: WOOFi-style boxed report format, risk flags, reg watch.
- v1.0.0: Initial release.
