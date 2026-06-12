---
name: "@5312/fvg-delta-crypto-engine-build"
version: 6.0.0
description: "Builds and app/bot to print Crypto Futures Signals based on a Strategy."
---

# FVG-Delta Crypto Signal Engine v6.0

A production FastAPI service that scans MEXC UST-M perpetual futures on **closed
15-minute candles**, runs a strict lock-forward Smart-Money-Concept (SMC) staged
state machine, draws annotated chart screenshots, sends per-trade Telegram alerts,
and serves a live dashboard with an in-memory Trade History. Everything lives in
`assets/app.py`; the rest is config, docs, and entrypoints.

## The strategy — five locked stages
Each stage is searched ONCE and its bar index is stored; stages only advance, hard-
invalidate, or expire. Never skip or regress.

0. **Zone** — a clean impulse leaves an FVG. A valid impulse is a tight burst of
   **≥3 consecutive same-direction candles** that *creates* the FVG and never
   re-enters it (rejects staggered/cluttered legs).
1. **First liquidity + BoS** — the first retracement (one candle closing past the
   immediate impulse candle's open, OR a 2+ candle pullback) sets the liquidity
   line. Hard rules: a **gap** must exist between that line and the FVG (it may
   never rest on the FVG edge), and **BoS sits above liquidity for longs / below
   for shorts**. A BoS *close* through the impulse wick extreme confirms Stage 1.
2. **Sweep** — price breaks and CLOSES past the first liquidity, into the gap.
3. **FVG interaction** — price reaches the FVG. A wick THROUGH that closes back
   inside is still valid; only a CLOSE beyond the FVG invalidates.
4. **Verified entry** — an opposite-direction confirmation candle (strong body or
   long-wick rejection + opposite close). SL anchors beyond the interaction wick
   (breathing room), TP1 = midpoint, TP2 = max(3R, resting liquidity).

## Automatic leverage
`leverage = round_to_5(LEV_TARGET_SL_LOSS_PCT / stop_distance_%)`, clamped to
`[LEV_MIN, LEV_MAX]` (20–50) and the pair's exchange max. Default target = 50% of
margin at SL. Wider stop → lower leverage. TP is uncapped (rides TP1/TP2).

## Per-trade Telegram lifecycle
A confirmed Stage-4 trade emits its own alert chain, each fired once on candle
close: **Entry Confirmed → TP1 Hit** (close 50% + move SL to break-even) **→ SL Hit
/ TP2 Hit / Break-Even Close**. Only terminal Stage-4 outcomes reach Trade History;
Stage 1–3 invalidations are removed beforehand.

## Universe (why majors show up)
`load_symbols` ranks the MEXC perp universe by 24h quote turnover (`amount24`) via
`/contract/ticker` and keeps the top `UNIVERSE_TOP_N`, so BTC/ETH/SOL/XRP lead.
Tokenized equities/commodities/indices are excluded (`UNIVERSE_EXCLUDE` + the
`UNIVERSE_EXCLUDE_CONTAINS="STOCK"` substring rule for the xStock family).

## Run it
```bash
# 1. credentials (never paste keys in chat — use the secure env flow)
cp .env.example .env   # set TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID
# 2. local
bash assets/run_one_shot.sh
# 3. docker / Hugging Face Spaces (Docker SDK)
docker build -t fvg-delta assets/ && docker run -p 7860:7860 --env-file .env fvg-delta
```
Endpoints: `/` (dashboard), `/health`, `/api/state`, `/api/chart.png?symbol=BTC_USDT`.
Without Telegram creds the UI still runs; alerts are skipped and logged.

## Tuning & gotchas
- All knobs are env vars with production-safe defaults — see
  `assets/VARIABLES_AND_SECRETS_GUIDE.txt` (§14 covers every v6.0 variable).
- Decisions use `bars[-2]` (last CLOSED candle); `bars[-1]` (forming) is never used.
- Cron/weekly times are UTC. Dashboard times render in the viewer's browser zone;
  Telegram uses its own received time (no embedded timezone).
- MEXC sends brotli — keep the `brotli` package installed and send
  `Accept-Encoding: gzip, deflate`.
- Prefer adding new tunables to `CFG` (env override + default) over hard-coding, and
  keep stage strictness intact (sequential, no skipping, close-through = invalidation).

## Files (in `assets/`)
`app.py` (engine), `Dockerfile`, `start.sh`, `run_one_shot.sh`, `preflight_check.py`,
`requirements.txt`, `AGENT.md` (maintainer guide + v6.0 changelog),
`STRATEGY_DETAILED_SPEC.txt`, `VARIABLES_AND_SECRETS_GUIDE.txt`, `README.md`.
Read `assets/AGENT.md` before editing `app.py`.
