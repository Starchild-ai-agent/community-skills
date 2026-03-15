---
name: "@1247/yield-optimizer"
version: 1.0.0
description: "Autonomous USDC yield optimization across DeFi protocols. Scans 60+ pools on 6 chains (Ethereum, Arbitrum, Base, Optimism, Polygon, Avalanche) across 8+ protocols (Aave V3, Compound V3, Morpho, Pendle, Spark, Fluid, Sky). Use when the user asks about yield farming, best stablecoin rates, DeFi yields, where to deposit USDC, or wants autonomous yield management."
author: starchild
tags: [defi, yield, aave, compound, morpho, pendle, usdc, lending, stablecoin, autonomous]

metadata:
  starchild:
    emoji: "🌾"
    skillKey: yield-optimizer
    requires:
      bins: [python3]
    install:
      - kind: pip
        package: requests

user-invocable: true
---

# Yield Optimizer

Autonomous USDC yield optimization across DeFi lending protocols and chains.

## What This Does

Scans real-time yields from DeFi Llama, ranks opportunities by risk-adjusted return, recommends allocations, and can execute deposits/withdrawals via the wallet skill.

**Data source:** DeFi Llama Yields API (free, no key, real-time).

## Supported Protocols & Chains

| Protocol | Type | Chains |
|----------|------|--------|
| Aave V3 | Lending | ETH, ARB, Base, OP, Polygon, Avax |
| Compound V3 | Lending | ETH, ARB, Base, OP, Polygon |  
| Morpho (V1 + Blue) | Lending | ETH, Base |
| Pendle | Yield tokenization | ETH, ARB |
| Spark / Sky | Lending | ETH |
| Fluid | Lending | ETH |
| Euler | Lending | ETH, ARB, Base |

**Stablecoins tracked:** USDC, USDT, DAI, USDS, sDAI, sUSDe, GHO

## Core Workflows

### 1. Scan & Report

When user asks "what are the best yields?" or "where should I put my USDC?":

1. Run `python3 skills/yield-optimizer/scripts/scan_pools.py`
2. Present top opportunities grouped by risk tier
3. Highlight the best rate per chain and the overall best

**Risk tiers:**
- **Tier 1 (Safe):** Aave V3, Compound V3, Spark — established, audited, >$100M TVL
- **Tier 2 (Moderate):** Morpho, Euler, Fluid — newer but audited, >$10M TVL
- **Tier 3 (Aggressive):** Pendle, smaller pools — higher yields, more complexity

### 2. Recommend Allocation

When user has a specific amount to deploy:

1. Scan current rates
2. Filter by user's risk preference (default: Tier 1-2)
3. Suggest allocation:
   - **Conservative:** 100% best Tier 1 pool
   - **Balanced:** 70% Tier 1 / 30% Tier 2
   - **Aggressive:** 50% Tier 1 / 30% Tier 2 / 20% Tier 3
4. Show expected annual yield in dollar terms

### 3. Execute Deposit

When user confirms a recommendation:

1. Check wallet balances via wallet skill (`wallet_balance` on target chain)
2. If USDC is on wrong chain, suggest bridging (across-bridge skill)
3. For Aave V3 deposits, use the contract addresses from `references/contracts.json`
4. Execute: approve USDC → supply to Aave pool
5. Verify position via aToken balance read

**Prerequisites — Wallet Policy:** Before any on-chain execution, load the **wallet-policy** skill and propose the standard wildcard policy.

### 4. Monitor & Rebalance

For scheduled autonomous operation:

1. Scan yields every hour
2. Compare current position APY vs best available
3. If delta > 0.5% AND gas cost < 0.1% of position — recommend rebalance
4. Log all decisions (hold/rebalance) with reasoning

Schedule via: `schedule_task(command="python3 skills/yield-optimizer/scripts/scan_pools.py --json", schedule="every 1 hour")`

## Decision Logic

```
scan pools → filter (TVL > $100K, supported protocols) → rank by APY

IF no current position:
  → recommend deposit to best risk-adjusted pool

IF current position exists:
  apy_delta = best_available - current_apy
  IF apy_delta < 0.5%: HOLD (not worth gas)
  IF gas_cost > 0.1% of position: HOLD (too expensive)  
  ELSE: REBALANCE (withdraw → bridge if needed → deposit)
```

## Key Gotchas

- **APY ≠ APR.** DeFi Llama returns APY (compounded). Don't double-compound when projecting.
- **Reward APY is temporary.** `apyReward` (token incentives) can vanish overnight. Weight `apyBase` higher for stability.
- **TVL matters.** High APY + low TVL = likely unsustainable or risky. Filter >$100K minimum, prefer >$10M.
- **Gas costs eat small positions.** Ethereum mainnet Aave deposit ≈ $5-15. A $500 position rebalancing for 0.3% more APY loses money.
- **Bridge time.** Cross-chain moves take 2-15 minutes. Don't show as instant.
- **Pendle yields are structured.** They represent fixed-rate or leveraged yield — not simple lending. Flag this to users.

## Script Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `scan_pools.py` | Fetch & rank all pools | `python3 scripts/scan_pools.py` |
| `scan_pools.py --json` | JSON output for automation | Scheduled monitoring |
| `scan_pools.py --chain Base` | Filter by chain | Chain-specific query |
| `scan_pools.py --protocol aave-v3` | Filter by protocol | Protocol-specific query |

## Integration with Other Skills

- **wallet** — balance checks, transaction execution
- **across-bridge** — cross-chain USDC transfers when rebalancing
- **wallet-policy** — ensure policy is set before on-chain operations
- **coinglass / market-data** — broader market context for yield decisions
