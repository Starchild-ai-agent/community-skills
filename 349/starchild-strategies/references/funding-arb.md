# funding rate arbitrage

> ⚠️ Before executing any trade: verify order book depth, use limit orders on thin books, verify fills post-trade, and cancel stale orders before retrying.

## overview

Cross-venue delta-neutral strategy that captures funding rate differentials between any two perpetual futures venues. Shorts the venue with higher funding rates, longs the venue with lower rates. Zero directional exposure, pure funding yield.

## how it works

1. **Monitor** funding rates across two or more perp venues (e.g. hourly, 8-hourly)
2. **Identify** assets where the rate spread exceeds the entry threshold (0.02%/day)
3. **Enter** matched positions: long on the lower-funding venue, short on the higher-funding venue
4. **Collect** funding payments on each venue's schedule
5. **Exit** when the spread narrows below the exit threshold (0.005%/day) or risk limits are breached

## intent

"I want to earn yield from funding rate differences between two exchanges without taking directional risk."

## parameters

| Parameter | Description | Default | Range |
|-----------|-------------|---------|-------|
| `venue_a` | First perp venue | - | Any supported DEX/CEX |
| `venue_b` | Second perp venue | - | Any supported DEX/CEX |
| `assets` | Assets to monitor for arb | BTC, ETH | Any perp-listed asset on both venues |
| `leverage` | Leverage per leg | 5 | 2-10 |
| `min_spread_daily` | Minimum daily spread to enter (%) | 0.02 | 0.01-0.10 |
| `exit_spread_daily` | Spread threshold to close (%) | 0.005 | 0.001-0.01 |
| `max_notional_per_pair` | Maximum notional per asset pair | 25000 | 5000-100000 |
| `max_imbalance_pct` | Max % difference between legs before rebalancing | 5 | 3-20 |
| `emergency_stop_loss_pct` | Total capital drawdown to halt | 10 | 5-20 |
| `check_interval_minutes` | How often to check rates | 60 | 15-480 |

## target assets (examples)

| Asset type | Examples | Typical spread range |
|------------|----------|---------------------|
| Majors (BTC, ETH) | Low but consistent | 0.01-0.05%/day |
| RWA perps (stocks, commodities) | Higher but volatile | 0.05-0.15%/day |
| Mid-cap alts | Periodic spikes | 0.02-0.20%/day |

Weekend funding rates on some venues spike dramatically, which can drive the majority of profit. Monitor and adjust accordingly.

## capital requirements

- Minimum: $10k ($5k per venue)
- Recommended: $30k ($15k per venue)
- Capital must be deposited on both venues before trading

## projected yield

At $30k capital, 5x leverage, based on typical rate differentials:

- Conservative (weekday only): ~3-5%/month
- With weekend spikes: ~8-15%/month
- Annualized: ~100-175% APY

Returns vary significantly by venue pair and market conditions.

## entry logic

1. Compute daily funding rate for each asset on both venues. Normalize to same time basis (e.g. daily).
2. Calculate spread: `spread = abs(rate_venue_a - rate_venue_b)`.
3. If spread >= `min_spread_daily`, identify which venue pays more.
4. Check order book depth on both venues. If either book is too thin, skip.
5. Open long on the lower-rate venue, short on the higher-rate venue, equal notional.
6. Confirm both fills before proceeding. If second leg fails, close first leg immediately.

**Strong signal:** spread > 2x the entry threshold with consistent direction over 24h+.

## exit logic

