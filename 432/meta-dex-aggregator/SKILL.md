---
name: "@432/meta-dex-aggregator"
description: "Meta DEX Aggregator - aggregator of aggregators. Compares quotes across ParaSwap, Odos, KyberSwap, CowSwap, Matcha/0x, and 1inch to find the best swap price. Includes safety layer: price impact detection, gas-adjusted ranking, MEV protection flagging, slippage warnings, outlier quote rejection, built-in execution with verification, CowSwap order polling, historical quote logging, winner analytics, market orders, auto-verify, and retry logic."
version: 5.0.1
tools:
  - bash
  - oneinch_quote
  - oneinch_tokens
  - oneinch_check_allowance
  - oneinch_approve
  - oneinch_swap
  - oneinch_cross_chain_quote
  - oneinch_cross_chain_swap
  - wallet_info
  - wallet_balance
  - wallet_transfer
  - wallet_sign_typed_data
  - wallet_propose_policy
  - sessions_spawn
---

# Meta DEX Aggregator - Multi-Source Quote Comparison with Safety Layer

Aggregator of aggregators. Queries 5 DEX aggregators in parallel (ParaSwap,
Odos, KyberSwap, Matcha/0x, CowSwap), plus 1inch via agent tool call.
Ranks by gas-adjusted net output with per-chain live gas prices, and runs
safety checks before execution.

## Getting Started (First-Time Users)

**Do these steps ONCE before your first swap:**

### Step 1: Get your wallet address
```
wallet_info()
# Returns: { wallet_address: "0x...", chain_type: "ethereum" }
# Save this - you'll need it as --wallet parameter for all commands
```

### Step 2: Check your balance
```
wallet_balance(chain="arbitrum")  # or whichever chain you're swapping on
# Confirm you have the source token AND enough ETH/native for gas
```

### Step 3: Set up wallet policy
The wallet needs permission to send transactions. Use `wallet_propose_policy`:
```
wallet_propose_policy(
  chain_type="ethereum",
  title="Allow DEX Swaps",
  description="Allow the meta-dex-aggregator to execute swaps and token approvals on EVM chains.",
  rules=[
    {"name": "Deny key export", "method": "exportPrivateKey", "conditions": [], "action": "DENY"},
    {"name": "Allow all operations", "method": "*", "conditions": [], "action": "ALLOW"}
  ]
)
```
**⚠️ Do NOT use `"method": "eth_sendTransaction"` with empty conditions - Privy rejects this with a 400 error. Always use `"method": "*"` for broad access.**

The user must approve this in the UI before any swaps will work.

### Step 4: You're ready
Now follow the Quote → Approve → Execute → Verify workflow below.

## Features

- **6 aggregators** compared in parallel (ParaSwap, Odos, KyberSwap, CowSwap, 1inch, Matcha/0x)
- **Market orders** via 1inch for instant execution (`--market-order`)
- **Auto-verify** post-swap balance checking (`--auto-verify`)
- **Retry logic** with fallback to next best aggregator on failure
- **CowSwap polling** for MEV-protected batch auction orders
- **Cross-chain swaps** via LI.FI and 1inch Fusion+
- **Historical logging** to JSONL for trend analysis
- **Analytics** - winner stats, price trends, slippage analysis, CSV export
- **Quote monitoring** with alerts when target price is reached

## Safety Features

1. **Price Impact** - Fetches fair market price from DefiLlama coins API
   (+ DexScreener fallback), compares vs quote output.
   Thresholds: 3% warning, 5% high, 10% critical (blocks swap).
2. **Gas-Adjusted Ranking** - `netOut = amountUsd - gasUsd`. Best route ≠ most tokens.
3. **MEV Protection Flags** - CowSwap and 0x Gasless are flagged `isMEVSafe`.
   Recommends MEV-safe route when within 0.5% of best price.
4. **Slippage Warnings** - Sandwich risk >1%, stablecoin pairs >0.05%, too-low revert risk.
5. **Outlier Detection** - Quotes >5% worse than best are flagged as outliers.
6. **Post-Swap Verification** - Mandatory balance checks, flags >2% deviation.

## Aggregators

