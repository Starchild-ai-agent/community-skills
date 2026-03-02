# rsi reversal

> ⚠️ Before executing any trade: verify order book depth, use limit orders on thin books, verify fills post-trade, and cancel stale orders before retrying.

RSI reversal strategy that longs assets when oversold and shorts assets when overbought, betting on mean reversion. Runs once daily, fully automated.

## How it works

The strategy splits assets into two pools: things you'd want to buy in a dip (BTC, ETH, and other "hard money" assets) and things you'd want to short in a rally (VC-backed altcoins that tend to bleed). It uses the 14-period daily RSI to time entries and exits.

When an asset's RSI drops below the entry threshold, it's considered oversold and the strategy opens a long. When RSI rises above the exit threshold, it closes. The inverse logic applies for shorts.

The strategy runs a single daily cycle: scan all assets, close positions that no longer qualify, open new ones that do, set stop losses and take profits.

## Intent

"I want to buy strong crypto assets when they're beaten down and short weak ones when they're overextended, using RSI as the signal."

## Parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `long_assets` | Assets eligible for longs | BTC, ETH, WOO, ZEC, XMR | Any perp-listed asset |
| `short_assets` | Assets eligible for shorts | ARB, APT, SUI, OP, AVAX, NEAR, ICP... | Any perp-listed asset |
| `rsi_period` | RSI lookback in candles | 14 | 7-21 |
| `timeframe` | Candle timeframe | 1d | 1d, 4h, 1h |
| `long_entry` | RSI below this = open long | 40 | 20-50 |
| `long_exit` | RSI above this = close long | 55 | 50-70 |
| `short_entry` | RSI above this = open short | 60 | 50-80 |
| `short_exit` | RSI below this = close short | 45 | 30-50 |
| `leverage` | Position leverage | 15 | 1-20 |
| `max_positions` | Max concurrent positions | 8 | 1-15 |
| `position_size_pct` | Capital per position (%) | 10 | 5-25 |
| `stop_loss_pct` | Stop loss (%) | 5 | 2-10 |
| `take_profit_pct` | Take profit (%) | 25 | 10-50 |
| `allow_shorts` | Enable short-side trading | true | true/false |
| `cycle_interval` | Hours between cycles | 24 | 1-24 |

## Entry logic

**Longs:**
1. Asset is in the `long_assets` pool
2. 14-period daily RSI is below `long_entry` (default 40)
3. No existing position in that asset
4. Max positions not reached
5. Risk checks pass (margin ratio, daily loss limit, drawdown)

**Shorts:**
1. Asset is in the `short_assets` pool
2. 14-period daily RSI is above `short_entry` (default 60)
3. No existing position in that asset
4. Max positions not reached
5. `allow_shorts` is enabled

**Strong signals:** RSI below 35 (oversold) or above 65 (overbought) get priority and larger sizing via `dynamic_sizing_multiplier`.

## Exit logic

- Longs close when RSI rises above `long_exit` (default 55)
- Shorts close when RSI drops below `short_exit` (default 45)
- Stop loss: -5% from entry (hard stop, always set)
- Take profit: +25% from entry

## Risk management

- Max 8 concurrent positions
- 5% stop loss per position (non-negotiable)
- 10% max daily loss (pauses trading for the day)
- 20% max drawdown (pauses trading until manual reset)
- 10% minimum margin ratio (triggers alert)
- Idempotency lock prevents duplicate cycles
- Market bias check: if BTC RSI < 35, favor longs; if > 65, favor shorts

## Cycle flow

```
Every 24 hours:
  1. Acquire idempotency lock
  2. Reconcile with exchange (log current state)
  3. Fetch RSI for all assets
  4. Run risk checks (margin, drawdown, daily loss)
  5. Evaluate existing positions (close if RSI crossed exit)
  6. Open new positions where signals qualify
  7. Set SL/TP on all new positions
  8. Save report, release lock
```

## Capital requirements

Minimum: ~$200 (enough for 2-3 positions at low leverage)
Recommended: $500-$1,000 for full diversification across 6-8 positions

## What to understand

- This is a mean-reversion strategy. It bets that oversold things bounce and overbought things fade. It will underperform in strong trending markets where RSI stays extreme.
- Daily timeframe means slow entries. It won't catch intraday moves.
- The short side is riskier (unlimited upside on the asset = unlimited loss). The 5% stop loss is critical.
- RSI thresholds can be tuned. Tighter thresholds (e.g. long at 30 instead of 40) = fewer trades but higher conviction. Wider = more trades but more noise.
- Works best in choppy, range-bound markets.

## Running costs

### Exchange fees

| Fee type | Rate | Per $100 position |
|----------|------|-------------------|
| Entry (market order) | 0.05% | $0.05 |
| Exit (SL/TP trigger) | 0.05% | $0.05 |
| **Round-trip** | **0.10%** | **$0.10** |

With 8 positions rotating weekly: ~$3.20/month in fees.

