# rsi rotation

> ⚠️ Before executing any trade: verify order book depth, use limit orders on thin books, verify fills post-trade, and cancel stale orders before retrying.

Momentum rotation strategy that ranks assets by RSI or price momentum over the past 3-6 months, goes long the strongest performers and shorts the weakest. Decades of data show top-performing stocks or sectors continue outperforming, with momentum spreads historically producing several percent yearly advantage over laggards. Rebalances monthly to capture shifting leadership.

## how it works

Select a universe of assets (e.g., top 20 crypto tokens by market cap). Compute momentum for each asset over a lookback period (default 90 days) using RSI, price return, or other momentum indicator. Rank assets by momentum score. Go long the top `n` leaders and short the bottom `n` laggards, equal-weighted within each basket. Hold positions for a holding period (default 30 days), then re-rank and rotate. The strategy bets on momentum persistence: assets that have performed well tend to continue performing well, while weak assets tend to remain weak.

## intent

"I want to capture the momentum factor by buying recent winners and selling recent losers, rotating periodically to stay with the trend."

## parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `universe` | Assets to consider (symbols) | BTC, ETH, SOL, ADA, DOT, AVAX, LINK, MATIC, XRP, DOGE, LTC, BCH, UNI, AAVE, COMP, SNX, MKR, SUSHI, CRV, YFI | Any perp-listed assets |
| `momentum_type` | Momentum calculation method | rsi_90d | rsi_90d, return_90d, return_180d, sharpe_90d |
| `lookback_days` | Days for momentum calculation | 90 | 30-180 |
| `ranking_period` | Days between re‑ranking and rotation | 30 | 7-90 |
| `leaders_count` | Number of top assets to go long | 5 | 1-10 |
| `laggards_count` | Number of bottom assets to short | 5 | 1-10 |
| `leverage` | Leverage per leg (each side) | 2 | 1-5 |
| `position_size_pct` | Capital allocated per asset (%) | 10 | 5-20 |
| `stop_loss_pct` | Stop loss per position (%) | 10 | 5-20 |
| `take_profit_pct` | Take profit per position (%) | 30 | 15-50 |
| `max_hold_days` | Maximum days before forced rotation | 90 | 30-180 |
| `timeframe` | Candle timeframe for prices | 1d | 1d, 4h, 1h |
| `allow_shorts` | Enable short side | true | true/false |
| `market_cap_filter` | Minimum market cap rank | 50 | 20-100 |
| `volume_filter` | Minimum daily volume (USD) | 1000000 | 500000-5000000 |

## entry logic

1. Compute momentum score for each asset in `universe` over `lookback_days`:
   - If `momentum_type` is `rsi_90d`, compute 14-period RSI using daily candles, then average RSI over last 90 days.
   - If `momentum_type` is `return_90d`, compute total return over last 90 days.
   - If `momentum_type` is `return_180d`, compute total return over last 180 days.
   - If `momentum_type` is `sharpe_90d`, compute Sharpe ratio (return/volatility) over last 90 days.
2. Rank assets by momentum score descending (highest momentum = leader).
3. Select top `leaders_count` assets for long basket, bottom `laggards_count` assets for short basket (if `allow_shorts` is true).
4. For each selected asset:
   - Long leaders with `position_size_pct` capital at `leverage`.
   - Short laggards with same notional size.
5. Ensure all positions are opened simultaneously (hedged). If any leg fails, cancel the others.

## exit logic

- Scheduled rotation: after `ranking_period` days, close all positions and re-rank.
- Stop loss: if position hits `stop_loss_pct` loss, close that position only.
- Take profit: if position hits `take_profit_pct` gain, close that position only.
- Max hold: if position held longer than `max_hold_days`, close regardless.
- Emergency exit: if asset drops out of `universe` (market cap rank > `market_cap_filter` or volume < `volume_filter`), close position.

## risk management

- Max concurrent positions: `leaders_count` + `laggards_count` (default 10).
- Stop loss at `stop_loss_pct` per position limits loss per asset.
- Daily loss limit: 5% of capital (pauses trading for the day).
- Max drawdown: 15% (pauses trading until manual reset).
- Margin ratio minimum 15% (triggers alert).
- Idempotency lock prevents duplicate entries.
- Market regime filter: if overall market momentum is negative (average return < -5% over 30 days), reduce position size by 50%.

## cycle flow

