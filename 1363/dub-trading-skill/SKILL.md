---
name: "@1363/dub-trading-skill"
version: 2.0.0
description: "Dub's personal trading methodology — range trading with scaled entries/exits, volume profile levels, VWAP anchored analysis, and geopolitical risk awareness. Use when recommending trades or analyzing setups for this user."
author: dub
tags: [trading, btc, range-trading, risk-management, volume-profile, vwap]

metadata:
  starchild:
    emoji: "📊"
    skillKey: dub-trading-skill
    requires:
      bins: [python]

user-invocable: true
---

# Dub's Trading Skill

## Overview

This skill encapsulates Dub's trading methodology — a disciplined, risk-first approach to crypto range trading built on volume profile, anchored VWAPs, and market structure. The core edge is fading range extremes in rotational environments and scaling into external liquidity grabs.

**Markets:** BTC and ETH (primarily BTC)
**Typical leverage:** 5-10x
**Platform:** Orderly Network (Orange Perps DEX)
**Charting:** MMT (MarketMaker Tools) — free for all users
**Last updated:** 2026-03-25
**Status:** Active — proven methodology with confirmed edge on external liquidity grab setups

---

## Core Philosophy

**Range Trading / Mean Reversion**
- Fade BOTH extremes: long VAL (Value Area Low), short VAH (Value Area High)
- **Above-VAH deviation = major short opportunity** — overextensions snap back hard
- Wait for price to come to you — never chase mid-range
- "Not chasing" is a feature, not a bug
- Only interested at range extremes for rotation to the other side
- Back inside value = rotational environment → fade extremes, don't front-run, let acceptance dictate bias

**Risk First**
- Hard stops mandatory on every position
- Defined risk before any entry
- Account preservation > hero calls

**Technical + Macro Confluence**
- Volume Profile (VAH/POC/VAL) as primary framework
- Anchored VWAPs (Quarterly, Yearly, Monthly, Developing) for HTF confluence
- Stochastic crosses for timing (primary oscillator)
- RSI confirmation (oversold <35, overbought >65)
- Geopolitical events heavily weighted — not a hard override, but a strong factor in all decisions

---

## The Framework: Multi-Timeframe Value Area + VWAP Analysis

### Hierarchy of Levels (HTF to LTF)

This is the core analytical framework. Every trade decision flows from understanding where price sits relative to these nested levels.

**Macro Anchors (Yearly/Quarterly):**
| Level | Type | Significance |
|-------|------|-------------|
| 2024 VAH | Yearly range high | Major resistance — only broken on true trend change |
| Quarterly VWAP / Developing Yearly VWAP | Anchored VWAP | Key rejection/acceptance zone — HTF trend filter |
| 2024 VWAP | Yearly anchored | Major support — loss of this = regime change |
| Quarterly VAL / Developing Yearly VAL | Anchored VWAP | Major support confluence |

**Monthly Anchors:**
| Level | Type | Significance |
|-------|------|-------------|
| Previous Month VAH (PmVAH) | Prior month range | Resistance on retests |
| Previous Month VWAP (PmVWAP) | Prior month fair value | Mean reversion magnet |
| Previous Month VAL (PmVAL) | Prior month range low | Support on retests |
| March VWAP / Current Month VWAP | Developing | Dynamic intra-month fair value |

**Current Range (the tradeable range):**
| Level | Type | How to trade |
|-------|------|-------------|
| VAH | Value Area High | **Short zone** — fade with scaled entries |
| POC | Point of Control | Fair value / magnet — first target for range trades |
| VAL | Value Area Low | **Long zone** — fade with scaled entries |

### How Levels Interact

The power of this framework is **confluence** — when multiple timeframes align at the same price:

- **Strong support example:** VAL + 2024 VWAP + Quarterly VAL + PmVAL all cluster at same zone → high-conviction long zone
- **Strong resistance example:** Quarterly VWAP + Developing Yearly VWAP at same level → rejection here = HTF short signal
- **Invalidation is acceptance:** A level is only "lost" or "broken" when price **accepts** above/below it (sustained closes, not just wicks)

### Reading the Environment

| Market State | How to Identify | How to Trade |
|-------------|----------------|-------------|
| **Rotational (inside value)** | Price between VAL and VAH, mean-reverting | Fade extremes, target POC, don't front-run |
| **Trending (outside value)** | Price accepted above VAH or below VAL | Trade with trend, use pullbacks to prior VAH/VAL |
| **External liquidity grab** | Price spikes beyond range into HTF level, then reverses | Best R:R setup — scale into the reversal (see strategy below) |
| **Breakout / acceptance** | Price tests VAH/VAL and holds above/below with conviction | Old resistance becomes support (or vice versa) — flip bias |

---

## Entry Rules

### The Scaled Entry (5 or 10 levels)

**Default: 5-Level Scale**
1. Identify range zone (VAL for longs, VAH for shorts)
2. Scale 5 orders through the zone
3. Spacing: 0.5-1.5% apart through key levels

**Aggressive: 10-Level Scale (for HTF setups)**
- Used for external liquidity grab setups where there's deep confluence
- Scale 10 orders from near current price through the entire zone
- Example: Short scaling from just above market through VAH to PmVAH

