---
name: "@1363/dub-trading-skill"
version: 1.2.0
description: "Dub's personal trading methodology — range trading with scaled entries/exits, stochastic + RSI signals, hard stops, and geopolitical risk awareness. Use when recommending trades or analyzing setups for this user."
author: dub
tags: [trading, hyperliquid, btc, range-trading, risk-management]

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

This skill encapsulates Dub's trading methodology — a disciplined, risk-first approach to crypto range trading. Activate this skill when analyzing markets, recommending trades, or managing positions for this user.

**Account:** ~$276 USDC on Hyperliquid  
**Typical leverage:** 5-10x  
**Markets:** BTC and ETH  
**Last updated:** 2026-03-06  
**Status:** Active learning — rigorous training toward autonomous trading in Dub's style

---

## Core Philosophy

**Range Trading / Mean Reversion**
- Fade BOTH extremes: long VAL (Value Area Low), short VAH (Value Area High)
- **Above-VAH deviation = major short opportunity** — overextensions snap back hard
- Wait for price to come to you — never chase mid-range
- "Not chasing" is a feature, not a bug
- Only interested at range extremes for rotation to other side

**Risk First**
- Hard stops mandatory on every position
- Defined risk before any entry
- Account preservation > hero calls

**Technical + Fundamental**
- Stochastic crosses for timing (primary)
- RSI confirmation (oversold <35, overbought >65)
- Geopolitical events are heavily weighted — not a hard override, but a strong factor in all decisions

---

## Entry Rules

### The 5-Level Scaled Entry (Default)

**Pattern:**
1. Identify range zone (VAL support or VAH resistance)
2. Scale 5 orders through the zone
3. Example: ETH VAL zone — 0.12 ETH × 5 levels = 0.6 ETH total

**Spacing:** 0.5-1.5% apart through key levels

### Technical Triggers

| Indicator | Signal | Action |
|-----------|--------|--------|
| Stochastic K crosses D | From oversold (<20) | Buy signal |
| Stochastic K crosses D | From overbought (>80) | Sell signal |
| RSI | Below 35 | Oversold, potential long |
| RSI | Above 65 | Overbought, potential short |

### When NOT to Enter

- **Geopolitical escalation** — War, major news = preserve capital
- **Weekend** — Thin liquidity, gap risk
- **Chasing price** — "Not chasing" rule
- **Post-loss emotional state** — Wait for A+ setup

---

## Exit Rules

### Scaled Take Profits (Default)

**Pattern:**
- Match entry scaling: 5 TPs at resistance zones
- Target zones:
  - POC (Point of Control) — range middle
  - Opposite extreme (VAH if long, VAL if short)
  - External liquidity (above/below range for wick captures)

### Trade Direction Logic

| Price Location | Direction | Target |
|----------------|-----------|--------|
| At/below VAL | Long | Rotation to POC → VAH |
| At/above VAH | Short | Rotation to POC → VAL |
| Above VAH (deviation) | **Short (major swing)** | Snap back into range — best R:R. **CONFIRMED: External liq grab thesis works. Scale 10 orders through zone, target HTF range lows.** |
| Below VAL (deviation) | Long (major swing) | Snap back into range. Mirror of above — scale longs through external liq zone below VAL. |
| Mid-range (POC area) | **No trade** | Wait for extreme |

### Stop Losses

**Hard stops mandatory:**
- Place below/above range extremes with buffer
- Typical risk: 5-10% of account — always as minimal as possible
- Move stops in front of entry after the first decent price move in the intended direction — position becomes risk-free ASAP
- Early exit OK — If thesis breaks (e.g., war news), close before stop

---

## Risk Management

1. **Defined risk before entry** — Know max loss
2. **Stops always** — No "hope and monitor"
3. **Geopolitical awareness** — Major news events heavily weighted in all decisions
4. **Weekend caution** — Avoid new positions
5. **No revenge trading** — After loss, wait for A+ setup
6. **Preservation first** — "Live to trade another day"

---

## Communication Style

- **Updates:** Concise, data-driven, no fluff
- **Position reports:** Current PnL, entry avg, distance to stops/TPs
- **Order confirmations:** Full table with sizes, prices, order IDs
- **No Telegram** — Chat interface only

---

## Decision Framework

When Dub asks about a trade or setup:

1. **Check the thesis** — Does it fit range trading?
2. **Verify triggers** — Stochastic cross? RSI oversold/overbought?
3. **Assess risk** — Defined stop? Proper size?
4. **Check external factors** — War/news? Weekend? Chasing?
5. **Recommend scaled entries** — 5-level preferred
6. **Always include stops** — Hard stop or "not entering without one"

