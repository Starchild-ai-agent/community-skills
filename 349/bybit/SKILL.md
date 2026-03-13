---
name: "@349/bybit"
description: "Trade spot and perpetual futures on Bybit — market/limit/stop/trailing/TP+SL combo orders, account balances, positions, and market data. Supports Bybit Spot and Linear Perpetuals (USDT). Requires BYBIT_API_KEY and BYBIT_SECRET in environment for trading. Use when trading on Bybit, checking Bybit balances or positions, placing TP+SL combo orders, or accessing Bybit market data."
version: 1.0.1
author: starchild
tags: [cex, bybit, trading, spot, futures, perpetuals]
---

# Bybit Skill

Trade on Bybit — one of the top derivatives exchanges — directly from Starchild.

Supports **Spot** and **Linear Perpetuals (USDT-margined)**. Uses the bundled `scripts/ccex_core.py` engine.

---

## Setup

### 1. Get your Bybit API Keys

1. Log in to [bybit.com](https://www.bybit.com)
2. Go to **Account → API** (or My Profile → API Management)
3. Create API key — enable **Read/Write** for Spot and Derivatives
4. Save your API key and secret

### 2. Add to environment

Add to `workspace/.env`:

```
BYBIT_API_KEY=your_api_key_here
BYBIT_SECRET=your_secret_here
```

### 3. Install dependencies

```bash
pip install --break-system-packages ccxt
```

### 4. Optional but recommended (persist across restarts)

```bash
grep -q "pip install --break-system-packages ccxt" workspace/setup.sh || \
  echo "pip install --break-system-packages ccxt" >> workspace/setup.sh
```

---

## What You Can Do

### Market Data (No API key needed)

- Get current price / ticker
- View orderbook
- Candlestick OHLCV data
- List all markets

### Account (API key required)

- Check spot and derivatives balances
- View open orders
- View order history
- View open positions (perpetuals)

### Trading (API key required)

- Market orders
- Limit orders
- Stop market / stop limit
- Take profit orders
- Trailing stop (amount-based)
- **TP + SL attached to entry order in one shot**
- Futures orders with reduce-only

---

## Workflow

**ALWAYS follow this order:**

1. Check balance before trading
2. Get current price
3. Place order
4. Verify via positions or open orders

---

## How to Execute

```bash
python3 skills/bybit/scripts/ccex_core.py <action> --exchange bybit [options]
```

### Examples

**Get ETH/USDT price:**
```bash
python3 skills/bybit/scripts/ccex_core.py ticker --exchange bybit --symbol ETH/USDT
```

**Check balances:**
```bash
python3 skills/bybit/scripts/ccex_core.py balance --exchange bybit
```

**Buy 0.01 ETH at market:**
```bash
python3 skills/bybit/scripts/ccex_core.py order --exchange bybit \
  --symbol ETH/USDT --side buy --type market --amount 0.01
```

**Limit buy ETH at $2,800:**
```bash
python3 skills/bybit/scripts/ccex_core.py order --exchange bybit \
  --symbol ETH/USDT --side buy --type limit --amount 0.01 --price 2800
```

**Stop loss at $2,500:**
```bash
python3 skills/bybit/scripts/ccex_core.py order --exchange bybit \
  --symbol ETH/USDT --side sell --type stop --amount 0.01 --stop_price 2500
```

**Trailing stop (amount-based, $50 trail):**
```bash
python3 skills/bybit/scripts/ccex_core.py order --exchange bybit \
  --symbol ETH/USDT --side sell --type stop --amount 0.01 --trailing_delta 50
```

**Futures: Long 0.1 ETH perpetual:**
```bash
python3 skills/bybit/scripts/ccex_core.py order --exchange bybit \
  --symbol ETH/USDT --side buy --type market --amount 0.1 --futures
```

**Close futures position (reduce-only):**
```bash
python3 skills/bybit/scripts/ccex_core.py order --exchange bybit \
  --symbol ETH/USDT --side sell --type market --amount 0.1 --futures --reduce_only
```

**View open positions:**
```bash
python3 skills/bybit/scripts/ccex_core.py position --exchange bybit --futures
```

**Cancel order:**
```bash
python3 skills/bybit/scripts/ccex_core.py cancel --exchange bybit \
  --symbol ETH/USDT --order_id abc123
```

---

## Bybit-Specific Notes

### TP + SL Combo
Bybit supports attaching both a take profit AND stop loss to an entry order simultaneously — use the raw Bybit API via a custom params dict in the script. For simple stop or TP, the unified CCXT API handles it.

For combined TP+SL on entry, use this pattern in a custom script:
```python
exchange.create_order("ETH/USDT", "market", "buy", 0.1, None, {
    "takeProfit": "3200",
    "stopLoss": "2500",
    "tpTriggerBy": "LastPrice",
    "slTriggerBy": "LastPrice",
})
```

### Unified Account
Bybit uses a "Unified Trading Account" — spot, derivatives, and options share the same margin pool. CCXT handles this automatically.

### OCO on Bybit
Bybit does not support native OCO. `ccex-core` simulates OCO with two separate orders and warns you to cancel one manually when the other fills.

### Rate Limits
Bybit allows 10 requests/second (order endpoints). CCXT handles this automatically.

---

## First-Run Sanity Check

Run this after setup to verify everything before placing trades:

```bash
python3 skills/bybit/scripts/ccex_core.py ticker --exchange bybit --symbol ETH/USDT
```

If credentials are configured, also test private access:

```bash
python3 skills/bybit/scripts/ccex_core.py balance --exchange bybit
```

---

## Error Handling

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `Missing dependency: ccxt` | ccxt not installed | `pip install --break-system-packages ccxt` |
| `Missing API credentials for bybit` | BYBIT_API_KEY/BYBIT_SECRET not set | Add to `workspace/.env` |
| `10003 Invalid API key` | Wrong key in .env | Re-check BYBIT_API_KEY |
| `10006 Too many visits` | Rate limit hit | CCXT handles; reduce call frequency |
| `Insufficient balance` | Not enough funds | Check balance first |
| `110014 Reduce-only position does not exist` | No open position | Check positions first |
