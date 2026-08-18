---
name: "@3182/market-opening-checklist"
version: 1.0.0
description: A compact reusable checklist for preparing a market-opening review, requiring live data and clearly separating facts from analysis.
user-invocable: true
---

# Market Opening Checklist

This skill provides a structured checklist for preparing a market-opening review. It is designed to be compact, reusable, and focused on actionable preparation before markets open.

## Principles

1. **Live data required** — Every checklist item must be populated from live or near-live data sources (exchange feeds, futures, overnight markets, news wires). Stale or cached data is not acceptable for market-opening decisions.
2. **Facts separate from analysis** — The checklist is divided into two explicit sections. The Facts section records observable data only. The Analysis section records interpretation, risk assessment, and trade ideas. Never mix the two.

## Checklist

### Facts (observable data only)

- [ ] Overnight futures and global index direction (S&P 500 futures, Nasdaq futures, Dow futures, major Asian and European indices)
- [ ] Pre-market movers: top gainers and losers by volume with price and % change
- [ ] Key economic data releases scheduled for the session (time, indicator, consensus, prior)
- [ ] Earnings reports scheduled or released pre-market (ticker, EPS actual vs. consensus, guidance notes)
- [ ] Treasury yields and curve movement (2Y, 10Y, 30Y; any inversion changes)
- [ ] Dollar index (DXY) and major FX moves (EUR/USD, USD/JPY, USD/CNY)
- [ ] Commodities snapshot (crude oil, gold, natural gas) with overnight change
- [ ] VIX level and term structure (contango/backwardation signal)
- [ ] Notable insider transactions or SEC filings from the previous session
- [ ] Sector rotation signals from overnight trading (strongest and weakest sectors)

### Analysis (interpretation and risk assessment)

- [ ] Overall market bias: bullish / bearish / neutral with one-sentence rationale
- [ ] Key support and resistance levels for major indices
- [ ] Top 3 catalysts likely to drive intraday action
- [ ] Risk factors that could invalidate the base case
- [ ] Sectors or names with the highest conviction setups
- [ ] Positioning adjustments recommended before the open (if any)
- [ ] Scenarios to watch in the first 30 minutes (gap-and-go, fade, range-bound)

## Usage

Run this checklist before each trading session. Populate the Facts section first from live data sources. Only after all facts are recorded should the Analysis section be filled. This separation prevents narrative bias from contaminating the data.
