# Grid bot

> ⚠️ Before executing any trade: verify order book depth, use limit orders on thin books, verify fills post-trade, and cancel stale orders before retrying.

Automated grid trading strategy for perpetual futures. Places buy and sell limit orders at fixed price intervals across a range, profiting from price oscillation regardless of direction.

## How it works

A grid bot divides a price range into equally spaced levels. At every level below the current price, it places a buy order. At every level above, a sell order. When a buy fills, it immediately places a sell one level up. When a sell fills, it immediately places a buy one level down. Each completed round-trip (buy low, sell high) captures the grid spacing as profit, minus fees.

The bot doesn't predict direction. It profits from oscillation. The more the price bounces within the range, the more round-trips complete, the more profit accumulates. It only loses if price moves decisively outside the range.

## Intent

"I want to profit from price chop within a range without predicting direction."

## Parameters

| Parameter | Description | How to think about it |
|-----------|-------------|----------------------|
| `asset` | What to trade | Any perp with sufficient liquidity |
| `grid_lower` | Bottom of range | Support level or worst-case downside |
| `grid_upper` | Top of range | Resistance level or expected ceiling |
| `grid_levels` | Number of grid lines | More levels = smaller profit per fill, but more fills |
| `leverage` | Position leverage | Lower is safer for grids (2-5x recommended) |
| `capital` | Total capital allocated | Divided equally across all levels |

### Derived parameters (the AI should calculate these)

| Derived | Formula | What it means |
|---------|---------|---------------|
| `grid_spacing` | (upper - lower) / levels | Dollar distance between each level |
| `capital_per_level` | capital / levels | How much USDC backs each grid line |
| `position_size` | (capital_per_level * leverage) / current_price | Asset quantity per order |
| `profit_per_fill` | grid_spacing * position_size | Gross profit per round-trip |
| `breakeven_fills` | fees_per_roundtrip / profit_per_fill | Fills needed to cover fees (must be < 1) |

## How the AI should help with configuration

When a user says "I want to run a grid bot on BTC with $1,000", the oracle should walk through this:

### 1. Determine the range

