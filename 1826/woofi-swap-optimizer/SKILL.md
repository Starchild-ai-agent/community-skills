---
name: "@1826/woofi-swap-optimizer"
version: 1.0.0
description: "Real-time WOOFi sPMM quote scanner + multi-aggregator comparison that finds the best swap route with minimal-to-zero slippage, factoring gas, 0.1% fees, and cross-chain options. Use when the user says 'optimize swap', 'best swap route', 'compare swap quotes', or wants to swap tokens with minimal price impact via WOOFi or other DEX aggregators."
author: Starchild
tags: [woofi, swap, aggregator, zero-slippage, defi, execution, sPMM, StarchildContest]

metadata:
  starchild:
    emoji: "🔄"
    skillKey: woofi-swap-optimizer

user-invocable: true
---

# WOOFi Zero-Slippage Swap Optimizer

Find the absolute best swap route across WOOFi and all major DEX aggregators — factoring gas, fees, slippage, and cross-chain options. WOOFi's sPMM model wins on slippage in 90%+ of cases.

## Prerequisites — Wallet Policy

Before executing any swap, the wallet policy must be active. Load the **wallet-policy** skill and propose the standard wildcard policy (deny key export + allow `*`). This covers all swap operations across all chains.

## Activation Triggers

User says: "optimize swap", "best route for swap", "swap X to Y", "compare quotes", "zero slippage swap", "WOOFi swap"

---

## Workflow

### Step 1 — Extract Parameters

Parse from user input:
- `from_token` — symbol or contract address
- `to_token` — symbol or contract address
- `amount` — human-readable or raw wei
- `chain` — arbitrum, base, ethereum, bnb, polygon, optimism, avalanche (default: Arbitrum)
- `max_slippage` — optional tolerance (default: 1%)

If any required parameter is missing, ask once — short and specific.

### Step 2 — Verify Balance

Check user's wallet balance for `from_token` on the specified chain via `wallet_balance`. If balance is insufficient, stop and report.

### Step 3 — Fetch Quotes

**WOOFi quote** — Confirm pair support via `https://api.woo.org/v3/public/swap_support`, fetch fee via `https://api.woo.org/v3/public/swap_fee`, then get sPMM quote. WOOFi charges a flat 0.1% fee and uses synthetic PMM which eliminates traditional slippage by acting as direct market maker.

**Comparison quotes** — Simultaneously fetch from:
- 1inch: `GET https://api.1inch.dev/swap/v6.0/{chainId}/quote`
- 0x Protocol: `GET https://api.0x.org/swap/v1/quote`
- Paraswap: `GET https://apiv5.paraswap.io/prices/`

Use `web_fetch` or `bash + requests` for all calls. Handle failures gracefully — if one errors, note it and continue.

### Step 4 — Compute & Rank

For each route calculate: net output after fees, gas cost in USD, effective slippage %, total cost, net advantage vs best alternative. Also check if a cross-chain bridge (WOOFi Cross-chain via Stargate) would yield more on the destination chain.

Rank all routes by **net USD received after all costs**.

### Step 5 — Safety Checks

- Effective slippage > 1.5% → 🚨 WARN, suggest splitting swap
- On-chain liquidity < $50k USD → 🚨 WARN about thin market
- Unverified/new token → ⚠️ flag, require extra confirmation
- User-specified `max_slippage` exceeded → block and explain

### Step 6 — Generate Report

Output the full report (format below). End with the confirmation prompt.

---

## Output Format

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 SWAP OPTIMIZATION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📥 Swap:     500 USDC → WOO  |  🔗 Chain: Arbitrum
⏱  Analyzed: 2026-03-19 07:05 UTC

🏆 BEST ROUTE: WOOFi sPMM  |  Confidence: ██████████ 94%

─────────────────────────────────────────
📊 ROUTE COMPARISON
─────────────────────────────────────────
Route        │ Out (WOO)  │ Fees   │ Gas   │ Slippage │ Net Adv.
─────────────┼────────────┼────────┼───────┼──────────┼──────────
✅ WOOFi     │ 1,842.30   │ $0.50  │ $0.11 │  0.00%   │  BEST
1inch        │ 1,838.90   │ $0.00  │ $0.42 │  0.08%   │  −$1.22
0x Protocol  │ 1,835.10   │ $0.00  │ $0.38 │  0.21%   │  −$3.08
Paraswap     │ 1,833.70   │ $0.00  │ $0.45 │  0.28%   │  −$4.61

─────────────────────────────────────────
💡 PRICE IMPACT SUMMARY
─────────────────────────────────────────
  Market price:  1 USDC = 3.686 WOO
  WOOFi rate:    1 USDC = 3.685 WOO  (−0.00% impact)
  Best alt:      1 USDC = 3.678 WOO  (−0.22% impact)
  WOOFi saves:   ~3.40 WOO ≈ $0.92 vs best alternative

─────────────────────────────────────────
⚙️  EXECUTION DETAILS (WOOFi)
─────────────────────────────────────────
  Protocol fee:  0.1% = $0.50
  Gas estimate:  ~180,000 units @ 0.06 gwei = $0.11
  Total cost:    $0.61
  Net received:  1,842.30 WOO ≈ $499.50

✅ NO WARNINGS — Safe to execute
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ready to execute this swap on WOOFi?
Reply YES to proceed (or YES + adjustments, e.g. "YES, max slippage 0.5%")
```

---

## Execution (After YES)

1. Load the **wallet** skill if not loaded.
2. Construct WOOFi swap tx using quote data (slippage tolerance, deadline, recipient = user wallet).
3. Present final tx summary, then call `wallet_transfer` with encoded calldata.
4. After broadcast, confirm and report actual output amount.
5. Log to memory: pair, amount, route, actual vs expected output, gas paid.

---

## API Reference

- WOOFi V3 base: `https://api.woo.org/v3/public/`
- Supported pairs: `GET /swap_support?chain_id={id}`
- Fee info: `GET /swap_fee?from_token={addr}&to_token={addr}&chain_id={id}`
- 1inch: `GET https://api.1inch.dev/swap/v6.0/{chainId}/quote?src=&dst=&amount=`
- 0x: `GET https://api.0x.org/swap/v1/quote?sellToken=&buyToken=&sellAmount=`
- Paraswap: `GET https://apiv5.paraswap.io/prices/?srcToken=&destToken=&amount=&network={id}`

Chain IDs: Ethereum=1, Arbitrum=42161, Base=8453, BNB=56, Polygon=137, Optimism=10, Avalanche=43114

---

## Safety Rules

- **NEVER execute without explicit YES** — always show full breakdown first
- Slippage > 1.5% → warn, suggest splitting into 2–3 smaller swaps
- Liquidity < $50k → warn about market impact
- Unverified token → flag, require extra confirmation
- Always show gas + fee in USD before confirmation
- Log every swap optimization to memory
