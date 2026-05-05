---
name: "@1390/woofi-yield"
version: 1.0.0
description: "Comprehensive yield protocol reference covering Aave V3/V4, Spark (Savings + SparkLend), and Morpho V2 vaults — deposit/withdraw flows, contract interfaces, pool registries, and GraphQL APIs across 10+ chains. Essential for WOOFi ecosystem DeFi yield strategies."
author: woonetwork
tags: [yield, defi, aave, spark, morpho, lending, vaults, erc-4626, woofi]
---

# Woofi Yield Skill — Aave, Spark & Morpho Deposit / Withdraw

## Aave

### Aave V3

## 1. Overview

Aave V3 is the largest decentralized lending protocol. Users supply an underlying asset (e.g. USDC) and receive an **aToken** in return. aTokens are minted 1:1 with the supplied asset; their balance grows automatically over time to reflect accrued interest.

Key points:
- V3 uses `supply()` (renamed from V2's `deposit()`)
- aToken balances rebase — no need to claim rewards separately
- `supplyWithPermit()` is available for gasless approvals on EIP-2612 tokens

**Supported chains:**

| Chain      | chainId |
|------------|---------|
| Ethereum   | 1       |
| Arbitrum   | 42161   |
| Optimism   | 10      |
| Polygon    | 137     |
| Avalanche  | 43114   |
| Base       | 8453    |
| BNB Chain  | 56      |
| Gnosis     | 100     |
| Scroll     | 534352  |
| Linea      | 59144   |
| Sonic      | 146     |

#### 2. Pool & Token Registry

##### Pool Addresses

| Chain      | chainId | Pool Address                                 |
|------------|---------|----------------------------------------------|
| Ethereum   | 1       | `0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2` |
| Arbitrum   | 42161   | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` |
| Optimism   | 10      | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` |
| Polygon    | 137     | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` |
| Avalanche  | 43114   | `0x794a61358D6845594F94dc1DB02A252b5b4814aD` |
| Base       | 8453    | `0xA238Dd80C259a72e81d7e4664a9801593F98d1c5` |
| BNB Chain  | 56      | `0x6807dc923806fE8Fd134338EABCA509979a7e0cB` |
| Gnosis     | 100     | `0xb50201558B00496A145fE76f7424749556E326D8` |
| Scroll     | 534352  | `0x11fCfe756c05AD438e312a7fd934381537D3cFfe` |
| Linea      | 59144   | `0xc47b8C00b0f69a36fa203Ffeac0334874574a8Ac` |

##### USDC Reserves

| Chain      | Underlying                                   | aToken                                       |
|------------|----------------------------------------------|----------------------------------------------|
| Ethereum   | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | `0x98C23E9d8f34FEFb1B7BD6a91B7FF122F4e16F5c` |
| Arbitrum   | `0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8` | `0x625E7708f30cA75bfd92586e17077590C60eb4cD` |
| Optimism   | `0x7F5c764cBc14f9669B88837ca1490cCa17c31607` | `0x625E7708f30cA75bfd92586e17077590C60eb4cD` |
| Polygon    | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | `0x625E7708f30cA75bfd92586e17077590C60eb4cD` |
| Avalanche  | `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E` | `0x625E7708f30cA75bfd92586e17077590C60eb4cD` |
| Base       | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | `0x4e65fE4DbA92790696d040ac24Aa414708F5c0AB` |
| BNB Chain  | `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d` | `0x00901a076785e0906d1028c7d6372d247bec7d61` |
| Gnosis     | `0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83` | `0xc6B7AcA6DE8a6044E0e32d0c841a89244A10D284` |
| Scroll     | `0x06eFdBFf2a14a7c8E15944D1F4A48F9F95F663A4` | `0x1D738a3436A8C49CefFbaB7fbF04B660fb528CbD` |
| Linea      | `0x176211869cA2b568f2A7D4EE941E073a821EE1ff` | `0x374D7860c4f2f604De0191298dD393703Cce84f3` |
| Sonic      | `0x29219dd400f2Bf60E5a23d13Be72B486D4038894` | `0x578Ee1ca3a8E1b54554Da1Bf7C583506C4CD11c6` |

##### USDT Reserves

Sonic, Scroll, and Gnosis do not have USDT reserves on Aave V3.

| Chain      | Underlying                                   | aToken                                       |
|------------|----------------------------------------------|----------------------------------------------|
| Ethereum   | `0xdAC17F958D2ee523a2206206994597C13D831ec7` | `0x23878914EFE38d27C4D67Ab83ed1b93A74D4086a` |
| Arbitrum   | `0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9` | `0x6ab707Aca953eDAeFBc4fD23bA73294241490620` |
| Optimism   | `0x94b008aA00579c1307B0EF2c499aD98a8ce58e58` | `0x6ab707Aca953eDAeFBc4fD23bA73294241490620` |
| Polygon    | `0xc2132D05D31c914a87C6611C10748AEb04B58e8F` | `0x6ab707Aca953eDAeFBc4fD23bA73294241490620` |
| Avalanche  | `0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7` | `0x6ab707Aca953eDAeFBc4fD23bA73294241490620` |
| BNB Chain  | `0x55d398326f99059fF775485246999027B3197955` | `0xa9251ca9DE909CB71783723713B21E4233fbf1B1` |
| Linea      | `0xA219439258ca9da29E9Cc4cE5596924745e12B93` | `0x88231dfEC71D4FF5c1e466D08C321944A7adC673` |

##### WETH Reserves

| Chain      | Underlying                                   | aToken                                       | Note      |
|------------|----------------------------------------------|----------------------------------------------|-----------|
| Ethereum   | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` | `0x4d5F47FA6A74757f35C14fD3a6Ef8E3C9BC514E8` |           |
| Arbitrum   | `0x82aF49447D8a07e3bd95BD0d56f35241523fBab1` | `0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8` |           |
| Optimism   | `0x4200000000000000000000000000000000000006` | `0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8` |           |
| Polygon    | `0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619` | `0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8` |           |
| Avalanche  | `0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB` | `0xe50fA9b3c56FfB159cB0FCA61F5c9D750e8128c8` | WETH.e    |
| Base       | `0x4200000000000000000000000000000000000006` | `0xD4a0e0b9149BCee3C920d2E00b5dE09138fd8bb7` |           |
| BNB Chain  | `0x2170Ed0880ac9A755fd29B2688956BD959F933F8` | `0x2E94171493fAbE316b6205f1585779C887771E2F` | ETH       |
| Gnosis     | `0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1` | `0xa818F1B57c201E092C4A2017A91815034326Efd1` |           |
| Scroll     | `0x5300000000000000000000000000000000000004` | `0xf301805bE1Df81102C957f6d4Ce29d2B8c056B2a` |           |
| Linea      | `0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34f` | `0x787897dF92703BB3Fc4d9Ee98e15C0b8130Bf163` |           |
| Sonic      | `0x50c42dEAcD8Fc9773493ED674b675bE577f2634b` | `0xe18Ab82c81E7Eecff32B8A82B1b7d2d23F1EcE96` |           |

##### WBTC / BTC Reserves

Sonic, Scroll, and Gnosis do not have WBTC reserves on Aave V3.

| Chain      | Underlying                                   | aToken                                       | Note      |
|------------|----------------------------------------------|----------------------------------------------|-----------|
| Ethereum   | `0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599` | `0x5Ee5bf7ae06D1Be5997A1A72006FE6C607eC6DE8` | WBTC      |
| Arbitrum   | `0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f` | `0x078f358208685046a11C85e8ad32895DED33A249` | WBTC      |
| Optimism   | `0x68f180fcCe6836688e9084f035309E29Bf0A2095` | `0x078f358208685046a11C85e8ad32895DED33A249` | WBTC      |
| Polygon    | `0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6` | `0x078f358208685046a11C85e8ad32895DED33A249` | WBTC      |
| Avalanche  | `0x50b7545627a5162F82A992c33b87aDc75187B218` | `0x078f358208685046a11C85e8ad32895DED33A249` | WBTC.e    |
| Base       | `0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf` | `0xBdb9300b7CDE636d9cD4AFF00f6F009fFBBc8EE6` | cbBTC     |
| BNB Chain  | `0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c` | `0x56a7ddc4e848EbF43845854205ad71D5D5F72d3D` | BTCB      |
| Linea      | `0x3aAB2285ddcDdaD8edf438C1bAB47e1a9D05a9b4` | `0x37f7E06359F98162615e016d0008023D910bB576` | WBTC      |

#### 3. Pool Contract Interface

##### Write Functions

```solidity
// Supply `amount` of `asset` to the pool on behalf of `onBehalfOf`
// referralCode is deprecated — pass 0
function supply(
    address asset,
    uint256 amount,
    address onBehalfOf,
    uint16 referralCode
) external;

// Withdraw `amount` of `asset` from the pool, sending to `to`
// Pass type(uint256).max to withdraw the entire balance
function withdraw(
    address asset,
    uint256 amount,
    address to
) external returns (uint256);

// Supply with EIP-2612 permit (gasless approval)
function supplyWithPermit(
    address asset,
    uint256 amount,
    address onBehalfOf,
    uint16 referralCode,
    uint256 deadline,
    uint8 permitV,
    bytes32 permitR,
    bytes32 permitS
) external;
```

##### ERC-20 Approve (prerequisite for supply)

```solidity
// Approve the Pool to spend underlying tokens on behalf of msg.sender
IERC20(underlying).approve(poolAddress, amount);
```

#### 4. Operation Flows

##### Deposit Flow

```
1. Resolve the Pool address and underlying token address for the target chain/asset.

2. Check user balance:
   balance_raw = IERC20(underlying).balanceOf(user)

3. Approve Pool to spend underlying:
   IERC20(underlying).approve(pool_address, amount_raw)

4. Execute supply:
   pool.supply(underlying, amount_raw, user, 0)
   → User receives aTokens automatically (1:1 with supplied amount)
```

##### Withdraw Flow

```
1. Resolve the Pool address and underlying token address.

2. Check aToken balance (= withdrawable amount):
   aBalance_raw = IERC20(aToken).balanceOf(user)

3. Execute withdraw:
   pool.withdraw(underlying, amount_raw, user)
   → aTokens are burned, underlying tokens sent to `user`

   For full withdrawal, pass type(uint256).max as amount:
   pool.withdraw(underlying, type(uint256).max, user)
```

##### Native ETH Handling

Aave V3 does not accept native ETH directly. To supply/withdraw native ETH, use the **WrappedTokenGatewayV3** contract:

```solidity
// Deposit native ETH (wraps to WETH internally)
function depositETH(address pool, address onBehalfOf, uint16 referralCode) external payable;

// Withdraw to native ETH (unwraps WETH internally)
// User must approve aWETH to the gateway first
function withdrawETH(address pool, uint256 amount, address to) external;
```

#### 5. Aave V3 GraphQL API

**Endpoint:** `https://api.v3.aave.com/graphql`

##### Query Reserve APY

```graphql
query {
  reserves {
    chain { name chainId }
    asset { underlying { symbol address } }
    summary { supplyApy { normalized } borrowApy { normalized } }
    canBorrow
    canSupply
  }
}
```

The `supplyApy.normalized` field returns the annualized supply rate as a decimal (e.g. `0.035` = 3.5% APY).

### Aave V4

## 1. Overview

Aave V4 launched on **Ethereum mainnet on 2026-03-30**. It introduces a **Hub-and-Spoke** architecture: users interact with Spoke contracts, and funds flow to a shared Liquidity Hub. This replaces V3's per-chain isolated Pool model.

Key points:
- Users call `supply()` / `withdraw()` on a **Spoke** contract (not a Pool)
- Reserves are identified by `reserveId` (uint256) instead of asset address
- No `referralCode` parameter
- Three Hubs: **Core**, **Prime**, **Plus** — each Spoke is connected to one Hub
- Currently **Ethereum only**

**Supported chains:**

| Chain    | chainId |
|----------|---------|
| Ethereum | 1       |

#### 2. Hub & Spoke Registry

##### Hub Addresses (Ethereum)

| Hub   | Address                                      |
|-------|----------------------------------------------|
| Core  | `0xCca852Bc40e560adC3b1Cc58CA5b55638ce826c9` |
| Plus  | `0x06002e9c4412CB7814a791eA3666D905871E536A` |
| Prime | `0x943827DCA022D0F354a8a8c332dA1e5Eb9f9F931` |

##### Spoke Addresses (Ethereum)

| Spoke              | Address                                      |
|--------------------|----------------------------------------------|
| Main               | `0x94e7A5dCbE816e498b89aB752661904E2F56c485` |
| Bluechip           | `0x973a023A77420ba610f06b3858aD991Df6d85A08` |
| Lido E             | `0xe1900480ac69f0B296841Cd01cC37546d92F35Cd` |
| EtherFi E          | `0xbF10BDfE177dE0336aFD7fcCF80A904E15386219` |
| Kelp E             | `0x3131FE68C4722e726fe6B2819ED68e514395B9a4` |
| Ethena Correlated  | `0x58131E79531caB1d52301228d1f7b842F26B9649` |
| Ethena Ecosystem   | `0xba1B3D55D249692b669A164024A838309B7508AF` |
| Lombard BTC        | `0x7EC68b5695e803e98a21a9A05d744F28b0a7753D` |
| Forex              | `0xD8B93635b8C6d0fF98CbE90b5988E3F2d1Cd9da1` |
| Gold               | `0x65407b940966954b23dfA3caA5C0702bB42984DC` |

##### Peripheral Contracts (Ethereum)

| Contract             | Address                                      |
|----------------------|----------------------------------------------|
| Native Token Gateway | `0xe68ab4F90Fe026B9873F5F276eD2d7efBbbE42Be` |
| Signature Gateway    | `0xfbC184337Dc6595D8bf62968Bda46e7De7AF9c3d` |

##### Token Addresses (Ethereum)

| Token | Address                                      |
|-------|----------------------------------------------|
| USDC  | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| USDT  | `0xdAC17F958D2ee523a2206206994597C13D831ec7` |
| WETH  | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` |
| WBTC  | `0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599` |

#### 3. Spoke Contract Interface

##### Write Functions

```solidity
// Supply `amount` of the reserve identified by `reserveId` on behalf of `onBehalfOf`
// Returns (suppliedAmount, mintedShares)
function supply(
    uint256 reserveId,
    uint256 amount,
    address onBehalfOf
) external returns (uint256, uint256);

// Withdraw `amount` of the reserve identified by `reserveId` on behalf of `onBehalfOf`
// Returns (withdrawnAmount, burnedShares)
function withdraw(
    uint256 reserveId,
    uint256 amount,
    address onBehalfOf
) external returns (uint256, uint256);
```

##### ERC-20 Approve (prerequisite for supply)

```solidity
// Approve the Spoke contract to spend underlying tokens on behalf of msg.sender
IERC20(underlying).approve(spokeAddress, amount);
```

#### 4. Operation Flows

##### Deposit Flow

```
1. Identify the target Spoke address and look up the reserveId for the asset (see Section 5).

2. Check user balance:
   balance_raw = IERC20(underlying).balanceOf(user)

3. Approve Spoke to spend underlying:
   IERC20(underlying).approve(spoke_address, amount_raw)

4. Execute supply:
   (suppliedAmount, mintedShares) = spoke.supply(reserveId, amount_raw, user)
```

##### Withdraw Flow

```
1. Identify the target Spoke address and look up the reserveId for the asset (see Section 5).

2. Execute withdraw:
   (withdrawnAmount, burnedShares) = spoke.withdraw(reserveId, amount_raw, user)
   → Underlying tokens are sent to `user`
```

##### Native ETH Handling

Aave V4 provides a **Native Token Gateway** for supplying/withdrawing native ETH without manual wrapping:

```
Gateway address: 0xe68ab4F90Fe026B9873F5F276eD2d7efBbbE42Be
```

#### 5. Reserve ID Lookup

Aave V4 identifies reserves by `reserveId` (uint256), not by asset address. To obtain the `reserveId` for a given asset, perform a **two-step on-chain lookup**:

##### Function Signatures

```solidity
// Step 1 — on the Hub contract
// Returns the Hub-internal asset ID for the given underlying token address
function getAssetId(address underlying) external view returns (uint256);

// Step 2 — on the Spoke contract
// Maps (hub, assetId) → reserveId used in supply()/withdraw()
function getReserveId(address hub, uint256 assetId) external view returns (uint256);
```

##### Lookup Example

```
hub_address   = <Hub address from Section 2>       // e.g. Core Hub
spoke_address = <Spoke address from Section 2>     // e.g. Main Spoke

// Step 1: get the Hub-internal asset ID
assetId   = hub.getAssetId(USDC_ADDRESS)

// Step 2: convert to Spoke-specific reserveId
reserveId = spoke.getReserveId(hub_address, assetId)

// Now use reserveId in supply()/withdraw()
spoke.supply(reserveId, amount, user)
```

**Note:** `reserveId` values are **per-Spoke** — the same underlying asset can have different `reserveId` values across different Spokes. Always look up the `reserveId` for the specific Spoke you intend to interact with.

##### Additional View Functions on Spoke

| Function | Returns | Description |
|----------|---------|-------------|
| `getReserve(uint256 reserveId)` | `Reserve` struct | Full reserve details: underlying address, hub, assetId, decimals, collateralRisk, flags |
| `getReserveCount()` | `uint256` | Total number of reserves in the Spoke |
| `getReserveConfig(uint256 reserveId)` | `ReserveConfig` | Collateral risk parameters, paused/frozen status |

#### 6. Aave V4 GraphQL API

**Endpoint:** `https://api.v4.aave.com/graphql`

##### Query Reserve APY

```graphql
query {
  reserves {
    chain { name chainId }
    asset { underlying { symbol address } }
    summary { supplyApy { normalized } borrowApy { normalized } }
    canBorrow
    canSupply
  }
}
```

The `supplyApy.normalized` field returns the annualized supply rate as a decimal (e.g. `0.035` = 3.5% APY).

#### 7. Key Differences from V3

| Aspect              | Aave V3                              | Aave V4                                 |
|---------------------|--------------------------------------|-----------------------------------------|
| Architecture        | Isolated Pool per chain              | Hub-and-Spoke, shared Liquidity Hub     |
| Entry point         | `Pool.supply(asset, ...)`            | `Spoke.supply(reserveId, ...)`          |
| Reserve identifier  | `address asset`                      | `uint256 reserveId`                     |
| Referral code       | `uint16 referralCode` (pass 0)       | Removed                                 |
| Return values       | None (supply) / uint256 (withdraw)   | (uint256, uint256) tuple for both       |
| Chains              | 10+ chains                           | Ethereum only (as of 2026-04)           |
| Liquidity sharing   | None — isolated per deployment       | Cross-Spoke via shared Hub              |
| Native ETH gateway  | WrappedTokenGatewayV3                | Native Token Gateway                    |

## Spark

## 1. Overview

Spark is a DeFi platform within the Sky (formerly MakerDAO) ecosystem, comprising two product lines:

- **Spark Savings** — ERC-4626 vaults (spUSDC, spUSDT, spETH, etc.) that optimize yield via the Spark Liquidity Layer
- **SparkLend (Markets)** — Aave V3 fork lending pool; supply assets to receive spTokens

Savings products span 6 chains; SparkLend is deployed only on Ethereum and Gnosis.

**Supported chains:**

| Chain     | chainId | Savings | SparkLend |
|-----------|---------|---------|-----------|
| Ethereum  | 1       | Yes     | Yes       |
| Base      | 8453    | Yes     | No        |
| Arbitrum  | 42161   | Yes     | No        |
| Optimism  | 10      | Yes     | No        |
| Unichain  | 130     | Yes     | No        |
| Gnosis    | 100     | Yes     | Yes       |

---

## 2. Spark Savings — Vault Registry

**Product categories:**

- **V2 Vaults** (spUSDC, spUSDT, spETH) — Spark-native ERC-4626 vaults deploying strategies via the Liquidity Layer
- **Legacy** (sUSDS, sDAI) — Sky protocol Savings Rate wrappers (not listed here)

Only USDC / USDT / ETH / BTC related vaults are listed below.

### spUSDC (Spark USDC Vault)

| Chain     | Vault Address                                | Underlying (USDC)                            |
|-----------|----------------------------------------------|----------------------------------------------|
| Ethereum  | `0x28B3a8fb53B741A8Fd78c0fb9A6B2393d896a43d` | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| Avalanche | `0x28B3a8fb53B741A8Fd78c0fb9A6B2393d896a43d` | `0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E` |

> **Note:** Avalanche has spUSDC in the address registry. Base / Arbitrum / Optimism / Unichain have a different savings product (sUSDC) that is a USDS-backed wrapper, not a direct USDC vault.

### sUSDC (Savings USDC — USDS-backed)

| Chain     | Vault Address                                | Underlying (USDC)                            |
|-----------|----------------------------------------------|----------------------------------------------|
| Base      | `0x3128a0F7f0ea68E7B7c9B00AFa7E41045828e858` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Arbitrum  | `0x940098b108fB7D0a7E374f6eDED7760787464609` | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` |
| Optimism  | `0xCF9326e24EBfFBEF22ce1050007A43A3c0B6DB55` | `0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85` |
| Unichain  | `0x14d9143BEcC348920b68D123687045db49a016C6` | `0x078D782b760474a361dDA0AF3839290b0EF57AD6` |

### spUSDT (Spark USDT Vault — Ethereum only)

| Chain     | Vault Address                                | Underlying (USDT)                            |
|-----------|----------------------------------------------|----------------------------------------------|
| Ethereum  | `0xe2e7a17dFf93280dec073C995595155283e3C372` | `0xdAC17F958D2ee523a2206206994597C13D831ec7` |

### spETH (Spark ETH Vault — Ethereum only)

| Chain     | Vault Address                                | Underlying (WETH)                            |
|-----------|----------------------------------------------|----------------------------------------------|
| Ethereum  | `0xfE6eb3b609a7C8352A241f7F3A21CEA4e9209B8f` | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` |

### BTC

No Spark Savings vault exists for BTC.

---

## 3. Spark Savings — ERC-4626 Contract Interface

All Spark Savings vaults (spUSDC, spUSDT, spETH, sUSDC) implement the standard ERC-4626 interface.

### Read Functions (view)

```solidity
// Returns the address of the underlying ERC-20 asset
function asset() external view returns (address);

// Total amount of the underlying asset managed by the vault
function totalAssets() external view returns (uint256);

// Vault share balance of `account`
function balanceOf(address account) external view returns (uint256);

// Convert `shares` to asset amount (no fees, no slippage)
function convertToAssets(uint256 shares) external view returns (uint256);

// Convert `assets` to share amount (no fees, no slippage)
function convertToShares(uint256 assets) external view returns (uint256);

// Preview how many shares a deposit of `assets` would yield
function previewDeposit(uint256 assets) external view returns (uint256);

// Preview how many assets a redeem of `shares` would yield
function previewRedeem(uint256 shares) external view returns (uint256);
```

### Write Functions (state-changing)

```solidity
// Deposit `assets` of underlying token, mint shares to `receiver`
function deposit(uint256 assets, address receiver) external returns (uint256 shares);

// Withdraw exactly `assets`, burning shares from `owner`, sending assets to `receiver`
function withdraw(uint256 assets, address receiver, address owner) external returns (uint256 shares);

// Redeem exactly `shares`, sending resulting assets to `receiver` (preferred for full withdrawal)
function redeem(uint256 shares, address receiver, address owner) external returns (uint256 assets);
```

### ERC-20 Approve (prerequisite for deposit)

```solidity
// Approve the vault to spend underlying tokens on behalf of msg.sender
IERC20(underlying).approve(vaultAddress, amount);
```

---

## 4. Spark Savings — Operation Flows

### Deposit Flow

```
1. Query underlying token address:
   underlying = vault.asset()

2. Check user balance:
   balance_raw = IERC20(underlying).balanceOf(user)

3. Approve vault to spend underlying:
   IERC20(underlying).approve(vault_address, amount_raw)

4. Preview expected shares:
   expected_shares = vault.previewDeposit(amount_raw)

5. Execute deposit:
   shares = vault.deposit(amount_raw, receiver)
```

### Withdraw Flow (prefer `redeem`)

Using `redeem` is preferred over `withdraw` because it operates on shares (which the user holds) rather than a specific asset amount, avoiding rounding issues.

```
1. Check user share balance:
   shares = vault.balanceOf(user)

2. Preview expected assets:
   expected_assets = vault.previewRedeem(shares)

3. Execute redeem:
   assets = vault.redeem(shares, receiver, owner)
```

### Full Withdrawal

```solidity
vault.redeem(vault.balanceOf(user), user, user)
```

### Liquidity Notes

- No lock-up period
- V2 vaults retain ~10% idle liquidity for instant withdrawals
- Large withdrawals are handled via Savings Liquidity Intents (typically fulfilled within minutes)

---

## 5. SparkLend (Markets) — Pool & Token Registry

SparkLend is an Aave V3 fork deployed only on Ethereum and Gnosis.

### Pool Addresses

| Chain    | chainId | Pool Address                                 | WETH Gateway                                 |
|----------|---------|----------------------------------------------|----------------------------------------------|
| Ethereum | 1       | `0xC13e21B648A5Ee794902342038FF3aDAB66BE987` | `0xBD7D6a9ad7865463DE44B05F04559f65e3B11704` |
| Gnosis   | 100     | `0x2Dae5307c5E3FD1CF5A72Cb6F698f915860607e0` | `0xBD7D6a9ad7865463DE44B05F04559f65e3B11704` |

### Ethereum Token Reserves

| Asset | Underlying                                   | spToken                                      |
|-------|----------------------------------------------|----------------------------------------------|
| USDC  | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | `0x377C3bd93f2a2984E1E7bE6A5C22c525eD4A4815` |
| USDT  | `0xdAC17F958D2ee523a2206206994597C13D831ec7` | `0xe7dF13b8e3d6740fe17CBE928C7334243d86c92f` |
| WETH  | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` | `0x59cD1C87501baa753d0B5B5Ab5D8416A45cD71DB` |
| WBTC  | `0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599` | `0x4197ba364AE6698015AE5c1468f54087602715b2` |

### Gnosis Token Reserves

| Asset | Underlying                                   | spToken                                      |
|-------|----------------------------------------------|----------------------------------------------|
| USDC  | `0xDDAfbb505ad214D7b80b1f830fcCc89B60fb7A83` | `0x5850D127a04ed0B4F1FCDFb051b3409FB9Fe6B90` |
| USDT  | `0x4ECaBa5870353805a9F068101A40E0f32ed605C6` | `0x08B0cAebE352c3613302774Cd9B82D08afd7bDC4` |
| WETH  | `0x6A023CCd1ff6F2045C3309768eAd9E68F978f6e1` | `0x629D562E92fED431122e865Cc650Bc6bdE6B96b0` |

> **Note:** Gnosis does not have a WBTC reserve.

---

## 6. SparkLend — Pool Contract Interface

SparkLend uses the same interface as Aave V3 (it is an Aave V3 fork).

### Read Functions (view)

```solidity
// Returns reserve data including aToken address, liquidity index, current rates
function getReserveData(address asset) external view returns (DataTypes.ReserveData memory);

// Returns user account data (total collateral, total debt, available borrows, etc.)
function getUserAccountData(address user) external view returns (
    uint256 totalCollateralBase,
    uint256 totalDebtBase,
    uint256 availableBorrowsBase,
    uint256 currentLiquidationThreshold,
    uint256 ltv,
    uint256 healthFactor
);
```

### Write Functions (state-changing)

```solidity
// Supply `amount` of `asset` on behalf of `onBehalfOf`; referralCode is currently inactive (pass 0)
function supply(address asset, uint256 amount, address onBehalfOf, uint16 referralCode) external;

// Supply with ERC-2612 permit (single tx approve + supply)
function supplyWithPermit(
    address asset, uint256 amount, address onBehalfOf, uint16 referralCode,
    uint256 deadline, uint8 permitV, bytes32 permitR, bytes32 permitS
) external;

// Withdraw `amount` of `asset` to `to`; pass type(uint256).max for full withdrawal
function withdraw(address asset, uint256 amount, address to) external returns (uint256);
```

### ERC-20 Approve (prerequisite for supply)

```solidity
// Approve the Pool to spend underlying tokens on behalf of msg.sender
IERC20(underlying).approve(poolAddress, amount);
```

---

## 7. SparkLend — Operation Flows

### Deposit (Supply) Flow

```
1. Check user balance:
   balance_raw = IERC20(underlying).balanceOf(user)

2. Approve Pool to spend underlying:
   IERC20(underlying).approve(pool_address, amount_raw)

3. Execute supply:
   pool.supply(underlying, amount_raw, user, 0)
   // referralCode = 0 (inactive)
```

### Withdraw Flow

```
1. Check user spToken balance:
   sp_balance = IERC20(spToken).balanceOf(user)

2. Execute withdraw:
   pool.withdraw(underlying, amount_raw, user)
```

### Full Withdrawal

```solidity
pool.withdraw(underlying, type(uint256).max, user)
```

### Native ETH via WETH Gateway

For native ETH deposits/withdrawals, use the WETH Gateway contract instead of the Pool directly:

```solidity
// Deposit native ETH
IWETHGateway(gateway).depositETH{value: amount}(pool_address, onBehalfOf, 0);

// Withdraw to native ETH (requires spWETH approval to gateway)
IWETHGateway(gateway).withdrawETH(pool_address, amount, to);
```

---

## 8. Spark API

- No dedicated REST/GraphQL API (unlike Aave or Morpho)
- **Rate queries:** via on-chain `getReserveData()` or The Graph subgraph
- **Savings rates:** via ERC-4626 `convertToAssets()` method or SSR Oracle

---

## 9. Data Sources

All contract addresses sourced from:

- `github.com/sparkdotfi/spark-address-registry` (Ethereum.sol, Base.sol, Arbitrum.sol, Optimism.sol, Unichain.sol, Gnosis.sol)
- `github.com/marsfoundation/sparklend-deployments` (primary-latest.json for chain 1 and 100)
- Etherscan / GnosisScan verification

## Morpho

### 1. Overview

Morpho V2 vaults are **ERC-4626** standard tokenized vaults. Users deposit an underlying asset (e.g. USDC) and receive vault shares representing their proportional claim on the vault's total assets.

**Supported chains:**

| Chain    | chainId |
|----------|---------|
| Ethereum | 1       |
| Monad    | 143     |

---

### 2. Vault Registry

All vaults below are Morpho V2; V1 is excluded.

#### USDC Vaults

| Vault Name                     | Chain    | Vault Address                                | Underlying | URL |
|--------------------------------|----------|----------------------------------------------|------------|-----|
| Steakhouse Reservoir USDC      | Ethereum | `0xBEeFF047C03714965a54b671A37C18beF6b96210` | USDC       | https://app.morpho.org/ethereum/vault/0xBEeFF047C03714965a54b671A37C18beF6b96210/steakhouse-reservoir-usdc |
| SkyMoney USDC Risk Capital     | Ethereum | `0x56bfa6f53669B836D1E0Dfa5e99706b12c373ecf` | USDC       | https://app.morpho.org/ethereum/vault/0x56bfa6f53669B836D1E0Dfa5e99706b12c373ecf/skymoney-usdc-risk-capital |
| Re Ecosystem Vault             | Ethereum | `0xD1E9242e075Db4bdd3f3c721D7d5fd4180A94A7e` | USDC       | https://app.morpho.org/ethereum/vault/0xD1E9242e075Db4bdd3f3c721D7d5fd4180A94A7e/re-ecosystem-vault |

#### USDT Vaults

| Vault Name                     | Chain    | Vault Address                                | Underlying | URL |
|--------------------------------|----------|----------------------------------------------|------------|-----|
| SkyMoney USDT Savings          | Ethereum | `0x23f5E9c35820f4baB695Ac1F19c203cC3f8e1e11` | USDT       | https://app.morpho.org/ethereum/vault/0x23f5E9c35820f4baB695Ac1F19c203cC3f8e1e11/skymoney-usdt-savings |
| Steakhouse High Yield Instant  | Ethereum | `0xbeeff07d991C04CD640DE9F15C08ba59c4FEDEb7` | USDT       | https://app.morpho.org/ethereum/vault/0xbeeff07d991C04CD640DE9F15C08ba59c4FEDEb7/steakhouse-high-yield-instant |
| Steakhouse High Yield USDT0    | Monad    | `0xbeeff300E9A9caeC7beEA740ab8758D33b777509` | USDT0      | https://app.morpho.org/monad/vault/0xbeeff300E9A9caeC7beEA740ab8758D33b777509/steakhouse-high-yield-usdt0 |

#### ETH Vaults

| Vault Name                     | Chain    | Vault Address                                | Underlying | URL |
|--------------------------------|----------|----------------------------------------------|------------|-----|
| Steakhouse Prime ETH           | Monad    | `0xbeef04b01e0275D4ac2e2986256BB14E3Ff6ef42` | ETH        | https://app.morpho.org/monad/vault/0xbeef04b01e0275D4ac2e2986256BB14E3Ff6ef42/steakhouse-prime-eth |
| Steakhouse Prime Instant       | Ethereum | `0xbeef0046fcab1dE47E41fB75BB3dC4Dfc94108E3` | ETH        | https://app.morpho.org/ethereum/vault/0xbeef0046fcab1dE47E41fB75BB3dC4Dfc94108E3/steakhouse-prime-instant |
| KPK ETH Prime V2               | Ethereum | `0xBb50A5341368751024ddf33385BA8cf61fE65FF9` | ETH        | https://app.morpho.org/ethereum/vault/0xBb50A5341368751024ddf33385BA8cf61fE65FF9/kpk-eth-prime-v2 |

#### BTC Vaults

| Vault Name                     | Chain    | Vault Address                                | Underlying | URL |
|--------------------------------|----------|----------------------------------------------|------------|-----|
| Hyperithm cbBTC Apex           | Monad    | `0xe09A93786275546690247d70f1767cF0b69e8Ea0` | cbBTC      | https://app.morpho.org/monad/vault/0xe09A93786275546690247d70f1767cF0b69e8Ea0/hyperithm-cbbtc-apex |

---

### 3. ERC-4626 Contract Interface

All Morpho V2 vaults implement the ERC-4626 standard. Below are the core function signatures.

#### Read Functions (view)

```solidity
// Returns the address of the underlying ERC-20 asset
function asset() external view returns (address);

// Total amount of the underlying asset managed by the vault
function totalAssets() external view returns (uint256);

// Vault share balance of `account`
function balanceOf(address account) external view returns (uint256);

// Convert `shares` to asset amount (no fees, no slippage)
function convertToAssets(uint256 shares) external view returns (uint256);

// Convert `assets` to share amount (no fees, no slippage)
function convertToShares(uint256 assets) external view returns (uint256);

// Preview how many shares a deposit of `assets` would yield
function previewDeposit(uint256 assets) external view returns (uint256);

// Preview how many assets a redeem of `shares` would yield
function previewRedeem(uint256 shares) external view returns (uint256);
```

#### Write Functions (state-changing)

```solidity
// Deposit `assets` of underlying token, mint shares to `receiver`
function deposit(uint256 assets, address receiver) external returns (uint256 shares);

// Withdraw exactly `assets`, burning shares from `owner`, sending assets to `receiver`
function withdraw(uint256 assets, address receiver, address owner) external returns (uint256 shares);

// Redeem exactly `shares`, sending resulting assets to `receiver` (preferred for full withdrawal)
function redeem(uint256 shares, address receiver, address owner) external returns (uint256 assets);
```

#### ERC-20 Approve (prerequisite for deposit)

```solidity
// Approve the vault to spend underlying tokens on behalf of msg.sender
IERC20(underlying).approve(vaultAddress, amount);
```

---

### 4. Operation Flows

#### Deposit Flow

```
1. Query underlying token address:
   underlying = vault.asset()

2. Check user balance:
   balance_raw = IERC20(underlying).balanceOf(user)

3. Approve vault to spend underlying:
   IERC20(underlying).approve(vault_address, amount_raw)

4. Preview expected shares:
   expected_shares = vault.previewDeposit(amount_raw)

5. Execute deposit:
   shares = vault.deposit(amount_raw, receiver)
```

#### Withdraw Flow (prefer `redeem`)

Using `redeem` is preferred over `withdraw` because it operates on shares (which the user holds) rather than a specific asset amount, avoiding rounding issues.

```
1. Check user share balance:
   shares = vault.balanceOf(user)

2. Preview expected assets:
   expected_assets = vault.previewRedeem(shares)

3. Execute redeem:
   assets = vault.redeem(shares, receiver, owner)
```

#### Full Withdrawal

```solidity
vault.redeem(vault.balanceOf(user), user, user)
```

---

### 5. Morpho GraphQL API

**Endpoint:** `https://api.morpho.org/graphql`

#### Query Vault APY

```graphql
query {
  vaultByAddress(address: "0xBEeFF047C03714965a54b671A37C18beF6b96210", chainId: 1) {
    address
    symbol
    asset {
      symbol
      decimals
      address
    }
    state {
      totalAssets
      apy
      netApy
    }
  }
}
```

#### Batch Query (all tracked vaults)

Use multiple `vaultByAddress` calls with GraphQL aliases:

```graphql
query {
  steakhouseUSDC: vaultByAddress(address: "0xBEeFF047C03714965a54b671A37C18beF6b96210", chainId: 1) {
    address
    symbol
    state { apy netApy totalAssets }
  }
  skymoneyUSDC: vaultByAddress(address: "0x56bfa6f53669B836D1E0Dfa5e99706b12c373ecf", chainId: 1) {
    address
    symbol
    state { apy netApy totalAssets }
  }
  # ... add remaining vaults
}
```
