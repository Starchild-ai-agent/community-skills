---
name: "@1365/xfree02"
description: Query sponsored Nansen on-chain intelligence endpoints through an open, no-API-key gateway. No wallet, no signup, no signature required from the caller.
author: starchild
version: 1.1.1
tags: [nansen, onchain, analytics, sponsored, open]
---

# xfree02 — Sponsored Nansen Skill

A CLI for querying Nansen on-chain intelligence endpoints through a fully open
gateway. **No API key, no wallet, no signup, no signature.** A sponsor pays the
upstream cost on behalf of callers, subject to daily quotas and a campaign-wide
budget ceiling.

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
python3 skills/xfree02/scripts/xfree02.py call /api/v1/chains/chain-rank
```

Setting `XFREE02_API_KEY` is optional. When set to a recognised key, the call is
billed against that key's own quota bucket instead of the anonymous IP bucket.
An unrecognised key is silently ignored — the gateway never returns 401.

## Campaign

This is a time-boxed sponsored campaign, not a permanent free service.

- Total campaign budget: **$100** (10000 cents), a cumulative hard ceiling that
  does **NOT** reset daily.
- Campaign ends: **2026-08-14T23:59:59Z**. After that instant, every sponsored
  call returns HTTP `402 campaign_ended`.
- When the $100 is spent, calls return HTTP `402 campaign_budget_exhausted`.
- Both responses include `direct_url` pointing at the upstream endpoint so the
  caller can pay for it themselves.
- Check live status via `GET /health` (below) — it reports
  `campaign_budget_usd`, `campaign_spent_usd`, `campaign_remaining_usd`, and
  `campaign_active`.

## Environment variables

| Variable           | Required for          | Default                                              |
|--------------------|-----------------------|------------------------------------------------------|
| `XFREE02_BASE_URL` | all subcommands       | `https://1365-xfree02-gateway.community.iamstarchild.com` |
| `XFREE02_API_KEY`  | optional — only for a dedicated quota bucket | — (omit for anonymous access)         |

Both variables are optional. `XFREE02_BASE_URL` defaults to the public gateway
above. `XFREE02_API_KEY` is only needed if you want a caller's spend to be
tracked under a specific key rather than the client's IP.

## Direct HTTP (no CLI)

The gateway is plain HTTP. All endpoints are keyless.

- `GET https://1365-xfree02-gateway.community.iamstarchild.com/health` —
  status + live budget (per-caller quota, global quota, campaign spend
  remaining, campaign end time, `campaign_active`).
- `GET https://1365-xfree02-gateway.community.iamstarchild.com/catalog` —
  all **54** endpoints; each entry has keys: `path`, `price_usd`,
  `body_source`, `required_fields`, `example_body`, `label`, `sponsored`. This
  is how you discover a valid request body without the CLI.
- `POST https://1365-xfree02-gateway.community.iamstarchild.com/v1{path}` —
  the sponsored call. Every Nansen endpoint is POST; `GET` on a POST path
  returns HTTP `405`.

## Subcommands

The script ships inside this skill at `scripts/xfree02.py`. It is a plain
Python 3 script with no dependencies beyond the standard library; there is no
PATH shim — invoke it as `python3 skills/xfree02/scripts/xfree02.py <subcommand> ...`.

### `catalog`

List available endpoints as a markdown table.

```bash
python3 skills/xfree02/scripts/xfree02.py catalog --sponsored-only --max-price 0.01
```

### `show`

Print the required fields, all fields, and example body for one endpoint.

```bash
python3 skills/xfree02/scripts/xfree02.py show /api/v1/perp-screener
```

### `call`

POST to `{XFREE02_BASE_URL}/v1{path}` with a JSON body. If neither `--body` nor
`--body-file` is given, the endpoint's `example_body` from the catalog is used
automatically. Some endpoints require concrete `from` / `to` dates; run
`show <path>` for the required fields rather than guessing.

```bash
python3 skills/xfree02/scripts/xfree02.py call /api/v1/chains/chain-rank
```

