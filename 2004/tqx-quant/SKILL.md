---
name: "@2004/tqx-quant"
version: 2.0.0
description: |
  TQX (tqx.trade) HK/US stock quant workflow via tqx-cli: cross-sectional factor analysis, event-driven strategy backtests on the panda_backtest engine, and agent-driven automated paper trading.

  Use when the user wants to run factor IC/IR analysis, backtest a Python trading strategy on Hong Kong or US stocks, or set up agent-automated trading (e.g. "backtest a moving-average strategy on AAPL", "analyze a momentum factor on HK stocks", "let the agent trade my paper account").
author: starchild-2004
tags: [quant, backtest, factor-analysis, stocks, tqx, trading]
---

# TQX Quant — Factor Analysis & Strategy Backtest

TQX (https://www.tqx.trade) is a HK/US stock quant platform. This skill drives it through the official `tqx-cli` pip package. Everything below was verified end-to-end against the live service.

**Docs routing:** TQX maintains official online skill docs — treat those as the source of truth for the full API surface; this skill adds the verified onboarding flow, working templates, and a failure-mode table that the official docs do not cover. (Official doc links: see tqx.trade — the site is a JS SPA, so if `web_fetch` returns empty content, fall back to the reference material in this skill.)

## User onboarding (first-time setup, ~3 minutes)

1. **Register** at https://www.tqx.trade (email signup). A PAPER (simulation) account is provisioned automatically — all workflows below are safe to run on it.
2. **Collect credentials securely**: agents must use `request_env_input` for `TQX_EMAIL` and `TQX_PASSWORD` — never ask for credentials in chat.
3. **Install + login + verify**:

```bash
pip install tqx-cli
tqx-cli login --email "$TQX_EMAIL" --password "$TQX_PASSWORD"
tqx-cli --json balance        # non-error response = onboarding complete
```

Token is cached in `~/.tqx/config.yaml`.

4. **First quick win** (recommended demo): run the "5d momentum" factor analysis from §1 below — completes in ~1–2 min and produces IC/IR/Sharpe numbers you can show immediately.

**⚠️ Token expiry gotcha (verified):** both accessToken AND refresh_token can expire together. Do NOT only match one specific error string — re-login on ANY response containing `LOGIN_REQUIRED`, `均已失效`, or `Please log in to continue`. A strict matcher silently fails and every later call returns auth errors.

## CLI command map

```
factor_create / factor_run / factor_result / factor_list / factor_delete
strategy_create / strategy_run / strategy_result / strategy_list / strategy_delete
backtest_result   # per-backtest detail: summary/account/position/profit/trade/log sections
workflow_list / workflow_stop / balance
```

Add `--json` for machine-readable output.

## 1. Factor analysis (cross-sectional IC/IR)

```bash
tqx-cli --json factor_create --market us --name "5d momentum" \
  --formula "close/ref(close,5)-1" \
  --start-date 20250101 --end-date 20250701 --group-number 2
tqx-cli --json factor_run <factor_id>          # waits and returns results
```

**Result parsing gotcha:** the result JSON has TWO formats depending on backend version — legacy `nodes[].result_json` and current root-level `factor_analysis`. Handle both. Key metrics: IC mean, IR, t-stat, annualized group returns, Sharpe.

## 2. Strategy backtest (panda_backtest engine)

```bash
tqx-cli --json strategy_create --market us --name "AAPL SMA cross" \
  --code "$(cat strategy.py)" \
  --start-date 20250101 --end-date 20250701 \
  --start-capital 1000000 --commission-rate 0.0003 --slippage 0.001 --frequency 1d
tqx-cli --json strategy_run <strategy_id>
```

### Strategy code contract (ALL verified the hard way)

```python
from panda_backtest.api.stock_us_api import *   # US market — MANDATORY
# HK market: from panda_backtest.api.stock_hk_api import *

def initialize(context):
    # Account ID is per-user — discover it once, do NOT hardcode.
    # The '8888' from CN-market docs does NOT exist for HK/US backtests.
    context.account = list(context.stock_account_dict.keys())[0]
    context.symbol = 'AAPL.US'   # symbol format: TICKER.US / 00700.HK
    context.prices = []
    context.holding = False

def handle_data(context, bar_dict):
    bar = bar_dict[context.symbol]
    # bar CAN be None on some days — unguarded access kills the run (error 10070)
    if bar is None or getattr(bar, 'close', None) is None or bar.close <= 0:
        return
    context.prices.append(bar.close)
    if len(context.prices) < 20:
        return
    s = sum(context.prices[-5:]) / 5
    l = sum(context.prices[-20:]) / 20
    if s > l and not context.holding:
        order_shares(context.account, context.symbol, 500)   # 3 args: account, symbol, qty
        context.holding = True
    elif s < l and context.holding:
        order_shares(context.account, context.symbol, -500)
        context.holding = False
```

Hard rules learned from real failures:

| Symptom | Root cause | Fix |
|---|---|---|
| `禁止使用危险函数 dir()` | Security filter blocks introspection | Never use `dir()`/`eval()`/`exec`; to inspect context, `raise Exception(str(...))` and read the error_detail in run logs |
| `访问了不存在的键` on order | Wrong account ID (e.g. `'8888'`) | Use `list(context.stock_account_dict.keys())[0]` |
| `order_shares() missing 1 required positional argument` | Called with 2 args | Signature is `order_shares(account, symbol, quantity)` |
| `股票X不属于当前股票回测市场` | Wrong symbol suffix | US = `TICKER.US`, HK = `XXXXX.HK`; `.O`/`.N`/bare tickers are rejected |
| Backtest SUCCESS but 0 trades, `标的不在当前回测数据集内` | Date range beyond ingested market data (recent months may not be loaded even though the benchmark series exists) | Shift the window earlier (e.g. use last year's range); verify trades>0 in the `trade` section before trusting metrics |
| `frequency` rejected | Only `1d` and `1M` are valid | — |

### Reading results

`strategy_run`/`strategy_result` returns run status + node outputs. For full detail, extract the backtest id from run logs (`BacktestNodeIdentifier:` line) or node output, then:

```bash
tqx-cli --json backtest_result <backtest_id> --section summary   # profit, alpha, beta, sharpe, IR
tqx-cli --json backtest_result <backtest_id> --section trade     # ⚠️ always check trades executed
tqx-cli --json backtest_result <backtest_id> --section log       # per-order rejection reasons
```

**A run can report SUCCESS with zero trades** (orders silently rejected day by day). Always confirm the `trade` section is non-empty before reporting performance numbers.

### Debugging failed runs

Error details are NOT in the top-level status — fetch run logs and read `error_detail`, which includes the exact strategy line number and exception message:

```python
from tqx_cli.config import load_config
from tqx_cli.auth import require_login
from tqx_cli.workflow import get_run_logs
cfg = load_config(); token, uid, _ = require_login(cfg, cfg.get("_config_path"))
for l in get_run_logs(cfg, token, uid, run_id).get("logs") or []:
    if l.get("error_detail"): print(l["error_detail"])
```

## Cost & pacing

Backtests are billed in TQX compute credits (`tqx-cli balance`). A 6-month daily-frequency single-stock backtest takes ~2 minutes wall time. Poll `strategy_result` every 3s; don't fire concurrent runs of the same workflow.

## 3. Templates (copy-paste starting points)

### T1 — Momentum factor (cross-sectional, whole market)

```bash
tqx-cli --json factor_create --market us --name "5d momentum" \
  --formula "close/ref(close,5)-1" \
  --start-date 20250101 --end-date 20250701 --group-number 5
```

Other verified formulas: mean reversion `-(close/ref(close,5)-1)`, volume surge `volume/mean(volume,20)`.
Factor mode is whole-market cross-sectional only (`--market hk|us`) — it CANNOT target one stock; for single-stock questions use a strategy backtest (T2).

### T2 — Single-stock backtest (SMA cross on AAPL)

Use the strategy code contract in §2 verbatim — it IS the template. Change `context.symbol` and the signal logic only. Keep the None-bar guard and dynamic account discovery.

### T3 — Agent-driven automated trading loop (paper account)

Pattern verified over a 10-round live run (~21 min, end-to-end):

```
loop every N minutes:
  1. fetch live positions + account state
  2. compute signal (factor value or strategy rule)
  3. decide: buy / sell / hold  ← agent reasoning step
  4. place order (paper account, small fixed qty during development)
  5. journal the decision: {ts, reasoning, tool_calls, params, result, position_delta}
```

Hard rules for automation:
- **PAPER account only** until the user explicitly approves real trading; cap order size during development.
- **Journal every decision** (JSONL is enough) — users must be able to audit why each trade happened.
- **Re-login on ANY auth-ish error string** (see token gotcha above); a mid-loop token expiry must self-heal, not kill the loop.
- **Check compute balance before each backtest-class call** to avoid silent overdraft.

### T4 — Studio architecture blueprint (optional companion UI)

If the user wants a dashboard on top, the layered split that works:
- **UI layer**: expose only high-frequency params (formula, market, date range, group count, rebalance period, factor direction) + account switcher + NAV curve + decision timeline.
- **Agent layer**: everything complex (custom Python strategy code, stock pools, commission/slippage, execution) goes through conversation — the agent has the full CLI surface, the UI does not need it.
- **Audit layer**: decision journal + backtest history persisted to disk (`index.json` + per-run JSON), each record tagged with source = manual | agent, loadable and comparable.
