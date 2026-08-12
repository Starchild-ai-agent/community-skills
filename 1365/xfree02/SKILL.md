---
name: "@1365/xfree02"
description: Query sponsored Nansen on-chain intelligence endpoints through an open, no-API-key gateway. No wallet, no signup, no signature required from the caller.
author: starchild
version: 1.1.0
tags: [nansen, onchain, analytics, sponsored, open]
---

# xfree02 — Sponsored Nansen Skill

A CLI for querying Nansen on-chain intelligence endpoints through a fully open
gateway. **No API key, no wallet, no signup, no signature.** A sponsor pays the
upstream cost on behalf of callers, subject to daily quotas.

## Quickstart (no signup, no key)

The gateway is open. Anyone can POST to it directly. The call below is verified
to return HTTP 200 with `x-sponsored-cents: 1` and `x-caller-remaining-cents: <n>`
in the response headers:

```bash
curl -s -X POST "https://1365-xfree02-gateway.community.iamstarchild.com/v1/api/v1/chains/chain-rank" \
  -H "Content-Type: application/json" \
  -d '{}'
```

The CLI wraps the same flow. With no environment variables set, the gateway is
hit anonymously and the call is billed against a per-IP quota bucket:

```bash
xfree02 call /api/v1/chains/chain-rank
```

Setting `XFREE02_API_KEY` is optional. When set to a recognised key, the call is
billed against that key's own quota bucket instead of the anonymous IP bucket.
An unrecognised key is silently ignored — the gateway never returns 401.

## Environment variables

| Variable           | Required for          | Default                                              |
|--------------------|-----------------------|------------------------------------------------------|
| `XFREE02_BASE_URL` | all subcommands       | `https://1365-xfree02-gateway.community.iamstarchild.com` |
| `XFREE02_API_KEY`  | optional — only for a dedicated quota bucket | — (omit for anonymous access)         |

Both variables are optional. `XFREE02_BASE_URL` defaults to the public gateway
above. `XFREE02_API_KEY` is only needed if you want a caller's spend to be
tracked under a specific key rather than the client's IP.

## Subcommands

### `catalog`

List available endpoints as a markdown table.

```bash
export XFREE02_BASE_URL=https://1365-xfree02-gateway.community.iamstarchild.com
xfree02 catalog --sponsored-only --max-price 0.01
```

### `show`

Print the required fields, all fields, and example body for one endpoint.

```bash
xfree02 show /api/v1/perp-screener
```

### `call`

POST to `{XFREE02_BASE_URL}/v1{path}` with a JSON body. If neither `--body` nor
`--body-file` is given, the endpoint's `example_body` from the catalog is used
automatically. Some endpoints require concrete `from` / `to` dates; run
`xfree02 show <path>` for the required fields rather than guessing.

```bash
xfree02 call /api/v1/chains/chain-rank
```

On success the JSON body is printed to stdout and a one-line footer with
`x-sponsored-cents` / `x-caller-remaining-cents` is printed to stderr.

### `health`

GET `{XFREE02_BASE_URL}/health` and print the JSON response. No key required.
Example response:

```json
{
  "ok": true,
  "sponsored_endpoints": 30,
  "per_payer_cents_day": 10,
  "global_cents_day": 50,
  "auth": "open",
  "api_key_required": false,
  "anonymous_quota": "per client IP",
  "dry_run": false
}
```

## All endpoints are POST

Every endpoint in the Nansen catalog is a POST request. The `call` subcommand
always issues a POST, even if the body is empty.

## Sponsorship model

- The **sponsor** pays for every call. The caller needs no wallet and signs
  nothing.
- Two daily quotas are enforced:
  - **Per-caller** (`per_payer_cents_day`) — 10 cents/day. Keyed by `XFREE02_API_KEY`
    when set, otherwise by client IP.
  - **Global** (`global_cents_day`) — 50 cents/day across all callers (sponsor ceiling).
- Quotas reset at midnight UTC.
- Sponsored endpoints are those with `price_usd <= $0.01` (currently 30).

## Error responses

The gateway returns the following errors. There is **no** `missing_api_key` or
`invalid_api_key` response — authentication is always open.

