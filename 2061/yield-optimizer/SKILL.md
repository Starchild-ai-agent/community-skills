---
name: "@2061/yield-optimizer"
version: 2.0.0
description: "Autonomous USDC yield optimization across DeFi protocols. Scans 60+ pools on 6 chains (Ethereum, Arbitrum, Base, Optimism, Polygon, Avalanche) across 8+ protocols (Aave V3, Morpho, Pendle, Compound V3, Spark, Fluid, Euler). Auto-routes deposits to the highest-yielding protocol per chain. Includes a full web UI with multi-protocol deposit/withdraw. Use when the user asks about yield farming, best stablecoin rates, DeFi yields, where to deposit USDC, or wants autonomous yield management."
author: starchild
tags: [defi, yield, aave, morpho, pendle, compound, usdc, lending, stablecoin, autonomous, multi-protocol, multi-chain]

metadata:
  starchild:
    emoji: "🌾"
    skillKey: yield-optimizer
    requires:
      bins: [python3, node]
    install:
      - kind: pip
        package: requests

user-invocable: true
---

# Yield Optimizer v2

Autonomous USDC yield optimization across DeFi lending protocols and chains.
**Auto-routes deposits to the best protocol per chain** — Aave V3, Morpho (ERC-4626), or Pendle (PT fixed-rate).

## What This Does

1. Scans real-time yields from DeFi Llama + Morpho GraphQL + Pendle Hosted SDK
2. Compares protocols **per chain** and picks the winner
3. Routes deposits to the optimal protocol automatically
4. Withdraws from whichever protocol holds the position
5. Full web UI with wallet integration (MetaMask, Rabby, etc.)

**Data sources:** DeFi Llama Yields API, Morpho GraphQL API, Pendle Hosted SDK API (all free, no key).

## Supported Protocols & Chains

| Protocol | Type | Deposit Method | Chains |
|----------|------|---------------|--------|
| **Aave V3** | Lending pool | `pool.supply(asset, amount, onBehalfOf, 0)` | ETH, ARB, Base, OP, Polygon, Avax |
| **Morpho** | ERC-4626 vaults | `vault.deposit(assets, receiver)` | ETH, ARB, Base, OP |
| **Pendle** | PT fixed-rate | Hosted SDK → router swap | ETH, ARB, Base |
| Compound V3 | Lending | `comet.supply(asset, amount)` | ETH, ARB, Base, OP, Polygon |
| Spark / Sky | Lending | `pool.supply(...)` | ETH |
| Fluid | Lending | `vault.deposit(...)` | ETH |
| Euler | Lending | `vault.deposit(...)` | ETH, ARB, Base |

**Stablecoins tracked:** USDC, USDT, DAI, USDS, sDAI, sUSDe, GHO

## Architecture

### Backend (Node.js / Express)

```
server.js
├── /api/pools          — best protocol per chain (Aave vs Morpho vs Pendle)
├── /api/chains         — supported chain list
├── /api/tvl            — total TVL from DeFi Llama
├── /api/agent-activity — recent deposit/withdraw log
├── /api/vault/:addr    — user positions across all protocols
├── /api/deposit        — record deposit event
├── /api/withdraw       — record withdraw event
├── /api/usdc-balance/:addr — cross-chain USDC balance (RPC reads)
└── /api/pendle-swap    — get Pendle SDK calldata for PT swap
```

### Frontend (Vanilla JS + ethers.js)

```
public/
├── index.html   — landing page + dashboard
├── styles.css   — dark theme, glass-morphic UI
├── app.js       — dashboard logic, deposit/withdraw modals
└── wallet.js    — multi-protocol deposit routing
```

### Protocol Routing Logic

```
For each chain:
  1. Fetch Aave V3 APY from DeFi Llama
  2. Fetch Morpho vault APY from GraphQL (if vault exists on chain)
  3. Fetch Pendle PT implied APY from Hosted SDK (if market exists on chain)
  4. Return winner = max(aave_apy, morpho_apy, pendle_apy)

On deposit:
  IF winner == "aave"   → approve USDC → pool.supply()
  IF winner == "morpho"  → approve USDC → vault.deposit()
  IF winner == "pendle"  → approve USDC → router.swapExactTokenForPt()

On withdraw:
  Read user balances across all protocols
  IF has aTokens      → pool.withdraw()
  IF has Morpho shares → vault.withdraw() or vault.redeem()
  IF has Pendle PT     → router swap PT → USDC (or redeem at maturity)
```

