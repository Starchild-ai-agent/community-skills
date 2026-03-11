# volatility breakout

> ⚠️ Before executing any trade: verify order book depth, use limit orders on thin books, verify fills post-trade, and cancel stale orders before retrying.

Strategy that enters trends after periods of compressed volatility. Large directional moves often start when volatility falls to the lowest 20-30% of its historical range. Compressed markets release energy into outsized moves. Uses ATR or Bollinger Band width percentile to detect compression, enters on breakout confirmation.

## how it works

Monitor a single asset's volatility over a lookback period (e.g., 30 days). Calculate a volatility metric such as Average True Range (ATR) or Bollinger Band width (BBW). Compute the percentile of current volatility relative to the historical distribution. When percentile drops below a threshold (e.g., 20%), market is considered "compressed". Wait for a breakout beyond recent high/low with strong volume confirmation, then enter in the breakout direction. Hold until volatility expands beyond a target level or a trailing stop is hit.

## intent

"I want to capture large trending moves that emerge after quiet, low-volatility periods, entering early in the trend with momentum confirmation."

## parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `symbol` | Asset symbol | BTC | Any perp-listed asset |
| `volatility_indicator` | Volatility metric used | atr_percentile | atr_percentile, bbw_percentile |
| `lookback_days` | Days for historical volatility calculation | 30 | 14-90 |
| `compression_threshold` | Volatility percentile threshold to consider compressed (lower = stricter) | 20 | 10-30 |
| `breakout_window` | Lookback bars for recent high/low breakout detection | 20 | 10-50 |
| `breakout_confirmation` | Number of consecutive closes beyond breakout level required | 2 | 1-3 |
| `volume_factor` | Minimum volume ratio vs recent average for confirmation | 1.5 | 1.2-2.0 |
| `leverage` | Leverage per position | 3 | 1-5 |
| `position_size_pct` | Capital allocated per trade (%) | 20 | 10-30 |
| `trailing_stop_atr` | Trailing stop distance in ATR multiples | 2.0 | 1.5-3.0 |
| `target_expansion_atr` | Target volatility expansion multiple (exit when volatility > target) | 3.0 | 2.0-4.0 |
| `max_hold_days` | Maximum days before forced exit | 30 | 14-60 |
| `timeframe` | Candle timeframe for analysis | 4h | 1h, 4h, 1d |
| `atr_period` | Period for ATR calculation (if using atr_percentile) | 14 | 7-21 |
| `bb_period` | Period for Bollinger Bands (if using bbw_percentile) | 20 | 14-30 |
| `bb_std` | Standard deviations for Bollinger Bands | 2.0 | 1.5-2.5 |

## entry logic

1. Compute volatility metric (ATR or Bollinger Band width) over the last `lookback_days`. Calculate percentile of current value relative to historical distribution.
2. If percentile <= `compression_threshold`, market is compressed. Wait for breakout signal.
3. Breakout signal: price closes above highest high of last `breakout_window` bars (for long) or below lowest low (for short). Requires `breakout_confirmation` consecutive closes beyond the level.
4. Volume confirmation: volume of breakout bar(s) must be at least `volume_factor` times the average volume of the last `breakout_window` bars.
5. If both conditions satisfied, enter long (if breakout upward) or short (if breakout downward) with `position_size_pct` capital at `leverage`.
6. Place initial stop loss at entry price ± `trailing_stop_atr` × current ATR.

## exit logic

- Primary exit: volatility expands beyond `target_expansion_atr` × entry volatility (ATR). Exit when current ATR > entry ATR × target_expansion_atr.
- Trailing stop: update stop to entry price ± `trailing_stop_atr` × current ATR, locking in profit. Exit when stop triggered.
- Time‑based exit: if position held longer than `max_hold_days`, close regardless of profit/loss.
- Emergency exit: if volatility percentile rises above 70% (sudden spike) while in trade, exit to avoid whipsaw.

## risk management

- Max 1 position per symbol (no overlapping entries).
- Stop loss at `trailing_stop_atr` × current ATR limits loss per trade.
- Daily loss limit: 5% of capital (pauses trading for the day).
- Max drawdown: 15% (pauses trading until manual reset).
- Margin ratio minimum 15% (triggers alert).
- Breakout confirmation reduces false signals but may delay entry.
- Idempotency lock prevents duplicate entries.