| Status | `error`                    | Meaning                                              |
|--------|----------------------------|------------------------------------------------------|
| 404    | `unknown_endpoint`         | Path not in the catalog.                             |
| 403    | `not_sponsored`            | Endpoint price above the $0.01 sponsor cap.          |
| 402    | `payer_quota_exhausted`    | Per-caller quota (10¢/day) used up.                  |
| 402    | `global_quota_exhausted`   | Sponsor's global quota (50¢/day) used up.            |
| 502    | `payment_failed`           | Upstream payment failure.                            |

Both 402 responses include `retry_after_utc_date` (next UTC midnight) and
`direct_url` (the same endpoint on the Nansen proxy where you can pay yourself).

## Sponsored endpoints (price_usd ≤ $0.01)

| Path                                                    | Price  | Label                                      |
|---------------------------------------------------------|--------|--------------------------------------------|
| `/api/v1/chains/chain-rank`                             | $0.01  | Get chain growth rankings                  |
| `/api/v1/nansen-score/top-tokens`                       | $0.01  | Get Nansen Score Top Tokens                |
| `/api/v1/perp-screener`                                 | $0.01  | Get Perpetual Contract Screening Data      |
| `/api/v1/prediction-market/address-summary`             | $0.01  | Get Prediction Market Address Summary      |
| `/api/v1/prediction-market/categories`                  | $0.01  | Get Prediction Market Categories           |
| `/api/v1/prediction-market/event-screener`              | $0.01  | Get Prediction Market Event Screener       |
| `/api/v1/prediction-market/market-screener`             | $0.01  | Get Prediction Market Screener             |
| `/api/v1/prediction-market/ohlcv`                       | $0.01  | Get Prediction Market OHLCV Candles        |
| `/api/v1/prediction-market/orderbook`                   | $0.01  | Get Prediction Market Orderbook            |
| `/api/v1/prediction-market/trades-by-market`            | $0.01  | Get Prediction Market Trades by Market     |
| `/api/v1/profiler/address/current-balance`              | $0.01  | Get Address Current Balance Data           |
| `/api/v1/profiler/address/historical-balances`          | $0.01  | Get Address Historical Balances Data       |
| `/api/v1/profiler/address/pnl`                          | $0.01  | Retrieve address PnL data                  |
| `/api/v1/profiler/address/pnl-summary`                  | $0.01  | Get Address PnL Summary Data               |
| `/api/v1/profiler/address/related-wallets`              | $0.01  | Get Address Related Wallets Data           |
| `/api/v1/profiler/address/transactions`                 | $0.01  | Get Address Transactions Data              |
| `/api/v1/profiler/dex-trades`                           | $0.01  | Get Wallet DEX Trades                      |
| `/api/v1/profiler/perp-positions`                       | $0.01  | Get Perpetual Positions Data               |
| `/api/v1/profiler/perp-trades`                          | $0.01  | Get Perpetual Trade Data                   |
| `/api/v1/tgm/dex-trades`                                | $0.01  | Get "Token God Mode" (TGM) DEX trades data |
| `/api/v1/tgm/flow-intelligence`                         | $0.01  | Get TGM flow intelligence data             |
| `/api/v1/tgm/flows`                                     | $0.01  | Get TGM flows data                         |
| `/api/v1/tgm/jup-dca`                                   | $0.01  | Get TGM Jupiter DCA data                   |
| `/api/v1/tgm/position-intelligence`                     | $0.01  | Get TGM position intelligence data         |
| `/api/v1/tgm/token-information`                         | $0.01  | Get TGM token information data             |
| `/api/v1/tgm/token-ohlcv`                               | $0.01  | Retrieve token OHLCV candle data           |
| `/api/v1/tgm/transfers`                                 | $0.01  | Get TGM transfers data                     |
| `/api/v1/tgm/who-bought-sold`                           | $0.01  | Get TGM who bought/sold data               |
| `/api/v1/token-screener`                                | $0.01  | Retrieve token screener data               |
| `/api/v1/transaction-with-token-transfer-lookup`       | $0.01  | Get Transaction with Token Transfer Lookup |