### Funding rates (the real cost)

Perps charge funding every 8 hours. This is the dominant cost for leveraged strategies.

| Leverage | Capital | Notional exposure | Monthly funding (normal 0.01%/8h) |
|----------|---------|-------------------|-----------------------------------|
| 3x | $500 | $1,500 | $13.50 |
| 5x | $500 | $2,500 | $22.50 |
| 10x | $500 | $5,000 | $45.00 |
| 15x | $500 | $7,500 | $67.50 |

### Total monthly cost

| Leverage | Fees | Funding | Total | Break-even return |
|----------|------|---------|-------|-------------------|
| 3x | $3-5 | $6-14 | **$9-19** | **2-5% on $500** |
| 10x | $3-5 | $30-45 | **$33-50** | **7-11% on $500** |
| 15x | $3-5 | $45-70 | **$48-75** | **10-16% on $500** |

**Recommendation:** Start at 2-3x leverage. Funding is manageable, liquidation risk is low, break-even is achievable. Scale up after you have performance data.

## Configuration example

### Basic Configuration (Original)
```json
{
  "name": "RSI Reversal",
  "long_assets": ["BTC", "ETH"],
  "short_assets": ["ARB", "SUI", "OP"],
  "rsi": {
    "period": 14,
    "timeframe": "1d",
    "long_entry": 40,
    "long_exit": 55,
    "short_entry": 60,
    "short_exit": 45
  },
  "position": {
    "default_leverage": 10,
    "max_positions": 6,
    "position_size_pct": 12,
    "min_position_usd": 50,
    "max_position_usd": 300
  },
  "risk": {
    "stop_loss_pct": 5,
    "take_profit_pct": 20,
    "max_daily_loss_pct": 10,
    "max_drawdown_pct": 15
  },
  "schedule": {
    "cycle_time_utc": "00:00",
    "interval_hours": 24
  },
  "flags": {
    "enabled": true,
    "allow_shorts": true,
    "auto_set_sl_tp": true
  }
}
```

### Optimized Configuration (Recommended)
```json
{
  "name": "RSI Reversal v2",
  "long_assets": ["BTC", "ETH", "WOO", "ZEC", "XMR"],
  "short_assets": ["ARB", "APT", "SUI", "OP", "AVAX", "NEAR", "ICP"],
  "rsi": {
    "period": 14,
    "timeframe": "1d",
    "long_entry": 40,
    "long_exit": 55,
    "short_entry": 55,           // Lowered from 60 for more opportunities
    "short_exit": 45,
    "market_bias_oversold": 35,
    "market_bias_overbought": 65
  },
  "position": {
    "default_leverage": 5,       // Reduced from 15 to 5
    "max_leverage": 10,
    "max_positions": 8,
    "position_size_pct": 10,
    "min_position_usd": 300,     // Increased for fee efficiency
    "max_position_usd": 1000,
    "dynamic_sizing_multiplier": 2.5,
    "trailing_stop_pct": 10      // Added trailing stop
  },
  "risk": {
    "stop_loss_pct": 5,
    "take_profit_pct": 25,
    "max_daily_loss_pct": 10,
    "max_drawdown_pct": 20,
    "min_margin_ratio": 0.10
  },
  "schedule": {
    "cycle_time_utc": "00:00",
    "interval_hours": 24
  },
  "flags": {
    "enabled": true,
    "dry_run": false,
    "allow_shorts": true,
    "auto_set_sl_tp": true,
    "dynamic_sizing": true
  },
  "excludeSymbols": [],          // Event risk exclusions
  "notifications": {
    "on_trade": true,
    "on_signal": true,
    "daily_summary": true
  }
}
```

### Performance-Optimized Template
```javascript
// RSI Reversal Configuration Calculator
function calculateOptimalRSIParameters(marketVolatility = 'normal') {
  const params = {
    normal: {
      long_entry: 40,
      long_exit: 55,
      short_entry: 55,
      short_exit: 45,
      leverage: 5,
      stop_loss: 5,
      take_profit: 25
    },
    high: {
      long_entry: 35,
      long_exit: 60,
      short_entry: 65,
      short_exit: 40,
      leverage: 3,
      stop_loss: 8,
      take_profit: 30
    },
    low: {
      long_entry: 45,
      long_exit: 50,
      short_entry: 50,
      short_exit: 40,
      leverage: 8,
      stop_loss: 3,
      take_profit: 15
    }
  };
  
  return params[marketVolatility] || params.normal;
}

// Dynamic position sizing based on RSI strength
function calculatePositionSize(asset, rsi, baseSize) {
  if (rsi < 35) return baseSize * 2.0;   // Strong oversold
  if (rsi > 65) return baseSize * 1.5;   // Strong overbought
  if (rsi < 40) return baseSize * 1.2;   // Mild oversold
  if (rsi > 60) return baseSize * 1.1;   // Mild overbought
  return baseSize;
}
```
