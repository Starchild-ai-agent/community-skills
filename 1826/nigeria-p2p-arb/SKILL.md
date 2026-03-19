---
name: "@1826/nigeria-p2p-arb"
version: 1.0.0
description: "Real-time Binance P2P Naira rates vs USDT/USDC spot scanner + instant arbitrage alerts, plus live CBN/SEC/NIN policy & local crypto news watch. Built specifically for Nigerian traders on WOOFi/Starchild."
category: Trading
tags: [ngn, p2p, arbitrage, binance, cbn, nigeria, local, fiat, naira, StarchildContest]
author: "@1826"
requires: ["api.binance.com", "web-search", "wallet"]
metadata:
  starchild:
    emoji: "🇳🇬"
    display_name: "Nigeria P2P Arbitrage + Local Reg Watcher"
    contest: StarchildContest
---

# 🇳🇬 Nigeria P2P Arbitrage + Local Reg Watcher

Real-time Binance P2P NGN scanner + CBN/SEC reg watcher for Nigerian crypto traders.
Surfaces arb windows between P2P Naira rates and DEX spot, plus live policy alerts.

---

## Trigger phrases

- "check ngn p2p"
- "ngn arb"
- "p2p rates nigeria"
- "check naira rates"
- "cbn news"
- "crypto news nigeria"
- Any swap mentioning NGN, Naira, or Nigerian payment methods

---

## Workflow

### Step 1 — Extract parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `asset` | USDT | USDT or USDC |
| `trade_type` | BOTH | BUY / SELL / BOTH |
| `fiat` | NGN | Nigerian Naira |
| `payment_methods` | ALL | Bank Transfer, Opay, Palmpay, Kuda, GTBank, Zenith, Monobank |
| `amount` | 100 USDT | Min trade size for calc |

---

### Step 2 — Fetch Binance P2P rates

Call Binance P2P API for both BUY and SELL sides:

**Endpoint:**
```
POST https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search
```

**Payload (BUY side — user buying USDT for NGN):**
```json
{
  "fiat": "NGN",
  "page": 1,
  "rows": 10,
  "tradeType": "BUY",
  "asset": "USDT",
  "countries": [],
  "proMerchantAds": false,
  "shieldMerchantAds": false,
  "filterType": "all",
  "payTypes": []
}
```

Repeat for `"tradeType": "SELL"` and for `"asset": "USDC"`.

**Extract per ad:**
- `adv.price` — NGN rate per USDT
- `adv.minSingleTransAmount` / `adv.maxSingleTransAmount` — trade limits
- `adv.tradableQuantity` — available liquidity
- `adv.payMethods[].identifier` — accepted payment methods
- `advertiser.monthOrderCount` / `advertiser.monthFinishRate` — merchant credibility

