---
name: "@1365/xfree02"
version: 1.0.0
description: >-
  On-chain intelligence from Nansen — smart money flows, wallet PnL, token and
  perp screeners, prediction markets, historical holder data — with no Nansen
  account, no API key and no subscription. 54 endpoints reachable through the
  Starchild x402 marketplace, each priced from $0.01 in USDC and paid per call
  from the user's own wallet. Ships a catalog of every endpoint with its price
  and request body, so no paid call is ever wasted guessing the payload.
  Use when the user asks about smart money, whale or wallet activity, token
  holders, on-chain flows, perp leaderboards, or Nansen data of any kind.
author: starchild
tags:
  - nansen
  - x402
  - onchain
  - smart-money
  - wallet-analytics
  - usdc
  - crypto
delivery: script
metadata:
  starchild:
    emoji: 🔎
    skillKey: xfree02
    requires:
      bins:
        - python3
---

# xFREE02 — on-chain intelligence, no API key

Nansen sells 54 endpoints on the Starchild marketplace as pay-per-use x402.
There is no key and no signup: you sign a USDC payment per call and the gateway
returns the data. Paying is the easy part — **knowing what to send is the hard
part**, and that is what this skill carries.

| | |
|---|---|
| Service | `cdp-nansen` · `f17f7f91-a576-407c-bead-1eea320f7523` |
| Prices | 30 × $0.01 · 19 × $0.05 · 4 × $0.25 · 1 × $2.00 |
| Rails | Base `eip155:8453` · BSC `eip155:56` · X Layer `eip155:196` · Solana |
| Method | every endpoint is **POST** |
| Who pays | **the user's own wallet** — see Cost discipline |

## 1. Start with the catalog — it is free

`references/catalog.json` maps all 54 endpoints to price, required fields and a
request body. Reading it costs nothing. Guessing costs money.

```bash
python3 skills/xfree02/xfree02.py catalog --search "smart money"
python3 skills/xfree02/xfree02.py catalog --max-price 0.01
python3 skills/xfree02/xfree02.py show /api/v1/perp-screener
```

`body_source` says how much to trust the body:

| value | meaning | count |
|---|---|---|
| `generated` | built from Nansen's documented schema, required fields only | 44 |
| `none` (shown as `GAP`) | docs carry no schema — **you must pass `--json`** | 10 |

## 2. Pay and call

```bash
python3 skills/xfree02/xfree02.py call /api/v1/perp-screener \
  --json '{"date":{"from":"2026-08-01","to":"2026-08-12"}}'
```

Omit `--json` and the catalog example body is used. The spend cap defaults to
that endpoint's own listed price, so a call cannot overspend by accident;
raise it with `--max-usd`. Output is one JSON object from the x402 buyer:
`{success, status, paid, network, payer, settlement, body, error}`.

Exit codes: `0` paid & 2xx · `2` preflight blocked, nothing signed ·
`3` the `x402` skill is missing · `1` other failure.

## 3. Cost discipline — this spends real money

- **Confirm with the user before the first paid call of a session**, and always
  before `/api/v1/agent/fast` ($2.00 — two hundred times the cheap endpoints).
  Never put it in a loop.
- Scheduled/batch use: multiply price × runs/day and state the monthly figure
  before activating.
- The wallet needs USDC on one of the four rails. An empty wallet produces a
  402 loop, not a crash — fund via the `wallet` or `across-bridge` skills.

## 4. Known behaviour (measured, not assumed)

- Nansen **validates the body before settling**: a 422 costs $0. Malformed
  payloads are cheap here — the opposite of some x402 sellers.
- Bodies are **schema-derived and not yet confirmed against live calls.** Treat
  the first call to any endpoint as the verification.
- Five bodies are an empty `{}` because the schema declares no required fields;
  and some `required` objects do not mark their own sub-fields required — e.g.
  `perp-screener` yields `{"date": {}}` but almost certainly wants
  `from`/`to`. **On a 422, fill in the sub-fields and correct the entry in
  `references/catalog.json`** so the next agent doesn't repeat it.
- The 10 `GAP` endpoints are genuine doc gaps, not parser failures:
  `chains/chain-rank`, `nansen-score/top-tokens`, six `prediction-market/*`,
  `smart-money/pnl-leaderboard`, `v1beta1/tgm/historical-token-ohlcv`.

## 5. Dependency

Payment is delegated to the `x402` skill (`skills/x402/scripts/buy.py`), which
must be installed and set up once per machine:

```bash
bash skills/x402/setup.sh
```

Without it, `call` exits 3 with an explicit message. `catalog` and `show` work
regardless — they are offline reads.

## 6. Rebuilding the catalog

When Nansen updates its docs:

```bash
curl -sS -o output/nansen/llms-full.txt https://docs.nansen.ai/llms-full.txt
cd output/nansen && python3 build_catalog.py
cp catalog.json CATALOG.md /data/workspace/skills/xfree02/references/
```

`build_catalog.py` is offline and stdlib-only: it segments the docs dump,
matches sections by path (preferring sections that actually carry a schema
block over the pricing table that merely mentions the path), resolves `$ref`
recursively with a cycle guard, and refuses to invent field names — an absent
schema yields `body_source: none`.

## Rules

- Never fabricate a Nansen response. Every number comes from an actual paid call.
- Report the settlement tx hash when asked whether a call was paid.
- Pay the marketplace URL — never a third-party proxy — so the purchase is booked.
- Read the catalog before every call. It is free; the mistake is not.
