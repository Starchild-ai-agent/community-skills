---
name: "@432/meta-dex-aggregator"
description: "Meta DEX Aggregator — aggregator of aggregators. Compares quotes across ParaSwap, Odos, KyberSwap, CowSwap, Matcha/0x, and 1inch to find the best swap price. Includes safety layer: price impact detection, gas-adjusted ranking, MEV protection flagging, slippage warnings, outlier quote rejection, built-in execution with verification, CowSwap order polling, historical quote logging, winner analytics, market orders, auto-verify, and retry logic."
version: 3.1.1
tools:
  - bash
  - oneinch_quote
  - oneinch_tokens
  - oneinch_check_allowance
  - oneinch_approve
  - oneinch_swap
  - oneinch_cross_chain_quote
  - oneinch_cross_chain_swap
  - wallet_balance
  - wallet_transfer
---

# Meta DEX Aggregator — Multi-Source Quote Comparison with Safety Layer

**v3.0.0** — Now with built-in execution, CowSwap polling, historical logging, and analytics.

Aggregator of aggregators. Queries 6 DEX aggregators in parallel, ranks by
gas-adjusted net output, and runs safety checks before execution.

## New in v3.1.0

| Feature | Description |
|---------|-------------|
| **Market orders** | `--market-order` uses 1inch for instant execution (no limit order failures) |
| **Auto-verify** | `--auto-verify` fetches balances automatically via RPC |
| **Retry logic** | Fallback to next best aggregator on failure |
| **Better gas estimation** | Calibrated per aggregator (150k-300k vs flat 580k) |
| **Price freshness check** | Warns if quote is >30s old before execution |

## New in v3.0.0

| Feature | Description |
|---------|-------------|
| **Built-in execution** | `execute` command handles swap + verification in one flow |
| **CowSwap polling** | Auto-poll CowSwap orders until fulfilled (up to 2 min) |
| **Historical logging** | Every quote logged to JSONL for trend analysis |
| **Winner analytics** | `stats` command shows which aggregator wins most often |
| **Price trends** | `trend` command shows net output over time |
| **Slippage analysis** | `slippage` command analyzes competitive spreads |
| **CSV export** | `export` command for external analysis |
| **Quote monitoring** | `monitor` command alerts when target net output is reached |

## Safety Features

1. **Price Impact** — Fetches fair market price from DefiLlama coins API
   (+ DexScreener fallback), compares vs quote output.
   Thresholds: 3% warning, 5% high, 10% critical (blocks swap).
2. **Gas-Adjusted Ranking** — `netOut = amountUsd - gasUsd`. Best route ≠ most tokens.
3. **MEV Protection Flags** — CowSwap and 0x Gasless are flagged `isMEVSafe`.
   Recommends MEV-safe route when within 0.5% of best price.
4. **Slippage Warnings** — Sandwich risk >1%, stablecoin pairs >0.05%, too-low revert risk.
5. **Outlier Detection** — Quotes >5% worse than best are flagged as outliers.
6. **Post-Swap Verification** — Mandatory balance checks, flags >2% deviation.

## Aggregators

| Adapter | API Key | Status | MEV-Safe |
|---------|---------|--------|----------|
| ParaSwap | None needed | ✅ | ❌ |
| Odos | None needed | ✅ | ❌ |
| KyberSwap | None needed | ✅ | ❌ |
| CowSwap | None needed | ✅ | ✅ |
| 1inch | Native tool (platform-proxied) | ✅ | ❌ |
| Matcha/0x | `OX_API_KEY` in .env | ✅ | ❌ |

**CowSwap:** Batch auction protocol — solvers compete off-chain, user never exposed to MEV.
Gasless for the user (solvers pay). Supported on Ethereum, Arbitrum, Gnosis, Base.
Uses wrapped native tokens (WETH) internally — raw ETH is auto-converted.
Execution is order-based (EIP-712 signed intent), not raw transaction.

## Workflow: Quote with Safety Check

**Step 1 & 2 run in PARALLEL (no dependency between them):**

```bash
# 1. Get 5 aggregator quotes (ParaSwap, Odos, KyberSwap, CowSwap, Matcha/0x + safety)
cd skills/meta-dex-aggregator/scripts && \
  python3 meta_dex.py quote --chain base --from ETH --to USDC --amount 0.5 --slippage 0.5
```

```
# 2. Get 1inch quote via native tool (proxied, no API key needed)
oneinch_quote(chain="base", src="<from_addr>", dst="<to_addr>", amount="<amount_in_wei>")
# Returns: { "dstAmount": "<raw_amount>" }
# Convert: dstAmount / 10^decimals = human amount
```

**Step 3 — Merge & present:**
- Script returns quotes with: `aggregator`, `amountOutHuman`, `amountUsd`, `gasUsd`, `netOut`, `vsbestPct`
- 1inch native tool returns `dstAmount` (raw wei) — convert to human amount using token decimals
- Insert 1inch into the ranked table, recalculate `vsbestPct` if 1inch is the new winner
- The script's `safety` block (priceImpact, slippageWarnings, recommendation) applies to all quotes
- If `priceImpact.severity` is "high"/"critical" — WARN and **block the swap**
- Execute via `oneinch_swap` if 1inch wins, or `wallet_transfer` with tx data for others

