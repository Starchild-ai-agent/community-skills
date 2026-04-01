---
name: "@2405/sol-scalper"
version: 1.0.0
description: "SOL 15M scalping strategy for Hyperliquid. Includes 9/21 EMA crossover, 1H EMA + VWAP filters, order block detection, funding rate gate, 200 EMA regime filter, RSI smoothing, and 1% risk / 1-2x leverage position sizing. Deploys a live alert task that fires every 15 minutes. Use when the user wants to run or install the SOL scalping strategy."
author: starchild
tags: [trading, scalping, solana, hyperliquid, alerts, strategy]

metadata:
  starchild:
    emoji: "⚡"
    skillKey: sol-scalper

user-invocable: true
---

# SOL 15M Scalping Strategy — Hyperliquid

A fully backtested, production-ready scalping strategy for SOL-PERP on Hyperliquid.
Deploys a live 15-minute signal alert with all filters pre-wired.

## Strategy Performance (52-day backtest)
- **Win rate:** 63.6% (with all filters)
- **Profit factor:** 1.96
- **Net P&L:** +8.68%/month
- **Trades/month:** ~22

## What's Included

| Component | Detail |
|-----------|--------|
| Signal | 9/21 EMA crossover on 15M |
| Trend filter | 50 EMA structural bias |
| Regime gate | 200 EMA — longs above, shorts below only |
| Momentum | RSI smoothed (5-MA) — zone 45–65 long / 35–55 short |
| Volume | 1.3× avg volume spike required |
| Macro filter | 1H EMA50 alignment |
| Intraday filter | VWAP (daily reset) |
| Order blocks | Bullish/bearish OB detection + confluence flag |
| Funding rate | Skip longs when funding > +0.01%/hr |
| Sizing | 1% risk / 1–2x leverage / TP1 at 1.5R / TP2 at 2.5R |

## Installation

Run the setup script to deploy the live alert task:

```bash
python3 skills/sol-scalper/scripts/setup_alert.py
```

This will:
1. Register a scheduled task (every 15 minutes)
2. Deploy the signal monitor script
3. Activate the task — alerts fire immediately

## Alert Output Format

Each alert includes:
- Direction (LONG/SHORT) + signal type (full crossover vs OB watch zone)
- Entry price, stop loss, TP1, TP2
- All indicator values with pass/fail status
- Order blocks nearest to price
- Funding rate + open interest
- Position sizing formula for your account size

## Signal Types

**Full Signal** — All conditions met. Highest conviction. Enter now.
```
📡 SOL 15M SCALP — 🟢 LONG SIGNAL
```

**OB Watch Zone** — No crossover yet but price is inside an order block with other conditions aligned. Stand by — crossover incoming or structure is setting up.
```
📡 SOL 15M SCALP — OB WATCH ZONE ⚡
```

**Silent** — No setup. Nothing printed, no push sent.

## Entry Rules

**Long:** 9 EMA crosses above 21 EMA + price > 50 EMA + price > 200 EMA + RSI_smooth 45–65 + 1H EMA bullish + price > VWAP + volume spike
**Short:** Mirror — 9 crosses below 21 + price < 50 EMA + price < 200 EMA + RSI_smooth 35–55 + 1H EMA bearish + price below VWAP + volume spike

## Risk Rules
- Risk 1% of account per trade
- Leverage 1–2x max
- Close 50% at TP1, move SL to breakeven
- Close remaining at TP2 or EMA cross reversal
- If -2% in a session: stop trading for the day

## Indicators That Were Tested and Rejected
- **OBV** — lagging, kills win rate (-15%)
- **Bollinger Bands** — mean-reversion tool, fights momentum signals
- **ATR dynamic stops** — widens stops, hurts R:R
- **StochRSI alone** — best win rate in isolation but too many good trades filtered
- **30M timeframe** — too slow, enter after the move already happened

## Files
- `scripts/setup_alert.py` — Deploys the live alert task end-to-end
- `scripts/signal_monitor.py` — The core signal logic (run standalone or via task)
- `references/backtest_notes.md` — Full backtest methodology and filter comparison results