## Core Workflows

### 1. Scan & Report (CLI)

When user asks "what are the best yields?" or "where should I put my USDC?":

1. Run `python3 skills/yield-optimizer/scripts/scan_pools.py`
2. Present top opportunities grouped by risk tier
3. Highlight the best rate per chain and the overall best

```bash
python3 skills/yield-optimizer/scripts/scan_pools.py                     # Full report
python3 skills/yield-optimizer/scripts/scan_pools.py --json              # JSON for automation
python3 skills/yield-optimizer/scripts/scan_pools.py --chain Arbitrum    # Filter by chain
python3 skills/yield-optimizer/scripts/scan_pools.py --protocol pendle   # Filter by protocol
python3 skills/yield-optimizer/scripts/scan_pools.py --amount 10000 --risk balanced  # Allocation
```

### 2. Launch Web UI

For the full visual experience with wallet connection:

```bash
cd output/yield-agent-v4
npm install
node server.js    # starts on port 3456
```

Then use `preview_serve` to expose it.

### 3. Execute Deposit (Programmatic)

When user confirms a recommendation:

1. Check wallet balances via wallet skill
2. If USDC is on wrong chain, suggest bridging (across-bridge skill)
3. Determine best protocol for target chain (from `/api/pools`)
4. Execute the protocol-specific deposit flow
5. Verify position via balance read

**Prerequisites:** Load **wallet-policy** skill and propose standard wildcard policy before on-chain ops.

### 4. Monitor & Rebalance

For scheduled autonomous operation:

1. Scan yields every hour
2. Compare current position APY vs best available
3. If delta > 1% AND gas cost < 0.1% of position → recommend rebalance
4. Log all decisions with reasoning

```
schedule_task(
  command="python3 skills/yield-optimizer/scripts/scan_pools.py --json",
  schedule="every 1 hour"
)
```

## Risk Tiers

| Tier | Protocols | Characteristics |
|------|-----------|----------------|
| 🟢 **Safe** | Aave V3, Compound V3, Spark | Established, audited, >$100M TVL |
| 🟡 **Moderate** | Morpho, Euler, Fluid | Newer but audited, ERC-4626, >$10M TVL |
| 🔴 **Aggressive** | Pendle | Higher yields via PT fixed-rate, maturity risk |

## Contract Addresses

See `references/contracts.json` for:
- Aave V3 pool addresses per chain
- USDC token addresses per chain
- aToken addresses per chain
- RPC endpoints per chain

Morpho vault addresses:
- **Ethereum:** `0xBEEF01735c132Ada46AA9aA4c54623cAA92A64CB` (Steakhouse USDC)
- **Base:** `0xc1256Ae5FF1cf2719D4937adb3bbCCab2E00A2Ca` (Steakhouse USDC)
- **Arbitrum:** `0x2C8FBB630Bae56bBC27E286d0D4816D62e4C1509` (Steakhouse USDC)
- **Optimism:** `0x7BfA7e0e3De0e3a6B4399F9CAa1E444Dd3d55c54` (Gauntlet USDC Prime)

## Key Gotchas

- **APY ≠ APR.** DeFi Llama returns APY (compounded). Don't double-compound.
- **Reward APY is temporary.** `apyReward` (token incentives) can vanish. Weight `apyBase` higher.
- **TVL matters.** High APY + low TVL = unsustainable. Filter >$100K minimum, prefer >$10M.
- **Gas costs eat small positions.** Ethereum mainnet ≈ $5-15. Don't rebalance $500 for 0.3% more.
- **Pendle PT has maturity dates.** Full implied APY only if held to maturity. Early exit via AMM may differ.
- **Morpho vaults are ERC-4626.** Standard deposit/withdraw, but shares ≠ assets (use `convertToAssets`).
- **Bridge time.** Cross-chain moves take 2-15 minutes via Across. Don't show as instant.
- **USDC decimals.** Always 6 decimals. `parseUnits(amount, 6)` not 18.

## Integration with Other Skills

| Skill | Purpose |
|-------|---------|
| **wallet** | Balance checks, transaction execution |
| **across-bridge** | Cross-chain USDC transfers when rebalancing |
| **wallet-policy** | Ensure wallet policy is set before on-chain ops |
| **coinglass / market-data** | Broader market context for yield decisions |
| **charting** | Visualize yield trends over time |
