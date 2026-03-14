---
name: "@1458/dust-sweeper"
version: 2.0.0
description: "Scan a wallet for small-balance ERC-20 or SPL tokens ('dust') and swap them to ETH/USDC/SOL via Odos (EVM) or Jupiter (Solana). Use when the user says 'sweep my dust', 'clean up my wallet', 'sell my small token balances', or asks what tiny holdings they have. Supports Ethereum, Base, Arbitrum, and Solana."
author: starchild
tags: [wallet, defi, ethereum, base, arbitrum, solana, odos, jupiter, dust, erc20, spl, cleanup, multi-chain]

metadata:
  starchild:
    emoji: "🧹"
    skillKey: dust-sweeper

user-invocable: true
---

# Dust Sweeper v2

Identify and swap low-value tokens ("dust") to ETH, USDC, USDT, or SOL — across EVM chains and Solana. Uses **Odos** for EVM (batch-optimized, better execution than 1inch for multi-token sweeps) and **Jupiter** for Solana. No middlemen, no discount haircut, no 24h wait.

---

## Prerequisites — Wallet Policy

Before executing any swaps or approvals, the wallet policy must be active.  
Load the **wallet-policy** skill and propose the standard wildcard policy  
(deny key export + allow `*`). This covers all Odos approvals and swaps.

---

## Supported Chains

| Chain | Aggregator | Native Output |
|---|---|---|
| Ethereum mainnet | Odos | ETH |
| Base | Odos | ETH |
| Arbitrum | Odos | ETH |
| Solana | Jupiter | SOL |

Ask the user which chain(s) to scan. Default: **all chains** (scan everything, sweep what's profitable).

---

## Workflow

### Phase 1 — Discovery

**EVM chains (Ethereum, Base, Arbitrum):**
1. Call `wallet_balance(chain=<chain>)` **without** an `asset` filter for each chain — returns ALL tokens with non-zero balances.
2. For each token, get a USD value:
   - Use `cg_token_price(platform=<chain>, contract_addresses=<address>)` for price.
   - Fallback: Odos quote with full balance to probe the market.
3. Flag tokens as **dust** if their USD value is **below the dust threshold** (default: $50).

**Solana:**
1. Call `wallet_sol_balance()` **without** an `asset` filter — returns ALL SPL tokens.
2. Price each SPL token via `cg_token_price(platform="solana", contract_addresses=<mint_address>)`.
3. Flag as dust if below threshold.

Show the user the full dust inventory before executing anything.  
Format: `chain | token symbol | balance | USD value`

---

### Phase 2 — Profitability Filter

For each dust token:
1. Quote the full balance via the appropriate aggregator:
   - **EVM:** Odos quote, `dst = native ETH` (`0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`) or USDC/USDT if user prefers.
   - **Solana:** Jupiter quote, `outputMint = SOL` or USDC.
2. Estimate gas cost:
   - EVM: approve (~$1–3) + swap (~$3–8 mainnet, ~$0.10–0.50 Base/Arbitrum). Assume $10 on mainnet, $1 on L2s if no live data.
   - Solana: ~$0.001 per transaction.
3. **Skip** if: `quoted_output_usd < gas_cost_usd + MIN_PROFIT_USD` (default MIN_PROFIT = $2).
4. Report skipped tokens with reason ("gas would eat the value").

**L2 advantage:** On Base and Arbitrum, gas is cheap enough ($0.10–0.50) that tokens as small as ~$3–5 can be worth sweeping.

---

### Phase 3 — Execution

**EVM (Odos):**
1. Check allowance: skip approval if already approved for Odos router.
2. `odos_approve(chain=<chain>, token_address=...)` — approve Odos router.
3. `odos_swap(chain=<chain>, input_token=token_address, output_token=0xEeee..., amount=..., slippage=2.0)`.
4. Odos supports **multi-token batch swaps** — if multiple tokens need sweeping on the same chain, batch them into a single transaction where possible. This cuts gas vs. one-by-one.
5. After each swap/batch: report tokens swept, ETH/USDC received, tx hash.

**Solana (Jupiter):**
1. Use Jupiter swap route for each SPL token → SOL (or USDC).
2. Sign and send via `wallet_sol_transfer`.
3. Report: token name, amount swapped, SOL/USDC received, tx signature.

---

### Phase 4 — Summary

Report per chain:
- Tokens swept, total USD recovered
- Tokens skipped (unpriced, unprofitable, errored)
- Net ETH/SOL received

Final line: `"Swept N tokens across X chains, recovered ~$Y in ETH/SOL."`

---

## Key Parameters (ask user if not specified)

| Parameter | Default | Notes |
|---|---|---|
| Dust threshold | $50 USD | Tokens above this are NOT dust |
| Min profit after gas | $2 USD | Skip swaps that barely cover gas |
| Slippage | 2% | Dust tokens often have thin liquidity |
| Output token (EVM) | Native ETH | Or USDC/USDT if user prefers |
| Output token (Solana) | SOL | Or USDC |
| Chains to scan | All (ETH + Base + ARB + SOL) | User can narrow to specific chains |

---

## Token Addresses

**Native ETH (all EVM chains):** `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`

**Ethereum mainnet:**
- WETH: `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`
- USDC: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`
- USDT: `0xdAC17F958D2ee523a2206206994597C13D831ec7`

**Base:**
- USDC: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`

**Arbitrum:**
- USDC: `0xaf88d065e77c8cC2239327C5EDb3A432268e5831`

**Solana:**
- USDC mint: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`
- SOL mint (native): `So11111111111111111111111111111111111111112`

---

## Gotchas

**Odos vs 1inch:** Odos is optimized for multi-token routing and typically gives better execution on dust sweeps with thin liquidity. Prefer Odos for EVM. If Odos is unavailable, fall back to 1inch with same parameters.

**Unpriced tokens:** If CoinGecko returns no price and Odos/Jupiter return no quote, skip — don't waste gas on un-routable tokens.

**Fee-on-transfer tokens:** If a swap fails, log the error and move on. Don't abort the whole sweep.

**Batch vs single:** Odos PathFinder can handle multi-input single-output routes (many tokens → ETH in one tx). Use this when available — it's significantly cheaper on mainnet.

**Approvals are permanent.** Unlimited approvals to Odos router are standard practice. Offer exact-amount approvals if user is security-conscious.

**Gas spikes (mainnet):** If ETH gas > 30 gwei, warn the user. L2 sweeps (Base, Arbitrum) are almost always worth it regardless. Offer to schedule mainnet sweep for off-peak hours.

**Don't touch tokens the user might want.** Always confirm the sweep list before Phase 3. Never auto-execute without showing the inventory first.

**Solana dust is cheap to sweep.** At ~$0.001/tx, even $1 tokens can be worth sweeping on Solana. Lower the MIN_PROFIT threshold to $0.50 for Solana by default.

---

## Dry Run Mode

If the user says "what dust do I have?" or "show me my dust" without asking to sweep — run Phase 1 + Phase 2 only. Show the inventory and what would be profitable to sweep, but don't execute Phase 3.

---

## Scheduling

For recurring sweeps (e.g. "sweep my dust every Sunday"), use `schedule_task` with cron `0 10 * * 0` (Sunday 10am UTC). Note: wallet policy must be persistent. L2 chains are good candidates for frequent scheduled sweeps given low gas costs.
