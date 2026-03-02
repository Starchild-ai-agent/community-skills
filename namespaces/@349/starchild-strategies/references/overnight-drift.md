# overnight drift

> ⚠️ Before executing any trade: verify order book depth, use limit orders on thin books, verify fills post-trade, and cancel stale orders before retrying.

Strategy that captures the overnight drift effect observed in equity markets, adapted for 24/7 crypto markets by identifying "quiet hours" patterns. In traditional markets, a large portion of long-term returns historically come from close-to-open gaps rather than intraday moves, reflecting overnight information flow and institutional positioning. In crypto, similar patterns occur during low-volume periods (e.g., Asian overnight hours, weekends). Buy near the close of active hours, sell near the open of the next active session.

## how it works

Identify a consistent "quiet period" for a given crypto asset (e.g., 00:00-08:00 UTC for BTC when Asian markets dominate retail flow, or weekends when institutional participation drops). Compute historical returns during that period versus returns during the "active period". If the drift is statistically significant (Sharpe ratio >0.5 over the past 90 days), allocate capital to buy at the start of the quiet period and sell at the end. Use a rolling window to adapt to changing market regimes. Stop loss if intra-quiet-period volatility exceeds threshold.

## intent

"I want to capture the persistent overnight drift effect in crypto markets, betting that price moves during low-volume periods tend to be positive on average due to information accumulation and institutional positioning."

## parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `symbol` | Asset symbol | BTC | Any perp-listed asset |
| `quiet_start_utc` | Start of quiet period (UTC hour) | 0 | 0-23 |
| `quiet_end_utc` | End of quiet period (UTC hour) | 8 | 0-23 |
| `lookback_days` | Days for drift calculation | 90 | 30-180 |
| `min_sharpe` | Minimum Sharpe ratio to trade | 0.5 | 0.3-1.0 |
| `position_size_pct` | Capital allocated (%) | 20 | 5-40 |
| `leverage` | Leverage used | 2 | 1-5 |
| `stop_loss_pct` | Intra-period stop loss (%) | 3 | 1-10 |
| `max_hold_hours` | Maximum hours before forced exit | 12 | 8-24 |
| `timeframe` | Candle timeframe for entry/exit | 1h | 1h, 4h |
| `volatility_window` | Rolling window for volatility (hours) | 24 | 12-48 |
| `volatility_threshold` | Max volatility (std dev) to skip trade | 0.02 | 0.01-0.05 |
| `dry_run` | Test without real trades | true | true/false |

## entry logic

1. At `quiet_start_utc` each day, compute historical drift performance:
   - Fetch hourly prices for `symbol` over `lookback_days`.
   - Split each day into quiet period (`quiet_start_utc` to `quiet_end_utc`) and active period (rest).
   - Compute returns during quiet periods only.
   - Calculate Sharpe ratio of those returns (annualized, assuming zero risk-free rate).
2. Check current market conditions:
   - Compute rolling volatility over last `volatility_window` hours (std dev of hourly returns).
   - If volatility > `volatility_threshold`, skip trade (too risky).
3. If Sharpe ratio > `min_sharpe` and volatility check passes:
   - Enter long position at market price with `position_size_pct` capital at `leverage`.
   - Set stop loss at entry price × (1 - `stop_loss_pct` / 100).
4. Record entry timestamp for max hold tracking.

## exit logic

- Primary exit: at `quiet_end_utc`, close the position at market price.
- Stop loss: if price drops below stop loss level during quiet period, exit immediately.
- Time‑based exit: if position held longer than `max_hold_hours`, close regardless of profit/loss.
- Emergency exit: if volatility spikes above `volatility_threshold` after entry, exit early.
- Cancel any open order if not filled within 30 minutes of quiet start.

## risk management

- Max 1 position per symbol at a time (no overlapping quiet periods).
- Stop loss at `stop_loss_pct` limits loss per trade.
- Daily loss limit: 5% of capital (pauses trading for the day).
- Max drawdown: 15% (pauses trading until manual reset).
- Margin ratio minimum 20% (triggers alert).
- Sharpe ratio recalculated daily; stop trading if falls below `min_sharpe` for 5 consecutive days.
- Idempotency lock prevents duplicate entries.

