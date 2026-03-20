---
name: "@1826/nigeria-p2p-arb"
version: 1.3.0
description: Real-time Binance P2P Naira rates vs USDT/USDC spot scanner + instant arbitrage alerts, plus live CBN/SEC/NIN policy & local crypto news watch. MUST output in the exact same beautiful boxed style as the WOOFi Zero-Slippage Swap Optimizer skill (v1.1). Now includes explicit spot comparison and 9.7% premium highlighting.
category: Trading
tags: [ngn, p2p, arbitrage, binance, cbn, nigeria, local, fiat, naira, contest, StarchildContest]
author: "@1826"
requires: web search, wallet, premium data
---

# 🇳🇬 Nigeria P2P Arbitrage + Local Reg Watcher

**Version:** 1.3.0 | **Author:** @1826 | **Category:** Trading

---

## How to use this skill

When user says "check ngn p2p" or calls this skill, follow these steps exactly and output ONLY the full beautiful report — no extra text, no model names, no token counts, no "Key upgrade" notes, no signatures:

1. Pull live rates via p2p.army tracker (or Binance if available) for USDT/USDC/NGN.
2. Compare directly against current WOOFi/DEX spot price.
3. Calculate spreads, min amounts, and ₦500K profit examples.
4. Scan latest CBN/SEC/NIN news (last 48h).
5. Generate report with EXACT same structure as WOOFi skill:
   - Big header box with flag and date
   - BOTTOM LINE box
   - Full comparison table (add Spot Price & Spread vs Spot column)
   - RISK FLAGS section with bullets
   - LOCAL NEWS & REGULATORY WATCH section with bullets
   - ACT NOW? section
   - Powered by footer (no model credit)

Use the exact same ━━━━━━━━━, ╔════════════════╗ boxes, tables, emojis, bold green/red spreads as the WOOFi v1.1 report.

---

## Output Format (STRICT — copy this exactly)

```
╔══════════════════════════════════════════════════════╗
║     🇳🇬 NGN P2P ARBITRAGE REPORT  v1.3              ║
║     📅 {Day DD Mon YYYY · HH:MM WAT}                 ║
╚══════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💡 BOTTOM LINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{one-line summary: status + reference rate + premium over spot}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📊 LIVE RATES TABLE  (NGN · {Date})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Asset │ Side │ P2P Rate  │ Spot Rate │ Spread       │ ₦500K Profit
 ──────┼──────┼───────────┼───────────┼──────────────┼─────────────
 USDT  │ BUY  │ ₦{rate}   │ ₦{spot}   │🔴 +{x.xx}%   │  —
 USDT  │ SELL │ ₦{rate}   │ ₦{spot}   │🟢 +{x.xx}%   │ ~₦{profit} 💰
 USDC  │ BUY  │ ₦{rate}   │ ₦{spot}   │🔴 +{x.xx}%   │  —
 USDC  │ SELL │ ₦{rate}   │ ₦{spot}   │🟢 +{x.xx}%   │ ~₦{profit} 💰

 Spread = P2P rate vs CBN/DEX official spot rate
 Profit example = ₦500K sold via P2P vs DEX spot

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚠️  RISK FLAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 {bullet list of active risks — suspension, KYC, chargeback, liquidity}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📰 LOCAL NEWS & REGULATORY WATCH  (CBN / SEC / NIN · Last 48h)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 {3–4 fresh regulatory/news bullets}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💼 WALLET SUGGESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 {recommended route: DEX → token → platform → NGN, with net spread}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🎯 ACT NOW?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 {✅ GO or ⏳ WAIT with bullet reasons and best window}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚡ Powered by Starchild · Data: P2P Tracker (live)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Data Sources (in priority order)

1. **p2p.army** — `https://p2p.army/en/p2p/prices/binance?fiatUnit=NGN` (primary tracker)
2. **Binance P2P API** — `https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search` (if accessible)
3. **Web search** — "USDT NGN P2P rate today" as final fallback
4. **Spot rate** — CoinGecko USDT price × current CBN USD/NGN official rate

---

## Safety & Rules

- NEVER output any model name, token counts, footers like ↑↓ · $ · Claude, or extra commentary after the report.
- NEVER suggest illegal activity or VPN workarounds.
- Always note P2P counterparty & scam risks.
- Warn about current Nigerian KYC/AML/NIN requirements.
- Use only fresh data (nothing older than 5 minutes).
- Log every scan.

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.0.0 | Initial release — basic P2P rate fetch + reg watch |
| 1.1.0 | WOOFi-style boxed format, risk flags, ACT NOW CTA |
| 1.2.0 | Spot price column, visual spread indicators 🟢🔴, wallet suggestion |
| 1.3.0 | Strict output-only mode (no post-report commentary), p2p.army as primary source, 9.7% premium highlighting, full format template embedded |