## cycle flow

```
Every 4 hours:
  1. Acquire idempotency lock
  2. Fetch 4h candles for symbol
  3. Compute volatility percentile and breakout status
  4. Check existing position:
     - Update trailing stop based on current ATR
     - Exit if stop loss triggered
     - Exit if target volatility expansion reached
     - Exit if max hold days exceeded
     - Exit if emergency volatility spike detected
  5. If no position and market compressed:
     - Check breakout conditions (price, confirmation, volume)
     - If satisfied, enter long/short with initial stop
  6. Set stop‑loss order
  7. Save report, release lock
```

## capital requirements

Minimum: $300 (enough for one position with 3x leverage). Recommended: $1,000 for comfortable margin and multiple positions across different symbols.

Each position uses `position_size_pct` of capital (default 20%). At 3x leverage, notional exposure = capital × 0.20 × 3 = 0.6× capital. Keep margin ratio healthy.

## running costs

### Exchange fees

| Fee type | Rate | Per $100 position |
|----------|------|-------------------|
| Entry (market order) | 0.05% | $0.05 |
| Exit (market order) | 0.05% | $0.05 |
| **Round‑trip per trade** | **0.10%** | **$0.10** |

Assuming one trade per week: ~$0.40/month.

### Funding rates (the real cost)

Perpetual swaps charge funding every 8 hours. Directional positions pay/receive funding depending on market conditions.

| Leverage | Capital per trade | Notional per trade | Monthly funding (0.01%/8h) |
|------------------|-----------------|------------------|----------------------------|
| 3x | $200 | $600 | $5.40 |
| 5x | $200 | $1000 | $9.00 |

Monthly funding = ~$5‑$9 per position.

### Total monthly cost

| Leverage | Fees | Funding | Total | Break‑even return |
|----------|------|---------|-------|-------------------|
| 3x | $0.4 | $5-9 | **$5.4-9.4** | **0.8‑1.4% on $1,000** |
| 5x | $0.4 | $9-14 | **$9.4-14.4** | **1.2‑1.9% on $1,000** |

**Recommendation:** Start at 3x leverage. Funding costs are moderate, liquidation risk manageable. Increase leverage only after confirming breakout reliability.

## configuration example

```json
{
  "name": "Volatility Breakout",
  "symbols": ["BTC", "ETH", "SOL"],
  "parameters": {
    "volatility_indicator": "atr_percentile",
    "lookback_days": 30,
    "compression_threshold": 20,
    "breakout_window": 20,
    "breakout_confirmation": 2,
    "volume_factor": 1.5,
    "leverage": 3,
    "position_size_pct": 20,
    "trailing_stop_atr": 2.0,
    "target_expansion_atr": 3.0,
    "max_hold_days": 30,
    "timeframe": "4h",
    "atr_period": 14,
    "bb_period": 20,
    "bb_std": 2.0
  },
  "risk": {
    "max_daily_loss_pct": 5,
    "max_drawdown_pct": 15,
    "min_margin_ratio": 0.15,
    "emergency_volatility_percentile": 70
  },
  "schedule": {
    "cycle_interval_minutes": 240,
    "volatility_recalc_hours": 24
  },
  "flags": {
    "enabled": true,
    "dry_run": false,
    "allow_short": true,
    "notify_on_breakout": true
  }
}
```

## what to understand

- This strategy bets on volatility expansion after compression. It works well in regimes where volatility cycles between low and high.
- False breakouts are common. Using confirmation (multiple closes, volume) reduces false signals but also delays entry, potentially missing early move.
- Volatility percentile threshold of 20% means you'll wait for extremely quiet periods. Patience is required; trades may be infrequent.
- Trailing stop based on ATR adapts to market conditions but may be whipsawed in choppy environments.
- Funding rates can be costly for directional positions. Monitor funding rates for the asset; avoid trading assets with consistently high negative funding.
- Works best with liquid, trending assets (BTC, ETH, SOL). Avoid illiquid altcoins where breakouts may be fake.
- This strategy tends to perform well in trending markets after consolidation; performs poorly in range-bound, choppy markets where breakouts fail repeatedly.