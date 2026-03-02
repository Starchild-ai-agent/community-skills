# Lighter DEX API Reference

## Base URLs

- **Mainnet:** `https://mainnet.zklighter.elliot.ai`
- **Testnet:** `https://testnet.zklighter.elliot.ai`

## Authentication

Lighter uses **wallet-signed API keys**. Each API key is a private key that controls an index (2-255) on your account.

**To get an API key:**
1. Go to `app.lighter.xyz/apikeys`
2. Click "Generate API Key"
3. Choose index 2-255 (0 and 1 are reserved)
4. Copy the private key — this is your `LIGHTER_API_KEY`
5. Store it securely (whoever has this key controls trading on your account)

**Authentication format:**
```python
from lighter import SignerClient

client = SignerClient(
    url="https://mainnet.zklighter.elliot.ai",
    account_index=2,
    api_private_keys={2: "your_api_private_key"}
)
```

---

## Public Endpoints (No Auth Required)

### Get All Markets

```python
from lighter.api.info_api import InfoApi
from lighter.configuration import Configuration
from lighter.api_client import ApiClient

config = Configuration()
config.host = "https://mainnet.zklighter.elliot.ai"
api_client = ApiClient(configuration=config)
info_api = InfoApi(api_client=api_client)

markets = info_api.get_v1_info_markets_get()
```

**Returns:** Array of market objects with:
- `market_id`: Unique ID (BTC=1, ETH=0, XAU=92)
- `symbol`: Trading symbol ("BTC", "ETH", "XAU")
- `base_asset`: Base currency
- `quote_asset`: Quote currency (always "USDC")
- `status`: "Normal", "PostOnly", "CancelOnly"
- `mark_price`: Current mark price
- `index_price`: Index price
- `funding_rate`: Current funding rate
- `open_interest`: Total open interest
- `volume_24h`: 24h trading volume

### Get Orderbook

```python
orderbook = info_api.get_v1_info_orderbook_get(
    market_id=1,  # BTC
    limit=20
)
```

**Returns:**
```python
{
    "bids": [[price, size], [price, size], ...],
    "asks": [[price, size], [price, size], ...],
    "time": timestamp
}
```

### Get Candles (OHLCV)

```python
candles = info_api.get_v1_info_candles_get(
    market_id=1,
    interval="1h",  # 1m, 5m, 15m, 1h, 4h, 1d, 1w
    limit=100
)
```

**Returns:** Array of `[timestamp, open, high, low, close, volume]`

### Get Funding Rate

```python
funding = info_api.get_v1_info_funding_get(
    market_id=1
)
```

**Returns:**
```python
{
    "market_id": 1,
    "funding_rate": 0.0001,
    "predicted_funding_rate": 0.00012,
    "next_funding_time": timestamp
}
```

### Get Recent Trades

```python
trades = info_api.get_v1_info_trades_get(
    market_id=1,
    limit=50
)
```

**Returns:** Array of trades with `price`, `size`, `side`, `timestamp`

---

## Private Endpoints (Auth Required)

### Get Account Info

```python
account = client.get_account()
```

**Returns:**
```python
{
    "l1_address": "0x...",
    "total_equity": 10000.00,
    "usdc_balance": 5000.00,  # Available to trade
    "total_pnl": 500.00,
    "unrealized_pnl": 200.00,
    "realized_pnl": 300.00
}
```

### Get Positions

```python
positions = client.get_positions()
```

**Returns:** Array of positions:
```python
{
    "market_id": 1,
    "symbol": "BTC",
    "size": 0.5,  # Positive = long, negative = short
    "entry_price": 95000.00,
    "mark_price": 96000.00,
    "unrealized_pnl": 500.00,
    "leverage": 10,
    "liquidation_price": 85500.00
}
```

### Get Open Orders

```python
orders = client.get_open_orders()
```

**Returns:** Array of orders:
```python
{
    "order_id": 123456,
    "market_id": 1,
    "symbol": "BTC",
    "side": "buy",
    "type": "LIMIT",
    "price": 94000.00,
    "size": 0.1,
    "filled_size": 0.0,
    "remaining_size": 0.1,
    "status": "OPEN",
    "created_at": timestamp
}
```

### Place Order

```python
# Limit order
order = client.place_limit_order(
    market_id=1,
    side="buy",
    size=0.1,
    price=94000.00,
    reduce_only=False
)

# Market order
order = client.place_market_order(
    market_id=1,
    side="sell",
    size=0.1,
    reduce_only=True
)

# Stop loss
order = client.place_stop_order(
    market_id=1,
    side="sell",
    size=0.1,
    trigger_price=90000.00,
    reduce_only=True
)

# Take profit
order = client.place_take_profit_order(
    market_id=1,
    side="sell",
    size=0.1,
    trigger_price=100000.00,
    reduce_only=True
)
```

**Returns:**
```python
{
    "order_id": 123456,
    "status": "OPEN",
    "filled_size": 0.0,
    "remaining_size": 0.1
}
```

### Cancel Order

```python
result = client.cancel_order(
    market_id=1,
    order_id=123456
)
```

### Cancel All Orders

```python
# Cancel all
results = client.cancel_all_orders()

# Cancel for specific market
results = client.cancel_all_orders(market_id=1)
```

