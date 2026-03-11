#!/usr/bin/env python3
"""
Across Protocol Bridge: Bridge ETH or ERC-20 tokens between chains.
Usage: python3 bridge.py <from_chain_id> <to_chain_id> <amount_wei> <wallet_address> [token_symbol]

Supported tokens: ETH (default), USDC, USDT, WBTC, DAI
Supported chains: Ethereum (1), Arbitrum (42161), Optimism (10), Base (8453),
                  Polygon (137), BSC (56), Linea (59144), zkSync (324)

Examples:
  python3 bridge.py 42161 1 14150000000000000 0xYourWallet
      -> Bridge 0.01415 ETH from Arbitrum to Ethereum

  python3 bridge.py 42161 1 100000000 0xYourWallet USDC
      -> Bridge 100 USDC (6 decimals) from Arbitrum to Ethereum

The script:
1. Queries Across suggested-fees API for live quote + output amount
2. Encodes a depositV3() call to the SpokePool
3. Prints the calldata, target contract, and value to send
"""

import sys
import json
import requests
from eth_abi import encode

# ── Token addresses per chain ─────────────────────────────────────────────────

TOKENS = {
    "ETH": {   # Uses WETH as inputToken/outputToken for native ETH bridges
        1:     "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        42161: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        10:    "0x4200000000000000000000000000000000000006",
        8453:  "0x4200000000000000000000000000000000000006",
        137:   "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
        56:    "0x2170Ed0880ac9A755fd29B2688956BD959F933F8",
        59144: "0xe5D7C2a44FfDDf6b295A15c148167daaAf5Cf34",
        324:   "0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91",
    },
    "USDC": {
        1:     "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        42161: "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        10:    "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
        8453:  "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        137:   "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
        59144: "0x176211869cA2b568f2A7D4EE941E073a821EE1ff",
    },
    "USDT": {
        1:     "0xdAC17F958D2ee523a2206206994597C13D831ec7",
        42161: "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        10:    "0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
        137:   "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
    },
    "WBTC": {
        1:     "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        42161: "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",
        10:    "0x68f180fcCe6836688e9084f035309E29Bf0A2095",
    },
    "DAI": {
        1:     "0x6B175474E89094C44Da98b954EedeAC495271d0F",
        42161: "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",
        10:    "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",
        8453:  "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
        137:   "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
    },
}

# Native ETH indicator (value is sent as msg.value, not token transfer)
NATIVE_ETH_TOKEN = "0x0000000000000000000000000000000000000000"

# depositV3 function selector
DEPOSIT_V3_SELECTOR = "7b939232"

CHAIN_NAMES = {
    1: "Ethereum",
    42161: "Arbitrum",
    10: "Optimism",
    8453: "Base",
    137: "Polygon",
    56: "BSC",
    59144: "Linea",
    324: "zkSync Era",
}


# ── Quote ─────────────────────────────────────────────────────────────────────

def get_quote(origin_chain_id, dest_chain_id, amount_wei, token_symbol):
    input_token = TOKENS[token_symbol][origin_chain_id]
    output_token = TOKENS[token_symbol][dest_chain_id]

    url = "https://app.across.to/api/suggested-fees"
    params = {
        "inputToken": input_token,
        "outputToken": output_token,
        "originChainId": origin_chain_id,
        "destinationChainId": dest_chain_id,
        "amount": amount_wei,
    }
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ── Calldata encoding ─────────────────────────────────────────────────────────

def encode_deposit_v3(depositor, recipient, input_token, output_token,
                      input_amount, output_amount, dest_chain_id,
                      exclusive_relayer, quote_timestamp, fill_deadline,
                      exclusivity_deadline, message=b""):
    encoded = encode(
        ["address", "address", "address", "address",
         "uint256", "uint256", "uint256",
         "address", "uint32", "uint32", "uint32", "bytes"],
        [depositor, recipient, input_token, output_token,
         input_amount, output_amount, dest_chain_id,
         exclusive_relayer, quote_timestamp, fill_deadline,
         exclusivity_deadline, message]
    )
    return "0x" + DEPOSIT_V3_SELECTOR + encoded.hex()


# ── Deposit status tracking ───────────────────────────────────────────────────

