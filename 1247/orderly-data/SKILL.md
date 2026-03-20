---
name: "@1247/orderly-data"
version: 1.0.0
description: "Fetch Orderly Network metrics for content creation, reporting, and analysis."
author: starchild
tags: [orderly, data, metrics, analytics, defi, perps]
---

# 📊 Orderly Data API

Fetch Orderly Network metrics for content creation, reporting, and analysis.

## When to Use
- Content bot needs fresh Orderly metrics (volume, TVL, users, revenue)
- Building reports or dashboards about Orderly Network
- Comparing Orderly performance over time

## Auth

Two APIs with different auth:

| API | Base URL | Auth |
|-----|----------|------|
| **Data API** (internal metrics) | `https://data-api.orderly.network/orderly/api/v1` | `X-API-KEY` header with `ORDERLY_DATA_API_KEY` from `.env` |
| **Public API** (on-chain stats) | `https://api.orderly.org/v1/public` | No auth required |

## Endpoints

### Data API (requires `ORDERLY_DATA_API_KEY`)

| Endpoint | Description | Key Fields |
|----------|-------------|------------|
| `GET /metrics/overview?range=weekly` | Weekly/monthly KPIs over time | `avg_daily_volume`, `avg_daily_revenue`, `avg_new_users`, `avg_active_users` |
| `GET /metrics/volume-segments` | Volume by segment (B2B/B2C/MM) | `b2b_volume`, `b2c_volume`, `mm_volume` |
| `GET /metrics/stake-users` | $ORDER staker count | `unique_stakers` |
| `GET /metrics/stake-vs-supply` | Staked vs circulating | `total_staked`, `circulating_supply` |
| `GET /metrics/omnivault-tvl` | TVL by vault (weekly) | `total_tvl`, vault breakdowns |
| `GET /distributors/stats` | All distributor stats | `invitee_count`, `revenue_share_30d`, `volume_30d` |
| `GET /distributors/invitees?distributor_id=X` | Invitees for a distributor | `dex_name`, `volume`, `revenue` |
| `GET /data/summary` | API health + DB stats | `status` |

**`range` parameter:** Use `weekly` or `monthly` for `/metrics/overview`.

### Public API (no auth)

| Endpoint | Description | Key Fields |
|----------|-------------|------------|
| `GET /balance/stats` | Total platform holdings | `total_holding` (USDC TVL) |
| `GET /volume/stats` | Volume aggregates | `perp_volume_ytd`, `perp_volume_ltd`, `perp_volume_last_30_days` |
| `GET /funding_rates` | All perp funding rates | `est_funding_rate`, `last_funding_rate` per symbol |
| `GET /funding_rate/{symbol}` | Single symbol funding | e.g. `PERP_BTC_USDC` |
| `GET /trading_rewards/epoch_data` | $ORDER reward epochs | `epoch_id`, `reward_status`, `r_major`, `r_alts` |
| `GET /info` | All trading pairs/instruments | symbol specs, tick sizes |
| `GET /futures` | Futures contract info | contract details |
| `GET /token` | Supported tokens | token list |
| `GET /chain_info` | Supported chains | chain IDs, RPCs |

## Quick Start

```python
import os, requests

# Data API (authed)
DATA_BASE = "https://data-api.orderly.network/orderly/api/v1"
API_KEY = os.environ["ORDERLY_DATA_API_KEY"]
headers = {"X-API-KEY": API_KEY}

overview = requests.get(f"{DATA_BASE}/metrics/overview", params={"range": "weekly"}, headers=headers).json()

# Public API (no auth)
PUB_BASE = "https://api.orderly.org/v1/public"
volume = requests.get(f"{PUB_BASE}/volume/stats").json()
balance = requests.get(f"{PUB_BASE}/balance/stats").json()
```

## Content Bot Cheat Sheet

For a quick Orderly health snapshot, pull these three:

1. **Volume**: `GET /volume/stats` → `perp_volume_last_30_days`, `perp_volume_ytd`
2. **TVL**: `GET /balance/stats` → `total_holding`
3. **Growth**: `GET /metrics/overview?range=weekly` → latest week's `avg_daily_volume`, `avg_new_users`

### Current Numbers (as of March 20, 2026)
- **Perp Volume YTD:** $72.6B
- **Perp Volume LTD:** $186.8B
- **30d Volume:** $1.16B
- **Platform TVL:** $18.3M
- **Distributors:** 399
- **$ORDER Rewards:** 23M tokens distributed across 15 epochs

## Error Handling

- Data API returns `{"detail": "Invalid API key"}` on bad auth
- Public API returns `{"success": false, "code": -1106, "message": "..."}` on bad params
- Both return standard HTTP status codes

## Notes

- Data API metrics update daily; not real-time
- Public API balance/volume stats update every ~10 minutes
- Funding rates update every 8 hours (with estimated rates between)
