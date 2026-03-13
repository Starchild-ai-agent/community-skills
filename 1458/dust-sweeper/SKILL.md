---
name: "@1458/dust-sweeper"
version: 1.0.0
description: "Scan a wallet for small ERC-20 dust balances and swap them to ETH/USDC via 1inch. Use when the user says 'sweep my dust', 'clean up my wallet', 'sell my small token balances', or asks what tiny holdings they have."
author: starchild
tags: [wallet, defi, ethereum, 1inch, dust, erc20, cleanup]

metadata:
  starchild:
    emoji: "🧹"
    skillKey: dust-sweeper

user-invocable: true
---

# Dust Sweeper

Identify and swap low-value ERC-20 tokens ("dust") to ETH or USDC via 1inch. No middlemen, no discount haircut, no 24h wait — just the agent acting directly.

## Prerequisites — Wallet Policy

Before executing any swaps or approvals, the wallet policy must be active.
Load the **wallet-policy** skill and propose the standard wildcard policy
(deny key export + allow `*`). This covers all 1inch approvals and swaps.

---

## Workflow

### Phase 1 — Discovery

1. Call `wallet_balance(chain="ethereum")` **without** an `asset` filter — this returns ALL ERC-20 tokens with non-zero balances.
2. For each token returned, get a USD value:
   - Use `birdeye_token_overview(address=contract_address, chain="ethereum")` for the price.
   - Fallback: `oneinch_quote()` with a small amount to probe the market.
3. Flag tokens as **dust** if their total USD value is **below the dust threshold** (default: $50).
4. Show the user the dust inventory before executing anything. Format: token symbol, balance, USD value.

### Phase 2 — Profitability Filter

For each dust token, before approving:
1. Call `oneinch_quote(chain="ethereum", src=token_address, dst=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE, amount=full_balance_in_wei)` to quote against native ETH. If 1inch rejects native ETH as destination, fall back to WETH (`0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`).
2. Estimate gas cost: typical approve (~$1–3) + swap (~$3–8) at current gas price. If gas data isn't available, assume $10 total.
3. **Skip** any token where: `quoted_output_usd < gas_cost_usd + MIN_PROFIT_USD` (default MIN_PROFIT = $2).
4. Report skipped tokens with reason ("gas would eat the value").

### Phase 3 — Execution

For each token that passed the filter:
1. `oneinch_check_allowance(chain="ethereum", token_address=...)` — skip approval if already approved.
2. `oneinch_approve(chain="ethereum", token_address=...)` — unlimited approval to 1inch router.
3. `oneinch_swap(chain="ethereum", src=token_address, dst=0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE, amount=..., slippage=2.0)` — native ETH by default. If 1inch returns an error on native ETH destination, retry with WETH (`0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`).
4. After each swap, report: token name, amount swapped, ETH received, tx hash.

### Phase 4 — Summary

Report total: "Swept N tokens, recovered ~$X.XX in ETH." Include any skips and why.

---

## Key Parameters (ask user if not specified)

| Parameter | Default | Notes |
|---|---|---|
| Dust threshold | $50 USD | Tokens above this are NOT dust |
| Min profit after gas | $2 USD | Skip swaps that barely cover gas |
| Slippage | 2% | Dust tokens often have thin liquidity |
| Output token | Native ETH | Falls back to WETH if 1inch rejects native destination; can swap to USDC instead if user prefers |
| Chain | ethereum | Multi-chain support planned; start with mainnet |

---

## Token Addresses (Ethereum Mainnet)

- **WETH:** `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`
- **USDC:** `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`
- **Native ETH:** `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`

Always try **Native ETH** as the destination first — users get ETH directly, no unwrap needed. Only fall back to WETH if 1inch returns an error on the native ETH destination.

---

## Gotchas

**Birdeye may not know obscure tokens.** If `birdeye_token_overview` returns no price, use `oneinch_quote` with a tiny amount (1000 wei) — if it returns a quote, at least you know the token is swappable. If no quote either, skip it.

**Some tokens are non-transferable or fee-on-transfer.** If `oneinch_swap` fails, log the error and move on — don't abort the whole sweep.

**Approvals are permanent.** Unlimited approvals to 1inch are standard practice but worth mentioning to the user if they're security-conscious. Offer to use exact-amount approvals instead.

**Gas spikes kill profitability.** If ETH gas > 30 gwei, warn the user and suggest waiting. The sweep can be scheduled for off-peak hours.

**Don't touch tokens the user might want.** Before sweeping, confirm the list. Never auto-execute without showing the user what will be swept first.

---

## Dry Run Mode

If the user says "what dust do I have?" or "show me my dust" without asking to sweep, do Phase 1 + Phase 2 only — show the inventory and what would be profitable to sweep — but don't execute Phase 3.

---

## Scheduling

If the user wants recurring sweeps (e.g. "sweep my dust every Sunday"), use `schedule_task` with a cron expression (`0 10 * * 0` = Sunday 10am UTC). The task should run the sweep and report results via the daily context. Note this requires the wallet policy to be persistent.
