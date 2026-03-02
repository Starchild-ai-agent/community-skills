# zscore reversion

> ⚠️ Before executing any trade: verify order book depth, use limit orders on thin books, verify fills post-trade, and cancel stale orders before retrying.

Statistical arbitrage strategy that bets on mean reversion of standardized price spreads between two correlated assets. When the z-score of their normalized spread exceeds 2 standard deviations, expect reversion toward zero. Enter when extreme deviation occurs, exit as spread returns to mean.

## how it works

Select two assets with historically high correlation (rolling correlation >0.8). Compute the spread as log price ratio between the two assets. Standardize the spread over a lookback window to produce a z-score (mean 0, standard deviation 1). When z-score exceeds +2, asset A is expensive relative to B: short A, long B. When z-score falls below -2, asset A is cheap relative to B: long A, short B. Hold until z-score reverts toward zero, then close both legs simultaneously.

## intent

"I want to profit from temporary mispricing between two correlated assets, assuming their spread will revert to its historical mean."

## parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `pair_a` | First asset symbol | BTC | Any perp-listed asset |
| `pair_b` | Second asset symbol | ETH | Any perp-listed asset |
| `correlation_threshold` | Minimum rolling correlation to trade | 0.8 | 0.7-0.95 |
| `lookback_days` | Days for correlation/spread calculation | 30 | 14-60 |
| `z_entry` | Z-score threshold to open a trade | 2.0 | 1.5-3.0 |
| `z_exit` | Z-score target to close a trade | 0.5 | 0.2-1.0 |
| `leverage` | Leverage per leg (each side) | 3 | 1-5 |
| `max_position_size_pct` | Capital allocated per leg (%) | 15 | 5-25 |
| `stop_loss_z` | Stop loss in z-score units | 3.0 | 2.0-4.0 |
| `max_hold_days` | Maximum days before forced exit | 14 | 7-30 |
| `timeframe` | Candle timeframe for prices | 1h | 1h, 4h, 1d |
| `correlation_window` | Rolling window length (days) | 30 | 14-60 |
| `spread_type` | Spread calculation method | log_price_ratio | log_price_ratio, price_ratio, diff |

## entry logic

1. Compute rolling correlation between `pair_a` and `pair_b` over the last `lookback_days`. If correlation < `correlation_threshold`, skip trade.
2. Compute spread as log(price_a) - log(price_b). Compute z-score of spread over same lookback.
3. If z-score > `z_entry` (pair_a expensive relative to pair_b):
   - Short `pair_a` with `max_position_size_pct` capital at `leverage`.
   - Long `pair_b` with same notional size.
4. If z-score < -`z_entry` (pair_a cheap relative to pair_b):
   - Long `pair_a` with `max_position_size_pct` capital at `leverage`.
   - Short `pair_b` with same notional size.
5. Ensure both legs are opened simultaneously (hedged). If one leg fails, cancel the other.

## exit logic

- Primary exit: z-score crosses `z_exit` toward zero (e.g., from +2.5 to +0.4). Close both legs.
- Stop loss: if z-score moves further away beyond `stop_loss_z` (e.g., from +2.5 to +3.5), exit immediately.
- Time‑based exit: if position held longer than `max_hold_days`, close regardless of z-score.
- Emergency exit: if correlation drops below `correlation_threshold` while in trade, exit.

## risk management

- Max 2 concurrent pairs (i.e., 4 total positions). Prevents over‑concentration.
- Stop loss at `stop_loss_z` (e.g., 3.0) limits loss per trade.
- Daily loss limit: 5% of capital (pauses trading for the day).
- Max drawdown: 15% (pauses trading until manual reset).
- Margin ratio minimum 15% (triggers alert).
- Correlation check every hour; exit if correlation breaks down.
- Idempotency lock prevents duplicate entries.

## cycle flow