### Technical Triggers

| Indicator | Signal | Action |
|-----------|--------|--------|
| Stochastic K crosses D | From oversold (<20) | Buy signal |
| Stochastic K crosses D | From overbought (>80) | Sell signal |
| RSI | Below 35 | Oversold, potential long |
| RSI | Above 65 | Overbought, potential short |

### When NOT to Enter

- **Geopolitical escalation** — War, conflict, major news = preserve capital
- **Weekend** — Thin liquidity, gap risk
- **Chasing price** — "Not chasing" rule
- **Post-loss emotional state** — Wait for A+ setup
- **Mid-range (POC area)** — No edge, wait for extreme

---

## Exit Rules

### Scaled Take Profits (Default)

**Pattern:**
- Match entry scaling: TPs at key levels on the way to target
- Target zones:
  - POC (Point of Control) — range middle, first major target
  - Opposite extreme (VAH if long, VAL if short)
  - External liquidity (above/below range for runner targets)

### Trade Direction Logic

| Price Location | Direction | Target | Notes |
|----------------|-----------|--------|-------|
| At/below VAL | Long | POC → VAH | Fade range low |
| At/above VAH | Short | POC → VAL | Fade range high |
| Above VAH (external liq grab) | **Short (major swing)** | Snap back into range → POC → VAL | Best R:R setup. Scale 10 orders. CONFIRMED edge. |
| Below VAL (external liq grab) | Long (major swing) | Snap back into range → POC → VAH | Mirror of above |
| Mid-range (POC area) | **No trade** | Wait for extreme | Zero edge here |

### Stop Loss Rules

**Hard stops mandatory:**
- Place beyond range extreme with buffer
- Typical risk: 5-10% of account max
- **Move stop to breakeven ASAP** — after first decent move in intended direction, position becomes risk-free
- Early exit OK — If thesis breaks (e.g., macro news), close before stop hit

### Invalidation Logic

Invalidation is always about **acceptance**, not just a wick:
- **Short invalidation:** Price accepts above the key resistance level (e.g., VAH flips to support with sustained closes above)
- **Long invalidation:** Price accepts below the key support level
- If invalidated: close the trade, reassess, look for the next setup at the level where momentum stalls