| Adapter | API Key | Status | Notes |
|---------|---------|--------|-------|
| ParaSwap | None needed | ✅ | |
| Odos | None needed | ✅ | |
| KyberSwap | None needed | ✅ | |
| CowSwap | None needed | ⚠️ Rate limited | Batch auction - MEV protected, may skip when rate limited |
| 1inch | Native tool (platform-proxied) | ✅ | Call `oneinch_quote()` separately, merge manually |
| Matcha/0x | `OX_API_KEY` in .env | ✅ | |

**MEV Protection:** CowSwap uses off-chain batch auctions (solvers compete, no mempool exposure). The safety layer flags it when available. All aggregators are safe - CowSwap just has extra protection.

**Note:** CowSwap's public API is rate limited. The script gracefully skips it when rate limited (429). 1inch requires an API key, so the agent calls the platform's `oneinch_quote` tool (proxied, no user key needed) and merges the result into the comparison table.

**CowSwap specifics:** Gasless for the user (solvers pay gas). Supported on Ethereum, Arbitrum, Gnosis, Base.
Uses wrapped native tokens (WETH) internally - raw ETH is auto-converted.
Execution is order-based (EIP-712 signed intent), not raw transaction.

## Wallet Policy

See **Getting Started → Step 3** above. Policy must be approved by the user before any swap can execute.

## Workflow: Quote with Safety Check

**Step 1 & 2 run in PARALLEL (no dependency between them):**

```bash
# 1. Get 4 aggregator quotes (ParaSwap, Odos, KyberSwap, Matcha/0x + safety)
cd skills/meta-dex-aggregator/scripts && \
  python3 meta_dex.py quote --chain base --from ETH --to USDC --amount 0.5 --slippage 0.5
```

```
# 2. Get 1inch quote via native tool (proxied, no API key needed)
oneinch_quote(chain="base", src="<from_addr>", dst="<to_addr>", amount="<amount_in_wei>")
# Returns: { "dstAmount": "<raw_amount>" }
# Convert: dstAmount / 10^decimals = human amount
```

**Step 3 - Merge & present:**
- Script returns quotes with: `aggregator`, `amountOutHuman`, `amountUsd`, `gasUsd`, `netOut`, `vsbestPct`
- 1inch native tool returns `dstAmount` (raw wei) - convert to human amount using token decimals
- Insert 1inch into the ranked table, recalculate `vsbestPct` if 1inch is the new winner
- The script's `safety` block (priceImpact, slippageWarnings, recommendation) applies to all quotes
- If `priceImpact.severity` is "high"/"critical" - WARN and **block the swap**
- Execute via `oneinch_swap` if 1inch wins, or `wallet_transfer` with tx data for others (see Execution section below for exact param mapping)

## Pre-Swap: Token Approval (REQUIRED for ERC-20 source tokens)

**Before executing ANY swap where the source token is an ERC-20 (not native ETH), you MUST check and approve the token allowance.**

Native ETH (`0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE`) does NOT need approval. All other tokens do.

```
# Step 1: Check if the 1inch router has allowance to spend your source token
oneinch_check_allowance(chain="arbitrum", token_address="0xaf88d065e77c8cC2239327C5EDb3A432268e5831")
# Returns: { "allowance": "0", "needs_approval": true }

# Step 2: If needs_approval is true, approve the token
oneinch_approve(chain="arbitrum", token_address="0xaf88d065e77c8cC2239327C5EDb3A432268e5831")
# Returns: { "tx_hash": "0x..." }

# Step 3: Now proceed with the swap
```

**When to check:**
- Swapping USDC → ETH? Check USDC allowance first.
- Swapping ETH → USDC? No approval needed (ETH is native).
- Swapping USDC → WBTC? Check USDC allowance first.
- **Any ERC-20 as source = check allowance → approve if needed → then swap.**

**For non-1inch aggregators (ParaSwap, Odos, KyberSwap, etc.):** Some aggregators handle approval internally in the tx calldata. However, if the swap tx reverts, check allowance for the aggregator's router address (returned as `tokenApprovalAddress` in the quote). Only 1inch market orders via `oneinch_swap` use the explicit `oneinch_check_allowance` / `oneinch_approve` flow above.

## Workflow: Execute Swap

- `--market-order` flag for instant 1inch execution (no limit order failures)
- `--auto-verify` flag for automatic balance fetching (no manual args)
- Retry logic with fallback to next best aggregator on failure

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

### Executing via wallet_transfer (ParaSwap, Odos, KyberSwap, Matcha/0x)

