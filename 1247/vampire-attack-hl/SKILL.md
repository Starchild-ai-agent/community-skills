---
name: "@1247/vampire-attack-hl"
version: 1.0.0
author: starchild
tags: [hyperliquid, orderly, trading-costs, slippage, fees]
description: "Hyperliquid-only vampire attack analysis. Use when you need a personalized 30d cost-leakage report (fees + slippage) and an Orderly counterfactual savings pitch for a wallet."

metadata:
  starchild:
    emoji: "🧛"
    skillKey: vampire-attack-hl
    requires:
      bins: [python3]

user-invocable: true
---

# Vampire Attack HL

You analyze a wallet's Hyperliquid trade history, quantify cost leakage over the last 30 days, and generate a personalized migration report showing estimated savings if the same flow were routed through Orderly.

## Workflow

1. Collect wallet address
   - Default mode supports both: connected wallet or manual wallet input.
   - Validate it is a 0x-address.

2. Run analyzer script
   - Command:
     - `python3 skills/vampire-attack-hl/scripts/analyze_hl_wallet.py --wallet <0x...>`
   - Optional knobs:
     - `--days 30`
     - `--orderly-taker-bps 3.0`
     - `--orderly-maker-bps 0.0`
     - `--orderly-slippage-improvement-bps 0.0`

3. Read output JSON + markdown report path from script stdout
   - JSON = machine-readable facts
   - Markdown = client-facing pitch draft

4. Present conclusions
   - Always separate **exact** vs **estimated** metrics:
     - Exact: Hyperliquid fees/builder fees from fills
     - Estimated: slippage and counterfactual savings
   - Include both:
     - projected total savings
     - conservative fee-only savings baseline

## Interpretation Rules

- If projected savings > 0 and fee-only savings > 0: strong migration case.
- If projected savings > 0 but fee-only <= 0: migration case depends on slippage assumptions; present as conditional.
- If projected savings <= 0: do not force migration pitch; recommend re-running with tier-specific assumptions.

## Guardrails

- Do not call slippage "exact".
- Do not invent fee tiers. Use explicit assumptions shown in output.
- If no fills are found, report that clearly and ask for a different window/wallet.

## Resources

- Script: `skills/vampire-attack-hl/scripts/analyze_hl_wallet.py`
- Method: `skills/vampire-attack-hl/references/methodology.md`