**Example:** Short from VAH with invalidation at ~71.5k. If price breaks above and flips that to support with true acceptance → close and look higher for re-entry (next HTF resistance: PmVAH, Q'ly VWAP, etc.)

---

## Risk Management

1. **Defined risk before entry** — Know max loss before clicking
2. **Stops always** — No "hope and monitor"
3. **Geopolitical awareness** — De-risk during escalation, don't go hero mode
4. **Position sizing by conviction:**

| Context | Size |
|---------|------|
| With HTF trend | Full size |
| Counter-trend | **Half size** |
| Feeler / uncertain | **10% of capital** |
| A+ confluence zone | Full allocation |

5. **Monthly seasonality filter:**
   - Days 1-6: Expect retracement, possible month-low formation
   - After day 6: Low likely in, more confident entries
   - Size smaller in early month

---

## External Range Liquidity Grab Strategy (Signature Setup)

This is the highest-conviction setup in the methodology. **Confirmed edge** — has played out multiple times.

### The Thesis

When price has been ranging for weeks/months and builds up liquidity above VAH (or below VAL), large players will push price to grab that liquidity. The move is **not sustainable** — it's a liquidity event, not a breakout.

### How to Identify

1. **Extended range** — Price has been oscillating inside value for weeks
2. **Liquidity clusters visible** — Stops/liquidations stacked beyond range extremes
3. **Push beyond range** — Price moves sharply through VAH (or VAL)
4. **HTF resistance hit** — Move stalls at a major anchored level (Quarterly VWAP, Yearly VWAP, PmVAH)
5. **Signs of distribution** — Negative funding during upside push, CVD divergence, lack of genuine demand

### How to Trade It

1. **Identify the zone:** Map HTF resistance (Q'ly VWAP, Yearly VWAP, PmVAH) and current VAH
2. **Scale orders through the zone:** 10 limit orders from near current price through the external zone
3. **Set stops above the zone** — typically above the highest HTF level
4. **Targets:** Rotation back into value → POC → VAL (entire range traversal)
5. **Manage:** Move stop to breakeven after first move lower, scale out at POC, let runner target VAL

### Key Signals That Confirm the Grab

| Signal | What it tells you |
|--------|------------------|
| Negative funding during rally | Shorts paying longs to hold — distribution, not demand |
| CVD divergence (price up, CVD flat/down) | Spot not confirming the move |
| Hit HTF VWAP level and stall | Institutional level acting as ceiling |
| Multiple assets grab liq simultaneously | Coordinated move, not asset-specific strength |
| Return back inside value quickly | The move was a sweep, not a breakout |

### After the Grab

Once price returns inside value:
- Environment becomes **rotational** again
- Fade extremes, target POC
- Don't front-run the next leg — let acceptance dictate direction
- Unswept lows below become **targets** — expect them to get taken (timing is the only question)

---

## CVD & Flow Analysis

**Important nuance on CVD (Cumulative Volume Delta):**
- Don't over-weight short-term CVD readings in isolation
- Spot has been selling/flat for months — a large negative CVD reading is baseline, not a signal
- Look for CVD **divergence/shifts**, not absolute values
- Example: CVD diverges (flat/rising) while price drops → possible accumulation
- Example: CVD diverges (flat/falling) while price rises → possible distribution (confirms external liq grab thesis)

---

## Macro Catalysts & Geopolitical Risk

Macro events are a **core input**, not an afterthought:

- **Middle East tensions / conflict escalation** → Risk-off catalyst, supports short thesis, but don't override technicals entirely
- **High-impact economic events** (FOMC, CPI, employment) → Expect volatility, size accordingly
- **Geopolitical uncertainty builds** → Reduces conviction on longs, adds weight to short thesis
- **Always know what's on the calendar** for the week

### Integration with Technicals

Geopolitical events **do not override** the technical framework, but they **add weight**:
- If technicals say short AND macro says risk-off → full conviction
- If technicals say long BUT macro says risk-off → half size, tighter stops
- If technicals are neutral AND macro escalates → stay flat, wait

---

## Quality Filters (All Must Align)

| Filter | Description |
|--------|-------------|
| **Location** | At range extreme (VAL/VAH) or HTF confluence |
| **Structure** | No lower highs (for longs), no higher lows (for shorts) |
| **Momentum** | Lack of downside momentum (for longs), vice versa |
| **Time** | Monthly seasonality context |
| **Macro** | No conflicting geopolitical headwinds |

*Location alone is NOT enough. Structure + Momentum + Time + Macro must confirm.*

---

## Trade Management Rules

### Position Scaling Out at Targets
1. **50% off at first major target** (opposite range extreme / POC)
2. **Move SL to profit** — remaining position = free trade
3. **Let runner ride** with trailed stop toward next target

### Weekend Trading Behaviour
- Weekends have thin liquidity and are prone to manipulation
- Avoid opening new positions on weekends unless A+ setup
- If already in a position, monitor but don't panic on weekend wicks

### Acceptance vs Wicks
- A wick through a level is NOT a break — it's a test
- **Acceptance** = sustained closes beyond the level (multiple candles)
- Only change bias on acceptance, not wicks

---

## Indicator Settings

- **Stochastic:** "UnnamedPlayer" variant (modified stochastic)
- **Volume Profile:** TPO style with VAH/POC/VAL
- **VWAPs:** Quarterly, Yearly, Monthly (developing + prior), 2024 anchored
- **Monthly levels:** MoVAH, MoVWAP, MoVAL overlaid
- **Platform:** MMT v3.3.7 (MarketMaker Tools — now free for all users)

---

## Communication Style

When analyzing trades for Dub:
- **Lead with the level and the thesis** — what's the setup, where's the entry zone
- **R:R always** — show the risk/reward ratio
- **No fluff** — levels, thesis, invalidation, done
- **Think in terms of acceptance** — "if this level holds as support" not "if price goes up"
- **Use proper terminology** — VAH, VAL, POC, VWAP, acceptance, rotation, external liq

---

## Decision Framework

```
1. Where is price relative to value? (Inside, VAH, VAL, External?)
2. What's the HTF bias? (Trend, counter-trend, rotational?)
3. What levels have confluence? (VWAP + VA + Monthly = high confluence)
4. What macro events are active? (Geopolitical, economic calendar)
5. Is this a fade-the-extreme or external-liq-grab setup?
6. Size accordingly (conviction table)
7. Set entries, stops, and targets BEFORE executing
```

---

## Terminology

| Term | Meaning |
|------|---------|
| "In front of entry" (on a short) | SL placed *below* entry — no possible loss |
| "Secure profits" | Close a % of the position at market |
| "Runner" | Remaining position after partial close, riding risk-free |
| "Sweep the highs/lows" | Price moves to grab liquidity at extremes before reversing |
| "Acceptance" | Sustained closes beyond a level — not just a wick |
| "External range liq grab" | Price pushes beyond range to sweep stops, then reverses |
| "Rotation" | Price moving from one range extreme to the other |
| "Back inside value" | Price has returned to the VAH-VAL range after deviation |

---

## For The Agent

**Always reference:**
- The multi-timeframe value area + VWAP framework
- "Not chasing" rule
- Hard stop requirement (5-10% max risk, move to breakeven ASAP)
- Geopolitical risk awareness
- Acceptance vs wicks distinction

**Default to:**
- Patience over FOMO
- Scaled entries over single entries
- Risk-off when uncertain
- Cautious and reduced size when geopolitical risk is elevated

**After EVERY trade or TA update:**
- Update this SKILL.md immediately — no exceptions
- Extract any new lessons into the Core Philosophy
- Update framework levels if they've shifted

**PRIVACY: This skill documents the STRATEGY only. Never include:**
- Account balances or capital amounts
- Specific trade P&L in dollar terms
- Trade logs with entry/exit prices and exact sizes
- Any information that could identify the trader's account
