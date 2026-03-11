---
name: "@1363/copy-trade"
version: 1.0.0
description: "Copy trade Hyperliquid wallets — monitor profitable traders and mirror their positions automatically. Use when the user wants to follow a wallet, copy trades, set up auto-mirroring, or manage copy trade configurations."
author: dub
tags: [trading, hyperliquid, copy-trade, automation, defi]

metadata:
  starchild:
    emoji: "🔄"
    skillKey: copy-trade
    requires:
      env: [WALLET_SERVICE_URL]
      bins: [python3]
    install:
      - kind: pip
        package: requests

user-invocable: true
---

# Hyperliquid Copy Trade

Mirror positions from profitable Hyperliquid wallets onto your account. Works with the **hl-trader-rankings** skill to find wallets worth copying.

## Prerequisites — Wallet Policy

Before executing copy trades, the wallet policy must be active. Load the **wallet-policy** skill and propose the standard wildcard policy (deny key export + allow `*`).

## Workflow

### 1. Analyze First (hl-trader-rankings)

Never copy blind. Use hl-trader-rankings to evaluate a wallet before following:
- ROI and PnL history
- Drawdown profile
- Leverage habits
- Trading style (scalper vs swing vs position)

**Red flags:** Drawdown >30%, leverage >20x, <1 month history, single lucky trade.

### 2. Configure Copy Mode

Three sizing modes available:

**Proportional** — Scales target's position sizes by account ratio.
```
Your $200 account / Their $4M account = 0.005% ratio
Their $2M STRK short → Your ~$100 STRK short
```
Use `--scale` to adjust (0.5 = half size, 2.0 = double).

**Fixed** — Same USD amount for every position regardless of target's sizing.
```
--fixed-size 50 → Every copied position is ~$50 notional
```
Best for: testing, small accounts, equal-weighting.

**Custom** — Specify exact sizes per coin.
```python
custom_sizes = {"BTC": 0.001, "ETH": 0.01, "SOL": 1.0}
```
Best for: copying specific plays, not full portfolio.

### 3. Set Safety Rails

Always configure:
- `--max-leverage N` — Hard cap (default 10x, even if target uses 50x)
- `--max-position N` — Max USD per position (default $500)
- `--leverage N` — Override all positions to this leverage
- `--blacklist COIN1 COIN2` — Skip specific coins
- `--whitelist COIN1 COIN2` — Only copy these coins

### 4. Run Copy Check

**One-shot scan** (detect what needs changing):
```bash
python3 skills/copy-trade/scripts/orchestrator.py \
  --target 0xADDRESS \
  --mode fixed --fixed-size 50 --leverage 5 \
  --max-leverage 10 --max-position 200
```

**With your address** (compares actual positions):
```bash
python3 skills/copy-trade/scripts/orchestrator.py \
  --target 0xTARGET --my-address 0xYOURS \
  --mode proportional --my-account 200
```

**Check status:**
```bash
python3 skills/copy-trade/scripts/orchestrator.py --status
```

**Stop copying:**
```bash
python3 skills/copy-trade/scripts/orchestrator.py --stop
```

### 5. Execute Actions

The orchestrator outputs structured commands. Execute them in order:

```json
{
  "tool": "hl_leverage",
  "params": {"coin": "STRK", "leverage": 5, "cross": true}
}
{
  "tool": "hl_order", 
  "params": {"coin": "STRK", "side": "sell", "size": 100.0}
}
```

For each command: call the tool with the given params. Verify fills with `hl_account()` after.

### 6. Schedule Recurring Monitoring

For ongoing copy trading, schedule the orchestrator:

```python
schedule_task(
    command="python3 skills/copy-trade/scripts/orchestrator.py --target 0x... --mode fixed --fixed-size 50 --leverage 5",
    schedule="every 5 minutes"
)
```

The agent reviews output each cycle and executes any new actions.

## Sizing Cheat Sheet

| Account Size | Suggested Mode | Config |
|-------------|---------------|--------|
| <$500 | Fixed | `--fixed-size 20-50 --max-leverage 5` |
| $500-$2k | Proportional | `--scale 1.0 --max-leverage 10` |
| $2k-$10k | Proportional | `--scale 1.0 --max-position 1000` |
| >$10k | Proportional | `--scale 0.5-1.0` (conservative) |

## Risk Management

- **Daily loss limit** — Set in config JSON. Engine stops if hit.
- **Max positions** — Don't overextend. 5-10 max for small accounts.
- **Leverage cap** — Always cap. Target using 50x doesn't mean you should.
- **Latency** — Polling-based, not streaming. 1-5 min delay. Fine for swing/position traders, bad for scalpers.
- **Slippage** — Market orders may fill at different prices than target's entry. Worse on low-liquidity coins.

## Scripts

| Script | Purpose |
|--------|---------|
| `copy_engine.py` | Core diff engine — detects position changes |
| `orchestrator.py` | Bridges engine output to HL tool commands |

## State Management

State is tracked in `/data/workspace/output/copy_trade_state.json`:
- Positions we've copied
- Target snapshots (last known positions)
- Execution history

The state file is the source of truth for what we're mirroring. If you manually close a copied position, run `--stop` to reset state.
