---
name: "@1390/woofi-data"
version: 2.0.0
description: "Fetch WOOFi DEX metrics — trading stats, volume by source, earn yields, WOO staking, user portfolios, perps volume across 16 chains. Updated from woonetwork/woofi-skills."
tags: [defi, analytics, woofi, dex, yield, trading, perps]
author: "starchild"

metadata:
  starchild:
    emoji: "📊"
    skillKey: woofi-data

user-invocable: true
---

# 📊 WOOFi Data

Fetch WOOFi DEX metrics for market analysis, reporting, and DeFi research.

**Updated**: 2026-03-23 — Aligned with latest [woonetwork/woofi-skills](https://github.com/woonetwork/woofi-skills)

## When to Use

- User asks about WOOFi trading volume on specific chains
- Comparing DEX activity across multiple chains
- Checking WOOFi Earn vault TVL and APYs
- Analyzing volume sources (1inch, 0x, Paraswap, etc.)
- Monitoring WOO staking metrics and APR
- Querying user portfolio data (balances, positions, staking)
- Checking WOOFi Pro perpetuals volume
- Building DeFi dashboards or reports

## API Overview

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.woofi.com` |
| **Auth** | None (fully public) |
| **Rate Limit** | 5 requests/second |
| **Chains** | bsc, avalanche, polygon, arbitrum, optimism, linea, base, mantle, sonic, berachain, hyperevm, monad, solana, fantom, zksync, polygon_zkevm |

## Endpoints

### 1. Swap Support — `/swap_support`

Query supported networks, DEXs, and tokens for WOOFi swaps.

**Trigger phrases**: "swap support", "supported networks", "supported tokens", "which chains"

**Example:**
```bash
curl "https://api.woofi.com/swap_support"
```

**Response fields:**
- `networks` — List of supported chain names
- `dexes` — Supported DEX protocols per chain
- `tokens` — Supported token addresses per chain

### 2. Total Stats — `/multi_total_stat`, `/total_stat`, `/cumulate_stat`

Cross-chain aggregated trading statistics.

**Trigger phrases**: "total volume", "total stats", "cross chain stats", "24h stats", "overall volume"

**Example:**
```bash
# Cross-chain total
curl "https://api.woofi.com/multi_total_stat"

# Single chain total
curl "https://api.woofi.com/total_stat?network=arbitrum"

# Cumulative stat
curl "https://api.woofi.com/cumulate_stat?network=bsc"
```

### 3. Trading Stats — `/stat`

Volume, trader count, and transaction count by period and chain.

**Trigger phrases**: "trading stats", "trading volume", "woofi stats", "how much volume", "trader count"

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

### 4. Source Stats — `/source_stat`

Volume breakdown by integrator/aggregator source.

**Trigger phrases**: "volume by source", "top integrators", "who is sending volume", "traffic source"

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

### 5. Token Stats — `/token_stat`

Per-token 24-hour trading statistics including TVL, volume, and turnover rate.

**Trigger phrases**: "token stats", "token volume", "token tvl", "top tokens"

**Parameters:**
- `network` (required): chain name

**Example:**
```bash
curl "https://api.woofi.com/token_stat?network=arbitrum"
```

### 6. Solana Pool Stats — `/solana_stat`

Solana-specific raw pool statistics.

**Trigger phrases**: "solana stats", "solana pool", "solana trading"

**Example:**
```bash
curl "https://api.woofi.com/solana_stat"
```

### 7. Earn Yields — `/yield`

Vault TVL, APY, and yield composition per chain.

**Trigger phrases**: "earn tvl", "earn vault", "yield farming", "woofi earn", "tvl", "apy"

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

### 8. Earn Summary — `/earn_summary`

Supercharger vault APR summary across all networks, sorted by APR.

**Trigger phrases**: "earn summary", "supercharger", "earn apr", "best earn vault", "vault ranking"

**Example:**
```bash
curl "https://api.woofi.com/earn_summary"
```

**⚠️ Note**: Paused networks (`fantom`, `zksync`, `polygon_zkevm`) are excluded.

### 9. WOO Staking — `/stakingv2`

Global WOO token staking statistics including base APR and Multiplier Point boost.

**Trigger phrases**: "woo staking", "staking apr", "staked woo", "multiplier points"

**Example:**
```bash
curl "https://api.woofi.com/stakingv2"
```

**Response fields:**
- `total_woo_staked` — Total WOO staked in wei (÷ 10^18)
- `avg_apr` — Current average staking APR
- `base_apr` — Base APR component
- `mp_boosted_apr` — Multiplier-boosted APR component

### 10. User Portfolio — `/user_balances`, `/user_supercharger_infos`, `/user_stakingv2_infos`, `/boosted_apr_info`

User portfolio data including token balances, Supercharger positions, staking info, and boosted APR status.

**Trigger phrases**: "user balance", "user portfolio", "my position", "user staking", "boosted apr"

**Parameters:**
- `user` (required): User wallet address (checksummed for EVM)

**Example:**
```bash
curl "https://api.woofi.com/user_balances?user=0x..."
curl "https://api.woofi.com/user_supercharger_infos?user=0x..."
curl "https://api.woofi.com/user_stakingv2_infos?user=0x..."
curl "https://api.woofi.com/boosted_apr_info?user=0x..."
```

### 11. User Trading Volume — `/user_trading_volumes`, `/user_perp_volumes`

User swap and perpetual trading volume history.

**Trigger phrases**: "user trading volume", "my volume", "user perp volume", "trading history"

**Parameters:**
- `user` (required): User wallet address
- `period` (required): `7d`, `14d`, `30d` (different from stat endpoints!)

**Example:**
```bash
curl "https://api.woofi.com/user_trading_volumes?user=0x...&period=30d"
curl "https://api.woofi.com/user_perp_volumes?user=0x...&period=7d"
```

### 12. WOOFi Pro Perps — `/woofi_pro/perps_volume`

WOOFi Pro daily perpetual trading volume.

**Trigger phrases**: "perps volume", "woofi pro", "woofi dex", "perpetual volume"

**Example:**
```bash
curl "https://api.woofi.com/woofi_pro/perps_volume"
```

### 13. Integration Endpoints — `/integration/pairs`, `/integration/tickers`, `/integration/pool_states`

Trading pairs, 24-hour ticker data, and pool states for third-party integrations.

**Trigger phrases**: "trading pairs", "ticker data", "pool state", "integration pairs", "fee rate"

**Example:**
```bash
curl "https://api.woofi.com/integration/pairs?network=arbitrum"
curl "https://api.woofi.com/integration/tickers?network=arbitrum"
curl "https://api.woofi.com/integration/pool_states?network=arbitrum"
```

## Network Support Matrix

| Network | /stat | /source_stat | /token_stat | /yield | /earn_summary | /stakingv2 | /user_* | /integration |
|---------|-------|--------------|-------------|--------|---------------|------------|---------|--------------|
| BSC | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes |
| Avalanche | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes |
| Polygon | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes |
| Arbitrum | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes |
| Optimism | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes |
| Linea | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes |
| Base | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes |
| Mantle | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes |
| Sonic | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes |
| Berachain | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes |
| HyperEVM | Yes | Yes | Yes | No | — | — | Yes | Yes |
| Monad | Yes | Yes | Yes | No | — | — | Yes | Yes |
| Solana | Yes | Yes | Yes | No | — | — | No | — |
| Fantom | Yes | Yes | Yes | Yes | Paused | — | Yes | Yes |
| zkSync | Yes | Yes | Yes | Yes | Paused | — | Yes | Yes |
| Polygon zkEVM | Yes | Yes | Yes | Yes | Paused | — | Yes | Yes |
| (global) | — | — | — | — | — | Yes | — | — |

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

# WOO staking
r = requests.get("https://api.woofi.com/stakingv2").json()
woo_staked = int(r["data"]["total_woo_staked"]) / 1e18
print(f"Total WOO staked: {woo_staked:,.0f} WOO")
```

## Gotchas

1. **Wei conversion** — ALL USD values (`volume_usd`, `total_deposit`) are in wei. Always divide by 10^18.
2. **Chain names** — Use exact names from the supported list. "arbitrum" not "arb", "optimism" not "op".
3. **Period buckets** — `1m` returns 30 days of daily buckets, not a single aggregated value. Sum all buckets for total.
4. **Staking is global** — `/stakingv2` doesn't take a network param — it's the same across all chains.
5. **Trader counts** — Do NOT sum `trader_count` across time buckets — each bucket is independently unique-per-period.
6. **Period `1d`** — Returns hourly buckets. All other periods return daily buckets.
7. **User endpoints** — Period values are `7d`, `14d`, `30d` (different from stat endpoints).
8. **Cross-chain queries** — Require separate requests per network, then manual aggregation. Exception: `/multi_total_stat` and `/user_trading_volumes` aggregate automatically.
9. **Address format** — All EVM addresses should be checksummed.
10. **Paused networks** — `fantom`, `zksync`, `polygon_zkevm` are excluded from `/earn_summary`.

## Related Resources

- API docs: `https://api.woofi.com/llms.txt`
- Official docs: `https://learn.woo.org`
- Original skill: `https://github.com/woonetwork/woofi-skills`
