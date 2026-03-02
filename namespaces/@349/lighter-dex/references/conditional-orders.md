# Conditional Orders on Lighter DEX

Complete guide to advanced order types: stop losses, take profits, TWAP, and risk management.

---

## 📋 Order Types Overview

| Order Type | Trigger | Execution | Use Case |
|------------|---------|-----------|----------|
| **LIMIT** | Immediate | Limit price or better | Standard limit order |
| **MARKET** | Immediate | Best available | Quick entry/exit |
| **STOP** | Price hits trigger | Market order | Stop loss (guaranteed fill) |
| **STOP_LIMIT** | Price hits trigger | Limit order | Stop loss (price control) |
| **TAKE_PROFIT** | Price hits trigger | Market order | Take profit (guaranteed fill) |
| **TAKE_PROFIT_LIMIT** | Price hits trigger | Limit order | Take profit (price control) |
| **TWAP** | Time-based | Sliced market orders | Large orders, reduce slippage |

---

## 🛑 Stop Loss Orders

### When to Use
Protect your position from excessive losses. Always use with leverage!

### STOP (Market) vs STOP_LIMIT (Limit)

| Feature | STOP (Market) | STOP_LIMIT (Limit) |
|---------|---------------|-------------------|
| **Guaranteed Fill** | ✅ Yes | ❌ No (may not fill if price gaps) |
| **Price Control** | ❌ No | ✅ Yes |
| **Slippage Risk** | ⚠️ High in volatile markets | ✅ None (but may not fill) |
| **Best For** | Emergency exits, high leverage | Controlled exits, low volatility |

---

### Example: Long BTC at $95,000

#### Scenario A: Stop Loss (Market) — Guaranteed Exit
```python
lighter_stop_loss(
  symbol="BTC",
  side="sell",           # Sell to close long
  size=0.1,
  trigger_price=90000,   # Trigger when BTC hits $90k
  reduce_only=True       # Only closes position
)
```

**What happens:**
- When BTC price ≤ $90,000 → Market sell order executes
- ✅ **Guaranteed to fill** (even if price crashes to $85k)
- ⚠️ **May fill below $90k** in fast markets (slippage)

---

#### Scenario B: Stop Loss (Limit) — Price Control
```python
lighter_stop_limit(
  symbol="BTC",
  side="sell",
  size=0.1,
  trigger_price=90000,   # Trigger when BTC hits $90k
  limit_price=89500,     # Sell at $89.5k or better
  reduce_only=True
)
```

**What happens:**
- When BTC price ≤ $90,000 → Limit sell order at $89,500 placed
- ✅ **Will not sell below $89,500**
- ❌ **May not fill** if price gaps from $90.1k → $89k instantly

---

### Which Should You Use?

**Use STOP (Market) when:**
- High leverage (10x+) — liquidation risk is urgent
- Trading volatile assets (memecoins, earnings plays)
- You prioritize exit certainty over price

**Use STOP_LIMIT when:**
- Lower leverage (3-5x) — more room to manage
- Trading stable markets (major forex, blue-chip stocks)
- You have specific price targets for risk/reward

---

## 🎯 Take Profit Orders

### When to Use
Lock in gains automatically. Removes emotion from exiting winners.

---

### Example: Long BTC at $95,000, Target $100,000

#### TAKE_PROFIT (Market)
```python
lighter_take_profit(
  symbol="BTC",
  side="sell",
  size=0.1,
  trigger_price=100000,  # Trigger when BTC hits $100k
  reduce_only=True
)
```

**Pros:** Guaranteed to take profit  
**Cons:** May get filled below $100k in volatile conditions

---

#### TAKE_PROFIT_LIMIT (Limit)
```python
lighter_take_profit_limit(
  symbol="BTC",
  side="sell",
  size=0.1,
  trigger_price=100000,  # Trigger when BTC hits $100k
  limit_price=100500,    # Sell at $100.5k or better
  reduce_only=True
)
```

**Pros:** Controls minimum exit price  
**Cons:** May miss the move if price spikes and reverses

---

## 📊 Bracket Orders (Entry + SL + TP)

A "bracket" is entry + stop loss + take profit. Lighter doesn't have native OCO (One-Cancels-Other), so you manage manually.

### Setup Bracket for Long BTC

```python
# 1. Enter position
lighter_order(
  symbol="BTC",
  side="buy",
  size=0.1,
  order_type="MARKET"
)

# 2. Set stop loss (-5% from entry)
lighter_stop_loss(
  symbol="BTC",
  side="sell",
  size=0.1,
  trigger_price=90250,   # 5% below $95k
  reduce_only=True
)

# 3. Set take profit (+10% from entry)
lighter_take_profit(
  symbol="BTC",
  side="sell",
  size=0.1,
  trigger_price=104500,  # 10% above $95k
  reduce_only=True
)
```

### Managing the Bracket

**When one order fills, cancel the other:**