- Spread drops below `exit_spread_daily` for 24h straight: close both legs
- Spread inverts (you're paying net funding instead of collecting): close immediately
- Cumulative funding collected exceeds 3x entry cost: tighten exit threshold
- Emergency stop: total account drawdown exceeds `emergency_stop_loss_pct`

## risk management

- **Max imbalance**: `max_imbalance_pct` between legs before rebalancing
- **Emergency stop**: `emergency_stop_loss_pct` drawdown on total capital
- **Max notional per pair**: `max_notional_per_pair`
- **One-legged exposure**: If one venue goes down or an order fails, treat it as directional. Set stop loss on exposed leg immediately. Wait for recovery, then hedge with limit orders.
- **Idempotency**: Track position state. Never open duplicate legs.

### execution discipline (critical for this strategy)

This strategy lives and dies on execution quality. The profit margins are tiny (0.05-0.15%/day). A single sloppy market order can wipe out weeks of funding yield.

**Entry execution:**
1. Check order book depth on BOTH venues before entering
2. Enter the MORE LIQUID venue first, confirm fill
3. Enter the less liquid venue second using limit IOC orders only
4. If the second leg fails or fills at unacceptable slippage, immediately close the first leg
5. Maximum acceptable entry cost: 0.1% combined across both legs
6. If books are too thin to enter within budget, SKIP the pair entirely

**Exit execution:**
1. Calculate the cost of exiting (spread x qty on both venues) BEFORE placing any exit orders
2. Compare exit cost against projected remaining yield
3. If exit cost > 2 days of remaining yield, it may be cheaper to hold and wait
4. Exit one leg at a time using limit orders, verify each fill before proceeding
5. Never market order the exit. Thin books hurt exits just as much as entries.

**Rate shift monitoring:**
- Check spreads every cycle (hourly minimum)
- If spread inverts, flag immediately
- If spread drops below 0.01%/day for 24h straight, prepare exit plan
- Weekend rate spikes are temporary. Don't enter or exit based on a single spike.
- Track cumulative funding received vs entry cost. Know your break-even point at all times.

## cycle flow

```
Every [check_interval_minutes]:
  1. Fetch current funding rates from both venues
  2. For each monitored asset, compute spread
  3. If no position and spread >= threshold, evaluate entry
  4. If position exists:
     a. Check imbalance between legs, rebalance if needed
     b. Check if spread has dropped below exit threshold
     c. Check emergency stop conditions
  5. Log cumulative funding, spread history, position state
```

## running costs

### exchange fees

| Fee type | Typical rate | Per $10k position |
|----------|-------------|-------------------|
| Taker fee (entry/exit) | 0.03-0.05% | $3-5 |
| Round-trip (both legs, both venues) | ~0.15-0.20% | $15-20 |

Entry cost is significant relative to daily yield. Break-even typically takes 1-2 days at normal spreads.

### funding rates (this is revenue, not cost)

Unlike other strategies where funding is a cost, here funding IS the profit source. Net funding collected = spread x notional x time.

### total monthly cost

| Capital | Entry/exit fees (2 rotations) | Net funding revenue | Expected profit |
|---------|------------------------------|--------------------|-----------------| 
| $10k | $30-40 | $200-500 | **$160-460** |
| $30k | $90-120 | $600-1500 | **$480-1380** |

## configuration example

```json
{
  "strategy": "funding-rate-arbitrage",
  "venues": {
    "a": {
      "name": "venue_a_name",
      "funding_interval_hours": 8
    },
    "b": {
      "name": "venue_b_name",
      "funding_interval_hours": 1
    }
  },
  "assets": [
    {
      "symbol": "BTC",
      "venue_a_symbol": "PERP_BTC_USDC",
      "venue_b_symbol": "BTC-PERP",
      "max_leverage": 10,
      "target_leverage": 5,
      "enabled": true,
      "max_notional": 25000
    },
    {
      "symbol": "ETH",
      "venue_a_symbol": "PERP_ETH_USDC",
      "venue_b_symbol": "ETH-PERP",
      "max_leverage": 10,
      "target_leverage": 5,
      "enabled": true,
      "max_notional": 25000
    }
  ],
  "risk": {
    "max_notional_per_pair": 25000,
    "max_total_notional": 100000,
    "max_imbalance_pct": 5,
    "min_spread_daily": 0.02,
    "exit_spread_daily": 0.005,
    "emergency_stop_loss_pct": 10
  },
  "execution": {
    "order_type": "LIMIT_IOC",
    "max_retries": 3,
    "check_interval_minutes": 60
  }
}
```

## what to understand

- This is a **yield strategy**, not a trading strategy. You're collecting a spread, not betting on direction.
- Execution cost is the biggest risk. Sloppy entries/exits can easily exceed the funding you collect.
- Funding rates change constantly. A profitable spread today can vanish or invert tomorrow.
- Capital is split across venues. You need accounts and deposits on both.
- Venue risk is real. If one exchange goes down or freezes withdrawals, you're stuck with one-legged exposure.
- RWA perps (stocks, commodities) often have wider funding spreads than crypto, but also have trading hours and weekend closures to consider.
- Start with majors (BTC, ETH) on well-established venues. Move to higher-spread assets only after you understand the execution dynamics.
- Monitor for at least 48h before deploying full capital on a new venue pair.
