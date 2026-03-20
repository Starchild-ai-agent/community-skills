---
name: "@1458/woofi"
version: 1.0.0
description: "Fetch WOOFi DEX data — swap volume, traders, staking, TVL across chains. Use when the user asks about WOOFi metrics, volume breakdown, chain performance, or WOO staking stats."
author: ranyi1115
tags: [woofi, dex, volume, defi, woo, trading, onchain]

metadata:
  starchild:
    emoji: "🐶"
    skillKey: woofi

user-invocable: true
---

# WOOFi Skill

Fetch live WOOFi swap and staking data. No API key required — all endpoints are public.

## Base URLs

- **Swap stats**: `https://fi-api.woo.org/swap_stats`
- **Staking**: `https://fi-api.woo.org/staking`

## Key Endpoints

### Volume & Traders by Chain (30d)
```
GET https://fi-api.woo.org/swap_stats?type=monthly&network={chain}
```
Chains: `arbitrum`, `base`, `bsc`, `optimism`, `solana`, `polygon`, `avalanche`, `ethereum`

Returns: `volume`, `traders`, `traders_peak_daily`, daily breakdown

### Daily Time Series
```
GET https://fi-api.woo.org/swap_stats?type=daily&network={chain}
```

### WOO Staking
```
GET https://fi-api.woo.org/staking
```
Returns: total staked, APR (note: APR inflated by MP boosts — report as "up to X%")

## Gotchas

- Optimism shows unusually high peak trader counts (likely bots or airdrop farmers) — flag if >5x other chains
- APR from staking endpoint includes MP (Multiplier Points) boost — real base APR is lower
- `volume` is in USD
- No auth header needed

## Quick Script