Ask or infer:
- Current price (fetch live)
- Expected trading range (user's thesis, or use recent high/low)
- Risk tolerance (wider range = safer but less profitable per fill)

Example reasoning:
> "BTC is at $68,000. The 30-day range has been $62,000 to $74,000. I'll suggest $60,000 to $80,000 for some buffer."

### 2. Calculate optimal grid levels

The key tradeoff: more levels = more fills but each fill earns less. Too few levels = large gaps, fewer fills. The constraint is that profit per fill must exceed fees per round-trip.

```
Fee per round-trip = 2 * (taker_fee * position_notional)

Typical DEX perp fees:
  Maker fee: 0.02-0.03% (limit orders, which grids use)
  Taker fee: 0.03-0.05% (market orders, used for initial setup)

  Round-trip fee = 2 * 0.02% * notional = 0.04% of position size

Profit per fill = grid_spacing * qty
Fee per fill = 0.04% * (qty * avg_price)

Grid spacing MUST be > 0.04% of price for the grid to be profitable
  At BTC $68,000: minimum spacing = $27.20
  At ETH $2,500: minimum spacing = $1.00
```

Recommended: grid spacing should be at least 3-5x the minimum to account for funding rates and slippage.

### 3. Account for funding rates

Perps have funding rates (typically every 8 hours). A grid bot holds positions for extended periods, so funding matters.

```
Funding impact:
  Positive funding = longs pay shorts (common in bull markets)
  Negative funding = shorts pay longs (common in bear markets)

  At 0.01% per 8h: ~0.03% per day, ~1% per month

  If the grid bot is net long (price below midpoint of range),
  positive funding eats into profits.

  Mitigation:
  - Keep leverage low (reduces funding paid on notional)
  - Center the grid around current price
  - Monitor funding and pause if consistently > 0.05% per 8h
```

The oracle should check current funding rate and warn if it's elevated.

### 4. Present the configuration

Example output for "$1,000 BTC grid bot":

```
Grid bot configuration
======================

Asset:          BTC perpetual
Range:          $60,000 - $80,000
Grid levels:    30
Grid spacing:   $666.67
Capital:        $1,000
Leverage:       3x
Per level:      $33.33 ($100 notional at 3x)
Position size:  0.00147 BTC per level

Expected performance:
  Profit per fill:    $0.98
  Fee per fill:       $0.04
  Net per fill:       $0.94
  Daily fills (est):  2-8 (depends on volatility)
  Daily profit (est): $1.88 - $7.52
  Monthly (est):      $56 - $225

Risk:
  Max drawdown if BTC hits $60,000: ~$180
  Max drawdown if BTC hits $80,000: ~$180 (short side)
  Funding cost at 0.01%/8h: ~$0.30/day on full deployment

Current funding rate: [fetched live]
Recommendation: [proceed / adjust range / reduce leverage]
```

### 5. Risk warnings the oracle should always include

- **Range break risk:** If price leaves the range, the bot stops filling and you hold a directional position at max exposure. Set alerts at range boundaries.
- **Funding drag:** Funding rates can silently eat profits over weeks. The oracle should calculate break-even daily fills accounting for funding.
- **Leverage and liquidation:** At 3x leverage with 30 levels, a 33% adverse move from entry risks liquidation. The oracle should calculate the liquidation price and ensure it's outside the grid range.
- **Minimum order size:** Exchanges have minimum order quantities. If capital_per_level is too small, orders will be rejected. The oracle should check this and suggest fewer levels or more capital.

## Grid spacing guidelines by asset

| Asset | Price range | Recommended spacing | Min spacing (fees) |
|-------|-------------|--------------------|--------------------|
| BTC | $60k-$80k | $500-$1,000 | $27 |
| ETH | $2k-$4k | $30-$80 | $1 |
| SOL | $100-$200 | $2-$5 | $0.05 |
| WOO | $0.10-$0.30 | $0.005-$0.01 | $0.00004 |

These are guidelines. The oracle should calculate based on actual fees for the exchange being used.

## Cycle flow

```
Every 30 seconds:
  1. Fetch current price
  2. Check risk limits (drawdown, net position, daily loss)
  3. Detect filled orders
  4. For each filled buy at level N:
     - Place sell at level N+1
  5. For each filled sell at level N:
     - Place buy at level N-1
  6. Retry failed paired orders (throttled every 5 min)
     - If a paired sell/buy failed previously (e.g. exchange
       price range rejection), retry it automatically
     - No restart needed, bot self-heals
  7. Maintain grid (fill any empty levels)
  8. Log status
```

### Self-healing behavior

Some exchanges reject limit orders that are too far from market price (e.g. outside ~10% of current price). When this happens:

- The bot records the fill but the paired order fails
- Every 5 minutes, it retries all failed paired orders
- As price moves closer to those levels, the orders get accepted automatically
- No manual intervention or restart required

This means the grid adapts to exchange limitations without human oversight.

## Capital requirements

Minimum: $100 (very few levels, wide spacing, limited fills)
Recommended: $500-$2,000 for meaningful daily returns
Sweet spot: capital_per_level should result in position sizes well above exchange minimums

## What to understand

- Grid bots are **not** a set-and-forget money printer. They work in ranging markets and bleed in trending ones.
- The range selection is the most important decision. Too narrow = frequent range breaks. Too wide = tiny profit per fill.
- Low leverage (2-5x) is strongly recommended. Grids hold positions for extended periods, and high leverage + funding + adverse moves = liquidation.
- Funding rates are a hidden cost. In a strong bull market with 0.05%+ funding, a net-long grid bot can lose money even while filling orders.
- More grid levels is not always better. Each level needs enough capital to meet minimum order sizes, and the spacing must exceed fees.
- The bot should be monitored at least daily. Automated alerts at range boundaries are essential.

## Running costs

### Exchange fees

Grid bots use limit orders (maker fees), which are cheap:

| Fee type | Rate | Per fill ($50 notional) |
|----------|------|------------------------|
| Maker (limit order) | 0.02% | $0.01 |
| Round-trip (buy + sell) | 0.04% | $0.02 |

| Market volatility | Daily fills | Monthly fees |
|------------------|-------------|-------------|
| Low (0.5% daily range) | 1-3 | $0.60-1.80 |
| Normal (1-2% range) | 3-8 | $1.80-4.80 |
| High (3%+ range) | 8-20 | $4.80-12.00 |

### Funding rates

Grid bots often hold net directional positions for extended periods. Funding is the hidden cost.

| Net exposure scenario | Funding (0.01%/8h) | Monthly |
|----------------------|-------------------|---------|
| $500 (price near midpoint) | $0.15/day | $4.50 |
| $1,500 (moderately off-center) | $0.45/day | $13.50 |
| $3,000 (near range edge) | $0.90/day | $27.00 |

### Total monthly cost

| Capital | Fees | Funding | Total | Break-even return |
|---------|------|---------|-------|-------------------|
| $500 | $1-5 | $4-14 | **$5-19** | **1.0-3.8%** |
| $1,000 | $1-5 | $5-27 | **$6-32** | **0.6-3.2%** |
| $2,000 | $2-8 | $5-27 | **$7-35** | **0.4-1.8%** |

**Key insight:** Grid bots at low leverage have very achievable break-even targets. The risk isn't monthly costs, it's range breaks (price leaving the grid entirely).

## Configuration example

### Basic Configuration (Static Range)
```json
{
  "name": "Grid Bot",
  "asset": "BTC",
  "symbol": "BTC-PERP",
  "grid_lower": 60000,
  "grid_upper": 80000,
  "grid_levels": 30,
  "leverage": 3,
  "capital": 1000,
  "polling_interval_ms": 30000,
  "risk": {
    "max_drawdown_usd": -100,
    "max_net_position": 0.05,
    "pause_on_range_break": true,
    "funding_rate_alert": 0.05
  }
}
```

### Optimized Configuration (Dynamic Range - RECOMMENDED)
```json
{
  "name": "Grid Bot v3",
  "asset": "BTC",
  "symbol": "BTC-PERP",
  "range_percent": 6,
  "grid_levels": 20,
  "leverage": 3,
  "capital": 2000,
  "capital_per_level": 100,
  "polling_interval_ms": 30000,
  "dynamic_range": true,
  "recenter_threshold_percent": 10,
  "risk": {
    "max_drawdown_usd": -200,
    "max_net_position": 0.08,
    "pause_on_range_break": true,
    "funding_rate_alert": 0.03,
    "min_profit_per_fill_ratio": 3.0
  }
}
```

### Performance-Optimized Template
```javascript
// Grid Bot Configuration Calculator
function calculateOptimalGrid(currentPrice, capital, volatilityPercent = 5) {
  const rangePercent = Math.max(4, Math.min(8, volatilityPercent * 1.2));
  const lower = currentPrice * (1 - rangePercent / 100);
  const upper = currentPrice * (1 + rangePercent / 100);
  
  // Optimal levels: balance profit per fill vs frequency
  const levels = Math.min(30, Math.max(15, Math.round(capital / 100)));
  const spacing = (upper - lower) / levels;
  
  // Ensure profitable after fees (0.04% round-trip)
  const minSpacing = currentPrice * 0.0004; // 0.04%
  if (spacing < minSpacing * 3) {
    // Reduce levels to increase spacing
    const newLevels = Math.floor((upper - lower) / (minSpacing * 3));
    return {
      lower,
      upper,
      levels: Math.max(10, newLevels),
      spacing: (upper - lower) / Math.max(10, newLevels),
      capitalPerLevel: capital / Math.max(10, newLevels)
    };
  }
  
  return { lower, upper, levels, spacing, capitalPerLevel: capital / levels };
}
```