### Modify Order

```python
result = client.modify_order(
    market_id=1,
    order_id=123456,
    size=0.2,
    price=93000.00
)
```

### Update Leverage

```python
result = client.update_leverage(
    market_id=1,
    leverage=10  # 1x to 100x
)
```

### Get Historical Orders

```python
orders = client.get_historical_orders(
    market_id=1,
    limit=50
)
```

### Get User Trades

```python
trades = client.get_user_trades(
    market_id=1,
    limit=50
)
```

---

## Market IDs Reference

| Symbol | Market ID | Category |
|--------|-----------|----------|
| ETH | 0 | Crypto |
| BTC | 1 | Crypto |
| SOL | 2 | Crypto |
| DOGE | 3 | Crypto |
| XRP | 4 | Crypto |
| ... | ... | ... |
| XAU | 92 | Commodity (Gold) |
| XAG | 93 | Commodity (Silver) |
| AAPL | 100 | Stock |
| MSFT | 101 | Stock |
| NVDA | 102 | Stock |
| TSLA | 103 | Stock |
| EURUSD | 150 | Forex |
| GBPUSD | 151 | Forex |

**Note:** Use `lighter_market()` or the public API to get the full current list.

---

## Order Types

| Type | Method | Parameters | Behavior |
|------|--------|------------|----------|
| **Limit** | `place_limit_order` | `price` (required) | Rests on book until filled or cancelled |
| **Market** | `place_market_order` | None (uses best price) | Fills immediately at best available |
| **Stop Loss** | `place_stop_order` | `trigger_price` (required) | Triggers market order when price hits trigger |
| **Take Profit** | `place_take_profit_order` | `trigger_price` (required) | Triggers market order when price hits trigger |

**Common parameters:**
- `reduce_only`: If `True`, order only reduces existing position (never opens new)
- `size`: Order size in base asset (e.g., 0.1 for 0.1 BTC)

---

## Error Codes

| HTTP Code | Meaning | Common Causes |
|-----------|---------|---------------|
| 400 | Bad Request | Invalid parameters, wrong symbol name, size too small |
| 401 | Unauthorized | Invalid API key, key not registered |
| 403 | Forbidden | API key lacks permissions, account restricted |
| 429 | Rate Limited | Too many requests (wait and retry) |
| 500 | Server Error | Lighter backend issue (retry later) |

**Common error messages:**
- `"Insufficient balance"` — Not enough USDC for margin
- `"Order size too small"` — Below minimum order size for that market
- `"Invalid price"` — Price outside acceptable range
- `"Position not found"` — Trying to close a position you don't have
- `"Order not found"` — Order ID doesn't exist or already filled/cancelled

---

## Rate Limits

- **Public endpoints:** 100 requests/minute
- **Private endpoints:** 60 requests/minute
- **Order placement:** 10 orders/second per account

**Best practices:**
- Cache market data locally (prices update every second)
- Use WebSocket for real-time updates (if available)
- Batch operations when possible

---

## WebSocket (Real-Time Data)

Lighter supports WebSocket for real-time market data:

```python
import websocket
import json

ws_url = "wss://mainnet.zklighter.elliot.ai/ws"
ws = websocket.WebSocket()
ws.connect(ws_url)

# Subscribe to orderbook
ws.send(json.dumps({
    "type": "subscribe",
    "channel": "orderbook",
    "market_id": 1
}))

# Listen for updates
while True:
    data = json.loads(ws.recv())
    print(data)
```

**Available channels:**
- `orderbook` — Real-time orderbook updates
- `trades` — Real-time trade executions
- `ticker` — Price ticker updates
- `funding` — Funding rate updates

---

## Deposit & Withdrawal

**These are on-chain operations, NOT available via API:**

1. **Deposit:**
   - Go to `app.lighter.xyz`
   - Connect wallet
   - Click "Deposit"
   - Send USDC to the Lighter bridge contract

2. **Withdraw:**
   - Go to `app.lighter.xyz`
   - Click "Withdraw"
   - Specify amount
   - Confirm transaction (takes ~5 minutes to settle)

**Minimum deposit:** 10 USDC  
**Withdrawal fee:** ~1 USDC (bridge fee)

---

## Best Practices

1. **Always check positions before trading** — Know your existing exposure
2. **Use reduce_only for closing** — Prevents accidentally opening opposite position
3. **Monitor funding rates** — High positive = longs pay shorts (expensive to hold)
4. **Check orderbook depth** — Market orders can slip in thin markets
5. **Use limit orders when possible** — Maker fees are often lower than taker
6. **Set stop losses** — Protect against liquidation
7. **Start small** — Test with small sizes before scaling
8. **Monitor liquidation prices** — Keep sufficient margin buffer

---

## Security Notes

⚠️ **Your API key is as powerful as your wallet private key for trading purposes:**

- Anyone with your API key can trade on your account
- They cannot withdraw funds (withdrawals require wallet signature)
- Store API keys securely (environment variables, secret managers)
- Rotate keys periodically
- Never commit API keys to git or share them publicly

**To revoke an API key:**
1. Go to `app.lighter.xyz/apikeys`
2. Delete the key
3. Generate a new one if needed