## Workflow: Execute Swap (v3.1.0 — Market Orders + Auto-Verify)

**NEW in v3.1.0:**
- `--market-order` flag for instant 1inch execution (no limit order failures)
- `--auto-verify` flag for automatic balance fetching (no manual args)
- Retry logic with fallback aggregators on failure

### **Option A: Market Order (Recommended for < $100 swaps)**

```bash
# Instant execution via 1inch market order
cd skills/meta-dex-aggregator/scripts && \
  python3 meta_dex.py execute --chain arbitrum --from ETH --to USDC --amount 0.005 \
    --market-order --wallet 0x... --slippage 2.0

# Response:
# {
#   "step": "market_order_ready",
#   "mode": "market_order",
#   "instruction": "Execute via oneinch_swap(chain='arbitrum', src='0x...', dst='0x...', amount='...', slippage=2.0)"
# }

# Agent executes:
oneinch_swap(chain="arbitrum", src="0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE", dst="0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8", amount="5000000000000000", slippage=2.0)

# Auto-verify after execution:
python3 meta_dex.py execute --chain arbitrum --from ETH --to USDC --amount 0.005 \
  --market-order --wallet 0x... --auto-verify --expected-out <actual_received_wei>
```

### **Option B: Limit Order with Auto-Verification**

```bash
# Get quote and execute
python3 meta_dex.py execute --chain arbitrum --from ETH --to USDC --amount 0.005 \
  --aggregator kyberswap --wallet 0x... --slippage 1.0

# Execute tx via wallet_transfer...

# Auto-verify (no manual balance args needed):
python3 meta_dex.py execute --chain arbitrum --from ETH --to USDC --amount 0.005 \
  --aggregator kyberswap --wallet 0x... --verify --auto-verify --expected-out 10770000
```

**Option B: Manual swap (legacy)**

```bash
# Get swap tx data
python3 meta_dex.py swap --chain base --from ETH --to USDC --amount 0.5 \
  --aggregator odos --wallet 0x... --slippage 0.5

# Execute and verify manually (see Post-Swap Verification section)
```

## Post-Swap Verification (MANDATORY)

**v3.0.0: Use the `execute --verify` command for automatic verification.**

Manual verification workflow (if not using execute command):

```
# 1. Record balances BEFORE the swap
wallet_balance(chain="base", asset="eth")   → pre_from_balance
wallet_balance(chain="base", asset="usdc")  → pre_to_balance

# 2. Execute the swap (wallet_transfer or oneinch_swap)

# 3. For CowSwap: poll until fulfilled
# Use cowswap_poll_order(chain, order_uid) function
# Poll every 5s for up to 180s

# 4. Verify balances AFTER the swap
wallet_balance(chain="base", asset="eth")   → post_from_balance
wallet_balance(chain="base", asset="usdc")  → post_to_balance

# 5. Verify with CLI
python3 meta_dex.py execute --verify \
  --chain base --from ETH --to USDC --amount 0.5 --aggregator kyberswap \
  --wallet 0x... \
  --pre-from-balance <pre_eth> --pre-to-balance <pre_usdc> \
  --post-from-balance <post_eth> --post-to-balance <post_usdc> \
  --expected-out <expected_out_wei>

# Returns: {"verification": "PASSED"|"FAILED", "deviationPct": 0.5, ...}
```

**Rules:**
- **Never report success without checking post-swap balances** — tx confirmed ≠ expected outcome
- **Compare actual received vs quoted amount** — if deviation >2%, flag it to the user
- **For CowSwap orders:** Orders are filled asynchronously by solvers (can take up to 2 minutes).
  Use `cowswap_poll_order(chain, order_uid)` to poll until `status == "fulfilled"`.
- **For 1inch via oneinch_swap:** The tool returns a tx hash. Wait for confirmation, then check balances.
- **Include in confirmation:** tx hash, actual amounts spent/received, price achieved (received/spent)

## Cross-Chain Swaps

When src_chain ≠ dst_chain, use `xquote` to compare cross-chain routes:

```bash
python3 skills/meta-dex-aggregator/scripts/meta_dex.py xquote \
  --src-chain arbitrum --dst-chain polygon \
  --from ETH --to USDC --amount 0.5 \
  --wallet $WALLET --slippage 3
```

**Cross-chain sources:**
- **LI.FI** — aggregates 20+ bridges (Relay, Stargate, Across, Hop, etc.). Returns ready-to-sign tx data. Execute via `wallet_transfer(to, amount=value, data, chain_id, gas_limit)`. Track status with `curl -s "https://li.quest/v1/status?txHash={hash}&fromChain={src_id}&toChain={dst_id}"`.
- **1inch Fusion+** — intent-based atomic swaps (gasless, resolver handles both chains). The script returns a `needsToolCall: true` marker. Complete with `oneinch_cross_chain_quote` tool for the quote, then `oneinch_cross_chain_swap` for execution.

