---
name: "@349/okx-onchainos-suite"
version: 1.0.0
description: "Unified wrapper for OKX OnchainOS capabilities (wallet, market, token, signal, trenches, swap, gateway, security, portfolio, audit log). Use when users want any OKX OnchainOS workflow without installing many separate skills."
author: starchild-agent
tags: [okx, onchainos, dex, wallet, swap, market-data]
license: MIT
metadata:
  starchild:
    emoji: "⚡"
    skillKey: okx-onchainos-suite
    requires:
      env: [OKX_API_KEY, OKX_SECRET_KEY, OKX_PASSPHRASE]
      anyBins: [onchainos]
user-invocable: true
---

# OKX OnchainOS Suite (Unified)

This is a consolidated wrapper skill for the full OKX OnchainOS package.

## Why this exists

The upstream package contains many individual skills. This wrapper keeps the top-level `skills/` directory clean by grouping all module skills under:

`skills/okx-onchainos-suite/modules/`

Included modules:
- okx-agentic-wallet
- okx-audit-log
- okx-dex-market
- okx-dex-signal
- okx-dex-swap
- okx-dex-token
- okx-dex-trenches
- okx-onchain-gateway
- okx-security
- okx-wallet-portfolio

## How to use

Use this skill as the single entrypoint for all OnchainOS requests.

Intent routing:
- Wallet login/balance/send/history → agentic-wallet
- Public address portfolio lookup → wallet-portfolio
- Token price/K-line/PnL → dex-market
- Token discovery/holder distribution/honeypot → dex-token
- Smart money/whale/KOL buys → dex-signal
- New meme launches/dev reputation/bundler → dex-trenches
- Swap quote/approve/execute → dex-swap
- Gas estimate/simulation/broadcast/status → onchain-gateway
- Tx/signature/DApp security & approvals → security
- Export command logs/audit history → audit-log

## Runtime

`onchainos` CLI should be installed and available in PATH.
Required environment variables for authenticated calls:
- `OKX_API_KEY`
- `OKX_SECRET_KEY`
- `OKX_PASSPHRASE`

## Notes

- This is a workspace consolidation wrapper.
- Original module files are preserved under `modules/` for reference and maintenance.
