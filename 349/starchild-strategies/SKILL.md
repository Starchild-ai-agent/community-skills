---
name: "@349/starchild-strategies"
version: 2.0.0
description: Library of algorithmic trading strategies for perpetual futures. Organized into three families - mean reversion, momentum & trend, and market neutral. Use when a user wants to run a trading strategy, asks what strategies are available, or describes a trading idea that matches one of these patterns.
author: Star Child
tags: [trading, strategies, perpetual-futures, algorithms, backtesting]
---

# starchild strategies v2

Nine curated trading strategies for perpetual futures markets.

## workflow

1. **User describes intent** → match to category or specific strategy from catalog.json
2. **Load decision tree** from `references/` for full strategy logic  
3. **Configure interactively** using `scripts/configure.py`
4. **Validate with backtest** using `scripts/backtest.py`
5. **Execute** through platform's strategy engine

## strategy selection guide

| User says... | Category | Strategy |
|---|---|---|
| "buy dips, sell rips" | mean reversion | rsi reversal |
| "oversold/overbought signals" | mean reversion | rsi reversal |
| "trade the spread between BTC/ETH" | mean reversion | convergence trade |
| "pairs trading" | mean reversion | zscore reversion |
| "follow the trend" | momentum | volatility breakout |
| "breakout after quiet periods" | momentum | volatility breakout |  
| "gap continuation" | momentum | gap continuation |
| "rank and rotate assets" | momentum | rsi rotation |
| "set up a grid" | market neutral | grid bot |
| "earn funding without risk" | market neutral | funding arb |
| "overnight trading" | market neutral | overnight drift |

## automation scripts

- `scripts/configure.py` - Interactive strategy configurator with risk calculations
- `scripts/backtest.py` - Quick validation against recent market data  
- `scripts/risk_calc.py` - Capital requirements and fee analysis
- `scripts/market_scan.py` - Current market regime assessment for strategy selection

## progressive disclosure

1. **Browse catalog.json** for overview (complexity, capital, holding period)
2. **Load decision tree** from `references/{strategy-name}.md` only when selected
3. **Configure using scripts** for interactive setup with validation
4. **Deploy with monitoring** using generated JSON configs

> ⚠️ All strategies enforce pre-trade liquidity checks and fill verification.

Use `scripts/configure.py {strategy-id}` to generate ready-to-deploy configs.