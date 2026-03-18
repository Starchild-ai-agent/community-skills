---
name: "@1368/polymarket-trade"
version: 1.0.0
description: Place real bets on Polymarket prediction markets using the agent wallet. Buy/sell outcome tokens, check balances, manage orders. Requires USDC on Polygon and wallet policy allowing EIP-712 signing.
author: starchild
tags: [polymarket, trading, prediction-markets, polygon, defi]
tools: [wallet_sign_typed_data, wallet_transfer, wallet_balance, bash, web_search, web_fetch]
metadata:
  starchild:
    emoji: "🎲"
    skillKey: polymarket-trade
---

# Polymarket Trading Skill

Trade on Polymarket CLOB using the agent's Polygon wallet in **EOA mode** (signature_type=0).

## Architecture

| Mode | sig_type | How it works | Gas? |
|---|---|---|---|
| **EOA (we use this)** | `0` | Agent wallet = signer AND maker. No proxy. | Yes — POL for one-time approvals |
| Safe/Proxy | `2` | Gnosis Safe proxy holds funds, EOA signs. | No (relayer pays) |

**Why EOA?** Simpler — no proxy deployment, no relayer. Only gas cost is ~$0.01 POL for one-time approvals. CLOB orders are gasless after that.

## First-Time Onboarding

If `POLY_API_KEY` is NOT in `.env`, follow these steps:

### 1. Get Wallet Address
Use `wallet_info` to get the agent's Polygon address → this becomes `POLY_WALLET`.

### 2. Create API Credentials
Sign an EIP-712 `ClobAuth` message and POST to CLOB to get API key/secret/passphrase.

Domain: `{ name: "ClobAuthDomain", version: "1", chainId: 137, verifyingContract: "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E" }`
Types: `ClobAuth: [address, timestamp(string), nonce(uint256), message(string)]`
Message: `{ address: WALLET, timestamp: NOW, nonce: "0", message: "This message attests that I control the given wallet" }`

1. Sign with `wallet_sign_typed_data`
2. POST `https://clob.polymarket.com/auth/api-key` (VPN required) with L1 auth headers
3. Save to `.env`: `POLY_API_KEY`, `POLY_SECRET`, `POLY_PASSPHRASE`, `POLY_WALLET`

### 3. Fund the Wallet
Send to the agent wallet address on Polygon:
- **USDC** (native Polygon USDC `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`) — betting bankroll
- **POL** (~1 POL / ~$0.20) — gas for approval txs

### 4. Approve USDC (One-Time, needs POL)
Approve both CTF Exchange contracts to spend USDC (max allowance):

```python
from eth_abi import encode
from eth_utils import function_signature_to_4byte_selector
sel = function_signature_to_4byte_selector("approve(address,uint256)")
USDC = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
# Approval 1: CTF Exchange
data1 = sel + encode(['address','uint256'], ['0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E', 2**256-1])
# wallet_transfer(to=USDC, amount="0", chain_id=137, data="0x"+data1.hex())
# Approval 2: CTF Exchange Neg-Risk
data2 = sel + encode(['address','uint256'], ['0xC5d563A36AE78145C45a50134d48A1215220f80a', 2**256-1])
# wallet_transfer(to=USDC, amount="0", chain_id=137, data="0x"+data2.hex())
```

### 5. Verify
```bash
python3 skills/polymarket-trade/scripts/poly_research.py balance
```
Should show USDC balance and allowance > 0. Setup complete.

### Wallet Policy
Agent needs: `eth_signTypedData_v4` (order signing) + `eth_sendTransaction` on chain 137 (approvals).

---

## VPN Requirement

**All CLOB API requests are geo-blocked.** The script auto-routes through `sc-vpn.internal:8080` (default: Germany). Gamma API is NOT blocked.

Set region in `.env`: `POLY_VPN_REGION=de`

## Contracts (Polygon)

| Contract | Address |
|---|---|
| CTF Exchange | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` |
| CTF Exchange (neg-risk) | `0xC5d563A36AE78145C45a50134d48A1215220f80a` |
| USDC | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` |

## ⚠️ MANDATORY: User Confirmation Before Betting

**NEVER place a bet without explicit user confirmation.** Always:
1. Research & analyze → present findings
2. Suggest bet with R/R → user reviews
3. User requests changes → adjust
4. **User explicitly confirms** → ONLY THEN execute

## Workflow: Link → Bet

### 1. Market Lookup
```bash
python3 skills/polymarket-trade/scripts/poly_research.py lookup "<polymarket_url>"
```

### 2. Research
- Read resolution criteria, end date, sources
- `web_search` for news, expert opinions, data
- Assess market price vs estimated fair probability
- Present: overview, prices, key facts, probability estimate, edge

### 3. Orderbook & R/R
```bash
python3 skills/polymarket-trade/scripts/poly_research.py orderbook <token_id>
python3 skills/polymarket-trade/scripts/poly_research.py rr <token_id> <YES|NO> <size_usd>
```

### 4. Present Suggested Bet (WAIT for confirmation)
```
📊 Suggested Bet:
  Market: "Will X happen?"
  Side: YES @ $0.35 (market: 35%, est: 55%)
  Size: $20 → 57.14 tokens
  Win: +$37.14 | Lose: -$20.00 | R/R: 1:1.86
```

### 5. Execute (ONLY after confirmation)
```bash
# a. Check balance
python3 skills/polymarket-trade/scripts/poly_research.py balance

# b. Prepare order (outputs domain/types/message/meta JSON)
python3 skills/polymarket-trade/scripts/poly_research.py prepare <token_id> BUY <price> <size> [neg_risk] [tick_size]

# c. Sign with wallet_sign_typed_data (primaryType: "Order")

# d. Post signed order
python3 -c "
import sys; sys.path.insert(0, '/data/workspace/skills/polymarket-trade/scripts')
from poly_research import post_signed_order
s, r = post_signed_order('<token_id>', '<signature>', <meta_dict>)
print(s, r)
"

# e. Verify
python3 skills/polymarket-trade/scripts/poly_research.py orders
```

## Other Commands

```bash
python3 skills/polymarket-trade/scripts/poly_research.py search "query"      # Find markets
python3 skills/polymarket-trade/scripts/poly_research.py positions           # Current positions
python3 skills/polymarket-trade/scripts/poly_research.py trades              # Recent trades
python3 skills/polymarket-trade/scripts/poly_research.py cancel <order_id>   # Cancel order
python3 skills/polymarket-trade/scripts/poly_research.py cancel_all          # Cancel all
```

## Notes
- Prices = probabilities: $0.55 = 55% implied, costs $0.55/token, pays $1 if correct
- tick_size: 0.01 or 0.001 (from market data — always check)
- neg_risk markets use CTF_EXCHANGE_NEG
- Orders are GTC by default, 0 bps maker fee
- Min order ~5 tokens (varies by market)