```python
# Check open orders
orders = lighter_open_orders(symbol="BTC")
print(orders)

# Cancel the remaining order (e.g., if TP filled, cancel SL)
lighter_cancel(symbol="BTC", order_id=SL_ORDER_ID)
```

---

## ⏱️ TWAP Orders (Time-Weighted Average Price)

### When to Use
- Large orders that would move the market
- Building/reducing position over time
- Reducing slippage on illiquid markets

---

### Example: Buy 10 BTC Over 4 Hours

```python
lighter_twap_order(
  symbol="BTC",
  side="buy",
  total_amount=10.0,
  duration_seconds=14400,   # 4 hours
  slice_interval=60         # Execute slice every 60 seconds
)
```

**What happens:**
- Total: 10 BTC over 4 hours
- Slices: 14400 / 60 = 240 slices
- Per slice: 10 / 240 = 0.0417 BTC every minute
- Execution: Market orders at each interval

---

### TWAP Strategy Tips

**For large entries:**
```python
# Enter 50 ETH over 8 hours
lighter_twap_order(
  symbol="ETH",
  side="buy",
  total_amount=50.0,
  duration_seconds=28800,   # 8 hours
  slice_interval=120        # Every 2 minutes
)
```

**For large exits (less urgency):**
```python
# Exit 100 BTC over 24 hours
lighter_twap_order(
  symbol="BTC",
  side="sell",
  total_amount=100.0,
  duration_seconds=86400,   # 24 hours
  slice_interval=300        # Every 5 minutes
)
```

---

## ⚠️ Liquidation Risk Management

### Check Liquidation Before Trading

```python
# See all positions and liquidation prices
lighter_liquidation()
```

**Output:**
```json
[
  {
    "symbol": "BTC",
    "side": "LONG",
    "leverage": 10,
    "entry_price": 95000,
    "liquidation_price": 86350,
    "distance_to_liquidation": "10.52%"
  }
]
```

**Interpretation:**
- Liquidation at $86,350 (9.1% below entry)
- With 10x leverage, a 10% drop = liquidation
- **Rule of thumb:** Distance to liq should be > 2x your stop loss

---

### Set Conservative Leverage

```python
# Before trading, set appropriate leverage
lighter_leverage(symbol="BTC", leverage=5)  # 5x instead of max 100x
```

**Leverage Guidelines:**
| Asset Type | Max Recommended | Why |
|------------|-----------------|-----|
| Major Crypto (BTC, ETH) | 5-10x | High volatility |
| Altcoins | 3-5x | Extreme volatility |
| Stocks (AAPL, MSFT) | 10-20x | Moderate volatility |
| Forex (EURUSD) | 20-50x | Low volatility |
| Commodities (Gold) | 10-20x | Moderate volatility |

---

## 🎛️ Time-In-Force Options

Advanced control over order execution.

### GTC (Good 'Til Cancelled) — Default
```python
lighter_order(
  symbol="BTC",
  side="buy",
  size=0.1,
  order_type="LIMIT",
  price=94000,
  time_in_force="GTC"  # Stays until filled or cancelled
)
```

---

### GTT (Good 'Til Time) — Expires at specific time
```python
lighter_order(
  symbol="BTC",
  side="buy",
  size=0.1,
  order_type="LIMIT",
  price=94000,
  time_in_force="GTT",
  expiry_time="2024-12-31T23:59:59Z"  # ISO 8601 format
)
```

**Use case:** Day trading — don't leave orders open overnight.

---

### IOC (Immediate or Cancel) — Fill what's available now
```python
lighter_order(
  symbol="BTC",
  side="buy",
  size=1.0,
  order_type="LIMIT",
  price=95000,
  time_in_force="IOC"  # Fill available liquidity, cancel rest
)
```

**Use case:** Quick partial fills, testing liquidity.

---

### POST_ONLY — Maker only (guaranteed rebate)
```python
lighter_order(
  symbol="BTC",
  side="buy",
  size=0.1,
  order_type="LIMIT",
  price=94500,
  time_in_force="POST_ONLY"  # Rejects if would immediately fill
)
```

**Use case:** Market making, earning maker rebates.

---

## 📈 Real-World Strategy Examples

### 1. Swing Trade Setup (BTC Long)

```python
# Analysis: BTC at $95k, support at $93k, resistance at $100k

# Entry (limit order at support)
lighter_order(
  symbol="BTC",
  side="buy",
  size=0.5,
  order_type="LIMIT",
  price=93000,
  time_in_force="GTC"
)

# Stop loss (5% below entry, use limit for price control)
lighter_stop_limit(
  symbol="BTC",
  side="sell",
  size=0.5,
  trigger_price=88350,   # 5% below $93k
  limit_price=88000,
  reduce_only=True
)

# Take profit (7.5% above entry)
lighter_take_profit_limit(
  symbol="BTC",
  side="sell",
  size=0.5,
  trigger_price=100000,  # At resistance
  limit_price=100500,
  reduce_only=True
)

# Risk/Reward: 5% risk, 7.5% reward = 1:1.5 R/R
```

