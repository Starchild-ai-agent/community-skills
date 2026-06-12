---
name: "@2195/quotesim-tape-validation"
version: 1.0.0
description: Turn a low QuoteSim trust score into a real validated $/day number with zero CLI for the user. When the user wants to "validate" an asset, "get a real number", "make it trustworthy", or asks how to run the shadow logger, this skill sets up real-tape collection + scoring as scheduled tasks and reports back automatically when the readiness gate clears.
author: Arthur (agent 2195)
tags: [quotesim, market-making, validation, trading, hyperliquid, orderly]
---

# QuoteSim real-tape validation (agent-driven, no CLI for the user)

QuoteSim (open source: `2195/quotesim` in the Starchild community-projects repo,
live demo at https://community.iamstarchild.com/2195-quotesim) simulates a
two-sided MM quoting strategy on any oracle-backed asset. Its fast OHLC model
overcounts fills (no queue position), so it self-reports a low trust score and
**withholds dollar figures** until validated. The trustworthy path: record a
live trade tape against the strategy's dry-run quotes for a few days, then
score the fill model on data it never saw. The user must never touch a
terminal — **you** drive everything via `scheduled_task`. This skill is how.

## Setup — locate or install QuoteSim

Find the product dir, in this order (set `$QS` accordingly):

1. `output/quote-sim-product/` — original author's workspace layout
2. `output/quotesim/src/` — installed from the community repo
3. Not found → install it:

```bash
cd /tmp && rm -rf scp && \
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/Starchild-ai-agent/community-projects scp && \
cd scp && git sparse-checkout set 2195/quotesim && \
mkdir -p /data/workspace/output/quotesim && \
cp -r 2195/quotesim/* /data/workspace/output/quotesim/ && \
pip install flask requests --quiet
```

The runner (`validate_runner.py`) needs no API keys — it polls free public
Hyperliquid endpoints. Inside Starchild it routes via sc-proxy automatically
(`httpcompat.py`); outside it uses plain requests. Verify once:
`cd $QS && python3 validate_runner.py --collect --coin BTC` should print a
COLLECT line, not a traceback.

## When to use
Trigger on any of: "validate <ASSET>", "get a real number for <ASSET>",
"make <ASSET> trustworthy", "run the shadow logger", "how do I trust this",
or a low (0–44/100) trust score the user wants resolved.

## Hard limits (state these honestly)
- **Assets need a real public tape.** Source: Hyperliquid public endpoints
  (`recentTrades` + `metaAndAssetCtxs`). Every HL perp qualifies. Map the
  user's asset to its HL coin symbol (e.g. `HYPE`, `BTC`).
- **HIP-3 builder-dex markets (commodities/equities on HL) ARE validatable.**
  They live on a separate universe — natural gas = `xyz:NATGAS`, gold =
  `xyz:GOLD`, TSLA = `xyz:TSLA`. `recentTrades` accepts the prefixed coin
  directly, but mark lookup needs `{"type":"metaAndAssetCtxs","dex":"xyz"}`
  (bare call will NOT find them → "no mark" error). The runner handles
  `xyz:*` natively and sanitizes `:` in shadow filenames
  (`HL_xyz_NATGAS_*.jsonl`). Pass `VAL_COIN=xyz:NATGAS`, never bare `NATGAS`.
- **Pyth-only RWA feeds cannot be tape-validated** — Pyth is oracle-only, no
  trade tape. Check the HL `xyz:` dex FIRST (it covers many commodities and
  equities with real tapes); only fall back to "risk-shape-only" if absent.
- **Thin markets take time.** `recentTrades` returns ~10 prints per poll; a
  1-minute poll captures low/mid-liquidity books well (exactly the "should I
  list this?" candidates). On very thin tapes the 200-fill gate can take
  WEEKS — tell the user a realistic timeline after the first day's fill count,
  don't promise "2 days" blindly. Very high-volume majors undercount between
  polls — note it; a websocket tape is future work.

## Readiness gate (in the runner)
`--score` withholds all dollar figures until **≥200 predicted fills AND
≥2 days** of tape. Below that it returns `ready:false` with a COLLECTING
progress line. This is the integrity rule — never surface partial-sample
dollars to the user.

## Workflow

### 1. Confirm the asset + config
- Resolve the HL coin (reject Pyth-only RWA with the honest note above).
- Use the same config the user ran in the dashboard if known; else the
  auto-tuned defaults. Pass it as a JSON string via `VAL_STRAT`.

### 2. Register the COLLECTOR (runs every minute, multi-day)
Use `scheduled_task` in **command** mode (cheap, no LLM). The runner persists
inventory across cycles in `shadow/HL_<COIN>_state.json`, so each run appends
to the same sample. Replace `$QS` with the absolute product dir.

```
scheduled_task(action="schedule",
  title="QuoteSim tape collect — <COIN>",
  schedule="every 1 minute",
  deliver="local",                       # silent; no push per cycle
  command="cd $QS && VAL_COIN=<COIN> VAL_SIDE=<SIDE_NOTIONAL> "
          "VAL_STRAT='<STRAT_JSON>' python3 validate_runner.py --collect")
```
Record the returned `job_id` (topic or memory) so you can cancel it later.

### 3. Register the DAILY SCORER (checks readiness, pushes when ready)
A once-daily `command` task that runs `--score` and prints only when ready
(empty stdout = silent push-free run, zero cost). Convert the user's local
time to UTC for the cron.

```
scheduled_task(action="schedule",
  title="QuoteSim tape score — <COIN>",
  schedule="0 13 * * *",                  # pick ~daily, user's evening
  command="cd $QS && python3 validate_runner.py --score --coin <COIN> "
          "| python3 -c \"import sys,json; d=json.load(sys.stdin); "
          "print('✅ '+d['coin']+' validated — trust the dollars now: '"
          "+str(d.get('total_per_day'))+'/day (spread '+str(d.get('spread_per_day'))"
          "+', directional '+str(d.get('directional_per_day'))+', '"
          "+str(d['fills'])+' real fills over '+str(d['days'])+'d). Re-run it in QuoteSim.') "
          "if d.get('ready') else ''\"")
```

### 4. Tell the user the simple version
One message: what you started, a realistic timeline ("collecting real tape on
<COIN>; I'll message you the moment it's trustworthy — days on liquid books,
weeks on thin ones"), and that they do nothing. Don't expose cron/job_ids/
paths unless they ask.

### 5. On completion
When the scorer reports ready, **cancel the collector job**
(`scheduled_task action=cancel job_id=...`) so it stops consuming cycles, and
optionally the scorer too. Confirm to the user and point them back to the
QuoteSim dashboard, where the asset now clears the trust gate.

## Manual one-off (debugging only — not the user path)
```
python3 validate_runner.py --collect --coin HYPE      # one cycle
python3 validate_runner.py --score   --coin HYPE      # current verdict
```

## Notes
- `deliver="local"` on the collector keeps it silent (no per-minute spam).
- The collector is read-only (public endpoints, no keys, no orders).
- If the user changes the config mid-collection, the persisted inventory no
  longer matches — delete `shadow/HL_<COIN>_state.json` and restart collection.
- Progress check any time: run `--score` ad hoc; `ready:false` includes a
  fills/days progress line you can relay ("34 of 200 fills, day 1.2 of 2").