```
Every hour:
  1. Acquire idempotency lock
  2. Fetch hourly prices for both assets
  3. Compute rolling correlation and spread z‑score
  4. Check existing positions:
     - Close if z‑score crossed exit threshold
     - Close if correlation threshold breached
     - Close if stop loss triggered
     - Close if max hold days exceeded
  5. For each eligible pair (correlation > threshold):
     - If z‑score > entry threshold and no position, open short‑A/long‑B
     - If z‑score < -entry threshold and no position, open long‑A/short‑B
  6. Set stop‑loss orders on both legs
  7. Save report, release lock
```

## capital requirements

Minimum: $500 (enough for one pair with 3x leverage per leg). Recommended: $1,000‑$2,000 for two pairs with comfortable margin.

Each leg uses `max_position_size_pct` of capital (default 15%). At 3x leverage, each leg's notional exposure = capital × 0.15 × 3 = 0.45× capital. For two pairs (four legs), total notional exposure = 1.8× capital. Keep margin ratio healthy.

## running costs

### Exchange fees

| Fee type | Rate | Per $100 leg |
|----------|------|--------------|
| Entry (market order) | 0.05% | $0.05 |
| Exit (market order) | 0.05% | $0.05 |
| **Round‑trip per leg** | **0.10%** | **$0.10** |

Two legs per pair, two pairs possible: up to 4 legs. Assuming each leg turns over weekly: ~$1.60/month in fees.

### Funding rates (the real cost)

Perpetual swaps charge funding every 8 hours. Both long and short legs pay/receive funding; net cost depends on funding rate direction.

| Leverage per leg | Capital per leg | Notional per leg | Monthly funding (0.01%/8h) |
|------------------|-----------------|------------------|----------------------------|
| 3x | $150 | $450 | $4.05 |
| 5x | $150 | $750 | $6.75 |

For two pairs (four legs), monthly funding = ~$16‑$27.

### Total monthly cost

| Leverage | Fees | Funding | Total | Break‑even return |
|----------|------|---------|-------|-------------------|
| 3x | $1-2 | $12-20 | **$13-22** | **1.6‑2.7% on $1,000** |
| 5x | $1-2 | $20-30 | **$21-32** | **2.4‑3.7% on $1,000** |

**Recommendation:** Start at 3x leverage per leg. Funding is manageable, liquidation risk is low. Increase leverage only after confirming correlation stability.

## configuration example

```json
{
  "name": "Z‑Score Reversion",
  "pairs": [
    {"asset_a": "BTC", "asset_b": "ETH"},
    {"asset_a": "SOL", "asset_b": "AVAX"}
  ],
  "parameters": {
    "correlation_threshold": 0.8,
    "lookback_days": 30,
    "z_entry": 2.0,
    "z_exit": 0.5,
    "stop_loss_z": 3.0,
    "max_hold_days": 14,
    "timeframe": "1h",
    "leverage": 3,
    "max_position_size_pct": 15,
    "max_pairs": 2
  },
  "risk": {
    "max_daily_loss_pct": 5,
    "max_drawdown_pct": 15,
    "min_margin_ratio": 0.15,
    "emergency_correlation_break": 0.7
  },
  "schedule": {
    "cycle_interval_minutes": 60,
    "correlation_recalc_hours": 24
  },
  "flags": {
    "enabled": true,
    "dry_run": false,
    "allow_negative_funding_harvest": false,
    "notify_on_correlation_break": true
  }
}
```

## what to understand

- This is a market‑neutral strategy. It profits from relative mispricing, not directional moves. Returns are often modest but consistent.
- Correlation can break down during structural market shifts (e.g., a hard fork, regulatory news). The emergency exit is essential.
- Z‑score thresholds of 2.0 mean you'll trade about 5% of the time (assuming normal distribution). Be patient.
- Funding rates can eat profits. If both legs are long/short assets with similar funding, net cost may be low; if one leg pays positive funding and the other negative, you could even earn funding. Monitor.
- Execution must be simultaneous: opening one leg without the other exposes you to directional risk. Use limit orders or ensure both legs fill.
- Works best with highly correlated, liquid pairs (BTC/ETH, SOL/AVAX, etc.). Avoid illiquid pairs.
- This strategy tends to perform well in range‑bound markets and poorly during strong trending regimes where correlations diverge permanently.