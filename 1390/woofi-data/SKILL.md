---
name: "@1390/woofi-data"
version: 3.0.0
description: "Fetch WOOFi DEX metrics — trading stats, volume by source, earn yields, WOO staking, user portfolios, perps volume, swap quotes across 16 chains. Updated from woonetwork/woofi-skills v1.1."
tags: [defi, analytics, woofi, dex, yield, trading, perps, swap, quote]
author: "starchild"

metadata:
  starchild:
    emoji: "📊"
    skillKey: woofi-data

user-invocable: true
---

# 📊 WOOFi Data

Fetch WOOFi DEX metrics for market analysis, reporting, and DeFi research.

**Updated**: 2026-03-23 — Aligned with [woonetwork/woofi-skills](https://github.com/woonetwork/woofi-skills) v1.1 (2026-03-20)

**What's New in v3.0.0:**
- Added `/swap` endpoint for quote requests (quote only, execution requires wallet integration)
- Added `/integration/pool_states` for real-time pool liquidity data
- Added `/analytics/daily_fee` for protocol revenue tracking
- Updated network support matrix with 16 chains

## When to Use

- User asks about WOOFi trading volume on specific chains
- Comparing DEX activity across multiple chains
- Checking WOOFi Earn vault TVL and APYs
- Analyzing volume sources (1inch, 0x, Paraswap, etc.)
- Monitoring WOO staking metrics and APR
- Querying user portfolio data (balances, positions, staking)
- Checking WOOFi Pro perpetuals volume
- **Getting swap quotes for token exchanges** (NEW)
- **Checking pool liquidity and reserves** (NEW)
- **Tracking protocol revenue** (NEW)
- Building DeFi dashboards or reports

## API Overview

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.woofi.com` |
| **Auth** | None (fully public) |
| **Rate Limit** | 5 requests/second |
| **Chains** | bsc, avalanche, polygon, arbitrum, optimism, linea, base, mantle, sonic, berachain, hyperevm, monad, solana, fantom, zksync, polygon_zkevm, sei |

## Endpoints

### 1. Swap Support — `/swap_support`

Query supported networks, DEXs, and tokens for WOOFi swaps.

**Trigger phrases**: "swap support", "supported networks", "supported tokens", "which chains"

**Example:**
```bash
curl "https://api.woofi.com/swap_support"
```

**Response fields:**
- `dexs` — List of DEX integrations per chain (uni_swap, sushi_swap, curve, woofi, etc.)
- `network_infos` — Chain metadata (name, RPC URL, chain ID, explorer, bridge support)
- `token_infos` — Supported tokens with address, symbol, decimals, `swap_enable` flag
- `swap_enable` — Whether swapping is currently active for this token/network
- `bridge_enable` — Whether cross-chain bridging is supported

**⚠️ Note**: Paused networks (fantom, zksync, polygon_zkevm) have `swap_enable=false` for all tokens.

### 2. Swap Quote — `/swap` 🆕

Get swap quote for token exchange. Returns routing info, expected output amount, and price impact.

**Trigger phrases**: "swap quote", "quote ETH to USDC", "how much USDC for 1 ETH", "swap price"

**Parameters:**
- `from_token` (required): Source token contract address (or `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE` for native ETH)
- `to_token` (required): Destination token contract address
- `from_amount` (required): Amount in smallest unit (wei for ETH, 6 decimals for USDC)
- `network` (required): Chain name (e.g., "arbitrum", "bsc", "base")
- `slippage` (optional): Slippage tolerance in basis points (e.g., 50 = 0.5%, default: 50)

**Example:**
```bash
# Quote: 0.1 ETH → USDC on Arbitrum
curl "https://api.woofi.com/swap?from_token=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE&to_token=0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8&from_amount=100000000000000000&network=arbitrum"
```

**Response structure:**
```json
{
  "status": "ok",
  "data": {
    "from_token": {...},
    "to_token": {...},
    "from_amount": "100000000000000000",
    "to_amount": "245000000",  # Expected output (in to_token decimals)
    "price_impact": "0.15",   # Price impact percentage
    "routing_info": {
      "sources": [
        {"name": "woofi", "percentage": "60.5"},
        {"name": "uni_swap", "percentage": "39.5"}
      ]
    },
    "gas_estimate": "150000"
  }
}
```

**⚠️ Important:**
- This endpoint returns a **quote only** — it does NOT execute the swap
- To execute, you need to integrate with WOOFi's smart contracts or use a wallet
- `from_amount` must be in the token's smallest unit (wei for 18-decimal tokens)
- `to_amount` will be in the destination token's decimal precision
- For native ETH, use address `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`

### 3. Total Stats — `/multi_total_stat`, `/total_stat`, `/cumulate_stat`

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

### 4. Trading Stats — `/stat`

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

### 5. Source Stats — `/source_stat`

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
- `name` — Source name (e.g. "1inch", "0x", "Paraswap", "WOOFi", "KyberSwap", "ODOS")
- `volume_usd` — Volume in wei (÷ 10^18 = USD)
- `percentage` — Share of total volume (string, e.g. "45.2")
- `traders`, `txs` — Unique wallets and tx count

**Known integrators:** 1inch, 0x, ODOS, KyberSwap, Paraswap, THORSwap, OKX, BitKeep, Firebird, Transit Swap, Hera Fireance, Yeti, Joy, ZetaFarm, Slingshot, unizen, 1delta, KALM, ONTO, Velora, Nativo, etc.

### 6. Token Stats — `/token_stat`

Per-token 24-hour trading statistics including TVL, volume, and turnover rate.

**Trigger phrases**: "token stats", "token volume", "token tvl", "top tokens"

**Parameters:**
- `network` (required): chain name

**Example:**
```bash
curl "https://api.woofi.com/token_stat?network=arbitrum"
```

### 7. Solana Pool Stats — `/solana_stat`

Solana-specific raw pool statistics.

**Trigger phrases**: "solana stats", "solana pool", "solana trading"

**Example:**
```bash
curl "https://api.woofi.com/solana_stat"
```

### 8. Earn Yields — `/yield`

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

### 9. Earn Summary — `/earn_summary`

Supercharger vault APR summary across all networks, sorted by APR.

**Trigger phrases**: "earn summary", "supercharger", "earn apr", "best earn vault", "vault ranking"

**Example:**
```bash
curl "https://api.woofi.com/earn_summary"
```

**⚠️ Note**: Paused networks (`fantom`, `zksync`, `polygon_zkevm`) are excluded.

### 10. WOO Staking — `/stakingv2`

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

### 11. User Portfolio — `/user_balances`, `/user_supercharger_infos`, `/user_stakingv2_infos`, `/boosted_apr_info`

User portfolio data including token balances, Supercharger positions, staking info, and boosted APR status.

**Trigger phrases**: "user balance", "user portfolio", "my position", "user staking", "boosted apr"

**Parameters:**
- `user` or `user_address` (required): User wallet address (checksummed for EVM)

**Example:**
```bash
curl "https://api.woofi.com/user_balances?user_address=0x..."
curl "https://api.woofi.com/user_supercharger_infos?user_address=0x..."
curl "https://api.woofi.com/user_stakingv2_infos?user_address=0x..."
curl "https://api.woofi.com/boosted_apr_info?user_address=0x..."
```

### 12. User Trading Volume — `/user_trading_volumes`, `/user_perp_volumes`

User swap and perpetual trading volume history.

**Trigger phrases**: "user trading volume", "my volume", "user perp volume", "trading history"

**Parameters:**
- `user` or `user_address` (required): User wallet address
- `period` (required): `7d`, `14d`, `30d` (different from stat endpoints!)

**Example:**
```bash
curl "https://api.woofi.com/user_trading_volumes?user_address=0x...&period=30d"
curl "https://api.woofi.com/user_perp_volumes?user_address=0x...&period=7d"
```

### 13. WOOFi Pro Perps — `/woofi_pro/perps_volume`

WOOFi Pro daily perpetual trading volume.

**Trigger phrases**: "perps volume", "woofi pro", "woofi dex", "perpetual volume"

**Example:**
```bash
curl "https://api.woofi.com/woofi_pro/perps_volume"
```

### 14. Integration Endpoints — `/integration/pairs`, `/integration/tickers`, `/integration/pool_states` 🆕

Trading pairs, 24-hour ticker data, and pool states for third-party integrations.

**Trigger phrases**: "trading pairs", "ticker data", "pool state", "integration pairs", "fee rate", "pool liquidity"

**Example:**
```bash
curl "https://api.woofi.com/integration/pairs?network=arbitrum"
curl "https://api.woofi.com/integration/tickers?network=arbitrum"
curl "https://api.woofi.com/integration/pool_states?network=arbitrum"
```

**Pool states response includes:**
- `reserve` — Token reserve in the WooPP pool
- `fee_rate` — Trading fee rate (in basis points)
- `max_gamma` — Maximum gamma parameter for sPMM pricing
- `max_notional_swap` — Maximum notional swap size
- `cap_bal` — Maximum balance cap for the token
- `price` — Current oracle price (18-decimal fixed point)
- `spread` — Price spread from the oracle

### 15. Protocol Revenue — `/analytics/daily_fee` 🆕

Daily net protocol revenue breakdown for WOOFi Swap and WOOFi Pro.

**Trigger phrases**: "protocol revenue", "daily fee", "woofi revenue", "fee breakdown"

**Parameters:**
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format

**Example:**
```bash
curl "https://api.woofi.com/analytics/daily_fee?start_date=2026-03-01&end_date=2026-03-20"
```

**Response:**
```json
{
  "status": "ok",
  "data": [
    {
      "date": "2026-03-20",
      "swap": 1732.845286,   # Swap revenue (USD)
      "pro": 845.123456      # Pro perps revenue (USD)
    }
  ]
}
```

## Network Support Matrix

| Network | /stat | /source_stat | /token_stat | /yield | /earn_summary | /stakingv2 | /user_* | /integration | /swap |
|---------|-------|--------------|-------------|--------|---------------|------------|---------|--------------|-------|
| BSC | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes | Yes |
| Avalanche | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes | Yes |
| Polygon | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes | Yes |
| Arbitrum | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes | Yes |
| Optimism | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes | Yes |
| Linea | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes | Yes |
| Base | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes | Yes |
| Mantle | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes | Yes |
| Sonic | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes | Yes |
| Berachain | Yes | Yes | Yes | Yes | Yes | — | Yes | Yes | Yes |
| HyperEVM | Yes | Yes | Yes | No | — | — | Yes | Yes | Yes |
| Monad | Yes | Yes | Yes | No | — | — | Yes | Yes | Yes |
| Solana | Yes | Yes | Yes | No | — | — | No | No | Yes |
| Fantom | Yes | Yes | Yes | Yes | Paused | — | Yes | Yes | Paused |
| zkSync | Yes | Yes | Yes | Yes | Paused | — | Yes | Yes | Paused |
| Polygon zkEVM | Yes | Yes | Yes | Yes | Paused | — | Yes | Yes | Paused |
| Sei | — | — | — | — | — | — | — | — | Pro only |
| (global) | — | — | — | — | — | Yes | — | — | — |

## Common Patterns

### Get swap quote: 0.1 ETH → USDC on Arbitrum

```python
import requests

# First, get token addresses from swap_support
r = requests.get("https://api.woofi.com/swap_support").json()
arb_tokens = r["data"]["arbitrum"]["token_infos"]
eth_addr = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"
usdc_addr = "0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8"

# Get quote
r = requests.get(
    "https://api.woofi.com/swap",
    params={
        "from_token": eth_addr,
        "to_token": usdc_addr,
        "from_amount": "100000000000000000",  # 0.1 ETH in wei
        "network": "arbitrum"
    }
).json()

if r["status"] == "ok":
    to_amount = int(r["data"]["to_amount"]) / 1e6  # USDC has 6 decimals
    print(f"0.1 ETH → ${to_amount:,.2f} USDC")
    print(f"Price impact: {r['data']['price_impact']}%")
```

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

### Get protocol revenue for a date range

```python
import requests

r = requests.get(
    "https://api.woofi.com/analytics/daily_fee",
    params={"start_date": "2026-03-01", "end_date": "2026-03-20"}
).json()

total_swap = sum(d["swap"] for d in r["data"])
total_pro = sum(d["pro"] for d in r["data"])
print(f"Swap revenue: ${total_swap:,.2f}")
print(f"Pro revenue: ${total_pro:,.2f}")
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

# Pool states
r = requests.get("https://api.woofi.com/integration/pool_states?network=arbitrum").json()
print(f"Pool data: {r['data']}")
```

## Gotchas

1. **Wei conversion** — ALL USD values (`volume_usd`, `total_deposit`) are in wei. Always divide by 10^18.
2. **Token decimals vary** — USDC has 6 decimals, ETH has 18. Adjust `from_amount` and parse `to_amount` accordingly.
3. **Chain names** — Use exact names from the supported list. "arbitrum" not "arb", "optimism" not "op".
4. **Period buckets** — `1m` returns 30 days of daily buckets, not a single aggregated value. Sum all buckets for total.
5. **Staking is global** — `/stakingv2` doesn't take a network param — it's the same across all chains.
6. **Trader counts** — Do NOT sum `trader_count` across time buckets — each bucket is independently unique-per-period.
7. **Period `1d`** — Returns hourly buckets. All other periods return daily buckets.
8. **User endpoints** — Period values are `7d`, `14d`, `30d` (different from stat endpoints).
9. **Cross-chain queries** — Require separate requests per network, then manual aggregation. Exception: `/multi_total_stat` and `/user_trading_volumes` aggregate automatically.
10. **Address format** — All EVM addresses should be checksummed.
11. **Paused networks** — `fantom`, `zksync`, `polygon_zkevm` are excluded from `/earn_summary` and have `swap_enable=false`.
12. **Native ETH** — Use `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE` as the token address for ETH.
13. **Swap quote is read-only** — The `/swap` endpoint returns a quote only. Execution requires wallet integration with WOOFi smart contracts.

## Related Resources

- API docs: `https://api.woofi.com/llms.txt`
- Official docs: `https://learn.woo.org`
- Original skill: `https://github.com/woonetwork/woofi-skills`
- Python SDK: `https://github.com/woonetwork/woofi-python-sdk`
