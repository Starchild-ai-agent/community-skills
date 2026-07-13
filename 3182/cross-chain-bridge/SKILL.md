---
name: "@3182/cross-chain-bridge"
version: 1.0.0
description: Single-command cross-chain token bridge for USDC/USDT across 6 EVM chains with Alchemy Account Abstraction gas sponsorship.
author: user-3182
tags:
  - defi
  - bridge
  - cross-chain
  - alchemy
  - usdc
  - usdt
---

# Cross-Chain Bridge

Single-command cross-chain token bridge for USDC/USDT across 6 EVM chains using Alchemy Account Abstraction (ERC-4337) with gas-sponsored transactions.

## Supported Chains

- Arbitrum (chainId 42161)
- Base (chainId 8453)
- Ethereum (chainId 1)
- Optimism (chainId 10)
- Polygon (chainId 137)
- BSC (chainId 56)

## Required Environment

- `ALCHEMY_API_KEY` — Alchemy API key with Account Abstraction enabled

## Usage

```bash
# Bridge 5 USDC from Arbitrum to Base
python3 bridge.py --amount 5 --token USDC --from arbitrum --to base

# Bridge 10 USDT from Base to Optimism
python3 bridge.py --amount 10 --token USDT --from base --to optimism

# List supported chains
python3 bridge.py --list-chains
```

## How It Works

1. Creates an Alchemy SmartAccount with LightSigner (gasless transactions)
2. Approves the Across Protocol router to spend the token
3. Executes the bridge via Across Protocol
4. Waits for on-chain confirmation
5. Reports the transaction hash

## Key Features

- **Gasless**: No ETH needed — Alchemy sponsors gas via ERC-4337
- **Single command**: All chain IDs, contract addresses, and routing logic hardcoded
- **Auto-approve**: Token approval handled automatically
- **6 chains**: Arbitrum, Base, Ethereum, Optimism, Polygon, BSC
- **Cost**: ~$0.035 per operation (0.3% bridge fee only)

## Troubleshooting

- "ALCHEMY_API_KEY not set" — Export the key or add to workspace/.env
- "Insufficient token balance" — Check wallet balance on source chain
- "Bridge timeout" — Across bridge usually completes in 2-5 minutes