On success the JSON body is printed to stdout and a one-line footer with
`x-sponsored-cents` / `x-caller-remaining-cents` is printed to stderr.

### `health`

GET `{XFREE02_BASE_URL}/health` and print the JSON response. No key required.
Example response (live):

```json
{
  "ok": true,
  "sponsored_endpoints": 30,
  "per_payer_cents_day": 50,
  "global_cents_day": 5000,
  "auth": "open",
  "api_key_required": false,
  "anonymous_quota": "per client IP",
  "max_calls_per_caller_per_day": 50,
  "max_calls_per_day_total": 5000,
  "campaign_budget_usd": 100.0,
  "campaign_spent_usd": 0.13,
  "campaign_remaining_usd": 99.87,
  "campaign_end_utc": "2026-08-14T23:59:59Z",
  "campaign_active": true,
  "dry_run": false
}
```

## All endpoints are POST

Every endpoint in the Nansen catalog is a POST request. The `call` subcommand
always issues a POST, even if the body is empty.

## Sponsorship model

- The **sponsor** pays for every call. The caller needs no wallet and signs
  nothing.
- Each sponsored call costs exactly **1 cent**.
- Two daily quotas are enforced (reset at midnight UTC):
  - **Per-caller** (`per_payer_cents_day`) — **50 cents/day** = 50 sponsored
    calls/day. Keyed by `XFREE02_API_KEY` when set, else by client IP.
  - **Global** (`global_cents_day`) — **5000 cents/day = $50/day** = 5,000
    sponsored calls/day (daily sponsor ceiling).
- See **Campaign** above for the separate, non-resetting $100 cumulative budget
  ending 2026-08-14T23:59:59Z.
- Sponsored endpoints are those with `price_usd <= $0.01` (currently 30 of the
  54 catalog entries).

## Error responses

The gateway returns the following errors. There is **no** `missing_api_key` or `invalid_api_key` response — authentication is always open.

| Status | `error`                    | Meaning                                              |
|--------|----------------------------|------------------------------------------------------|
| 404    | `unknown_endpoint`         | Path not in the catalog.                             |
| 403    | `not_sponsored`            | Endpoint price above the $0.01 sponsor cap.          |
| 402    | `payer_quota_exhausted`    | Per-caller quota (50¢/day) used up.                  |
| 402    | `global_quota_exhausted`   | Sponsor's global quota ($50/day) used up.            |
| 422    | `upstream_error`           | Body was accepted by the gateway but rejected by Nansen (e.g. `Required field 'body -> chains' is missing`). The gateway forwards Nansen's own message in `upstream_body`. **This is the most common failure.** Fix it by supplying the missing field. |
| 402    | `campaign_budget_exhausted` | The $100 total campaign budget is spent. Includes `direct_url`. |
| 402    | `campaign_ended`           | Past 2026-08-14T23:59:59Z. Includes `direct_url`.    |
| 502    | `payment_failed`           | Upstream payment failure.                            |

The `payer_quota_exhausted` and `global_quota_exhausted` 402 responses include `retry_after_utc_date` (next UTC midnight) and `direct_url` (the same endpoint on the Nansen proxy where you can pay yourself).

**FAILED CALLS ARE NOT CHARGED.** Any non-2xx response — 404, 403, 422, 502,
and edge timeouts — rolls the reservation back, so the caller's quota and the
campaign budget are refunded automatically. Verified live.

## A warning about `example_body`

The catalog ships an `example_body` for all 54 endpoints and the CLI uses it
automatically when you pass no body. **Some example bodies are incomplete and
still get rejected with 422** — treat `example_body` as a starting point.

Concrete verified case: `/api/v1/token-screener` ships
`example_body: {"chains": ["arbitrum"]}`, but Nansen also requires exactly one
of `timeframe` or `date`, so the bare example returns
`422 upstream_error: Either 'timeframe' or 'date' must be provided`.

Always: read `required_fields` in the catalog (or run `show <path>`) before
relying on `example_body`, and read the 422 `upstream_body` — it names the
missing field precisely.

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