**Cross-chain workflow:**
1. Run `xquote` → get LI.FI routes + 1inch Fusion+ marker
2. Call `oneinch_cross_chain_quote` tool to fill in the 1inch quote
3. Compare all routes: output amount, total fees (gas + bridge + protocol), estimated time
4. Present table to user with clear winner
5. For execution: LI.FI routes → `wallet_transfer` with tx data; 1inch → `oneinch_cross_chain_swap`
6. Cross-chain is non-atomic — track status and confirm delivery on destination chain

**Safety notes for cross-chain:**
- Default slippage 3% (bridges need more than same-chain swaps)
- Always show estimated delivery time (4s to 10min depending on bridge)
- Always show fee breakdown (gas + bridge fees + protocol fees)
- After execution, track until funds arrive on destination chain
- LI.FI `DONE/PARTIAL` means bridge delivered but not the final token — may need a manual swap

## Historical Quote Logging (v3.0.0)

Every quote is automatically logged to `skills/meta-dex-aggregator/logs/{chain}_{FROM}_{TO}.jsonl`.

**What's logged:**
- Timestamp, chain, tokens, amount
- All aggregator quotes (amount, gas, netOut, vsBest)
- Winner aggregator
- Net output in USD

**Log retention:** Unlimited (append-only JSONL). Manually prune old logs if needed.

## Analytics Commands (v3.0.0)

### Winner Statistics
```bash
python3 meta_dex.py stats --chain arbitrum --from ETH --to USDC --days 7
```
Shows which aggregator wins most often, win rates, and average net output per aggregator.

### Price Trends
```bash
python3 meta_dex.py trend --chain arbitrum --from ETH --to USDC --days 7 --bucket-hours 4
```
Shows net output over time in 4-hour buckets (avg, min, max, count).

### Slippage Analysis
```bash
python3 meta_dex.py slippage --chain arbitrum --from ETH --to USDC --days 7
```
Analyzes competitive spreads between top 2 aggregators. Low spread = highly competitive.

### CSV Export
```bash
python3 meta_dex.py export --chain arbitrum --from ETH --to USDC --days 30 --output /tmp/quotes.csv
```
Exports all quotes to CSV for external analysis (Excel, Python, etc.).

## Quote Monitoring (v3.0.0)

Monitor for a target net output and alert when reached:

```bash
python3 meta_dex.py monitor --chain arbitrum --from ETH --to USDC --amount 1.0 \
  --target-net-out 2050 --interval 60 --max-runs 10
```

- Polls every 60 seconds
- Stops when net output ≥ $2050
- Max 10 polls (omit for unlimited)
- Returns immediately when target is met

**Use case:** "Alert me when ETH→USDC on Arbitrum nets >$2050 after gas"

Run this as a background task with `sessions_spawn` for non-blocking monitoring.

## Token Resolution — Smart Confirmation

Token resolution is tiered to avoid bothering the user for obvious tokens
while protecting against picking the wrong contract for ambiguous ones.

### Confidence levels returned by `resolve_token`:

| Confidence | Meaning | Action |
|-----------|---------|--------|
| `trusted` | Hardcoded canonical address (USDC, WETH, WBTC, etc.) | ✅ Auto-use, no confirmation |
| `exact` | User provided a 0x address directly | ✅ Auto-use, no confirmation |
| `single` | Only one token matches the symbol on this chain | ✅ Auto-use, no confirmation |
| `high` | Multiple matches but top has >10x volume of runner-up | ✅ Auto-use, no confirmation |
| `ambiguous` | Multiple plausible matches, none dominant | ⚠️ **MUST confirm with user** |

### When `confidence == "ambiguous"`:

The result includes a `candidates` list. Present them to the user:

```
I found multiple tokens matching "XYZ" on Arbitrum:

1. XYZ (XYZ Protocol) — 0x1234...5678 — $2.3M 24h vol
2. XYZ (XYZ Finance) — 0xabcd...ef01 — $180K 24h vol
3. XYZ (Old XYZ) — 0x9876...5432 — $12K 24h vol

Which one did you mean? (or paste the contract address directly)
```

Once the user picks, re-call with the address directly to bypass resolution.

### Trusted token coverage:

Ethereum, Arbitrum, Base, Optimism, Polygon, BSC, Avalanche, Gnosis —
all major tokens (WETH, USDC, USDT, DAI, WBTC, LINK, UNI, AAVE, stETH,
plus chain-specific tokens like ARB, OP, AERO, GMX, etc.)

## Chain Support

ethereum, bsc, polygon, optimism, arbitrum, avalanche, gnosis, fantom,
zksync, base, linea, scroll, sonic, unichain

## Safety Response Format

The `quote` command returns a `safety` block:
```json
{
  "recommendation": "✅ All checks passed. Best route looks safe.",
  "priceImpact": {"value": 0.02, "severity": "ok"},
  "slippageWarnings": [],
  "marketPrices": {"gas_token_price": 2170, "from_token_price": 2170, "to_token_price": 1.0}
}
```

Severity levels: `ok` | `warning` (3%) | `high` (5%) | `critical` (10%)

**CRITICAL: If severity is "high" or "critical", BLOCK the swap and warn the user explicitly.**
