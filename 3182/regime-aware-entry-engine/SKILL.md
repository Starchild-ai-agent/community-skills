---
name: "@3182/regime-aware-entry-engine"
version: 1.0.0
description: Build a regime-aware entry plan that outputs a 9-column execution table with first buy, add levels, stop, target, and action tags.
author: Agentway
tags: [trading, risk-management, entries]
---

# Regime-Aware Entry Engine

## When to use
Use this workflow when the user asks:
- "Is this dip a buy?"
- "What are the opportunities after a selloff?"
- "Give me entry/add/stop/target levels"
- "Build me a tactical watchlist"

Works for equities/ETFs (US/HK/A-share) with market data support.

## Output format (mandatory)
Always produce a table with:

- `Ticker`
- `First Buy`
- `Add1 (-8%)`
- `Add2 (-15%)`
- `Stop`
- `Target`
- `Upside`
- `Regime Tag` (`RISK_ON`, `RISK_OFF`, `PANIC`)
- `Action` (`BUY_NOW`, `WATCH`, `AVOID`)

## Workflow

### 1) Detect regime first
Use broad-market proxies before single-name calls:
- Growth beta proxy (e.g., QQQ)
- Broad market proxy (e.g., SPY)
- Sector stress proxy (e.g., SOXX/SMH when tech-led)
- Defensive relative strength (e.g., XLU/XLV vs XLK)

Classify:
- **RISK_ON**: breadth stable, growth leading, no stress spike
- **RISK_OFF**: broad pullback, cyclicals weak, defensives holding up
- **PANIC**: disorderly selloff / correlation spike / large intraday dislocations

### 2) Build candidate pool
Start with user’s watchlist first. If not provided, build from:
- prior winners with healthy pullback
- sector leaders with intact structure
- avoid low-liquidity names in stress regimes

### 3) Score each candidate
Use a simple composite score (0–100):
- **Trend quality (35%)**: still above key medium trend context; no structural break
- **Pullback quality (30%)**: meaningful discount from recent high, but not freefall
- **Risk efficiency (20%)**: stop distance vs expected upside
- **Liquidity/Execution (15%)**: spreads/volume/volatility practicality

### 4) Generate execution levels
- **First Buy**: current value zone (no chasing)
- **Add1**: approx -8% from first buy reference
- **Add2**: approx -15% from first buy reference
- **Stop**: invalidation level (structure break)
- **Target**: base-case recovery objective
- **Upside**: `(Target / current - 1)`

### 5) Apply regime guardrails
- In **RISK_ON**: normal position sizing, allow 2-stage adds
- In **RISK_OFF**: reduce first tranche size, prioritize quality balance sheets
- In **PANIC**: smaller probes only; keep larger cash buffer; avoid forced averaging

### 6) Produce clear actions
- `BUY_NOW`: in zone + structure acceptable
- `WATCH`: close but not yet in range / waiting confirmation
- `AVOID`: structure broken, governance risk, or asymmetry poor

## Messaging style
- Keep it execution-first, concise, and numeric.
- Do not promise certainty.
- Always include a one-line risk note: "Not investment advice; follow stop discipline."

## Quality checks before finalizing
- Levels are internally consistent (Add2 < Add1 < First Buy)
- Stop is below buy ladders for long setups
- Upside is computed from current price, not stale references
- Action tag matches regime + structure

## Optional extension (risk layer)
If governance/event risk is detected (management/legal/disclosure shock), force downgrade:
- Action cannot be `BUY_NOW` until risk is clarified
- Cap size at half normal risk budget

## Reuse pattern
For repeated daily usage:
1. Pull latest broad market + watchlist quotes
2. Recompute regime
3. Update table only where trigger state changed
4. Push only changed rows to avoid alert spam
