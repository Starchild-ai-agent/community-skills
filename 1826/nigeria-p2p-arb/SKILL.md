---
name: "@1826/nigeria-p2p-arb"
version: 1.1.0
description: Real-time Binance P2P Naira rates vs USDT/USDC spot scanner + instant arbitrage alerts, plus live CBN/SEC/NIN policy & local crypto news watch. Built specifically for Nigerian traders on WOOFi/Starchild. Beautiful formatted reports like WOOFi skill.
category: Trading
tags: [ngn, p2p, arbitrage, binance, cbn, nigeria, local, fiat, naira, contest, StarchildContest]
author: "@1826"
requires: ["api.binance.com", "web-search", "wallet"]
metadata:
  starchild:
    emoji: "🇳🇬"
    skillKey: nigeria-p2p-arb
---

# 🇳🇬 Nigeria P2P Arbitrage + Local Reg Watcher

Real-time Binance P2P NGN rate scanner, arb calculator, and Nigerian crypto regulatory/news watcher — formatted beautifully like the WOOFi Zero-Slippage Swap Optimizer skill.

---

## How to Use This Skill

When user says **"check ngn p2p"** or calls this skill, follow these steps exactly and output in the same beautiful boxed style as the WOOFi Zero-Slippage Swap Optimizer skill:

### Step 1 — Pull Live Binance P2P Rates
Fetch buy AND sell rates for USDT and USDC vs NGN across all popular payment methods:
- Bank Transfer
- OPay
- PalmPay
- Moniepoint
- Chipper Cash

Use this endpoint:
```
POST https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search
Body: {
  "fiat": "NGN",
  "page": 1,
  "rows": 10,
  "tradeType": "BUY",   // then "SELL"
  "asset": "USDT",      // then "USDC"
  "countries": [],
  "proMerchantAds": false
}
```

Extract top 5 rates for each combination (BUY/SELL × USDT/USDC).

### Step 2 — Get DEX Spot Price
Fetch current USDT/USDC USD spot price from CoinGecko for reference baseline.

### Step 3 — Calculate Arbitrage Spread
```
Buy Rate  = lowest NGN you pay per USDT on P2P (BUY side)
Sell Rate = highest NGN you receive per USDT on P2P (SELL side)
Spread %  = ((Sell Rate - Buy Rate) / Buy Rate) × 100
Net Profit Example = spread on ₦500,000 trade after ~1% platform fee
```

Flag any spread > 2% as a live arb opportunity.

### Step 4 — Scan Nigerian Crypto News & Regulations
Use web search to pull latest (last 24h) on:
- CBN circulars or policy updates
- SEC Nigeria crypto rulings
- NIN/BVN KYC enforcement news
- Binance Nigeria status
- Any local exchange suspensions or alerts

Summarise in 3–4 bullet points.

### Step 5 — Generate Beautiful Report

Use EXACTLY this format (same style as WOOFi v1.1):

```
╔══════════════════════════════════════════════════╗
║     🇳🇬 NGN P2P ARBITRAGE REPORT                ║
║     📅 [DATE & TIME WAT]                        ║
╚══════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💡 BOTTOM LINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1-line summary: e.g. "Spread is 3.2% — arb window open on USDT"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📊 LIVE P2P RATES  (Binance P2P · NGN)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Asset | Side | Best Rate (₦) | Spread % | Min Amt | Profit (₦500K) |
|-------|------|--------------|----------|---------|----------------|
| USDT  | BUY  | 1,612.00     |          | ₦10,000 |                |
| USDT  | SELL | 1,665.00     | +3.29%   | ₦5,000  | ~₦14,700 net   |
| USDC  | BUY  | 1,610.00     |          | ₦10,000 |                |
| USDC  | SELL | 1,661.00     | +3.17%   | ₦5,000  | ~₦14,200 net   |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚠️  RISK FLAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• P2P counterparty risk — only trade with verified merchants (100+ trades, >98% rate)
• NIN/BVN verification required on Binance Nigeria — ensure compliance
• Chargeback scam risk on bank transfer — use escrow, never release before payment confirmed
• Rates valid for ~5 mins max — re-check before executing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📰 LOCAL NEWS & REGULATORY WATCH (Last 24h)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• [bullet 1 — CBN/SEC/NIN update or "No new circulars in last 24h"]
• [bullet 2 — Binance Nigeria or exchange news]
• [bullet 3 — general Nigerian crypto market news]
• [bullet 4 — if available, else omit]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🎯 ACT NOW?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Recommendation: e.g. "✅ YES — USDT spread is attractive. Execute BUY → SELL within 10 mins.
 OR ❌ WAIT — spread too thin (<1.5%) to cover fees + risk right now."]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚡ Powered by Starchild · Data: Binance P2P (live)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Safety & Rules

- **NEVER** suggest illegal activity or CBN policy violations.
- Always display P2P counterparty & scam risk warnings.
- Always warn about NIN/BVN/KYC requirements.
- Use only fresh data — nothing older than 5 minutes.
- **NEVER** show model name or footer credit (no "Claude", "GPT", etc.).
- Log every scan timestamp.

---

## Example Trigger Phrases

- "Check NGN P2P"
- "What's the naira rate now?"
- "Is there an arb opportunity?"
- "Any CBN updates today?"
- "P2P scan"

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.1.0 | Beautiful WOOFi-style formatted output, full arb table, risk flags, news section, ACT NOW CTA |
| 1.0.0 | Initial release — basic P2P rate fetch + regulatory watcher |