## cycle flow

```
Every hour:
  1. Acquire idempotency lock
  2. Fetch hourly prices for symbol
  3. If current hour == quiet_start_utc:
      - Compute drift Sharpe ratio over lookback_days
      - Compute rolling volatility
      - If conditions met, open long position with stop loss
  4. If current hour == quiet_end_utc:
      - Close any open position for this symbol
  5. Check existing positions:
      - Close if stop loss triggered
      - Close if max hold hours exceeded
      - Close if volatility threshold breached
  6. Save report, release lock
```

## capital requirements

Minimum: $200 (enough for one symbol with 2x leverage). Recommended: $500‑$1,000 for comfortable margin.

Position uses `position_size_pct` of capital (default 20%). At 2x leverage, notional exposure = capital × 0.20 × 2 = 0.4× capital. For one symbol, total notional exposure = 0.4× capital. Keep margin ratio healthy.

## running costs

### Exchange fees

| Fee type | Rate | Per $100 position |
|----------|------|-------------------|
| Entry (market order) | 0.05% | $0.05 |
| Exit (market order) | 0.05% | $0.05 |
| **Round‑trip per trade** | **0.10%** | **$0.10** |

Assuming one trade per day: ~$3/month in fees.

### Funding rates (the real cost)

Perpetual swaps charge funding every 8 hours. Since this is a long-only strategy, you pay funding for the entire position.

| Leverage | Capital | Notional | Monthly funding (0.01%/8h) |
|----------|---------|----------|----------------------------|
| 2x | $100 | $200 | $1.80 |
| 5x | $100 | $500 | $4.50 |

For $500 capital at 2x leverage, monthly funding = ~$9.

### Total monthly cost

| Leverage | Fees | Funding | Total | Break‑even return |
|----------|------|---------|-------|-------------------|
| 2x | $3 | $9 | **$12** | **3.0‑3.4% on $500** |
| 5x | $3 | $22.5 | **$25.5** | **5.7‑6.1% on $500** |

**Recommendation:** Start at 2x leverage. Funding cost is manageable, liquidation risk is low. Increase leverage only after confirming drift persistence.

## configuration example

```json
{
  "name": "Overnight Drift",
  "symbols": ["BTC"],
  "parameters": {
    "quiet_start_utc": 0,
    "quiet_end_utc": 8,
    "lookback_days": 90,
    "min_sharpe": 0.5,
    "position_size_pct": 20,
    "leverage": 2,
    "stop_loss_pct": 3,
    "max_hold_hours": 12,
    "timeframe": "1h",
    "volatility_window": 24,
    "volatility_threshold": 0.02,
    "dry_run": true
  },
  "risk": {
    "max_daily_loss_pct": 5,
    "max_drawdown_pct": 15,
    "min_margin_ratio": 0.20,
    "emergency_volatility_break": 0.03
  },
  "schedule": {
    "cycle_interval_minutes": 60,
    "sharpe_recalc_hours": 24
  },
  "flags": {
    "enabled": true,
    "dry_run": false,
    "allow_weekend_trading": true,
    "notify_on_sharpe_drop": true
  }
}
```

## what to understand

- This strategy exploits a historical anomaly that may disappear if widely known. Backtest thoroughly before deploying live.
- Crypto markets are 24/7, so "overnight" is artificial. The chosen quiet period must align with actual low-volume periods (varies by asset and market cycle).
- Drift can reverse during high-volatility regimes (e.g., macro news, exchange hacks). The volatility filter is essential.
- Funding rates for long positions are a continuous cost; ensure drift returns exceed funding plus fees.
- Execution timing matters: entering/exiting at exact hour boundaries may suffer slippage. Consider using limit orders near the hour.
- Works best with high-liquidity assets (BTC, ETH) where spreads are tight. Avoid illiquid altcoins.
- This strategy tends to perform well in stable, trending markets and poorly during high-volatility, range-bound periods.