---

## Skill Evolution

**Update this skill after:**
- Major trades (entries, exits, size changes)
- New rules stated by Dub
- Strategy pivots
- Pattern observations
- Missed opportunities with lessons learned

**Update process:**
1. Edit SKILL.md with new observations
2. Add to "Decision Patterns" table after significant trades
3. Update "Current Market Views" when thesis changes
4. Never delete history — append only

---

## Decision Patterns (Observed)

| Date | Situation | User's Call | Outcome | Lesson |
|------|-----------|-------------|---------|--------|
| 2026-02-28 | VAH shorts, price crashed 5.7% | Held, then closed at loss | -$35 (thesis broken) | Don't hold through breakdown without stop |
| 2026-02-28 | VAL longs filled, war news broke | Closed early before stop hit | Saved $6.60 vs stop | Geopolitical = exit first, questions later |
| 2026-02-28 | Stochastic bottom + war fear | Passed on long (not chasing) | Missed 4% bounce | Preserved capital > FOMO, correct call |
| 2026-02-28 | Full VAL position, escalation news | Closed all longs pre-emptively | Avoided larger loss | Risk-off override works |
| 2026-03-02 | BTC at VAL ($65.8k) + CME gap + 2024 VWAP confluence | Small feeler long (10% capital, half-size bear market rule) | Entry $65,806, rallied to $69,354 (+5.4%) | Confluence zones = high conviction, but size conservatively in bear trend |
| 2026-03-02 | BTC reached VAH zone (~$69.3k) after VAL entry | Secured 50% at $69,354, moved SL to $67,400 (below POC) | +$0.57 realized, remaining half = free trade | **Textbook range rotation: VAL → VAH, secure profits at target, trail stop to lock profit** |
| 2026-03-03 | POC showing signs of breaking, structure shifting | Manually closed remaining 50% at $67,422 | +$0.26 on remainder, total trade +$0.83 | **Don't wait for stop when structure breaks — manual close preserved more profit than SL would have. POC broke immediately after exit.** |
| 2026-03-05 | BTC rallied to external range liquidity (~$72-73k) as predicted | Scaled 10 limit shorts $72.6k–$75.3k + market short at $72.2k | 6 of 10 limits filled, position ~0.013 BTC short, +$21.89 uPnL (+23% ROE) | **External range liquidity grab thesis played out perfectly. Scaling into the zone = better avg entry. Negative funding confirms market doesn't trust the rally.** |

---

## Chart References & Key Levels

### BTC/USD — Volume Profile Range — Updated 2026-03-05
**Key Levels:**
| Level | Price | Notes |
|-------|-------|-------|
| External Liquidity Zone | $72,000–$75,300 | **GRABBED** — short scaling zone, 6 of 10 orders filled |
| MoVAH (Monthly VAH) | $73,049 | Upper monthly extreme — inside the liq grab zone |
| VAH | $70,025 | Range high — previous fade zone |
| MoVWAP | $69,307 | Monthly VWAP |
| POC | $67,883 / $67,243 | High volume node — broke after long exit |
| VAL | $66,000 | Range low — **HTF short target zone** |
| MoVAL | $65,525 | Monthly VAL |
| 2024 VWAP | $65,167 | Major yearly anchored level |

**Key observations (March 2026):**
- External range liquidity grab to $72-73k played out exactly as outlined weeks prior
- POC broke immediately after long exit — confirmed structure deterioration
- Negative funding during rally = distribution, not genuine demand
- Both BTC and ETH grabbed external liquidity simultaneously
- Now positioned short, targeting HTF range lows (~$65-66k)

### ETH/USD — 4H (Binance Futures) — 2026-02-28 22:57 UTC
**Volume Profile Range:**
| Level | Price | Notes |
|-------|-------|-------|
| VAH | $2,070 | Range high — fade zone |
| POC | $1,966.50 | High volume node — magnet |
| VAL | $1,911 | Range low — buy zone |

**Current candle:** O $1,945.78 H $1,984.22 L $1,936.69 C $1,967.25
**Volume delta:** Buy 785M / Sell 753M / Delta +32M (slightly buy-dominant)
**Stochastic (UnnamedPlayer):** %K 43.18, %D 29.10 — crossed up from oversold, now mid-range

**Key observations:**
- Price just tapped POC ($1,966.50) — watching for acceptance or rejection
- Stochastic cross from the low called the $1,853 bottom perfectly
- Now mid-range — not a signal zone, wait for next extreme

