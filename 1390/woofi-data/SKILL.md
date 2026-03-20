---
name: "@1390/woofi-data"
version: 1.0.0
description: "Fetch WOOFi DEX metrics — trading stats, volume by source, earn yields, WOO staking across 13 chains. Use when analyzing DEX activity, comparing chain volumes, or checking WOOFi Earn vault APYs."
tags: [defi, analytics, woofi, dex, yield, trading]
author: "starchild"

metadata:
  starchild:
    emoji: "📊"
    skillKey: woofi-data

user-invocable: true
---

# 📊 WOOFi Data

Fetch WOOFi DEX metrics for market analysis, reporting, and DeFi research.

## When to Use

- User asks about WOOFi trading volume on specific chains
- Comparing DEX activity across multiple chains
- Checking WOOFi Earn vault TVL and APYs
- Analyzing volume sources (1inch, 0x, Paraswap, etc.)
- Monitoring WOO staking metrics and APR
- Building DeFi dashboards or reports

## API Overview

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.woofi.com` |
| **Auth** | None (fully public) |
| **Rate Limit** | 120 requests/minute |
| **Chains** | bsc, avax, polygon, arbitrum, optimism, linea, base, mantle, sonic, berachain, hyperevm, monad, solana |

## Endpoints

### 1. Trading Stats — `/stat`

Volume, trader count, and transaction count by period and chain.

**Parameters:**
- `period` (required): `1d`, `1w`, `1m`, `3m`, `1y`, `all`
- `network` (required): chain name from list above

**⚠️ CRITICAL: `volume_usd` is in wei — divide by 10^18 to get USD value**

**Example:**
```bash
curl "https://api.woofi.com/stat?period=1d&network=arbitrum"
```

**Response:**
```json
{
  "status": "ok",
  "data": [
    {
      "timestamp": 1710892800,
      "volume_usd": "1234567890123456789012",
      "traders": 1523,
      "txns": 8942
    }
  ]
}
```

### 2. Source Stats — `/source_stat`

Volume breakdown by integrator/aggregator source.

**Parameters:**
- `period` (required): `1d`, `1w`, `1m`, `3m`, `1y`, `all`
- `network` (required): chain name

**Example:**
```bash
curl "https://api.woofi.com/source_stat?period=1m&network=arbitrum"
```

**Response fields per source:**
- `name` — Source name (e.g. "1inch", "0x", "Paraswap", "WOOFi")
- `volume_usd` — Volume in wei (÷ 10^18 = USD)
- `percentage` — Share of total volume (string, e.g. "45.2")
- `traders`, `txs` — Unique wallets and tx count

### 3. Earn Yields — `/yield`

Vault TVL, APY, and yield composition per chain.

**Parameters:**
- `network` (required): chain name

**Example:**
```bash
curl "https://api.woofi.com/yield?network=base"
```

**Response structure:**
- `auto_compounding` — Map of vault address → vault data
  - `total_deposit` — TVL in wei (÷ 10^18 = USD)
  - `apy` — Current APY (decimal, e.g. 0.045 = 4.5%)
  - `source_apy` — Breakdown of yield sources
- `total_deposit` — Chain-wide total TVL in wei

### 4. WOO Staking — `/stakingv2`

Global WOO staking metrics (not chain-specific).

**Example:**
```bash
curl "https://api.woofi.com/stakingv2"
```

**Response fields:**
- `total_woo_staked` — Total WOO staked in wei (÷ 10^18)
- `avg_apr` — Current average staking APR
- `base_apr` — Base APR component
- `mp_boosted_apr` — Multiplier-boosted APR component

## Common Patterns

### Get total volume across all chains (last 30d)

Use the script in `scripts/total_volume.py`:

```bash
python skills/woofi-data/scripts/total_volume.py --period 1m
```

### Get total TVL across all earn vaults

Use the script in `scripts/total_tvl.py`:

```bash
python skills/woofi-data/scripts/total_tvl.py
```

### Quick single-chain query

```python
import requests

# Trading stats
r = requests.get("https://api.woofi.com/stat?period=1d&network=arbitrum").json()
volume_usd = int(r["data"][0]["volume_usd"]) / 1e18
print(f"Arbitrum 24h volume: ${volume_usd:,.0f}")

# Earn yields
r = requests.get("https://api.woofi.com/yield?network=base").json()
tvl = int(r["data"]["total_deposit"]) / 1e18
print(f"Base Earn TVL: ${tvl:,.0f}")
```

## Gotchas

1. **Wei conversion** — ALL USD values (`volume_usd`, `total_deposit`) are in wei. Always divide by 10^18.
2. **Chain names** — Use exact names from the supported list. "arbitrum" not "arb", "optimism" not "op".
3. **Period buckets** — `1m` returns 30 days of daily buckets, not a single aggregated value. Sum all buckets for total.
4. **Staking is global** — `/stakingv2` doesn't take a network param — it's the same across all chains.

## Related Resources

- API docs: `https://api.woofi.com/llms.txt`
- Official docs: `https://learn.woo.org`
- Original skill: `https://github.com/woonetwork/woofi-skills`
