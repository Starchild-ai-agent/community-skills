---
name: "@349/binance"
description: "Trade spot and futures on Binance — market/limit/stop/trailing/OCO orders, account balances, order history, and market data. Supports both Binance Spot and Binance Futures (USDM). Requires BINANCE_API_KEY and BINANCE_SECRET in environment for trading; market data is public. Use when trading on Binance, checking Binance balances, placing OCO orders, or accessing Binance market data."
version: 1.0.0
author: starchild
tags: [cex, binance, trading, spot, futures]
---

# Binance Skill

Trade on Binance — the world's largest CEX — directly from Starchild.

Supports **Spot** and **USDM Futures**. Uses the bundled `scripts/ccex_core.py` engine under the hood.

---

## Setup

### 1. Get your Binance API Keys

1. Log in to [binance.com](https://www.binance.com)
2. Go to **Profile → API Management**
3. Create a new API key — enable **Spot & Margin Trading** and **Futures Trading**
4. Save your API key and secret

### 2. Add to environment

Add to `workspace/.env`:

```
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET=your_secret_here
```

### 3. Install dependencies

```bash
pip install --break-system-packages ccxt
```

---

## What You Can Do

### Market Data (No API key needed)

- Get current price / ticker
- View orderbook (bids & asks)
- Candlestick OHLCV data
- List all available markets

### Account (API key required)

- Check spot and futures balances
- View open orders
- View order history
- View open futures positions

### Trading (API key required)

- Market orders
- Limit orders
- Stop market / stop limit orders
- Take profit orders
- Trailing stop orders (delta-based)
- **OCO orders (native Binance support)**
- Futures orders with reduce-only

---

## Workflow

**ALWAYS follow this order:**

1. Check balance before trading
2. Get current price / ticker
3. Place order
4. Confirm order via open orders or history

---

## How to Execute

All actions run via the bundled engine. Use `bash` to call:

```bash
python3 skills/binance/scripts/ccex_core.py <action> --exchange binance [options]
```

### Examples

**Get BTC/USDT price:**
```bash
python3 skills/binance/scripts/ccex_core.py ticker --exchange binance --symbol BTC/USDT
```

**Check balances:**
```bash
python3 skills/binance/scripts/ccex_core.py balance --exchange binance
```

**Buy 0.001 BTC at market:**
```bash
python3 skills/binance/scripts/ccex_core.py order --exchange binance \
  --symbol BTC/USDT --side buy --type market --amount 0.001
```

**Place limit buy at $90,000:**
```bash
python3 skills/binance/scripts/ccex_core.py order --exchange binance \
  --symbol BTC/USDT --side buy --type limit --amount 0.001 --price 90000
```

**Stop loss at $85,000:**
```bash
python3 skills/binance/scripts/ccex_core.py order --exchange binance \
  --symbol BTC/USDT --side sell --type stop --amount 0.001 --stop_price 85000
```

**Trailing stop (500 BIPS = 5%):**
```bash
python3 skills/binance/scripts/ccex_core.py order --exchange binance \
  --symbol BTC/USDT --side sell --type stop --amount 0.001 --trailing_delta 500
```

**OCO order — limit sell at $100k, stop at $85k:**
```bash
python3 skills/binance/scripts/ccex_core.py oco --exchange binance \
  --symbol BTC/USDT --side sell --amount 0.001 \
  --price 100000 --stop_price 85000 --stop_limit_price 84900
```

**Futures: Long 0.01 BTC on Binance USDM:**
```bash
python3 skills/binance/scripts/ccex_core.py order --exchange binance \
  --symbol BTC/USDT --side buy --type market --amount 0.01 --futures
```

**Cancel an order:**
```bash
python3 skills/binance/scripts/ccex_core.py cancel --exchange binance \
  --symbol BTC/USDT --order_id 12345678
```

---

## Binance-Specific Notes

### OCO Orders
Binance is the only major exchange with **native OCO support**. An OCO places a limit order and a stop-limit order simultaneously — when one fills, the other is automatically cancelled.

Parameters:
- `--price` — the limit (take profit) price
- `--stop_price` — the stop trigger price
- `--stop_limit_price` — the actual limit price when stop triggers (optional, defaults to 0.1% below stop)

### Futures vs Spot
Add `--futures` flag to any order command to route to **Binance USDM Futures** instead of spot.

### Rate Limits
Binance rate limits: 1200 requests/minute (weight-based). CCXT handles this automatically with `enableRateLimit: true`.

### Testnet
To use Binance testnet, set:
```
BINANCE_API_KEY=your_testnet_key
BINANCE_SECRET=your_testnet_secret
```
And modify the exchange config in `skills/binance/scripts/ccex_core.py` to add `"test": True` to options.

---

## Error Handling

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `Invalid API Key` | Wrong key in .env | Re-check BINANCE_API_KEY |
| `Timestamp for this request` | Clock skew | Sync system clock |
| `MIN_NOTIONAL` | Order too small | Increase amount (min ~$10 USDT) |
| `Insufficient balance` | Not enough funds | Check balance first |
| `OCO price rules violation` | Price ordering wrong | limit > current price > stop for sell OCO |