### Indicator Settings (from charts)
- **Stochastic:** "UnnamedPlayer" variant (appears to be modified stochastic)
- **Volume Profile:** TPO style with VAH/POC/VAL
- **Monthly levels:** MoVAH, MoVWAP, MoVAL overlaid
- **Yearly VWAP:** 2024 VWAP as macro support/resistance
- **Heatmap:** Blue heatmap orders overlay (ETH chart)
- **Platform:** MMT v2.2.3 (Bookmap/MarketProfile tool)

---

## Trade Management Rules (Learned)

### Position Scaling Out at Targets
1. **50% off at first major target** (opposite range extreme / VAH if long)
2. **Move SL to profit** (below POC or above entry) — remaining position = free trade
3. **Let runner ride** with trailed stop toward next target

### Size Rules by Conviction
| Context | Size |
|---------|------|
| With HTF trend (shorts in bear) | Full size |
| Counter-trend (longs in bear) | **Half size** |
| Feeler / uncertain structure | **10% of capital** |
| A+ confluence zone | Up to full allocation |

### Monthly Seasonality Filter
- **Days 1-6:** Expect retracement, month-low formation window
- **After day 6:** Low likely in place, more confident entries
- Size smaller in early month, fuller size after low confirmed

### Quality Filters (All Must Align)
| Filter | Description |
|--------|-------------|
| **Location** | At range extreme (VAL/VAH) |
| **Structure** | No lower highs (for longs), no higher lows (for shorts) |
| **Momentum** | Lack of downside momentum (for longs), vice versa |
| **Time** | Monthly seasonality context |

*Location alone is NOT enough. Structure + Momentum + Time must confirm.*

### External Range Liquidity Grab Strategy (HTF Short)

**The thesis:** After a range is established, price will eventually sweep above/below the range to grab external liquidity (stop losses + breakout traders). This is a distribution/accumulation event — NOT a real breakout. The move reverses hard back into and through the range.

**How Dub trades it:**
1. **Identify the range** — VAH/VAL/POC from volume profile
2. **Wait for the sweep** — Price breaks above VAH (for shorts) or below VAL (for longs) into external liquidity
3. **Scale into the reversal zone** — 10 limit orders spread through the liquidity zone
4. **Add a market order** for immediate exposure if structure supports it
5. **Target HTF range lows** (for shorts) or highs (for longs) — full range rotation
6. **Manual SL/TP management** — this is a swing trade, expect chop

**Leverage:** 10x (higher conviction due to HTF thesis alignment)
**Capital allocation:** 80% of account across scaled orders + 10% market order for base position
**Funding edge:** Negative funding on rallies = confirmation shorts are correct side

