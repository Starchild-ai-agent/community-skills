---
name: "@1247/cross-venue-router"
version: 2.0.0
description: Cross-venue smart order router + persistent strategies + risk monitoring across Hyperliquid and Orderly
author: starchild
tags: [trading, cross-venue, routing, dca, risk, hyperliquid, orderly]
tools:
  - hl_order
  - hl_account
  - hl_orderbook
  - hl_market
  - hl_candles
  - hl_funding
  - hl_balances
  - hl_leverage
  - hl_tpsl_order
  - hl_cancel
  - hl_cancel_all
  - hl_open_orders
  - hl_fills
  - woo_orderbook
  - woo_order
  - woo_positions
  - woo_holdings
  - woo_close
  - schedule_task
  - cancel_scheduled_task
  - list_scheduled_tasks
  - memory_store
  - memory_search
emoji: 🔀
tags: [trading, routing, dca, risk, portfolio, cross-venue]
---

# 🔀 Cross-Venue Router

**What:** A Starchild skill that makes Hyperliquid and Orderly act as one venue. Routes trades to best execution, runs persistent strategies in the background, monitors risk 24/7, and gives a unified portfolio view.

**Why it exists:** Current skills are single-venue and request-response. This skill adds three things that didn't exist:
1. **Cross-venue routing** — compare both venues, execute where cost is lowest
2. **Persistent strategies** — DCA, TWAP, grid, conditionals that keep running after conversation ends
3. **Always-on risk** — monitors positions across venues, alerts before problems

## Who it's for

Traders using Starchild who have accounts on both Hyperliquid and Orderly and want:
- Best execution without manually checking both venues
- Automated strategies that survive session restarts
- Portfolio-level risk awareness across venues

---

## 1. Routing Engine

### How routing works

When user says "buy 0.5 BTC":

1. **Pull orderbooks** from both venues simultaneously
   - `hl_orderbook(coin="BTC")` + `woo_orderbook(coin="BTC")`
2. **Walk the book** — simulate VWAP fill at requested size
3. **Add fees** to get true cost per venue
4. **Recommend** the cheaper venue (or split if V2)

### Fee reference (fallback if API unavailable)

| Venue | Maker | Taker |
|-------|-------|-------|
| Hyperliquid | 0.010% | 0.035% |
| Orderly | 0.020% | 0.050% |

Always try to pull live fees first (`hl_account` meta, Orderly fee endpoint).

### Cost formula

```
total_cost = vwap_fill_price × size × (1 + taker_fee_rate)
slippage = (vwap_fill_price - mid_price) / mid_price
effective_cost = slippage + fee_rate
```

Compare `effective_cost` across venues. Route to lowest.

### Output format

```
🔀 Routing: BUY 0.5 BTC

         Hyperliquid    Orderly
Mid:     $69,225        $69,325
VWAP:    $69,226        $69,340
Fee:     0.035%         0.050%
Cost:    $12.36         $19.52
Depth:   32.4 BTC       1.17 BTC

→ Route to Hyperliquid (37% cheaper)
Execute? [y/n]
```

Wait for user confirmation before executing. Never auto-execute a routed trade.

## 2. Persistent Strategies

Strategies use `schedule_task` for persistence. Each strategy stores state in `memory_store` under topic `strategy-{id}`.

### DCA (Dollar-Cost Average)
- **Trigger:** "DCA $100 into ETH every 4 hours on best venue"
- **Implementation:** `schedule_task(schedule="every 4 hours", task="...")` where task includes routing logic
- **State:** total invested, avg entry, fills count, venue breakdown
- **Stop conditions:** total budget hit, user cancels, price outside bounds

### TWAP (Time-Weighted Average Price)
- **Trigger:** "Buy 2 ETH over the next 6 hours"
- **Implementation:** Split into N slices (e.g., 12 × 0.167 ETH every 30 min), each slice routed independently
- **State:** slices remaining, fills so far, avg price achieved vs benchmark

### Grid
- **Trigger:** "Run a grid on ETH between $3,400–$3,800, 10 levels"
- **Implementation:** Place limit orders at grid levels. On fill, place opposite order one level away.
- **Venue selection:** Place on venue with better maker fees (usually HL at 0.01%)
- **State:** grid levels, active orders, realized PnL, fills per level

### Trailing Stop
- **Trigger:** "Trail my BTC long with 3% stop"
- **Implementation:** Poll every 5 min, update stop-loss price as price rises
- **State:** current trail price, high-water mark, trigger distance

### TP Ladder
- **Trigger:** "Take profit on my ETH: 25% at $4k, 50% at $4.5k, 25% at $5k"
- **Implementation:** Place limit sells at each level, or use `hl_tpsl_order` / Orderly TP
- **State:** levels, fill status per level

### Conditional Entry
- **Trigger:** "Buy ETH if BTC drops below $65k"
- **Implementation:** `schedule_task(schedule="every 15 minutes", task="check BTC price, if < 65000 then route buy ETH")` 
- **Self-destruct:** Cancel schedule after trigger fires or after user-set expiry

### Strategy management

All active strategies stored in memory topic `active-strategies`. Commands:
- "Show my strategies" → list all active with status + PnL
- "Pause DCA" → cancel scheduled task, preserve state
- "Resume DCA" → recreate schedule from saved state
- "Kill all strategies" → cancel all strategy-related scheduled tasks

### Task naming convention

All strategy tasks use label format: `strategy-{type}-{coin}-{timestamp}`
Example: `strategy-dca-ETH-1710864000`


## 3. Risk Monitoring

### Always-on monitor

