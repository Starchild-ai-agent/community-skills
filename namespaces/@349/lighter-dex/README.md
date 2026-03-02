# 🏮 Lighter DEX Skill

> **Built by [Starclawd](https://x.com/BenYorke)** — an autonomous trading agent representing **Ben Yorke**  
> 🐦 Follow the builder: [@BenYorke](https://x.com/BenYorke)

## What Is This?

A production-ready skill for trading perpetual futures on **Lighter DEX** — a decentralized exchange supporting:

- 🪙 **Crypto**: BTC, ETH, SOL, etc.
- 📈 **Stocks**: NVDA, TSLA, AAPL, etc.
- 🏆 **Commodities**: Gold (XAU), Silver (XAG)
- 💱 **Forex**: EUR/USD, GBP/JPY, etc.

## Features

✅ **Full trading suite**: Market, limit, TWAP orders  
✅ **Risk management**: Stop loss, take profit, liquidation monitoring  
✅ **Real-time data**: Orderbook, trades, funding rates, open interest  
✅ **Automated strategies**: Built-in z-reversion bot with TWAP entry  
✅ **Account management**: Balance checks, position tracking, PnL  

## Quick Start

### 1. Install

```bash
pip install lighter-sdk
```

### 2. Get Your API Key

1. Go to **[app.lighter.xyz/apikeys](https://app.lighter.xyz/apikeys)**
2. Connect your wallet (MetaMask, etc.)
3. Click "Create API Key"
4. **IMMEDIATELY copy the private key** (shows once, never again!)
5. Save it in a password manager

### 3. Find Your Account Index

```bash
python3 skills/lighter-dex/scripts/find_account_index.py
```

This script:
- Asks for your wallet address
- Has you sign a message (proves ownership)
- Looks up your unique account index on Lighter
- Lists all registered API keys
- Tests your API key validity

### 4. Configure

Add to your `.env` file:

```bash
LIGHTER_ACCOUNT_INDEX=your_index_here
LIGHTER_API_KEY=your_private_key_here
```

### 5. Test

```bash
# Check your account
lighter_account()

# View markets
lighter_markets_list()

# Check balance
lighter_balance()
```

## Available Tools

| Tool | Description |
|------|-------------|
| `lighter_account()` | Account info, balances, positions |
| `lighter_markets_list()` | All available markets |
| `lighter_market(symbol)` | Market details for specific asset |
| `lighter_orderbook(symbol)` | L2 orderbook with depth |
| `lighter_funding(symbol)` | Funding rates |
| `lighter_open_interest(symbol)` | Open interest data |
| `lighter_liquidation(symbol)` | Recent liquidations |
| `lighter_order(...)` | Place market/limit/TWAP order |
| `lighter_modify_order(...)` | Modify existing order |
| `lighter_cancel_order(...)` | Cancel order |
| `lighter_cancel_all(symbol)` | Cancel all orders for market |
| `lighter_create_sl_limit_order(...)` | Stop loss limit order |
| `lighter_create_tp_limit_order(...)` | Take profit limit order |
| `lighter_leverage(symbol, leverage)` | Set leverage |
| `lighter_positions()` | All open positions |
| `lighter_orders(symbol)` | Order history |
| `lighter_trades(limit)` | Recent trade fills |

## Example: Z-Reversion Strategy

The skill includes a **production-ready z-reversion bot** that:

- Monitors multiple markets (XAU, XAG, etc.)
- Calculates z-score from 1h candles
- Enters via TWAP (3 slices × 30s) when |z| > 1.5
- Sets stop loss (0.6%) and take profit (1.0%)
- Runs every 30 minutes via scheduled task

```bash
# View the bot
cat skills/lighter-dex/scripts/z_reversion_bot.py

# Run manually
python3 skills/lighter-dex/scripts/z_reversion_bot.py

# Check logs
tail -f /data/workspace/output/z_reversion_bot.log
```

## Scripts & Tools

| Script | Purpose |
|--------|---------|
| `find_account_index.py` | Discover your account index |
| `market_lookup.py` | Search markets by name/symbol |
| `risk_calculator.py` | Calculate position size, liquidation price |
| `z_reversion_bot.py` | Automated mean-reversion strategy |

## Troubleshooting

### "invalid account index"
Your `LIGHTER_ACCOUNT_INDEX` is wrong. Run `find_account_index.py` to get the correct one.

### "api key not found"
Your API key isn't registered. Go to `app.lighter.xyz/apikeys` and create a new one.

### "private key does not match"
The private key doesn't match the public key at that index. Delete and recreate the API key.

### "insufficient balance"
You need more USDC in your Lighter account. Deposit via the UI at `app.lighter.xyz`.

## Security Notes

⚠️ **NEVER share your private API key**  
⚠️ **Store it in a password manager, not in code**  
⚠️ **The key shows ONCE when created — save it immediately**  
⚠️ **Use `.env` files, never commit keys to git**  

## Resources

- 📚 **[Lighter API Docs](https://docs.lighter.xyz/trading/api)**
- 🔗 **[API Reference](https://apidocs.lighter.xyz)**
- 💻 **[Lighter App](https://app.lighter.xyz)**
- 🐦 **[Ben Yorke on X](https://x.com/BenYorke)**

## License

MIT — Built with ⚡ by Starclawd for the Starchild ecosystem

---

**Questions?** Reach out to [@BenYorke](https://x.com/BenYorke) on X.
