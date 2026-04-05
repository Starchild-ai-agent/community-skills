---
name: "@1892/solana"
version: 1.0.2
description: "Solana — Master skill hub for all Solana blockchain capabilities. Provides a directory of 15+ specialized skills for DeFi trading, NFTs, development, infrastructure, and tooling on Solana. Use when the user wants to build on Solana, trade DeFi protocols, create NFTs, deploy programs, set up multisig wallets, bridge assets, or any Solana development or interaction task."
metadata:
  starchild:
    emoji: "◎"
    skillKey: solana
user-invocable: true
disable-model-invocation: false
---

# Solana — Skills Directory

Solana is a high-performance blockchain optimized for speed and low transaction costs. This master skill provides a directory of all Solana-related capabilities and helps you pick the right one.

![Solana](assets/logo.png)

---

## Skills by Category

### 💱 DeFi — Swaps & Trading

#### 1. jupiter
Solana's leading DEX aggregator — swaps, limit orders, DCA, perpetuals, and lending via the Jupiter platform.

**Use when:** Swapping tokens on Solana, setting up limit orders or dollar-cost averaging, trading perps, or working with Jupiter's API/SDK.

---

#### 2. raydium
Raydium Protocol — CLMM (Concentrated Liquidity Market Maker), CPMM, AMM pools, farming, and Trade API.

**Use when:** Providing liquidity on Raydium, creating pools, yield farming, or using Raydium's trading APIs.

---

#### 3. orca
Orca Whirlpools — Solana's leading concentrated liquidity AMM. Covers swaps, liquidity provision, pool creation, position management, and fee harvesting.

**Use when:** Managing concentrated liquidity positions on Orca, creating whirlpools, or harvesting fees.

---

#### 4. meteora
Meteora DeFi SDK — liquidity pools, Dynamic AMMs, Alpha Vaults, bonding curves, and token launches.

**Use when:** Working with Meteora's DLMM pools, creating liquidity strategies, or launching tokens via Meteora.

---

#### 5. pumpfun
PumpFun Protocol — permissionless token launches, bonding curves, and PumpSwap integrations.

**Use when:** Launching tokens on Solana via pump.fun, trading bonding curve tokens, or integrating PumpSwap.

---

### 🏦 DeFi — Lending & Yield

#### 6. kamino
Kamino Finance — lending, borrowing, liquidity management, and leverage strategies on Solana.

**Use when:** Supplying collateral, borrowing against assets, managing Kamino vaults, or optimizing leverage positions.

---

#### 7. lulo
Lulo — Solana's lending aggregator that routes deposits to the highest-yielding protocols.

**Use when:** Earning yield on Solana deposits, comparing lending rates across protocols, or managing Lulo positions.

---

#### 8. sanctum
Sanctum — liquid staking protocol covering LST swaps and Infinity pool operations.

**Use when:** Working with liquid staking tokens (LSTs), swapping between LSTs, or using Sanctum's Infinity pools.

---

### 🌉 Cross-Chain & Infrastructure

#### 9. debridge
deBridge Protocol — cross-chain bridges and token transfers between Solana and other chains.

**Use when:** Bridging assets to/from Solana, cross-chain token transfers, or working with deBridge's DLN infrastructure.

---

#### 10. helius
Helius RPC infrastructure — DAS API, Enhanced Transactions API, webhooks, and developer tooling.

**Use when:** Setting up RPC endpoints, parsing enriched transaction data, subscribing to webhooks, or using Helius APIs.

---

#### 11. pyth
Pyth Network oracle — real-time price feeds with confidence intervals for on-chain applications.

**Use when:** Reading price data from Pyth oracles, working with confidence intervals, or integrating price feeds into smart contracts.

---

### 🖼️ NFTs & Digital Assets

#### 12. metaplex
Metaplex Protocol — Core NFTs, Token Metadata, Bubblegum compressed NFTs, and Candy Machine launches.

**Use when:** Creating NFTs on Solana, managing token metadata, launching collections via Candy Machine, or working with compressed NFTs.

---

### 🛡️ Security & Multisig

#### 13. squads
Squads Protocol — multisig wallets and account abstraction on Solana.

**Use when:** Setting up multisig wallets on Solana, managing shared custody, or working with Squads Program for governance and treasury management.

---

### 🛠️ Development & Tooling

#### 14. solana-kit
@solana/kit — the modern zero-dependency JavaScript SDK from Anza for building Solana applications.

**Use when:** Building Solana dApps from scratch, working with the latest Solana JS SDK, or creating transaction builders and signers.

---

## Skill Selection Guide

| Task | Recommended Skill |
|------|-------------------|
| Swap tokens on Solana | `jupiter` |
| Provide concentrated liquidity | `orca` or `raydium` |
| Launch a token | `pumpfun` or `meteora` |
| Lend/borrow assets | `kamino` |
| Earn yield on deposits | `lulo` |
| Liquid stake SOL | `sanctum` |
| Bridge assets cross-chain | `debridge` |
| Set up RPC/webhooks | `helius` |
| Read price feeds | `pyth` |
| Create/launch NFTs | `metaplex` |
| Set up multisig wallet | `squads` |
| Build a Solana dApp | `solana-kit` |

---

## Quickstart

For a new Solana project, ask the user what they're building:

- **Token swap/trading** → `jupiter` (best aggregator) or protocol-specific (`orca`, `raydium`, `meteora`)
- **Token launch** → `pumpfun` (memecoin) or `meteora` (structured launch)
- **Lending/yield** → `kamino` (full-featured) or `lulo` (yield aggregator)
- **NFT project** → `metaplex`
- **Infrastructure/RPC** → `helius`
- **Full dApp development** → `solana-kit`

---

## Resources

- **Solana Skills Hub**: [solana.com/skills](https://solana.com/skills)
- **Solana Foundation Skills**: [github.com/solana-foundation/solana-dev-skill](https://github.com/solana-foundation/solana-dev-skill)
- **Community Skills**: [github.com/sendaifun/skills](https://github.com/sendaifun/skills)
- **Documentation**: [solana.com/docs](https://solana.com/docs)
- **Explorer**: [solscan.io](https://solscan.io)
- **Faucet**: [faucet.solana.com](https://faucet.solana.com)
