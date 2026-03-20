---
name: "@1247/woofi-data"
version: 1.0.0
description: "Fetch WOOFi DEX metrics — trading stats, volume by source, earn yields, WOO staking. Covers 13 chains. No auth required."
tags: [defi, analytics, woofi, dex, yield]
author: "@1247"
---

# 📊 WOOFi Data API

Fetch WOOFi DEX metrics for content creation, reporting, and analysis.

## When to Use
- Content or reporting needs WOOFi trading volume, user counts, TVL
- Comparing DEX activity across chains
- Checking WOOFi Earn vault yields and APY
- Monitoring WOO staking metrics
- Analyzing volume by source/aggregator (1inch, 0x, Paraswap, etc.)

## API Details

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.woofi.com` |
| **Auth** | None required (fully public) |
| **Rate Limit** | 120 requests/minute |
| **Chains** | bsc, avax, polygon, arbitrum, optimism, linea, base, mantle, sonic, berachain, hyperevm, monad, solana |

## Endpoints

### 1. Trading Stats — `GET /stat`
Volume, trader count, and transaction count by period and chain.

**Parameters:**
- `period` (required): `1d`, `1w`, `1m`, `3m`, `1y`, `all`
- `network` (required): chain name from list above

**⚠️ volume_usd is in wei — divide by 10^18 to get USD value**

```bash
curl "https://api.woofi.com/stat?period=1d&network=arbitrum"
```

**Response fields:**
- `timestamp` — Unix epoch (seconds), start of time bucket
- `volume_usd` — Trading volume in wei (÷ 10^18 = USD)
- `traders` — Unique wallets
- `txs` / `txns` — Transaction count

### 2. Source Stats — `GET /source_stat`
Volume breakdown by integrator/aggregator source.

**Parameters:**
- `period` (required): `1d`, `1w`, `1m`, `3m`, `1y`, `all`
- `network` (required): chain name

```bash
curl "https://api.woofi.com/source_stat?period=1m&network=arbitrum"
```

**Response fields per source:**
- `name` — Source name (e.g. "1inch", "0x", "Paraswap", "WOOFi")
- `volume_usd` — Volume in wei (÷ 10^18 = USD)
- `percentage` — Share of total volume (string, e.g. "45.2")
- `traders`, `txs` — Unique wallets and tx count

### 3. Earn Yields — `GET /yield`
Vault TVL, APY, and yield composition per chain.

**Parameters:**
- `network` (required): chain name

```bash
curl "https://api.woofi.com/yield?network=base"
```

**Response structure:**
- `auto_compounding` — Map of vault address → vault data
  - `total_deposit` — TVL in wei (÷ 10^18 = USD)
  - `apy` — Current APY (decimal, e.g. 0.045 = 4.5%)
  - `source_apy` — Breakdown of yield sources
- `total_deposit` — Chain-wide total TVL in wei

### 4. WOO Staking — `GET /stakingv2`
Global WOO staking metrics (not chain-specific).

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
```python
import requests

chains = ["bsc", "avax", "polygon", "arbitrum", "optimism", "linea", "base", "mantle", "sonic", "berachain", "hyperevm", "monad", "solana"]
total = 0
for chain in chains:
    r = requests.get(f"https://api.woofi.com/stat?period=1m&network={chain}").json()
    if r.get("status") == "ok":
        for bucket in r["data"]:
            total += int(bucket["volume_usd"]) / 1e18
print(f"Total 30d volume: ${total:,.0f}")
```

### Get total TVL across all earn vaults
```python
import requests

chains = ["bsc", "avax", "polygon", "arbitrum", "optimism", "linea", "base", "mantle", "sonic", "berachain"]
total_tvl = 0
for chain in chains:
    r = requests.get(f"https://api.woofi.com/yield?network={chain}").json()
    if r.get("status") == "ok" and r["data"].get("total_deposit"):
        total_tvl += int(r["data"]["total_deposit"]) / 1e18
print(f"Total Earn TVL: ${total_tvl:,.0f}")
```

## LLM Integration
WOOFi also publishes an `llms.txt` file for AI agents:
`https://api.woofi.com/llms.txt`

## Source
- API: https://api.woofi.com
- Skills repo: https://github.com/woonetwork/woofi-skills
- Docs: https://learn.woo.org
