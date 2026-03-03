---
name: hyperclaw
version: 1.0.0
description: "Trade perpetual futures on HyperClaw.io — an Orderly Network-powered DEX. Use when the user mentions HyperClaw, wants to trade perps on HyperClaw, deposit/withdraw on HyperClaw, or check positions on HyperClaw."
author: hyperclaw
tags: [trading, perps, orderly, defi, hyperclaw]

metadata:
  starchild:
    emoji: "🦀"
    skillKey: hyperclaw

user-invocable: true
---

# HyperClaw Skill

HyperClaw.io is a perpetual futures DEX built on **Orderly Network** with broker ID `hyper_claw`. All trading, positions, and balances go through Orderly tools — this skill tells you the HyperClaw-specific config and conventions.

## Key Config

| Property | Value |
|----------|-------|
| Broker ID | `hyper_claw` |
| Underlying Protocol | Orderly Network |
| Settlement Chain | Arbitrum |
| Deposit Asset | USDC (native, Arbitrum) |
| Supported Perps | BTC, ETH, SOL (and others on Orderly) |
| Max Leverage | 10x (platform convention) |
| Website | https://hyperclaw.io |

## Prerequisites — Wallet Policy

Before executing any on-chain operation (deposit, withdrawal, bridging), the wallet policy must be active. Load the **wallet-policy** skill and propose the standard wildcard policy (deny key export + allow `*`).

## Workflow

### Deposit USDC to HyperClaw

1. Check wallet USDC balance on Arbitrum: `wallet_balance(chain="arbitrum", asset="usdc")`
2. If USDC is on another chain (e.g. Base), bridge first using **1inch Fusion+** (`oneinch_cross_chain_swap`)
3. Deposit to Orderly: `orderly_deposit(amount=X)`
4. Verify with `orderly_holdings()` — funds settle in 1-5 minutes

### Place a Trade

Use Orderly tools directly — there is no HyperClaw-specific order API:

```
orderly_order(symbol="PERP_BTC_USDC", side="buy", order_type="MARKET", quantity=0.001)
```

Always check `orderly_positions()` after to confirm fill.

### Withdraw from HyperClaw

```
orderly_withdraw(amount=X)
```

Funds return to the connected EVM wallet on Arbitrum.

### Check Account

```
orderly_account()       # fee tier, account ID
orderly_holdings()      # USDC balance
orderly_positions()     # open positions + unrealized PnL
orderly_orders()        # open/historical orders
```

## MAC_CLAW Trading Rules (HyperClaw Agent)

When operating as MAC_CLAW (autonomous trading agent) on HyperClaw:

| Rule | Value |
|------|-------|
| Max Leverage | 10x |
| Risk Per Trade | 0.5% of account |
| Daily Loss Hard Stop | 2% of account |
| Weekly Loss Hard Stop | 6% of account |
| Instruments | BTC, ETH, SOL perps |
| Activation Code | `gekko` |

Stop trading immediately if daily or weekly loss limits are hit. Resume next session.

## Signal Scan Checklist

Before any trade, check:
1. RSI (1h) — avoid entering >70 long or <30 short
2. MACD — confirm direction alignment
3. Bollinger Bands — entry near mid-band is safer than near extremes
4. Funding rate — negative funding favors longs (shorts paying), positive favors shorts
5. Position sizing — size = (account * 0.005) / (entry - stoploss)

## Notes

- Minimum order size on Orderly: 0.001 BTC, 0.01 ETH, 0.1 SOL
- With small accounts (<$100), minimum lot size may force >0.5% risk — log it, don't skip the trade
- HyperClaw frontend: https://hyperclaw.io — for UI actions (username, leaderboard) not yet exposed via API
- No public HyperClaw API as of v1.0.0 — all programmatic access goes through Orderly Network endpoints
