---
name: "@1826/nigeria-p2p-arb"
version: 1.5.0
description: Real-time Binance P2P Naira rates vs USDT/USDC spot scanner + instant arbitrage alerts, plus live CBN/SEC/NIN policy & local crypto news watch. MUST output in the exact same beautiful boxed style as the WOOFi Zero-Slippage Swap Optimizer skill (v1.1). Now includes ACT NOW? CTA for full symmetry.
category: Trading
tags: [ngn, p2p, arbitrage, binance, cbn, nigeria, local, fiat, naira, contest, StarchildContest]
author: "@1826"
requires: web search, wallet, premium data
---

## How to use this skill

When user says "check ngn p2p" or calls this skill, follow these steps exactly and output ONLY the full beautiful report — no extra text, no model names, no signatures:

1. Pull live rates via p2p.army tracker + Quidax for USDT/USDC/NGN.
2. Pull consistent live spot rate from premium APIs (CoinGecko USDT price × CBN USD/NGN rate).
3. Calculate spreads accurately using formula: `((p2p_rate - spot_rate) / spot_rate) × 100`
4. Calculate ₦500K profit: `((p2p_rate - spot_rate) / spot_rate) × 500,000`
5. Scan latest CBN/SEC/NIN news (last 48h).
6. Generate report with EXACT same structure as WOOFi v1.1 skill:
   - Big header box (╔══╗ style with flag + date)
   - BOTTOM LINE box (spot basis + premium % + one-line verdict)
   - Full comparison table (Asset │ Side │ P2P/Local Rate │ Spot (₦) │ Spread │ ₦500K Profit)
   - RISK FLAGS section with bullets
   - REG WATCH section with bullets (CBN/SEC/NIN last 48h)
   - WALLET SUGGESTION (best path + gross/net spread)
   - ACT NOW? section (clear YES/WAIT + reasons + timing window — same style as WOOFi)
   - Powered by footer

Use exact same ━━━━━━━━━, ╔════════════════╗ boxes, tables, emojis, 🔴/🟢 colored spreads.
Keep everything clean and professional. Full symmetry with WOOFi v1.1 output.

## Data Sources (priority order)

1. **p2p.army** — `https://p2p.army/en/p2p/prices/binance?fiatUnit=NGN` (primary P2P tracker)
2. **Quidax** — live USDT/NGN rate via monierate or direct (confirmed best local rate)
3. **CoinGecko** — USDT spot price in USD (tool: `coin_price(coin_ids="tether")`)
4. **CBN rate** — USD/NGN official rate via web search or CBN website
5. **Spot calc** — `spot_ngn = usdt_usd_price × cbm_usd_ngn_rate`

## Output Template

```
╔══════════════════════════════════════════════════════╗
║     🇳🇬 NGN P2P ARBITRAGE REPORT  v1.5              ║
║     📅 [Day DD Mon YYYY · HH:MM WAT]                ║
╚══════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💡 BOTTOM LINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📌 Spot: USDT = $[price] × CBN ₦[cbm] = ₦[spot]
 📌 Best P2P SELL rate: ₦[rate]/USDT ([platform])
 🟢/🔴 Premium over spot: +[X]% — [verdict]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📊 LIVE RATES TABLE  (NGN · [Date])
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

 Asset │ Side │ P2P / Local  │ Spot (₦)   │ Spread       │ ₦500K Profit
 ──────┼──────┼──────────────┼────────────┼──────────────┼─────────────
 USDT  │ BUY  │ ₦[rate]      │ ₦[spot]    │ 🔴 +[X]%     │     —
 USDT  │ SELL │ ₦[rate] ✅   │ ₦[spot]    │ 🟢 +[X]%     │ ~₦[amt] 💰
 USDC  │ BUY  │ ₦[rate]      │ ₦[spot]    │ 🔴 +[X]%     │     —
 USDC  │ SELL │ ₦[rate]      │ ₦[spot]    │ 🟢 +[X]%     │ ~₦[amt] 💰

 Spot basis: CoinGecko USDT $[price] × CBN ₦[cbm]
 Profit formula: ((P2P − Spot) / Spot) × ₦500,000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚠️  RISK FLAGS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [bullets]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 📰 REG WATCH  (CBN / SEC / NIN · Last 48h)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 [bullets]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 💼 WALLET SUGGESTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 Optimal path:
 WOOFi/DEX → USDT → [Exchange] SELL → NGN bank
 Best rate:       ₦[rate]/USDT 🟢
 Gross vs spot:   +[X]%
 Est. net (fees): ~[Y]% ✅/⚠️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 🎯 ACT NOW?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ✅ YES / ⏳ WAIT — [reason]:
  ✅ [positive factor]
  ✅ [positive factor]
  ❌ [blocker if any]
  ❌ [blocker if any]

 🕘 [Timing recommendation and target rate]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 ⚡ Powered by Starchild · @1826/nigeria-p2p-arb
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Safety & Rules

- NEVER output any model name, token counts, or extra commentary after the report.
- NEVER suggest illegal activity or unregulated workarounds.
- Always use consistent live spot rate for ALL spread calculations.
- Always note P2P counterparty & scam risks.
- Warn about current Nigerian KYC/AML/NIN requirements.
- Use only fresh data (nothing older than 5 minutes).
- Log every scan.

## Changelog

- v1.5.0 — Full ACT NOW? symmetry with WOOFi v1.1. Clean output only. No extra text.
- v1.4.0 — Consistent live spot rate (CBN × CoinGecko). Accurate spread formula.
- v1.3.0 — Strict output-only mode. Full format template embedded.
- v1.2.0 — Spot Price column added. Visual 🔴/🟢 spreads. p2p.army as primary source.
- v1.1.0 — WOOFi-style boxed report format. Risk flags. Reg news. ACT NOW CTA.
- v1.0.0 — Initial release.