Set up via: "Monitor my positions" or "Turn on risk alerts"

**Implementation:** `schedule_task(schedule="every 30 minutes", task="...")`

The monitor checks:

| Check | Threshold | Action |
|-------|-----------|--------|
| Liquidation buffer | <15% margin remaining | ⚠️ Alert user |
| Liquidation buffer | <8% margin remaining | 🚨 URGENT alert + suggest reduce |
| Notional exposure | >80% of account value | Warn over-leveraged |
| Single-asset concentration | >60% of portfolio | Warn concentration risk |
| Funding bleed | Paying >0.05%/8h cumulative | Suggest venue migration |
| Venue health | API errors or latency spike | Alert + pause strategies |

### Cross-venue aggregation

```
Portfolio snapshot:
├── Hyperliquid
│   ├── BTC-PERP: +0.5 long @ $68,200 (PnL: +$512)
│   ├── ETH-PERP: +3.0 long @ $3,450 (PnL: -$89)
│   └── Margin used: $4,200 / $12,000 (35%)
├── Orderly
│   ├── SOL-PERP: +50 long @ $142 (PnL: +$200)
│   └── Margin used: $1,800 / $5,000 (36%)
└── TOTAL
    ├── Net exposure: $58,750 long
    ├── Total margin: $6,000 / $17,000 (35%)
    └── Effective leverage: 3.5x
```

### Position migration

If funding rate diverges significantly between venues:
- "Your ETH long on HL is paying 0.08%/8h. Orderly charges 0.02%/8h. Want me to migrate?"
- Migration = close on expensive venue + open on cheap venue, routed atomically (close first, then open)

### Funding arbitrage

When same asset has divergent funding across venues (>0.01%/8h delta):
- Alert user to opportunity
- If user opts in: go long on negative-funding venue, short on positive-funding venue
- Monitor convergence, suggest exit when spread normalizes

## 4. Portfolio View

**Trigger:** "Show my portfolio" / "What's my exposure?"

Pulls from both venues simultaneously:
- `hl_account()` + `hl_balances()` for Hyperliquid
- `woo_positions()` + `woo_holdings()` for Orderly

Presents unified view:
- Positions by asset (merged across venues)
- Total PnL (realized + unrealized)
- Margin utilization per venue
- Net directional exposure
- Funding costs (daily/weekly projection)

## 5. Safety Rules

1. **No auto-execution on routed trades.** Always show comparison and wait for confirmation.
2. **Size sanity check.** If order is >25% of account equity, warn before proceeding.
3. **Strategy budget caps.** Every persistent strategy must have a max budget. No infinite DCA.
4. **Fail-safe on API errors.** If either venue API is unreachable during strategy execution, skip that slice and alert user. Do NOT blindly route to the other venue.
5. **Kill switch.** "Stop everything" cancels all scheduled strategies immediately.
6. **No margin increase without asking.** Never auto-increase leverage to fill an order.
7. **Liquidation guard.** Refuse to open new positions if either venue margin utilization >85%.
8. **Venue down handling.** If a venue is unreachable, all strategies on that venue pause automatically. Resume when healthy.

## 6. UX Flows

### First-time user
```
User: "Buy some ETH"
Agent: I can route this across Hyperliquid and Orderly for best execution.
       How much ETH? And market order or limit?
User: "0.5 ETH, market"
Agent: [runs routing comparison]
       HL: $1,732.50 total cost (0.02% slippage + 0.035% fee)
       Orderly: $1,738.20 total cost (0.05% slippage + 0.050% fee)
       → Hyperliquid is $5.70 cheaper. Execute there?
User: "yes"
Agent: [executes on HL, confirms fill]
       Filled 0.5 ETH @ $3,464.10 on Hyperliquid. Fee: $0.61.
```

### Setting up DCA
```
User: "DCA $500 into BTC weekly"
Agent: Got it. I'll buy ~$500 BTC every week, routed to whichever
       venue is cheapest at execution time.
       Budget cap? (I'll stop after this amount)
User: "$10,000 total"
Agent: Running: $500/week BTC DCA, best-venue routing, $10k cap.
       That's 20 weeks. I'll send you a summary after each buy.
       Say "show my strategies" anytime or "stop DCA" to kill it.
```

### Risk alert (push)
```
Agent: ⚠️ Risk Alert — ETH position on Hyperliquid
       Your margin buffer is at 12% (threshold: 15%).
       ETH is down 8% in the last 4 hours.
       Options:
       1. Reduce position by 30% (brings buffer to ~25%)
       2. Add $500 margin
       3. Move to Orderly (lower maintenance margin)
       4. Do nothing (I'll alert again at 8%)
```

## 7. Build Sequence

| Week | Deliverable |
|------|-------------|
| 1 | Routing engine: orderbook pull, VWAP walk, fee calc, comparison output |
| 2 | DCA + TWAP strategies with schedule_task persistence |
| 3 | Risk monitor: margin checks, liquidation alerts, kill switch |
| 4 | Portfolio view: cross-venue aggregation, funding projection |
| 5 | Grid + trailing stop + TP ladder strategies |
| 6 | Conditional triggers, funding arb detection |
| 7 | Position migration, venue health monitoring |
| 8 | Polish: error handling, edge cases, UX refinement |

### Supported assets (V1)
BTC, ETH, SOL — expand based on demand.

### Future venues (V2+)
Architecture is venue-agnostic. Adding a venue means:
1. Orderbook pull function
2. Order execution function
3. Position/balance query function
4. Fee schedule

dYdX, GMX, Vertex are natural next candidates.
