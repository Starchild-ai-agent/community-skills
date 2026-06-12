---
name: "@5326/fvg-delta-forex-engine"
version: 6.0.0
---

# FVG-Delta Forex Signal Engine v6.0

A production FastAPI service that scans the global forex market on **15-minute
candles**, runs a strict lock-forward Smart-Money-Concept (SMC) staged state
machine, and alerts on the late stages. It is the forex evolution of the
FVG-Delta crypto engine — **identical strategy**, refined for forex speed and
mechanics.

## What it scans

A curated, liquidity-screened universe (no illiquid exotics, no single stocks),
defined in `assets/instruments.py`:
- FX majors & minors (EUR/USD, GBP/JPY, EUR/GBP, …)
- Metals (XAU/USD gold, XAG/USD silver)
- Energy (WTI, Brent, NatGas)
- Indices (NAS100, S&P500, US30, DAX, FTSE100, Nikkei225, DXY)

Data is pulled from Yahoo Finance via `yfinance` — real 15m OHLC, no API key.

## The strategy (unchanged from crypto)

Stage 0 FVG/impulse context → Stage 1 first-liquidity lock + BoS close → Stage 2
liquidity sweep (close-through) → Stage 3 FVG interaction → Stage 4
opposite-direction confirmation = verified entry. Lock-forward: each transition
is searched once and locked; stages never silently regress.

## Forex refinements

- **Risk model:** pips / lot (default micro `0.01`) / `LEVERAGE` (default `500`,
  margin only) / required margin / $ risk-reward (P/L = pips × pip-value × lots).
  Spread-aware. Replaces the crypto ROI/auto-leverage model.
- **Intrabar Stage 3 + exits:** FVG touch registers on the forming candle; SL /
  TP / Break-even fire intrabar. Structural stages (1/2) stay close-based.
- **No TTL on Stage 3/4:** they resolve only on real triggers (Stage 3: close
  through FVG; Stage 4: SL / TP / Break-even).
- **Market clock:** Open/Closed badge, weekend + holidays, browser-tz countdown.
- **News radar:** ForexFactory weekly feed graded Safe / Caution / No-Trade with
  a short label + countdown, shown on the dashboard and inside Telegram alerts.

## Run it

```bash
# 1. credentials (never paste keys in chat — use the secure env flow)
cp .env.example .env   # set TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID; optional LEVERAGE / LOT_SIZE
# 2. local
bash assets/run_one_shot.sh
# 3. docker / Hugging Face Spaces (Docker SDK)
docker build -t fvg-forex assets/ && docker run -p 7860:7860 --env-file .env fvg-forex
```
Endpoints: `/` (dashboard), `/health`, `/api/state`, `/api/market`, `/api/news`,
`/api/chart.png?symbol=EUR/USD`. Without Telegram creds the UI still runs; alerts
are skipped and logged.

## Tuning & gotchas

- All knobs are env vars with production-safe defaults — see
  `assets/VARIABLES_AND_SECRETS_GUIDE.txt`.
- Structural stages (1/2) decide on the last CLOSED candle (`bars[-2]`); Stage-3
  touch and SL/TP/BE use the forming candle (`bars[-1]`) when `INTRABAR_*` is on.
- Cron/weekly times are UTC. The dashboard renders all times + countdowns in the
  viewer's browser timezone.
- `yfinance` needs outbound access to Yahoo; the news radar needs ForexFactory.
  Both are keyless. If a feed is unreachable the engine degrades gracefully.
- Pip values are broker-approximate defaults (override via `FVG_PIPVAL_<PAIR>`).

## Files (in `assets/`)

`app.py` (engine), `instruments.py`, `market_clock.py`, `economic_calendar.py`,
`risk_forex.py`, `Dockerfile`, `start.sh`, `run_one_shot.sh`, `preflight_check.py`,
`requirements.txt`, `AGENT.md` (maintainer guide), `STRATEGY_DETAILED_SPEC.txt`,
`VARIABLES_AND_SECRETS_GUIDE.txt`, `README.md`. Read `assets/AGENT.md` before
editing `app.py`.
