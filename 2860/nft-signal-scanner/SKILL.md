---
name: "@2860/nft-signal-scanner"
version: 0.1.0
description: |
  Scan Ethereum NFT collections for systematic trading signals. Use when evaluating paper trade opportunities, ranking collections by signal quality, or building evidence before live deployment. Focus on clean data from OpenSea + Alchemy.
author: Djani
tags: [nft, ethereum, signals, paper-trading, opensea]
metadata:
  starchild:
    emoji: "🔍"
    skillKey: nft-signal-scanner
user-invocable: true
---

## Core Principles

**Paper trading first.** Never suggest live capital deployment. All signals are for paper trading evidence only until 30-50 logged trades with documented win rate.

**Ethereum only.** This skill is strictly for ETH mainnet NFTs. Ignore other chains.

**Signal quality over noise.** Prioritize collections with reliable on-chain data, active but not manipulated volume, and clear listing/bid walls. Warn when data sources show staleness (especially Moralis bids).

**Data sources:**
- Primary: OpenSea API + Alchemy for ownership and transfers
- Avoid: Reservoir, SimpleHash (deprecated per user)
- Moralis: usable for some endpoints but flag stale bids explicitly

## When to Activate

Use this skill when the user asks about:
- NFT collection signals or rankings
- Paper trade ideas on Ethereum NFTs
- Systematic scanning rules
- Data quality checks on NFT endpoints

## Decision Framework

1. Start with collection overview (volume, floor, listed count, unique holders)
2. Check bid wall quality and spread
3. Look for consistent listing behavior vs wash trading patterns
4. Log every paper trade signal with entry reason, size, and expected exit
5. Track results before suggesting any pattern repetition

## Gotchas

- OpenSea rate limits are real — batch requests when possible
- Bid data can lag significantly on secondary sources
- Low liquidity collections often show fake floors from single large listings
- Always verify current block before trusting "recent activity" numbers

## Output Style

Return structured signals with:
- Collection name + contract
- Key metrics (floor, 24h volume, listed %, unique holders)
- Signal type (accumulation zone, bid wall strength, listing pressure)
- Paper trade parameters (suggested size, entry logic, invalidation)
- Data freshness note

Never output hype or price predictions. Only observable structure and data quality notes.