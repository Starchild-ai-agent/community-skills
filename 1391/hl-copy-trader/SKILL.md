---
name: "@1391/hl-copy-trader"
version: 1.0.0
description: "Copy-trade any Hyperliquid trader automatically. Mirrors their positions and orders at your capital scale, with risk controls. Use when user says 'copy trade', 'follow this trader', 'mirror this HL address', 'track this wallet on Hyperliquid', or provides an HL address and capital amount."
author: TomTom
tags: [copy-trading, hyperliquid, BTC, perps, risk-management, trading]

metadata:
  starchild:
    emoji: "📋"
    skillKey: hl-copy-trader
    requires:
      env: [WALLET_SERVICE_URL]

user-invocable: true
---

# HL Copy Trader

**名称 / Name:** HL Copy Trader

**描述（中文）:** 一键跟单 Hyperliquid 上的优质交易员。自动读取目标持仓，按你的资金比例等比缩放同步。资金始终在你自己的钱包中。

**Description (English):** One-click copy trading for top Hyperliquid traders. Automatically mirrors target positions scaled to your capital. Your funds stay in your own wallet.

---

## Prerequisites — Wallet Policy

Before any trade, wallet policy must be active. Load the **wallet-policy** skill and propose the standard wildcard policy (deny key export + allow `*`). Required for HL deposit, order signing, and cancellation.

---

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_address` | string | — | **Required.** Target trader's HL wallet address |
| `my_capital` | number | — | **Required.** Your capital in USDC |
| `risk_stop_pct` | number | 40 | Stop loss %. Liquidate all when account drops below `my_capital × (1 - risk_stop_pct/100)` |
| `sync_interval` | number | 5 | Sync frequency in minutes (1 / 3 / 5 / 15) |
| `max_leverage` | number | 10 | Cap leverage if target uses more |
| `copy_assets` | string | "all" | Coins to copy. "all" or comma-separated e.g. "BTC,ETH" |
| `min_order_size` | number | 10 | Skip scaled orders below this USDC notional |

---

## Initialization Flow

Run `scripts/setup.py` to initialize. It:
1. Reads the target's current HL account value
2. Computes `scale_ratio = my_capital / target_account_value`
3. Shows a confirmation summary to the user (see below)
4. On confirm: deposits if needed, sets leverage, mirrors current positions + orders
5. Registers the sync monitor scheduled task (every `sync_interval` minutes)

**Confirmation summary to show user before starting:**
```
Target trader:   {address} (truncated)
Target capital:  ${target_value:,.0f}
Your capital:    ${my_capital:,.0f}
Scale ratio:     1 : {ratio:.0f}
Stop-loss line:  ${stop_value:,.0f} (−{risk_stop_pct}%)
Sync frequency:  every {sync_interval} min
Assets:          {copy_assets}
Max leverage:    {max_leverage}x
Confirm? (yes/no)
```

---

## Sync Loop Logic

Run `scripts/sync.py` on every scheduled trigger. Steps:

1. **Risk check first** — if `account_value < stop_value`: close all positions, cancel all orders, pause task, notify user.
2. **Fetch target state** — positions + open orders via HL info API.
3. **Fetch my state** — positions + open orders + account value.
4. **Sync positions** — for each target position: scale size, cap leverage, open/adjust/close as needed. Close any position I hold that target no longer holds.
5. **Sync orders** — cancel orders target no longer has (via saved paul_oid→my_oid mapping). Place orders target added. Skip if scaled notional < `min_order_size` or asset not in `copy_assets`.
6. **Notify** — only if something changed. Silent on no-op runs.

State is stored in `tasks/{job_id}/state.json`:
```json
{
  "paused": false,
  "target_address": "0x...",
  "my_capital": 1000,
  "scale_ratio": 0.01,
  "stop_value": 600,
  "sync_interval": 5,
  "max_leverage": 10,
  "copy_assets": "all",
  "min_order_size": 10,
  "paul_orders": {"target_oid": "my_oid"},
  "lang": "zh"
}
```

---

## Notifications & Reports

**Language rule:** detect language from the user's setup command. Store in `state.json` as `lang: "zh"` or `lang: "en"`. All notifications and reports follow that language. User can switch anytime by saying "report in English" or "以后用中文汇报".

**Real-time (on change only):**
- zh: `[时间] 同步完成：新增 X 笔，取消 X 笔，调整 X 笔仓位`
- en: `[time] Synced: +X orders, −X cancelled, X positions adjusted`

**Daily (UTC 00:00):**
- Account value vs starting capital
- Current positions summary (coin, side, size, unrealized PnL)
- Distance to stop-loss line
- Target trader's day performance

**Weekly (Sunday UTC 00:00):**
- Total PnL ($ and %)
- Target trader's week PnL
- Copy deviation analysis (why my % ≠ target %)
- Operation stats
- Parameter tuning suggestions

---

## Risk Warning (always show on setup)

⚠️ Copy trading carries risk. Past performance ≠ future results.
- 5-min sync delay means your fills differ from the target's
- Small scaled orders may be skipped (below `min_order_size`)
- Start with small capital to validate before scaling up
- You can stop anytime — your funds stay in your own HL account

---

## Key Implementation Notes

- Use `HyperliquidClient` from `skills/hyperliquid/client.py` for all HL calls
- BTC minimum order size on HL is **0.001 BTC** — always `max(scaled_size, 0.001)`
- After opening position, verify fill via `get_account_state` before confirming
- Deduplication: run cleanup pass on my orders before first sync to avoid doubling
- Scale ratio must be recomputed if target's account value changes significantly (>20%)
- For the weekly report, compare realized PnL from fills, not mark-to-market

---

## Files

| File | Purpose |
|------|---------|
| `scripts/setup.py` | One-time initialization, confirmation, deposit, initial mirror |
| `scripts/sync.py` | Sync loop — called by scheduled task every N minutes |
| `references/api.md` | HL API notes and client method reference |
