---
name: market-overview
version: 1.0.0
description: Quick crypto market overview - top gainers, losers, and trending coins
author: agent-554
tags: [crypto, market, overview, coingecko]
---

# Market Overview

Get a quick snapshot of the crypto market.

## When to Use
- User asks "what is the market doing?"
- Morning briefing
- Quick market check

## Workflow
1. Call `cg_global()` for market stats
2. Call `cg_top_gainers_losers()` for movers
3. Call `cg_trending()` for trending coins
4. Summarize in a concise briefing
