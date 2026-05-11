# HL Copy Trader — API & Client Reference

## HyperliquidClient Methods Used

```python
from skills.hyperliquid.client import HyperliquidClient
c = HyperliquidClient()

# Address
my_addr = await c._get_address()

# Read state
acct = await c.get_account_state(address)  # marginSummary, assetPositions
orders = await c.get_open_orders(address)  # list of orders
fills = await c._info('userFills', user=address)  # list of fills

# Trade
await c.update_leverage(coin, leverage, is_cross=True)
await c.market_open(coin, is_buy, size)         # IoC market order
await c.market_close(coin, address)             # close full position
await c.place_order(coin, is_buy, size, price, order_type='limit')
await c.cancel_order(coin, oid)                 # cancel by oid
await c.cancel_all_orders(coin)

# Deposit
await c.deposit_usdc(amount)  # min 5 USDC, from Arbitrum wallet
```

## Order Status Shapes

```python
r = await c.place_order(...)
statuses = r['response']['data']['statuses']
st = statuses[0]

# Resting (limit order sitting in book)
my_oid = st['resting']['oid']

# Filled (market order or limit crossed)
avg_px = st['filled']['avgPx']
my_oid = st['filled']['oid']

# Error
err = st.get('error')  # string describing what went wrong
```

## HL Info API Shape

```python
# clearinghouseState
{
  "marginSummary": {
    "accountValue": "1000.00",
    "totalMarginUsed": "50.00",
    "withdrawable": "950.00"
  },
  "assetPositions": [
    {
      "position": {
        "coin": "BTC",
        "szi": "-0.001",        # negative = short
        "entryPx": "80000",
        "leverage": {"type": "cross", "value": 3},
        "unrealizedPnl": "5.00",
        "liquidationPx": "120000",
        "marginUsed": "25.00"
      }
    }
  ]
}

# openOrders
[
  {
    "coin": "BTC",
    "side": "B",            # B=buy, A=sell/ask
    "sz": "0.001",
    "limitPx": "75000",
    "oid": 12345678,
    "timestamp": 1234567890000
  }
]
```

## Minimum Sizes

| Coin | Min size | Size decimals |
|------|----------|---------------|
| BTC  | 0.001    | 3             |
| ETH  | 0.01     | 2             |
| SOL  | 0.1      | 1             |

Always `max(scaled_size, min_size)` before placing orders.

## State JSON Schema

```json
{
  "paused": false,
  "target_address": "0x...",
  "my_capital": 1000.0,
  "scale_ratio": 0.01,
  "stop_value": 600.0,
  "sync_interval": 5,
  "max_leverage": 10,
  "copy_assets": "all",
  "min_order_size": 10.0,
  "lang": "zh",
  "paul_orders": {
    "target_oid_string": "my_oid_string"
  },
  "started_at": "2025-01-01T00:00:00",
  "job_id": "interval_abc123",
  "last_sync": "2025-01-07T10:00:00",
  "last_account_value": 985.0
}
```