The `execute` command returns a `tx` object. Map it to `wallet_transfer` like this:

```
# Script returns:
# { "tx": { "to": "0xRouterAddr", "data": "0xCalldata...", "value": "500000000000000", "gas": "300000" }, "chainId": 42161 }

# Agent calls:
wallet_transfer(
  to="0xRouterAddr",           # tx.to
  amount="500000000000000",    # tx.value (in wei - "0" if selling ERC-20, not native)
  data="0xCalldata...",        # tx.data (the swap calldata)
  chain_id=42161,              # chainId from the result
  gas_limit="300000"           # tx.gas (optional but recommended)
)
```

**Chain ID reference:** ethereum=1, arbitrum=42161, base=8453, optimism=10, polygon=137, bsc=56, avalanche=43114, gnosis=100

### Executing CowSwap orders (EIP-712 signing)

CowSwap is order-based, not transaction-based. When the execute command returns `orderType: "cowswap_order"`:

1. The result contains `eip712Data` with the order to sign
2. Sign it with `wallet_sign_typed_data(domain=..., types=..., primaryType=..., message=...)`
3. Submit the signed order to CowSwap API via bash `curl`
4. Poll with the built-in `cowswap_poll_order` function or check the `pollEndpoint` URL
5. CowSwap orders are filled by solvers asynchronously (up to 2 minutes)

**If CowSwap seems complex, prefer `--market-order` for simplicity - it uses 1inch and executes instantly.**

## Post-Swap Verification (MANDATORY)

**Use the `execute --verify` command for automatic verification.**

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
- **Never report success without checking post-swap balances** - tx confirmed ≠ expected outcome
- **Compare actual received vs quoted amount** - if deviation >2%, flag it to the user
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
- **LI.FI** - aggregates 20+ bridges (Relay, Stargate, Across, Hop, etc.). Returns ready-to-sign tx data. Execute via `wallet_transfer(to, amount=value, data, chain_id, gas_limit)`. Track status with `curl -s "https://li.quest/v1/status?txHash={hash}&fromChain={src_id}&toChain={dst_id}"`.
- **1inch Fusion+** - intent-based atomic swaps (gasless, resolver handles both chains). The script returns a `needsToolCall: true` marker. Complete with `oneinch_cross_chain_quote` tool for the quote, then `oneinch_cross_chain_swap` for execution.

**Cross-chain workflow:**
1. Run `xquote` → get LI.FI routes + 1inch Fusion+ marker
2. Call `oneinch_cross_chain_quote` tool to fill in the 1inch quote
3. Compare all routes: output amount, total fees (gas + bridge + protocol), estimated time
4. Present table to user with clear winner
5. For execution: LI.FI routes → `wallet_transfer` with tx data; 1inch → `oneinch_cross_chain_swap`
6. Cross-chain is non-atomic - track status and confirm delivery on destination chain

**Safety notes for cross-chain:**
- Default slippage 3% (bridges need more than same-chain swaps)
- Always show estimated delivery time (4s to 10min depending on bridge)
- Always show fee breakdown (gas + bridge fees + protocol fees)
- After execution, track until funds arrive on destination chain
- LI.FI `DONE/PARTIAL` means bridge delivered but not the final token - may need a manual swap

## Historical Quote Logging

Every quote is automatically logged to `skills/meta-dex-aggregator/logs/{chain}_{FROM}_{TO}.jsonl`.

**What's logged:**
- Timestamp, chain, tokens, amount
- All aggregator quotes (amount, gas, netOut, vsBest)
- Winner aggregator
- Net output in USD

**Log retention:** Unlimited (append-only JSONL). Manually prune old logs if needed.

## Analytics Commands

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

## Quote Monitoring

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

## Token Resolution - Smart Confirmation

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

1. XYZ (XYZ Protocol) - 0x1234...5678 - $2.3M 24h vol
2. XYZ (XYZ Finance) - 0xabcd...ef01 - $180K 24h vol
3. XYZ (Old XYZ) - 0x9876...5432 - $12K 24h vol

Which one did you mean? (or paste the contract address directly)
```

Once the user picks, re-call with the address directly to bypass resolution.

### Trusted token coverage:

Ethereum, Arbitrum, Base, Optimism, Polygon, BSC, Avalanche, Gnosis -
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
