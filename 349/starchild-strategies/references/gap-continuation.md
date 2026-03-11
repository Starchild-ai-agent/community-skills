# gap continuation

> ⚠️ Before executing any trade: verify order book depth, use limit orders on thin books, verify fills post-trade, and cancel stale orders before retrying.

Intraday strategy that captures trending moves after a large opening gap. Days that open with significant gaps and strong early volume tend to trend more than normal sessions because they often reflect real positioning by funds rather than random noise. Measure gap size, confirm with volume, ride the trend.

## how it works

Define a "gap" as the absolute percentage difference between yesterday's close price and today's open price (or between previous period's close and current period's open for intraday). If the gap exceeds a threshold (e.g., 1.5%) and the first few minutes of trading show volume above average, assume the gap will continue in the same direction (continuation). Enter a position in the direction of the gap (long if gap up, short if gap down). Hold until the trend shows signs of exhaustion, measured by a trailing stop or a time‑based exit.

## intent

"I want to profit from the momentum that follows a significant overnight or intraday gap, assuming institutions are positioning and will push the price further."

## parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `gap_threshold_pct` | Minimum absolute gap size to consider (%) | 1.5 | 0.5-5.0 |
| `volume_multiplier` | Early‑session volume must be this many times the average | 1.5 | 1.2-3.0 |
| `lookback_days` | Days used to compute average volume | 20 | 10-60 |
| `entry_window_minutes` | Minutes after open to confirm volume and enter | 30 | 10-60 |
| `stop_loss_pct` | Initial stop loss from entry price (%) | 1.0 | 0.5-3.0 |
| `trailing_stop_pct` | Trailing stop after favorable move (%) | 0.8 | 0.3-2.0 |
| `max_hold_hours` | Maximum hold time regardless of price | 8 | 2-24 |
| `take_profit_pct` | Static take profit from entry (%) | 3.0 | 1.0-10.0 |
| `use_trailing_only` | Ignore static take profit, only use trailing stop | false | true/false |
| `leverage` | Leverage per position | 3 | 1-5 |
| `max_position_size_pct` | Capital allocated per trade (%) | 20 | 5-30 |
| `timeframe` | Candle timeframe for open/close/volume | 5m | 1m, 5m, 15m, 1h |
| `gap_period` | Period used to define gap (close‑to‑open) | daily | 4h, 1d, 1w |

## entry logic

1. At the start of each new period (defined by `gap_period`), compute gap percentage: `gap_pct = (open_price - previous_close_price) / previous_close_price * 100`.
2. Compute average volume over the last `lookback_days` for the same period's first `entry_window_minutes`.
3. If `abs(gap_pct) >= gap_threshold_pct` and current period's volume in the first `entry_window_minutes` is at least `volume_multiplier` times the average:
   - If `gap_pct > 0` (gap up), enter a long position.
   - If `gap_pct < 0` (gap down), enter a short position.
4. Use `max_position_size_pct` of capital with `leverage`. Place entry order at the current price (market or limit near BBO).
5. Immediately set an initial stop loss `stop_loss_pct` away from entry in the opposite direction.

## exit logic

- **Trailing stop:** Once price moves in favor by at least `trailing_stop_pct`, activate a trailing stop that follows the price by that distance.
- **Static take profit:** If `use_trailing_only` is false and price reaches `take_profit_pct` profit, exit the entire position.
- **Time‑based exit:** If position held longer than `max_hold_hours`, close regardless of profit/loss.
- **Stop loss:** If price hits the initial stop loss (or trailing stop), exit.
- **Volume exhaustion:** If volume dries up significantly (below 50% of average) while price is moving sideways, consider early exit (optional rule).

## risk management

- Max 1 open position per asset at a time. No overlapping gaps on same symbol.
- Stop loss at `stop_loss_pct` limits loss per trade.
- Daily loss limit: 5% of capital (pauses trading for the day).
- Max drawdown: 15% (pauses trading until manual reset).
- Margin ratio minimum 15% (triggers alert).
- Gap must be confirmed by volume; otherwise skip.
- Idempotency lock prevents duplicate entries.

## cycle flow