**Key confirmation signals:**
- Negative funding during the rally (market doesn't believe it)
- Liquidity grab matches pre-identified external liquidity zones from chart
- Both BTC and ETH grab external liquidity simultaneously (correlated move)

**Example — March 2026 BTC:**
- Range: VAL $65.5k → VAH $70k
- External liquidity zone: $72k–$75.3k (above MoVAH $73k)
- Execution: 10 limit shorts $72.6k–$75.3k + market short at $72.2k
- Result: 6 of 10 filled, +23% ROE and running, targeting range lows ~$65k

### Trade Scaling Formula (10-Order Method)

When scaling into a zone:
1. Define zone boundaries (e.g., $72.6k to $75.3k)
2. Divide into 10 evenly-spaced levels
3. Equal size per level (total = 80% of capital ÷ 10)
4. Optional: add market order with 10% of capital for immediate exposure
5. Remaining 10% = reserve for adjustments

This gives dollar-cost-averaged entry through the zone — if price extends further, avg entry improves. If it rolls early, you're still positioned.

### Weekend Trading Behaviour
- Weekend = thin liquidity, gap risk elevated → **no new positions, manage existing only**
- After a major move (liq grab + reversal), expect a **Sunday bounce** back toward the previous value area high
- Sunday bounce = opportunity to watch for rejection at VAH (~$69,400) before trend resumes
- If Sunday bounce fails to break back above VAH → trend continuation to VAL confirmed
- MoVAH is a separate, higher level — only relevant if price reclaims VAH first

### Agent Monitoring Rule
- When user flags a time-sensitive setup (CME open, specific catalyst), agent must **actively monitor** into that window and alert — not wait for user to check in.

---

## Current Market Views (as of 2026-03-06 23:02 UTC)

### BTC 4H Market Profile Context
| Level | Price | Notes |
|-------|-------|-------|
| 2024 VAH | $79,314 | Major HTF resistance |
| MoVAH | $72,673 | Monthly VAH — short entry zone |
| VAH | ~$69,400 | Current value area high — bounce target |
| MoVWAP | $68,717 | Monthly VWAP — current area |
| **POC** | **$67,882** | **High volume node — price sitting here now** |
| VAL | ~$65,500 | Current value area low — runner target |
| MoVAL / 2024 VWAP | $65,028 | Major HTF support — ultimate target |

### Current Read (2026-03-06 23:02 UTC)
- **What happened:** Textbook external range liquidity grab. Price swept above range highs → longs piled in → fakeout. Entered short at MoVAH rejection ($72,837). Price accepted back inside value area → melted straight to POC. 
- **Now on weekend trading hours** — thin liquidity, gap risk elevated
- **Bias:** Short thesis confirmed and intact. Sitting at POC, runner risk-free.
- **Active position:** 0.00514 BTC short, entry $72,837, SL $72,000, target VAL $65k

### Weekend Roadmap
1. **Sunday** — Watch for bounce back toward VAH (~$69,400)
2. **Reject VAH** → short trend continues to VAL $65,028 ✅ (runner target)
3. **Break + accept above VAH** → watch MoVAH next; break above MoVAH → reassess short thesis entirely

### Active Watchlist
| Setup | Asset | Level | Direction | Confluence | Status |
|-------|-------|-------|-----------|------------|--------|
| Runner target | BTC | $65,028 | TP | VAL + MoVAL + 2024 VWAP | **Active** |
| Sunday bounce resistance | BTC | $69,400 | Watch | VAH | Watching |
| Reassess level | BTC | $72,673 | SL zone | MoVAH break = thesis broken | Watching |
| Runner SL | BTC | $72,000 | Stop (risk-free) | Below entry | Active |
| VAH fade | ETH | TBD | Short | Range high rotation | Watching |

- **Next:** Patient through weekend. Watch Sunday bounce — expect rejection at VAH ~$69,400. Target VAL $65k if rejected. MoVAH only relevant if VAH is reclaimed.

---

## Completed Trade Log

### ✅ BTC Short — External Range Liquidity Grab (2026-03-06)

| Field | Value |
|-------|-------|
| **Entry** | $72,837 avg (10-order scaled ladder) |
| **Full size** | 0.01286 BTC |
| **Entry zone** | $72.6k–$75.3k (grab zone) |
| **Thesis** | External range liquidity grab + negative funding + distribution |
| **60% exit** | $67,994 — **+$37.36 realized, +66.5% ROE** |
| **40% runner** | 0.00514 BTC, SL $72,000 (risk-free) |
| **Duration** | ~1 day |
| **Outcome** | ✅ Textbook — played out exactly as planned |

**Key lessons:**
- Scaled ladder entries locked in excellent avg price even with partial fills
- Cancelled limit sells when bounce didn't materialise — stayed nimble
- Secured 60% at ~66% ROE, runner rides risk-free to target
- "In front of entry" SL = below entry on shorts (no possible loss)
- Patience through small bounces paid off — didn't stop out early

---

## For The Agent

**Primary Goal:** Learn Dub's trading style rigorously through every trade and TA session. The end goal is autonomous, profitable trading that mirrors his methodology exactly.

**Activate this skill when:**
- Dub asks "thoughts about long/short"
- Analyzing a potential entry or exit
- Reporting on open positions
- Setting up orders
- Receiving any TA or trade-related information

**Always reference:**
- The 5-level scaled entry/exit pattern
- "Not chasing" rule
- Hard stop requirement (5-10% max risk, move to breakeven ASAP)
- Geopolitical risk awareness

**Default to:**
- Patience over FOMO
- Scaled entries over single entries
- Risk-off when uncertain
- Cautious and reduced size when geopolitical risk is elevated

**After EVERY trade or TA update:**
- Update this SKILL.md immediately — no exceptions
- Log the trade in the Completed Trades section
- Extract any new lessons into the Core Philosophy
- Update current market view and active positions
- Do NOT publish to marketplace until Dub explicitly says so

**Terminology learned:**
- "In front of entry" on a short = SL placed *below* entry (no possible loss)
- "Secure profits" = close a % of the position at market
- "Runner" = remaining position after partial close, riding risk-free
- "Sweep the highs" = price moves up to grab liquidity at recent highs before reversing