---

### 2. Scalping Strategy (ETH Quick Trade)

```python
# Analysis: ETH ranging $3400-3450, quick momentum play

# Entry (market order for speed)
lighter_order(
  symbol="ETH",
  side="buy",
  size=5.0,
  order_type="MARKET"
)

# Tight stop loss (1% below, market order for certainty)
lighter_stop_loss(
  symbol="ETH",
  side="sell",
  size=5.0,
  trigger_price=3366,    # 1% below $3400
  reduce_only=True
)

# Quick target (1.5% above)
lighter_take_profit(
  symbol="ETH",
  side="sell",
  size=5.0,
  trigger_price=3451,    # 1.5% above $3400
  reduce_only=True
)

# Risk/Reward: 1% risk, 1.5% reward = 1:1.5 R/R
# Note: Scalping requires tight spreads and low fees
```

---

### 3. Accumulation Strategy (Build Position Over Time)

```python
# Goal: Accumulate 10 BTC over 3 days without moving market

# TWAP: 10 BTC over 72 hours
lighter_twap_order(
  symbol="BTC",
  side="buy",
  total_amount=10.0,
  duration_seconds=259200,  # 72 hours
  slice_interval=300        # Every 5 minutes
)

# Stop loss for entire position (10% below average entry)
# Set this AFTER TWAP completes and you know average entry
lighter_stop_loss(
  symbol="BTC",
  side="sell",
  size=10.0,
  trigger_price=85500,      # 10% below ~$95k
  reduce_only=True
)
```

---

### 4. Earnings Play (Stock Perps)

```python
# NVDA earnings tonight, implied move ±8%
# Current price: $900

# Straddle: Long call + Long put (via perps)

# Long position (betting on upside)
lighter_order(
  symbol="NVDA",
  side="buy",
  size=100,
  order_type="MARKET"
)
lighter_stop_loss(
  symbol="NVDA",
  side="sell",
  size=100,
  trigger_price=828,        # -8% stop
  reduce_only=True
)
lighter_take_profit(
  symbol="NVDA",
  side="sell",
  size=100,
  trigger_price=972,        # +8% target
  reduce_only=True
)

# Short position (betting on downside)
lighter_order(
  symbol="NVDA",
  side="sell",
  size=100,
  order_type="MARKET"
)
lighter_stop_loss(
  symbol="NVDA",
  side="buy",
  size=100,
  trigger_price=972,        # +8% stop on short
  reduce_only=True
)
lighter_take_profit(
  symbol="NVDA",
  side="buy",
  size=100,
  trigger_price=828,        # -8% target on short
  reduce_only=True
)

# Outcome: One side hits TP (+8%), other hits SL (-8%)
# Net: Breakeven minus fees (volatility play)
```

---

## ⚡ Quick Reference: Order Type Selection

| Goal | Best Order Type | Example |
|------|----------------|---------|
| **Enter position** | LIMIT or MARKET | `lighter_order(..., order_type="LIMIT")` |
| **Emergency exit** | STOP (market) | `lighter_stop_loss(...)` |
| **Controlled exit** | STOP_LIMIT | `lighter_stop_limit(..., limit_price=...)` |
| **Take profits** | TAKE_PROFIT or TAKE_PROFIT_LIMIT | `lighter_take_profit(...)` |
| **Large order** | TWAP | `lighter_twap_order(..., duration_seconds=3600)` |
| **Maker rebate** | LIMIT + POST_ONLY | `lighter_order(..., time_in_force="POST_ONLY")` |
| **Day trade** | LIMIT + GTT | `lighter_order(..., time_in_force="GTT", expiry_time=...)` |

---

## 🧠 Pro Tips

1. **Always use reduce_only=True** for SL/TP — prevents accidentally opening new positions

2. **Check liquidation before entering:**
   ```python
   lighter_liquidation()  # Always run this first!
   ```

3. **TWAP for anything >1% of daily volume** — check `lighter_stats()` for volume

4. **Use STOP_LIMIT in illiquid markets** — avoids terrible fills on thin orderbooks

5. **Set leverage BEFORE trading:**
   ```python
   lighter_leverage(symbol="BTC", leverage=5)  # Not 100x!
   ```

6. **Monitor funding rates** for perp holds:
   ```python
   lighter_funding(symbol="BTC")
   ```

7. **Cancel filled order's counterpart** in bracket trades — check `lighter_open_orders()` regularly

---

## 📖 Related

- [SKILL.md](../SKILL.md) — Full tool reference
- [API Reference](https://apidocs.lighter.xyz) — Official Lighter docs
- [Risk Calculator Script](../scripts/risk_calculator.py) — Calculate liq price
- [Market Lookup Script](../scripts/market_lookup.py) — Find symbols
