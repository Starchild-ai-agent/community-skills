---
name: across-bridge
version: 1.0.0
description: Bridge ETH and ERC-20 tokens between EVM chains using Across Protocol v3. Supports Ethereum, Arbitrum, Optimism, Base, Polygon, BSC, Linea, and zkSync Era.
author: starchild
tags: [bridge, defi, cross-chain, across, evm]
---

# Across Protocol Bridge Skill

Bridge ETH and ERC-20 tokens between EVM chains using Across Protocol v3 SpokePool.

## Supported Chains

| Chain | Chain ID |
|-------|----------|
| Ethereum | 1 |
| Arbitrum | 42161 |
| Optimism | 10 |
| Base | 8453 |
| Polygon | 137 |
| BSC | 56 |
| Linea | 59144 |
| zkSync Era | 324 |

## Supported Tokens

| Token | Notes |
|-------|-------|
| ETH | Native ETH (bridged via WETH internally) |
| USDC | Native USDC where available |
| USDT | Major chains |
| WBTC | Ethereum, Arbitrum, Optimism |
| DAI | Major chains |

## Workflow

### 1. Get a Quote + Build Transaction

```bash
pip install requests eth-abi
python3 skills/across-bridge/scripts/bridge.py <from_chain_id> <to_chain_id> <amount_wei> <wallet_address> [token_symbol]
```

**Examples:**

Bridge 0.01415 ETH from Arbitrum to Ethereum:
```bash
python3 skills/across-bridge/scripts/bridge.py 42161 1 14150000000000000 0xYourWallet
```

Bridge 100 USDC from Base to Arbitrum:
```bash
python3 skills/across-bridge/scripts/bridge.py 8453 42161 100000000 0xYourWallet USDC
```

The script outputs a JSON object with:
- `to` — SpokePool contract address on origin chain
- `value` — ETH value to send (amount for ETH bridges, `"0"` for ERC-20)
- `data` — encoded `depositV3()` calldata
- `output_amount_wei` — amount you'll receive on destination
- `estimated_fill_time_sec` — estimated seconds to receive funds
- `note` — for ERC-20: reminder to approve the SpokePool before sending

### 2. ERC-20 Approval (skip for ETH)

For ERC-20 tokens (USDC, USDT, etc.), approve the SpokePool to spend your tokens first:

```python
# Approve call: token.approve(spokePool, amount)
# Use wallet_transfer with the token contract's approve() calldata
```

The script output includes a `note` field with the token address and SpokePool address when approval is needed.

### 3. Execute the Transaction

```python
wallet_transfer(
    to="<SpokePool address from script>",
    amount="<value from script>",   # amount_wei for ETH, "0" for ERC-20
    chain_id=<origin chain id>,
    data="<data from script>"
)
```

### 4. Track Deposit Status

After broadcasting, check fill status using the deposit tx hash:

```bash
python3 skills/across-bridge/scripts/bridge.py status <origin_chain_id> <deposit_tx_hash>
```

Or verify arrival directly:
```python
wallet_balance(chain=<destination_chain>)
```

Across relayers typically fill within **seconds to a few minutes**. The `estimated_fill_time_sec` from the quote gives a per-route estimate.

## Usage Example

> User: "Bridge 50 USDC from Base to Arbitrum"

1. Run the script with token=USDC, from=8453, to=42161, amount=50000000
2. Check the `note` field — approve USDC to SpokePool if needed
3. Call `wallet_transfer` with the encoded calldata
4. After tx confirms, run `status` check or call `wallet_balance(chain="arbitrum")` to confirm arrival

## Notes

- **ETH bridges**: `msg.value` = amount (no approval needed)
- **ERC-20 bridges**: `msg.value` = 0, token approval required first
- Fees are deducted from output amount (~0.01–0.1% typically, varies by route)
- Quotes are live from `app.across.to/api/suggested-fees` — valid for ~30s
- `exclusivityDeadline` is handled correctly whether the API returns an offset or absolute timestamp

## Dependencies

```
requests
eth-abi
```

Install: `pip install requests eth-abi`