**Compile:**
- Best BUY rate (highest NGN/USDT — best if you're selling USDT)
- Best SELL rate (lowest NGN/USDT — best if you're buying USDT)
- Median BUY / SELL across top 5 ads
- Spread: `(best_buy - best_sell) / best_sell * 100`

---

### Step 3 — Fetch DEX/WOOFi spot price

Get current USDT/USD spot and NGN cross-rate:

1. **CoinGecko:** `GET /simple/price?ids=tether&vs_currencies=ngn,usd`
2. **WOOFi sPMM** (if available): quote 100 USDT → USDC on any supported chain for fee benchmarking
3. **Fallback:** Use USD/NGN from a forex API (exchangerate-api.com or similar)

Compute:
- `cg_ngn_rate` = CoinGecko's NGN/USDT (market rate)
- `p2p_buy_premium` = `(p2p_best_sell - cg_ngn_rate) / cg_ngn_rate * 100` — how much above market P2P sellers charge
- `p2p_sell_premium` = `(p2p_best_buy - cg_ngn_rate) / cg_ngn_rate * 100` — how much above market P2P buyers pay

---

### Step 4 — Calculate arbitrage windows

For each arb path, compute net profit after all costs:

| Path | Direction | Fees to deduct |
|------|-----------|---------------|
| CEX → P2P | Buy spot on exchange, sell on P2P | Exchange withdrawal fee + P2P 0% maker fee |
| P2P → DEX | Buy on P2P, bridge to DEX, sell | P2P taker fee (0%) + bridge gas + DEX swap fee |
| P2P Round-trip | Buy low on P2P method A, sell high on method B | Time risk, KYC limits |

**Net profit formula:**
```
net_ngn = (sell_rate × amount) - (buy_rate × amount) - fees_in_ngn
net_pct = net_ngn / (buy_rate × amount) × 100
```

Flag only arb windows where `net_pct ≥ 0.5%` — below that, noise.

**Risk score per opportunity:**
- 🟢 Low risk: merchant ≥500 trades, ≥98% completion, limit >$50
- 🟡 Medium: merchant 100–500 trades or 95–98% completion
- 🔴 High: new merchant, low completion, unusual payment method, no NIN badge

---

### Step 5 — Scan Nigerian crypto news & CBN/SEC updates

Use `web_search` with these queries (last 24h):

```
"CBN circular crypto" after:yesterday
"SEC Nigeria crypto" after:yesterday
"Binance Nigeria" after:yesterday
"EFCC crypto" after:yesterday
"NIN crypto KYC Nigeria" after:yesterday
"crypto tax Nigeria" after:yesterday
```

Also hit these sources directly if available:
- `cbn.gov.ng/out/Publications/circulars` (CBN circulars)
- `sec.gov.ng/news` (SEC press releases)
- `techcabal.com`, `nairametrics.com`, `bitcoinke.io` (local crypto news)

**Classify each result:**
- 🔴 URGENT — new ban, freeze, or enforcement action
- 🟡 WATCH — proposed regulation, hearing, or industry comment
- 🟢 INFO — market news, adoption story, non-urgent update

---

### Step 6 — Check wallet balance

Call `wallet_balance` for the user's connected chain:
- If they hold USDT/USDC: show which P2P sell path fits their balance
- If they hold NGN equivalent or need to buy: show best buy path
- If zero balance: skip wallet-specific suggestion, just show market data

---

### Step 7 — Generate report

Output this exact structure:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇳🇬  NIGERIA P2P ARB REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scanned: [timestamp UTC]  |  Asset: USDT/USDC
  Market NGN/USDT: ₦[rate]  (CoinGecko)

─────────────────────────────────────────────
📊  LIVE P2P RATES (Binance NGN)
─────────────────────────────────────────────
  [Table: Side | Best Rate | Median | Spread | Top Merchant | Risk]

─────────────────────────────────────────────
🏹  TOP ARB OPPORTUNITIES
─────────────────────────────────────────────
  [Table: # | Path | Buy Rate | Sell Rate | Net % | Net NGN/100 | Risk | Act?]

─────────────────────────────────────────────
📰  CBN/SEC/LOCAL NEWS (Last 24h)
─────────────────────────────────────────────
  [Classified news bullets]

─────────────────────────────────────────────
💼  WALLET SUGGESTION
─────────────────────────────────────────────
  [Balance-specific action or "fund wallet to trade"]

─────────────────────────────────────────────
⚠️  RISK FLAGS
─────────────────────────────────────────────
  [KYC/AML/NIN warnings, scam alert, liquidity notes]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

End every report with:
> "Act now? Reply **YES + path number** (e.g. YES 1) to prepare the trade, or **NEWS** for deeper reg analysis."

---

## Safety & Rules

- **NEVER** suggest or facilitate any activity that violates CBN, SEC, EFCC, or Nigerian AML laws.
- **Always** display KYC/NIN/TIN requirements prominently — non-compliance = frozen accounts.
- **Always** warn about P2P counterparty & scam risks (fake alerts, chargeback fraud, account freezes).
- **Never** use data older than 5 minutes for rates — P2P rates move fast.
- **Minimum credibility filter:** Only show merchants with ≥50 completed trades.
- **Log** every scan timestamp + top rates to the trading journal skill if available.
- On any URGENT regulatory news: lead with it before showing rates.

### Current Nigerian KYC baseline to always mention:
- NIN linkage required for all financial accounts
- CBN daily P2P transaction limits apply (verify current circular)
- Banks can freeze accounts flagged for "suspicious crypto activity"
- SEC sandbox rules still evolving — institutional rules ≠ retail rules

---

## Example

**User:** `Check NGN P2P now`

**Output:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🇳🇬  NIGERIA P2P ARB REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Scanned: 2026-03-19 07:31 UTC  |  Asset: USDT
  Market NGN/USDT: ₦1,593.20  (CoinGecko)

─────────────────────────────────────────────
📊  LIVE P2P RATES — Binance NGN
─────────────────────────────────────────────
Side  │ Best Rate  │ Median     │ Spread │ Top Merchant       │ Risk
──────┼────────────┼────────────┼────────┼────────────────────┼──────
BUY   │ ₦1,578.00  │ ₦1,581.40  │        │ ChukwuTrades (2.1k)│ 🟢
SELL  │ ₦1,602.50  │ ₦1,599.80  │ 1.54%  │ AbokiFX_P2P (987)  │ 🟢

  P2P Buy premium:  −0.95% below market (buyers paying below spot ✅)
  P2P Sell premium: +0.58% above market (sellers receiving above spot ✅)

─────────────────────────────────────────────
🏹  TOP ARB OPPORTUNITIES
─────────────────────────────────────────────
#  │ Path                        │ Buy ₦    │ Sell ₦   │ Net %  │ Net/100 USDT │ Risk
───┼─────────────────────────────┼──────────┼──────────┼────────┼──────────────┼──────
1  │ Spot CEX → Binance P2P Sell │ ₦1,593.20│ ₦1,602.50│ +0.58% │ +₦930        │ 🟢
2  │ P2P Buy (GTB) → USDT Hold   │ ₦1,578.00│ spot     │ +0.95% │ potential    │ 🟡
3  │ P2P Buy Opay → P2P Sell GTB │ ₦1,575.00│ ₦1,602.50│ +1.74% │ +₦2,750      │ 🟡

  ✅ Path 1 is cleanest — no counterparty hold risk, instant DEX settlement.
  ⚠️ Path 3 looks juicy but requires two P2P legs — double counterparty risk.

─────────────────────────────────────────────
📰  CBN/SEC/LOCAL NEWS (Last 24h)
─────────────────────────────────────────────
  🟢 INFO  — Techcabal: Nigerian fintech sector raises $120M in Q1 2026
  🟡 WATCH — SEC Nigeria signals new digital asset reporting framework by Q2
  🟢 INFO  — Nairametrics: P2P volumes up 34% YoY despite CBN monitoring

  No urgent bans or enforcement actions in the last 24 hours. ✅

─────────────────────────────────────────────
💼  WALLET SUGGESTION
─────────────────────────────────────────────
  No USDT/USDC detected on connected wallet.
  → Bridge USDT to Arbitrum/Base, then hit Path 1 for instant ₦930 on 100 USDT.

─────────────────────────────────────────────
⚠️  RISK FLAGS
─────────────────────────────────────────────
  🔴 NIN must be linked to your Binance account for P2P above ₦500k/day
  🟡 Banks (GTB, Zenith, UBA) have flagged crypto P2P transfers — use Opay/Kuda
  🟡 Chargeback fraud on Bank Transfer P2P — prefer merchants with escrow history
  🟢 Liquidity: ₦50M+ available across top 10 ads — no size constraints for <$500
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Act now? Reply YES + path number (e.g. YES 1) to prepare the trade,
or NEWS for deeper CBN/SEC regulatory analysis.
```

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-03-19 | Initial release — P2P scanner, arb calc, CBN/SEC watcher |
