---
name: "@1365/across-bridge"
version: 1.0.0
description: "Fast cross-chain bridging via Across protocol. Use when user wants to bridge tokens between chains (ETH, USDC, USDT, WETH, etc.) with fast settlement times and low fees."
author: "Star Child"
tags: ["defi", "bridge", "cross-chain", "across", "ethereum", "arbitrum", "base", "optimism", "polygon"]

metadata:
  starchild:
    emoji: "🌉"
    skillKey: across-bridge
    requires:
      bins: [python3]
    install:
      - kind: pip
        package: requests

user-invocable: true
---

# Across Bridge

Ultra-fast cross-chain token bridging with ~2 minute settlement times.

## Prerequisites — Wallet Policy

Before executing any bridge, the wallet policy must be active.
Load the **wallet-policy** skill and propose the standard wildcard
policy (deny key export + allow `*`). This covers all across-bridge
operations across all chains.

## When to Use

Speed-critical cross-chain transfers:
- **Speed first:** 1-3 minutes vs 7+ days for native bridges
- **Major routes:** Arbitrum ↔ Base, ETH ↔ L2s, full mesh support
- **Auto-conversion:** USDT → USDC in single bridge operation
- **Fee range:** 0.05-0.5% (excellent for urgent transfers)

## Core Decision Pattern

**User request:** "Bridge X tokens from Chain A to Chain B"

1. **Single quote call** → `/swap` API returns everything: quote, fees, transactions
2. **Present quote** → Expected output, fees (%), settlement time (~2 min)  
3. **Execute if approved** → Send approvals (if needed) → Send bridge transaction
4. **Verify completion** → Check destination balance after ~2 minutes

**Key insight:** The `/swap` endpoint provides complete transaction data, not just quotes. One API call gives you everything needed to execute.

## Quote Interpretation

**Good bridge quotes:**
- Fee <0.5% (competitive)
- Settlement <3 minutes (fast route)
- Output amount close to input (minimal conversion slippage)

**Red flags:**
- Fee >1% (expensive route, warn user)
- Settlement >10 minutes (congested route)
- Large output difference (poor liquidity)

## Supported Assets & Chains

**Chains:** Ethereum, Arbitrum, Base, Optimism, Polygon  
**Tokens:** ETH, WETH, USDC, USDT, DAI (most liquid pairs)

**Popular routes:**
- Arbitrum USDT → Base USDC (DeFi optimal)
- Ethereum ETH → Arbitrum ETH (L1 → L2)
- Base USDC → Arbitrum USDC (L2 ↔ L2)

## Technical Implementation

Use the script for complex API interactions:

```python
# Load the API helper
exec(open('skills/across-bridge/scripts/across_api.py').read())

# Get quote + transaction data
result = get_across_quote(
    input_token="0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",  # USDT on Arbitrum
    output_token="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC on Base
    amount="5000000",  # 5 USDT (6 decimals)
    origin_chain=42161,  # Arbitrum
    dest_chain=8453,  # Base
    depositor="0x..."  # User wallet
)
```

**Response handling:**
- `result['expectedOutputAmount']` → tokens user will receive
- `result['fees']['total']` → fee breakdown with percentage
- `result['swapTx']` → ready-to-send bridge transaction
- `result['approvalTxns']` → approval transactions (if needed)
- `result['expectedFillTime']` → settlement minutes

## Error Patterns

**API failures:**
- Missing `depositor`: Include wallet address in all calls
- Invalid amount format: Use string wei amounts ("5000000"), not numbers
- Unsupported route: Not all token pairs supported on all chains

**Execution failures:**
- Insufficient balance: Check balance before quoting
- Missing approvals: Send `approvalTxns[]` before bridge transaction
- High slippage: Routes with >1% fees may have poor liquidity

Always extract fee percentage and settlement time from quotes. Show both to user before executing.