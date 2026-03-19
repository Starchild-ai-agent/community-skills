---
name: "@1826/woofi-zero-slippage"
description: Optimize token swaps with zero/near-zero slippage using WOOFi's sPMM across 12+ chains. Query routes, calculate price impact, execute swaps with minimal slippage.
version: 1.0.0
author: Starchild
tags: [woofi, swap, zero-slippage, dex, cross-chain, defi, optimization]
display_name: 🦊 WOOFi Zero-Slippage Swap Optimizer
---

# WOOFi Zero-Slippage Swap Optimizer

Optimize token swaps with **zero/near-zero slippage** using WOOFi's sPMM (Synthetic Proactive Market Making) algorithm across 12+ EVM chains.

## What is WOOFi?

WOOFi uses **Synthetic Proactive Market Making (sPMM)** to simulate CEX-style orderbooks on-chain:
- **Near-zero slippage** for most trades
- **Tighter spreads** matching CEX prices
- **Deeper liquidity** through synthetic orderbook simulation

## Supported Chains

| Chain | Network ID | Quote Token | WooRouterV2 |
|-------|-----------|-------------|-------------|
| Arbitrum | 42161 | USDC | 0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7 |
| Avalanche | 43114 | USDC | 0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7 |
| BSC | 56 | BUSD/USDT | 0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7 |
| Optimism | 10 | USDC | 0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7 |
| Polygon | 137 | USDC | 0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7 |
| Base | 8453 | USDC | 0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7 |
| Linea | 59144 | USDC | 0x4c4AF8DBc524681930a27b2F1Af5bcC8062E6fB7 |
| zkSync | 324 | USDC | 0x09873bfECA34F1Acd0a7e55cDA591f05d8a75369 |

## Tools

### `woofi_query_swap`
Query optimal swap amount with zero slippage estimation.

**Parameters:** chain, from_token, to_token, amount (wei)
**Returns:** to_amount, price_impact, route, gas_estimate

### `woofi_get_supported_tokens`
Get all supported tokens on a chain.

**Parameters:** chain
**Returns:** quote_token, base_tokens[]

### `woofi_calculate_slippage`
Calculate expected slippage for swap size.

**Parameters:** chain, from_token, to_token, amount, tolerance (bps, default 50)
**Returns:** expected_slippage (bps), min_output, is_zero_slippage

### `woofi_build_swap_transaction`
Build swap transaction ready for signing.

**Parameters:** chain, from_token, to_token, amount, slippage_bps, recipient, use_router (default true)
**Returns:** to, data, value, gas_limit, min_output

### `woofi_compare_routes`
Compare WOOFi vs traditional AMM for best execution.

**Parameters:** chain, from_token, to_token, amount
**Returns:** woofi_output, amm_output, savings, savings_usd, recommendation

## Usage Examples

### Query Zero-Slippage Swap
```python
quote = woofi_query_swap(
    chain="base",
    from_token="0x4200000000000000000000000000000000000006",
    to_token="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    amount="1000000000000000000"
)
```

### Build and Execute Swap
```python
tx = woofi_build_swap_transaction(
    chain="arbitrum",
    from_token="native",
    to_token="0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
    amount="1000000000000000000",
    slippage_bps=50,
    recipient="0xYourAddress"
)
tx_hash = wallet_transfer(to=tx["to"], amount=tx["value"], data=tx["data"], chain_id=42161)
```

## How sPMM Achieves Zero Slippage

**Traditional AMM (x*y=k)**: Price moves against trader, slippage scales quadratically

**WOOFi sPMM**:
1. Synthetic oracle pricing from WOO Oracle
2. Proactive hedging on CEXs
3. Unified liquidity pools
4. CEX-matching spreads

Formula: `Price = Oracle_Price × (1 ± Spread)`

For trades <1% of pool, slippage approaches **zero**.

## Best Practices

1. **Always query first** with `woofi_query_swap`
2. **Set slippage**: 0-10 bps (zero tier), 10-50 bps (low), 50-100 bps (standard)
3. **Use WooRouterV2** for simplicity (handles native tokens, auto-routing)
4. **Test small** before large swaps

## Resources

- Docs: https://learn.woo.org/woofi-docs/woofi-dev-docs/
- GitHub: https://github.com/woonetwork/woofi_swap_smart_contracts
- App: https://fi.woo.org/
