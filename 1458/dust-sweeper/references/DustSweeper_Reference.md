# DustSweeper — Complete Reference for Starchild

> **Status: Deprecated (~2025).** Superseded by EIP-7702 (Pectra upgrade), which enables native batching in EOA wallets.
> Archived for reference and as the basis for a modern Starchild dust-sweeping agent capability.

---

## 1. What It Is

DustSweeper is a maker-taker DEX for ERC-20 "dust" — small token balances not worth swapping individually due to gas costs. Won top hackathon prize at ETHDenver 2022. Built by Paymagic Labs (corbpage).

**Core insight:** Gas cost is the blocker for small swaps. The protocol solves this by separating who *approves* from who *pays gas for the swap*.

- **Users (makers):** Pay ~$8 for `approve()` only. Never pay swap gas.
- **Bots (takers):** Scan for approved dust, batch-execute `sweepDust()`, pay all swap gas. Profit from buying dust at a discount to market price.

---

## 2. Contract

**Address:** `0x78106f7db3EbCEe3D2CFAC647f0E4c9b06683B39` (Ethereum Mainnet)
**License:** UNLICENSED
**Compiler:** Solidity ^0.8.13
**Verified:** Yes — Etherscan

### Dependencies
- `@rari-capital/solmate/src/utils/SafeTransferLib.sol`
- `@rari-capital/solmate/src/utils/ReentrancyGuard.sol`
- `@openzeppelin/contracts/access/Ownable.sol`
- `./Trustus.sol` — custom off-chain price oracle (signed attestations)

### Key Data Structures

```solidity
struct Token {
    bool tokenSetup;
    uint8 decimals;
    uint8 takerDiscountTier;   // discount bot gets when buying dust
}

struct CurrentToken {
    address tokenAddress;
    uint8 decimals;
    uint256 price;             // price from Trustus oracle
}

struct TokenPrice {
    address addr;
    uint256 price;
}

struct Native {
    uint256 balance;           // ETH to pay out to maker
    uint256 total;
    uint256 protocol;          // protocol fee split
}

struct Order {
    uint256 nativeAmount;      // ETH maker receives
    uint256 tokenAmount;       // dust tokens transferred out
    uint256 distribution;      // fee distribution
}
```

### Key Events
```solidity
event Sweep(
    address indexed makerAddress,
    address indexed tokenAddress,
    uint256 tokenAmount,
    uint256 ethAmount
);
event ProtocolPayout(uint256 protocolSplit, uint256 governorSplit);
```

### Key Errors
```solidity
error ZeroAddress();
error NoBalance();
error NotContract();
error NoTokenPrice(address tokenAddress);
error NoSweepableOrders();
error InsufficientNative(uint256 sendAmount, uint256 remainingBalance);
error OutOfRange(uint256 param);
```

### Core Function: sweepDust()

Called by taker bots. Bot provides:
1. Array of maker addresses + token addresses
2. Signed price attestation from Trustus oracle
3. ETH (msg.value) to pay makers

The contract:
- Verifies the oracle signature (Trustus)
- Checks each maker's token balance + approval
- Transfers tokens from maker → bot
- Sends ETH from bot → maker
- Takes protocol fee cut

### Admin Functions (Owner)
- `toggleSweepWhitelist()` — enable/disable bot whitelist
- `toggleSweepWhitelistAddress(address)` — add/remove bot from whitelist
- `toggleIsTrusted(address)` — manage Trustus oracle signers
- `withdrawToken(address)` — recover stuck tokens

---

## 3. The Trustus Oracle

Off-chain price attestation system. A trusted server:
1. Fetches token prices from DEX aggregators / CoinGecko
2. Signs price data with a private key
3. Bots include the signed payload in `sweepDust()` calls
4. Contract verifies signature on-chain before accepting prices

**For Starchild:** This role is naturally replaced by the agent itself querying live prices via CoinGecko/1inch and constructing the swap logic directly.

---

## 4. Taker Discount Tiers

Bots buy dust at a discount from market price. Tiers likely range ~5–20% depending on token liquidity/risk. This discount:
- Compensates bots for gas costs
- Scales to make unprofitable batches uneconomical (self-regulating)
- Creates the "dust is worth something, just not face value" market