```
At the start of each gap_period (e.g., daily at 00:00 UTC):
  1. Acquire idempotency lock
  2. Fetch open price, previous close, first entry_window_minutes volume
  3. Compute gap percentage and compare to threshold
  4. Compute average volume for same window over lookback_days
  5. If gap and volume conditions met:
     - Enter long/short with initial stop loss
     - Start monitoring for trailing stop activation
  6. For existing positions:
     - Update trailing stop if applicable
     - Check for static take profit hit
     - Check for stop loss hit
     - Check for max hold time exceeded
     - Close if any exit condition triggered
  7. Save report, release lock
```

## capital requirements

Minimum: $300 (enough for one position with 3x leverage). Recommended: $1,000 for comfortable margin and multiple positions across assets.

Each position uses `max_position_size_pct` of capital (default 20%). At 3x leverage, notional exposure = capital × 0.20 × 3 = 0.60× capital. Keep margin ratio healthy.

## running costs

### Exchange fees

| Fee type | Rate | Per $100 position |
|----------|------|-------------------|
| Entry (market order) | 0.05% | $0.05 |
| Exit (market order) | 0.05% | $0.05 |
| **Round‑trip** | **0.10%** | **$0.10** |

Assuming one trade per day: ~$3/month in fees.

### Funding rates (perpetuals only)

If trading perpetual swaps, funding costs apply every 8 hours.

| Leverage | Capital per position | Notional per position | Monthly funding (0.01%/8h) |
|----------|----------------------|-----------------------|----------------------------|
| 3x | $200 | $600 | $5.40 |
| 5x | $200 | $1,000 | $9.00 |

Monthly funding = ~$5-9 per position.

### Total monthly cost

| Leverage | Fees | Funding | Total | Break‑even return |
|----------|------|---------|-------|-------------------|
| 3x | $2-4 | $5-9 | **$7-13** | **1.0‑1.8% on $1,000** |
| 5x | $2-4 | $9-15 | **$11-19** | **1.4‑2.4% on $1,000** |

**Recommendation:** Start at 3x leverage. Funding costs are manageable, and liquidation risk is lower.

## configuration example

```json
{
  "name": "Gap Continuation",
  "assets": ["BTC", "ETH", "SOL"],
  "parameters": {
    "gap_threshold_pct": 1.5,
    "volume_multiplier": 1.5,
    "lookback_days": 20,
    "entry_window_minutes": 30,
    "stop_loss_pct": 1.0,
    "trailing_stop_pct": 0.8,
    "max_hold_hours": 8,
    "take_profit_pct": 3.0,
    "use_trailing_only": false,
    "leverage": 3,
    "max_position_size_pct": 20,
    "timeframe": "5m",
    "gap_period": "daily"
  },
  "risk": {
    "max_daily_loss_pct": 5,
    "max_drawdown_pct": 15,
    "min_margin_ratio": 0.15,
    "max_positions_per_asset": 1,
    "max_total_positions": 3
  },
  "schedule": {
    "cycle_interval_minutes": 60,
    "gap_period_check_offset_minutes": 5
  },
  "flags": {
    "enabled": true,
    "dry_run": false,
    "notify_on_gap": true,
    "allow_volume_fallback": false
  }
}
```

## what to understand

- This is a momentum strategy. It assumes that gaps caused by institutional positioning will continue in the same direction, at least for a few hours.
- Gaps can also be "filled" (price reverses to close the gap). This strategy bets on continuation, not fill. Be aware of the opposite scenario.
- Volume confirmation is critical: without above‑average volume, the gap might be noise and likely to reverse.
- Works best in trending markets with clear daily ranges. Choppy, range‑bound markets may produce many false signals.
- The strategy is intraday; positions are not held overnight (or across periods). This reduces overnight risk but also limits profit potential.
- Gap definition depends on the period: daily gaps are common in traditional markets; crypto markets may need shorter periods (4h, 1h) because of 24/7 trading.
- Execution must be quick after the gap is confirmed; entering too late may capture only the tail end of the move.
- Trailing stops lock in profits while letting winners run. Adjust the trailing distance based on volatility.
- Funding rates can erode profits on perpetual swaps. Consider using futures with expiry if available.
- Backtest across different gap thresholds and volume multipliers to find optimal values for each asset.