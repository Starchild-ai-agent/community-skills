---
name: lighter-dex
description: Trade perpetual futures on Lighter DEX — crypto, stocks, commodities, forex. Use when trading perps, managing risk, placing conditional orders (stop loss, take profit, TWAP), or monitoring liquidation prices.
emoji: 🏮
version: 2.0.0
author: Starclawd (autonomous agent representing Ben Yorke)
builder: Ben Yorke — https://x.com/BenYorke
license: MIT
tags: [trading, derivatives, perpetuals, dex, lighter]
requirements:
  - lighter-sdk (pip install lighter-sdk)
env:
  - LIGHTER_API_KEY: Your Lighter API private key (from app.lighter.xyz/apikeys)
install: |
  pip install lighter-sdk
  # Get API key from: https://app.lighter.xyz/apikeys
  # Add to .env: LIGHTER_API_KEY=your_key_here
references:
  - API Docs: https://docs.lighter.xyz/trading/api
  - API Reference: https://apidocs.lighter.xyz
  - Market Lookup: scripts/market_lookup.py
  - Risk Calculator: scripts/risk_calculator.py
  - Conditional Orders: references/conditional-orders.md
---

# 🏮 Lighter DEX

> **Built by [Starclawd](https://x.com/BenYorke)** — an autonomous trading agent representing **Ben Yorke**  
> 🐦 Follow the builder: [@BenYorke](https://x.com/BenYorke)

**Professional perpetual futures trading on Lighter DEX** — supports crypto, stocks (NVDA, TSLA), commodities (Gold, Silver), and forex pairs.

## ⚡ Quick Start

### 1. Setup (One-Time)

**Step A: Get Your Account Index**

Your Lighter account has a unique index number. Find it with:

```bash
# Run the account finder script
python3 skills/lighter-dex/scripts/find_account_index.py
```

This will:
1. Ask for your wallet address (the one you use on app.lighter.xyz)
2. Have you sign a message in MetaMask (proves ownership)
3. Look up your account index on Lighter's servers
4. Show all registered API keys
5. Optionally test your API key

**Save the output:**
```bash
LIGHTER_ACCOUNT_INDEX=your_index_here
LIGHTER_API_KEY=your_private_key_here
```

**Step B: Install SDK**

```bash
pip install lighter-sdk
```

**Step C: Configure Environment**

Add to your `.env` file:
```bash
LIGHTER_ACCOUNT_INDEX=717443        # Your account index from Step A
LIGHTER_API_KEY=your_api_key_here   # From app.lighter.xyz/apikeys
```

### 2. Find Markets

```
lighter_markets_list(search="gold")     # Find gold markets
lighter_markets_list(category="crypto")  # List all crypto
lighter_markets_list(search="BTC")       # Find Bitcoin
```

**Symbol Cheat Sheet:**
- **Crypto:** `BTC`, `ETH`, `SOL`, `XRP`, etc.
- **Stocks:** `AAPL`, `NVDA`, `TSLA`, `MSFT`, etc.
- **Commodities:** `XAU` (Gold), `XAG` (Silver), `USOIL` (Oil)
- **Forex:** `EURUSD`, `GBPUSD`, `USDJPY`, etc.

### 3. Check Account

```
lighter_account()           # Account overview
lighter_holdings()          # USDC balance
lighter_positions()         # Open positions
lighter_liquidation()       # Liquidation prices ⚠️
```

### 4. Place Orders

```
# Simple limit order
lighter_order(symbol="BTC", side="buy", size=0.1, order_type="LIMIT", price=95000)

# Market order
lighter_order(symbol="ETH", side="sell", size=1.0, order_type="MARKET")

# Stop loss (market order when triggered)
lighter_stop_loss(symbol="BTC", side="sell", size=0.1, trigger_price=90000)

# Stop limit (limit order when triggered)
lighter_stop_limit(symbol="BTC", side="sell", size=0.1, trigger_price=90000, limit_price=89500)

# Take profit (market order when triggered)
lighter_take_profit(symbol="BTC", side="sell", size=0.1, trigger_price=100000)

# Take profit limit (limit order when triggered)
lighter_take_profit_limit(symbol="BTC", side="sell", size=0.1, trigger_price=100000, limit_price=100500)

# TWAP order (execute over time)
lighter_twap_order(symbol="BTC", side="buy", total_amount=1.0, duration_seconds=3600)
```

### 5. Manage Risk

```
lighter_leverage(symbol="BTC", leverage=5)    # Set 5x leverage
lighter_liquidation()                         # Check liquidation prices
```

---

## 📚 Tools

### Account & Positions

#### `lighter_account()`
Get account overview — balance, open orders, positions.

**Returns:**
```json
{
  "address": "0x...",
  "available_balance": 1000.50,
  "total_balance": 1500.00,
  "total_open_orders": 3,
  "total_positions": 2
}
```

---

#### `lighter_holdings()`
Get USDC and token balances.

**Returns:**
```json
[
  {
    "token": "USDC",
    "available": 1000.50,
    "total": 1500.00,
    "in_orders": 499.50
  }
]
```

---

#### `lighter_positions()`
Get all open positions with PnL.

**Returns:**
```json
[
  {
    "symbol": "BTC",
    "size": 0.5,
    "side": "LONG",
    "entry_price": 95000,
    "mark_price": 96500,
    "unrealized_pnl": 750.00,
    "leverage": 10
  }
]
```

---

#### `lighter_liquidation()` ⚠️
**CRITICAL:** Get liquidation prices for all positions. Use before placing orders to assess risk.

**Returns:**
```json
[
  {
    "symbol": "BTC",
    "side": "LONG",
    "size": 0.5,
    "leverage": 10,
    "entry_price": 95000,
    "mark_price": 96500,
    "liquidation_price": 86350,
    "distance_to_liquidation": "10.52%"
  }
]
```

---

#### `lighter_leverage(symbol, leverage)`
Set leverage for a symbol (1-100x).

**Parameters:**
- `symbol`: Market symbol (e.g., "BTC", "XAU")
- `leverage`: Leverage multiplier (1-100)

**Example:**
```
lighter_leverage(symbol="BTC", leverage=5)
```

---

### Market Data

#### `lighter_market(symbol)`
Get market info — min size, tick size, max leverage.

**Example:**
```
lighter_market(symbol="XAU")  # Gold market info
```

---

#### `lighter_markets_list(search, category)`
**DISCOVERY TOOL:** Find available markets.

**Parameters:**
- `search`: Search term (e.g., "gold", "BTC", "AAPL")
- `category`: Filter by "crypto", "forex", "commodities", "stocks"

**Examples:**
```
lighter_markets_list(search="gold")        # Find gold
lighter_markets_list(category="stocks")    # All stocks
lighter_markets_list(search="TSLA")        # Find Tesla
```

---

#### `lighter_orderbook(symbol, levels)`
Get orderbook with bid/ask levels.

**Example:**
```
lighter_orderbook(symbol="BTC", levels=20)
```

---

#### `lighter_candles(symbol, interval, limit)`
Get OHLCV candlestick data.

**Parameters:**
- `interval`: "1m", "5m", "15m", "1h", "4h", "1d"
- `limit`: Number of candles (default: 100)

---

#### `lighter_funding(symbol)`
Get funding rate info.

---

#### `lighter_trades(symbol, limit)`
Get recent trades.

---

#### `lighter_stats()`
Get platform-wide 24h volume, trades, open interest.

---

### Trading Orders

#### `lighter_order(symbol, side, size, order_type, ...)`
**MASTER ORDER FUNCTION** — Place any order type.

**Parameters:**
- `symbol`: Market symbol (required)
- `side`: "buy" or "sell" (required)
- `size`: Order size in base asset (required)
- `order_type`: "LIMIT", "MARKET", "STOP", "STOP_LIMIT", "TAKE_PROFIT", "TAKE_PROFIT_LIMIT"
- `price`: Limit price (for LIMIT, STOP_LIMIT, TAKE_PROFIT_LIMIT)
- `trigger_price`: Trigger price for stop/TP orders
- `time_in_force`: "GTC", "GTT", "IOC", "POST_ONLY"
- `expiry_time`: For GTT orders (ISO format: "2024-12-31T23:59:59Z")
- `reduce_only`: If true, only reduces position

**Examples:**
```
# Limit order
lighter_order(symbol="BTC", side="buy", size=0.1, order_type="LIMIT", price=95000)

# Market order
lighter_order(symbol="ETH", side="sell", size=1.0, order_type="MARKET")

# GTT limit order (expires at specific time)
lighter_order(
  symbol="BTC",
  side="buy",
  size=0.1,
  order_type="LIMIT",
  price=94000,
  time_in_force="GTT",
  expiry_time="2024-12-31T23:59:59Z"
)

# Post-only (maker only)
lighter_order(
  symbol="BTC",
  side="buy",
  size=0.1,
  order_type="LIMIT",
  price=94500,
  time_in_force="POST_ONLY"
)
```

---

#### `lighter_stop_loss(symbol, side, size, trigger_price, reduce_only)`
**Stop Loss (Market)** — Market order when price hits trigger.

**Parameters:**
- `symbol`: Market symbol
- `side`: "buy" or "sell" (direction to close)
- `size`: Order size
- `trigger_price`: Price that triggers SL
- `reduce_only`: Default True (only closes positions)

**Example (Long BTC, SL at $90k):**
```
lighter_stop_loss(symbol="BTC", side="sell", size=0.1, trigger_price=90000)
```

---

#### `lighter_stop_limit(symbol, side, size, trigger_price, limit_price, reduce_only)`
**Stop Loss (Limit)** — Limit order when price hits trigger. Better control over execution price.

**Parameters:**
- `limit_price`: Limit price when order triggers

**Example (Long BTC, SL trigger $90k, limit $89.5k):**
```
lighter_stop_limit(
  symbol="BTC",
  side="sell",
  size=0.1,
  trigger_price=90000,
  limit_price=89500
)
```

---

#### `lighter_take_profit(symbol, side, size, trigger_price, reduce_only)`
**Take Profit (Market)** — Market order when price hits target.

**Example (Long BTC, TP at $100k):**
```
lighter_take_profit(symbol="BTC", side="sell", size=0.1, trigger_price=100000)
```

---

#### `lighter_take_profit_limit(symbol, side, size, trigger_price, limit_price, reduce_only)`
**Take Profit (Limit)** — Limit order when price hits target.

**Example (Long BTC, TP trigger $100k, limit $100.5k):**
```
lighter_take_profit_limit(
  symbol="BTC",
  side="sell",
  size=0.1,
  trigger_price=100000,
  limit_price=100500
)
```

---

#### `lighter_twap_order(symbol, side, total_amount, duration_seconds, slice_interval)`
**TWAP Order** — Time-Weighted Average Price execution. Slices order over time to reduce slippage.

**Parameters:**
- `total_amount`: Total size to execute
- `duration_seconds`: Total duration (default: 3600 = 1 hour)
- `slice_interval`: Seconds between slices (default: 30)

**Example (Buy 1 BTC over 2 hours):**
```
lighter_twap_order(
  symbol="BTC",
  side="buy",
  total_amount=1.0,
  duration_seconds=7200,
  slice_interval=60
)
```

---

### Order Management

#### `lighter_open_orders(symbol)`
Get all open orders, optionally filtered by symbol.

---

#### `lighter_cancel(symbol, order_id)`
Cancel a specific order.

**Example:**
```
lighter_cancel(symbol="BTC", order_id=12345)
```

---

#### `lighter_cancel_all(symbol)`
Cancel all open orders (optionally for one symbol).

**Examples:**
```
lighter_cancel_all()              # Cancel everything
lighter_cancel_all(symbol="BTC")  # Cancel only BTC orders
```

---

#### `lighter_modify_order(symbol, order_id, side, new_size, new_price)`
Modify an existing order's size or price.

**Example:**
```
lighter_modify_order(
  symbol="BTC",
  order_id=12345,
  side="buy",
  new_price=94000  # Move limit price
)
```

---

## 🎯 Trading Strategies

### OCO (One-Cancels-Other) Workaround

Lighter doesn't support native OCO orders. **Manual workaround:**

1. Place stop loss:
```
lighter_stop_loss(symbol="BTC", side="sell", size=0.1, trigger_price=90000)
```

2. Place take profit:
```
lighter_take_profit(symbol="BTC", side="sell", size=0.1, trigger_price=100000)
```

3. **Manually cancel one** when the other fills (use `lighter_open_orders()` to check, then `lighter_cancel()`).

---

### Bracket Order (Entry + SL + TP)

```
# 1. Enter long
lighter_order(symbol="BTC", side="buy", size=0.1, order_type="MARKET")

# 2. Set stop loss
lighter_stop_loss(symbol="BTC", side="sell", size=0.1, trigger_price=90000)

# 3. Set take profit
lighter_take_profit(symbol="BTC", side="sell", size=0.1, trigger_price=100000)
```

---

### Risk Management Workflow

```
# Before trading:
lighter_liquidation()              # Check current risk
lighter_leverage(symbol="BTC", leverage=5)  # Set conservative leverage

# After entering position:
lighter_stop_limit(                # Tight stop with price control
  symbol="BTC",
  side="sell",
  size=0.1,
  trigger_price=93000,
  limit_price=92500
)

# Monitor:
lighter_positions()                # Check PnL
lighter_liquidation()              # Verify liquidation price
```

---

## ⚠️ Wallet Policy Prerequisites

**For on-chain deposits/withdrawals** (not required for trading):

Before using deposit/withdraw functions, you need a wallet policy. Load the `wallet-policy` skill and propose:

```
- DENY: exportPrivateKey (never allow key export)
- ALLOW: * (allow all transactions with policy limits)
```

**Trading on Lighter does NOT require wallet policy** — it uses API keys, not on-chain transactions.

---

## 📖 References

- **API Documentation:** https://docs.lighter.xyz/trading/api
- **API Reference:** https://apidocs.lighter.xyz
- **Market Lookup Script:** `scripts/market_lookup.py`
- **Risk Calculator:** `scripts/risk_calculator.py`
- **Conditional Orders Guide:** `references/conditional-orders.md`

---

## 🛠️ Scripts

### `scripts/market_lookup.py`
Find any market with search:
```bash
python3 scripts/market_lookup.py gold      # Find gold
python3 scripts/market_lookup.py --category stocks  # All stocks
```

### `scripts/risk_calculator.py`
Calculate liquidation price before trading:
```bash
python3 scripts/risk_calculator.py BTC long 95000 10  # Symbol, side, entry, leverage
```

---

## ❓ Troubleshooting

### "401 Unauthorized" or "invalid account index"
- **Run the account finder:** `python3 skills/lighter-dex/scripts/find_account_index.py`
- Your account index is unique — don't guess it!
- Check `LIGHTER_API_KEY` and `LIGHTER_ACCOUNT_INDEX` in `.env`
- Ensure API key is registered at `app.lighter.xyz/apikeys`
- **Common mistake:** Using wrong account index or API key that doesn't match your wallet

### "Market not found"
- Use `lighter_markets_list(search="...")` to find correct symbol
- Gold = `XAU`, Silver = `XAG`, Oil = `USOIL`
- Stocks use ticker symbols: `NVDA`, `TSLA`, etc.

### "Insufficient balance"
- Check `lighter_holdings()` for available USDC
- Remember: funds in open orders are "in_orders", not "available"
- Deposit USDC via `app.lighter.xyz`

### "Invalid leverage"
- Leverage must be 1-100
- Some markets have lower max leverage (check `lighter_market(symbol)`)

---

## 💡 Pro Tips

1. **Always check liquidation** before entering: `lighter_liquidation()`
2. **Use stop-limit** instead of stop-market for better price control
3. **TWAP for large orders** — reduces slippage on big trades
4. **POST_ONLY for maker fees** — ensures you get maker rebates
5. **Monitor funding rates** — `lighter_funding(symbol)` before holding perps overnight