---

## 5. Version History

| Version | Tokens Supported | Key Changes |
|---------|-----------------|-------------|
| v1 (ETHDenver 2022) | ~80 | Initial concept, fixed token list |
| v2 (2023) | 5,000+ | `Trustus` oracle for dynamic pricing, gas optimizations, major token expansion |

---

## 6. Why It Was Deprecated

**EIP-7702 (Ethereum Pectra upgrade, 2025):** Allows EOAs (externally owned accounts) to temporarily set code, enabling wallets to:
- Batch `approve + swap` into a single atomic transaction
- Pay gas once for many operations
- Do natively what DustSweeper did via a protocol middleman

The core UX problem (gas-too-expensive-for-dust) is now solvable at the wallet layer.

---

## 7. Links

| Resource | URL |
|----------|-----|
| Site (deprecated) | https://dustsweeper.xyz |
| PRD (Mirror) | https://launch.mirror.xyz/EwldfOSzRyv2uwOg8hCctXdvfps4LygGZnIR2j_mrJk |
| V2 Announcement | https://launch.mirror.xyz/nZL8_LUPRmvKGJJnD3KSXyZtP-iDkkG5ie9_Dl5yvPo |
| Dune Dashboard | https://dune.com/corbpage/DustSweeper-Dashboard |
| Contract (Etherscan) | https://etherscan.io/address/0x78106f7db3ebcee3d2cfac647f0e4c9b06683b39#code |
| DoraHacks | https://dorahacks.io/buidl/2101 |
| Builder | Paymagic Labs (corbpage) |

---

## 8. Starchild Agent Capability Design

### Concept: "Sweep My Dust"

A native Starchild capability that:
1. Scans a user's wallet for dust tokens (small USD-value ERC-20 balances)
2. Gets live quotes for each token via 1inch
3. Filters to profitable swaps (value > gas cost)
4. Executes swaps (either directly or via 1inch aggregator)
5. Reports what was swept and total ETH recovered

### Two Implementation Approaches

#### A. Post-EIP-7702 (Modern — Recommended)

```
User: "Sweep my dust"
Agent:
  1. wallet_balance(chain="ethereum")  → discover all ERC-20 tokens
  2. For each token with balance < $50:
     a. coin_price() / birdeye_token_overview() → get market price
     b. oneinch_quote() → get actual swap quote + gas estimate
     c. Filter: keep only swaps where output > gas cost + min threshold
  3. For profitable tokens:
     a. oneinch_approve() → approve 1inch router
     b. oneinch_swap() → execute swap to ETH/USDC
  4. Report: "Swept 12 tokens, recovered $47.23 ETH"
```

#### B. DustSweeper Protocol-Compatible (Legacy, educational)

Interact with the existing contract (still deployed, bots may no longer be active):
- `approve()` tokens to `0x78106f7db3EbCEe3D2CFAC647f0E4c9b06683B39`
- Monitor for `Sweep` events to confirm bot execution

### Key Thresholds (configurable)
- **Dust threshold:** Token balance < $50 USD (configurable)
- **Min sweep value:** Must recover > $2 after gas (otherwise skip)
- **Gas price gate:** Pause sweeping if gas > 20 gwei (configurable)
- **Slippage:** Default 2% for dust tokens (often low liquidity)

### What Makes This a Good Agent Task
- Requires no real-time user interaction (fire and forget)
- Benefits from batching (check all tokens in one pass)
- Agent can price-check, gas-check, and execute atomically
- Natural fit for scheduling: "sweep my dust every Sunday"

---

## 9. Starchild Skill Plan

**Skill name:** `dust-sweeper`
**Tools needed:**
- `wallet_balance` — discover ERC-20 holdings
- `birdeye_token_overview` — get USD value of tokens
- `oneinch_quote` — get swap quotes with gas estimates
- `oneinch_approve` + `oneinch_swap` — execute swaps
- `coin_price` — fallback pricing for mainstream tokens

**Trigger phrases:**
- "Sweep my dust"
- "Clean up my wallet"
- "What dust do I have?"
- "Sell my small token balances"

**Skill file path:** `skills/dust-sweeper/SKILL.md`
