# 🏮 Lighter DEX Setup Guide

**Complete setup in 5 minutes** — get your API keys and account index configured.

---

## Step 1: Generate API Key on Lighter

1. Go to **https://app.lighter.xyz/apikeys**
2. Connect your wallet (MetaMask)
3. Click **"Create API Key"**
4. **IMMEDIATELY COPY BOTH VALUES:**
   - **Public Key** (shown permanently)
   - **Private Key** (shown ONCE — save it in a password manager!)
5. Note the **Index number** (0, 1, 2, etc.)

⚠️ **WARNING:** The private key is shown only once! If you lose it, you must delete the key and create a new one.

---

## Step 2: Find Your Account Index

Your Lighter account has a unique index number. Find it with:

```bash
python3 skills/lighter-dex/scripts/find_account_index.py
```

**The script will:**
1. Ask for your wallet address (the one you connected to Lighter)
2. Have you sign a message in MetaMask (proves ownership)
3. Look up your account index on Lighter's servers
4. Show all registered API keys
5. Optionally test your API key

**Example output:**
```
✅ FOUND YOUR ACCOUNT!
   Account Index: 717443
   Wallet: 0x86E72c27e41DC824AFd909B9424730e24CB9FAaB

📋 Registered API Keys:
   - Index 0: 64f2eea48c56fbd0...

💾 SAVE THIS:
   ACCOUNT_INDEX=717443
```

---

## Step 3: Configure Environment

Add to your `.env` file:

```bash
# Lighter DEX Configuration
LIGHTER_ACCOUNT_INDEX=717443        # From Step 2
LIGHTER_API_KEY=your_private_key    # From Step 1 (80 hex characters)
```

---

## Step 4: Test Connection

```bash
# Test account connection
python3 -c "
from lighter_sdk import LighterClient
client = LighterClient('https://mainnet.zklighter.elliot.ai')
# You'll need to add your account index and API key
"
```

Or use the skill commands:
```
lighter_account()
lighter_holdings()
```

---

## Troubleshooting

### "invalid account index"
- You're using the wrong account index
- Run `find_account_index.py` to get the correct one
- Don't guess — every wallet has a unique index

### "API key not found"
- The API key isn't registered to your account
- Go back to `app.lighter.xyz/apikeys` and create a new one
- Make sure you copied the full private key (80 hex characters)

### "401 Unauthorized"
- Check both `LIGHTER_ACCOUNT_INDEX` and `LIGHTER_API_KEY` in `.env`
- Verify the private key matches the public key shown on the website
- Try deleting and recreating the API key

---

## Security Notes

- **Never share your API private key** — it controls your Lighter account
- Store it in a password manager (1Password, Bitwarden, etc.)
- The private key is different from your MetaMask private key
- You can delete API keys anytime on `app.lighter.xyz/apikeys`

---

## Next Steps

Once configured, you can:
- ✅ Check balances: `lighter_holdings()`
- ✅ View positions: `lighter_positions()`
- ✅ Place orders: `lighter_order()`
- ✅ Set stop losses: `lighter_stop_loss()`
- ✅ Use TWAP: `lighter_twap()`
- ✅ Trade any market: crypto, stocks, commodities, forex

**Markets:**
- Crypto: `BTC`, `ETH`, `SOL`
- Stocks: `NVDA`, `TSLA`, `AAPL`
- Commodities: `XAU` (Gold), `XAG` (Silver)
- Forex: `EURUSD`, `GBPUSD`

---

**Need help?** Run the diagnostic script:
```bash
python3 skills/lighter-dex/scripts/find_account_index.py
```