def get_deposit_status(origin_chain_id, deposit_tx_hash):
    """Check fill status of a submitted bridge deposit."""
    url = "https://app.across.to/api/deposit/status"
    params = {
        "originChainId": origin_chain_id,
        "depositTxHash": deposit_tx_hash,
    }
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Handle status check mode
    if len(sys.argv) == 4 and sys.argv[1] == "status":
        origin_chain = int(sys.argv[2])
        tx_hash = sys.argv[3]
        print(f"🔍 Checking deposit status...")
        status = get_deposit_status(origin_chain, tx_hash)
        print(json.dumps(status, indent=2))
        return

    if len(sys.argv) < 5:
        print("Usage:")
        print("  Bridge:  python3 bridge.py <from_chain_id> <to_chain_id> <amount_wei> <wallet_address> [token_symbol]")
        print("  Status:  python3 bridge.py status <from_chain_id> <deposit_tx_hash>")
        print()
        print(f"  Supported tokens: {', '.join(TOKENS.keys())}")
        print(f"  Supported chains: {json.dumps(CHAIN_NAMES)}")
        sys.exit(1)

    origin_chain = int(sys.argv[1])
    dest_chain = int(sys.argv[2])
    amount_wei = int(sys.argv[3])
    wallet = sys.argv[4]
    token_symbol = sys.argv[5].upper() if len(sys.argv) > 5 else "ETH"

    # Validate
    if token_symbol not in TOKENS:
        print(f"Error: Unsupported token '{token_symbol}'. Supported: {', '.join(TOKENS.keys())}")
        sys.exit(1)
    if origin_chain not in TOKENS[token_symbol]:
        print(f"Error: {token_symbol} not supported on chain {origin_chain}.")
        print(f"  Available chains for {token_symbol}: {list(TOKENS[token_symbol].keys())}")
        sys.exit(1)
    if dest_chain not in TOKENS[token_symbol]:
        print(f"Error: {token_symbol} not supported on chain {dest_chain}.")
        print(f"  Available chains for {token_symbol}: {list(TOKENS[token_symbol].keys())}")
        sys.exit(1)

    origin_name = CHAIN_NAMES.get(origin_chain, str(origin_chain))
    dest_name = CHAIN_NAMES.get(dest_chain, str(dest_chain))

    print(f"🌉 Across Bridge: {token_symbol}")
    print(f"   {origin_name} (chain {origin_chain}) → {dest_name} (chain {dest_chain})")
    print(f"   Amount: {amount_wei} wei")
    print(f"   Wallet: {wallet}")
    print()

    # Step 1: Quote
    print("📊 Getting quote from Across API...")
    quote = get_quote(origin_chain, dest_chain, amount_wei, token_symbol)

    output_amount = int(quote["outputAmount"])
    spoke_pool = quote["spokePoolAddress"]
    timestamp = int(quote["timestamp"])
    fill_deadline = int(quote["fillDeadline"])
    exclusive_relayer = quote.get("exclusiveRelayer", "0x0000000000000000000000000000000000000000")

    # exclusivityDeadline: API may return an offset (int) or absolute timestamp
    # If the value is small (< 1e9), it's an offset; otherwise it's absolute.
    raw_excl = int(quote.get("exclusivityDeadline", 0))
    exclusivity_deadline = raw_excl if raw_excl > 1_000_000_000 else timestamp + raw_excl

    estimated_fill_time = quote.get("estimatedFillTimeSec", "unknown")

    fee_wei = amount_wei - output_amount
    fee_pct = (fee_wei / amount_wei) * 100

    print(f"   SpokePool:      {spoke_pool}")
    print(f"   Input:          {amount_wei} wei")
    print(f"   Output:         {output_amount} wei")
    print(f"   Fee:            {fee_wei} wei ({fee_pct:.4f}%)")
    print(f"   Est. fill time: {estimated_fill_time}s")
    print()

    # Step 2: Encode calldata
    input_token = TOKENS[token_symbol][origin_chain]
    output_token = TOKENS[token_symbol][dest_chain]

    calldata = encode_deposit_v3(
        depositor=wallet,
        recipient=wallet,
        input_token=input_token,
        output_token=output_token,
        input_amount=amount_wei,
        output_amount=output_amount,
        dest_chain_id=dest_chain,
        exclusive_relayer=exclusive_relayer,
        quote_timestamp=timestamp,
        fill_deadline=fill_deadline,
        exclusivity_deadline=exclusivity_deadline,
        message=b"",
    )

    # For native ETH, msg.value = amount; for ERC-20, msg.value = 0 (approval needed)
    is_native_eth = (token_symbol == "ETH")

    print("✅ Transaction ready:")
    result = {
        "to": spoke_pool,
        "value": str(amount_wei) if is_native_eth else "0",
        "data": calldata,
        "chain_id": origin_chain,
        "token": token_symbol,
        "input_token": input_token,
        "output_token": output_token,
        "output_amount_wei": str(output_amount),
        "estimated_fill_time_sec": estimated_fill_time,
        "note": None if is_native_eth else f"ERC-20 bridge: approve {amount_wei} of {input_token} to {spoke_pool} before sending this tx."
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