```
Every day:
  1. Acquire idempotency lock
  2. Fetch daily prices for all universe assets
  3. Compute momentum scores
  4. Check existing positions:
     - Close if stop loss or take profit triggered
     - Close if emergency filter breached
     - Close if max hold days exceeded
  5. If today is a rotation day (days since last rotation >= ranking_period):
     - Close all positions
     - Re‑rank assets
     - Open new long/short baskets
  6. Set stop‑loss and take‑profit orders on all positions
  7. Save report, release lock
```

## capital requirements

Minimum: $1,000 (enough for 10 positions with 2x leverage per leg). Recommended: $2,000‑$5,000 for comfortable margin and diversification.

Each leg uses `position_size_pct` of capital (default 10%). At 2x leverage, each leg's notional exposure = capital × 0.10 × 2 = 0.20× capital. For 10 positions (20 legs), total notional exposure = 4.0× capital. Keep margin ratio healthy.

## running costs

### Exchange fees

| Fee type | Rate | Per $100 leg |
|----------|------|--------------|
| Entry (market order) | 0.05% | $0.05 |
| Exit (market order) | 0.05% | $0.05 |
| **Round‑trip per leg** | **0.10%** | **$0.10** |

With 20 legs rotating monthly: ~$2.00/month in fees (assuming $100 per leg).

### Funding rates (the real cost)

Perpetual swaps charge funding every 8 hours. Both long and short legs pay/receive funding; net cost depends on funding rate direction.

| Leverage per leg | Capital per leg | Notional per leg | Monthly funding (0.01%/8h) |
|------------------|-----------------|------------------|----------------------------|
| 2x | $100 | $200 | $1.80 |
| 3x | $100 | $300 | $2.70 |
| 5x | $100 | $500 | $4.50 |

For 20 legs, monthly funding = ~$36‑$90.

### Total monthly cost

| Leverage | Fees | Funding | Total | Break‑even return |
|----------|------|---------|-------|-------------------|
| 2x | $2-3 | $30-40 | **$32-43** | **3.5‑4.8% on $1,000** |
| 3x | $2-3 | $45-60 | **$47-63** | **5‑6.8% on $1,000** |
| 5x | $2-3 | $75-100 | **$77-103** | **8‑10.8% on $1,000** |

**Recommendation:** Start at 2x leverage per leg. Momentum strategies require longer holding periods; higher leverage increases funding cost and liquidation risk. Increase leverage only after confirming momentum persistence.

## configuration example

```json
{
  "name": "RSI Rotation",
  "universe": ["BTC", "ETH", "SOL", "ADA", "DOT", "AVAX", "LINK", "MATIC", "XRP", "DOGE", "LTC", "BCH", "UNI", "AAVE", "COMP", "SNX", "MKR", "SUSHI", "CRV", "YFI"],
  "parameters": {
    "momentum_type": "rsi_90d",
    "lookback_days": 90,
    "ranking_period": 30,
    "leaders_count": 5,
    "laggards_count": 5,
    "leverage": 2,
    "position_size_pct": 10,
    "stop_loss_pct": 10,
    "take_profit_pct": 30,
    "max_hold_days": 90,
    "timeframe": "1d",
    "allow_shorts": true,
    "market_cap_filter": 50,
    "volume_filter": 1000000
  },
  "risk": {
    "max_daily_loss_pct": 5,
    "max_drawdown_pct": 15,
    "min_margin_ratio": 0.15,
    "market_regime_filter": true
  },
  "schedule": {
    "cycle_interval_hours": 24,
    "rotation_day_of_month": null
  },
  "flags": {
    "enabled": true,
    "dry_run": false,
    "allow_negative_funding_harvest": false,
    "notify_on_rotation": true
  }
}
```

## what to understand

- This is a momentum‑factor strategy. It bets on persistence of recent performance, not reversion. Returns can be strong during trending markets but suffer during reversals.
- Momentum can reverse suddenly (momentum crashes). The stop loss is essential.
- Ranking period of 30 days means you hold positions for a month; shorter periods increase turnover and costs.
- The short side carries unlimited loss potential if a laggard suddenly rallies. Ensure stop losses are always active.
- Funding rates can be asymmetric: leaders may have positive funding (cost to hold), laggards may have negative funding (income). Monitor net funding impact.
- Works best with a diversified universe of liquid assets. Avoid illiquid tokens.
- Market regime matters: momentum strategies perform poorly during high‑volatility, range‑bound markets. The market regime filter helps reduce exposure during unfavorable conditions.
- Historical backtests show momentum spreads of 3‑8% annually in traditional markets; crypto momentum may be stronger but more volatile.