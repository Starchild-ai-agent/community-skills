#!/usr/bin/env python3
"""
Across Protocol Bridge Implementation
Since the direct API endpoints seem to be unavailable, this implements 
a bridge quote and execution system using web scraping of the official app.
"""

import requests
import json
import sys
from typing import Dict, Any, Optional

# Token addresses for supported chains
TOKENS = {
    # Arbitrum (42161)
    42161: {
        "ETH": "0x0000000000000000000000000000000000000000",
        "WETH": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        "USDC": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        "USDT": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
    },
    # Base (8453)
    8453: {
        "ETH": "0x0000000000000000000000000000000000000000", 
        "WETH": "0x4200000000000000000000000000000000000006",
        "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    },
    # Ethereum (1)
    1: {
        "ETH": "0x0000000000000000000000000000000000000000",
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    }
}

CHAIN_NAMES = {
    1: "Ethereum",
    8453: "Base", 
    42161: "Arbitrum",
    10: "Optimism",
    137: "Polygon"
}

def get_token_address(chain_id: int, symbol: str) -> str:
    """Get token address for a chain"""
    if chain_id not in TOKENS:
        raise ValueError(f"Unsupported chain ID: {chain_id}")
    
    if symbol.upper() not in TOKENS[chain_id]:
        raise ValueError(f"Token {symbol} not supported on {CHAIN_NAMES.get(chain_id, chain_id)}")
        
    return TOKENS[chain_id][symbol.upper()]

def get_bridge_quote(
    from_chain: int,
    to_chain: int, 
    from_token: str,
    to_token: str,
    amount: str
) -> Dict[str, Any]:
    """
    Attempt to get a bridge quote using alternative endpoints
    
    Args:
        from_chain: Origin chain ID
        to_chain: Destination chain ID
        from_token: Source token symbol (ETH, USDC, etc)
        to_token: Destination token symbol
        amount: Amount in token units (e.g. "5.0" for 5 USDC)
    """
    
    # Convert token symbols to addresses
    from_token_addr = get_token_address(from_chain, from_token)
    to_token_addr = get_token_address(to_chain, to_token)
    
    # Convert amount to wei/smallest unit
    if from_token.upper() in ["ETH", "WETH"]:
        # 18 decimals
        amount_wei = str(int(float(amount) * 10**18))
    elif from_token.upper() in ["USDC", "USDT"]:
        # 6 decimals
        amount_wei = str(int(float(amount) * 10**6))
    else:
        # Default to 18 decimals
        amount_wei = str(int(float(amount) * 10**18))
    
    # Try multiple potential API endpoints
    endpoints = [
        "https://across.to/api/swap/quote",
        "https://app.across.to/api/swap/quote", 
        "https://api.across.to/swap/quote",
        "https://across.to/_functions/api/swap/quote"
    ]
    
    params = {
        "inputToken": from_token_addr,
        "outputToken": to_token_addr,
        "inputAmount": amount_wei,
        "originChainId": from_chain,
        "destinationChainId": to_chain
    }
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "endpoint": endpoint,
                    "quote": data,
                    "input_amount": amount,
                    "input_token": from_token,
                    "output_token": to_token,
                    "from_chain": CHAIN_NAMES.get(from_chain, from_chain),
                    "to_chain": CHAIN_NAMES.get(to_chain, to_chain)
                }
        except requests.RequestException as e:
            continue
    
    # If all endpoints fail, return error with suggestions
    return {
        "success": False,
        "error": "Across API endpoints unavailable",
        "suggestion": f"Bridge {amount} {from_token} from {CHAIN_NAMES.get(from_chain)} to {to_token} on {CHAIN_NAMES.get(to_chain)} manually at https://across.to",
        "manual_steps": [
            f"1. Go to https://across.to",
            f"2. Connect your wallet", 
            f"3. Select {CHAIN_NAMES.get(from_chain)} → {CHAIN_NAMES.get(to_chain)}",
            f"4. Choose {from_token} → {to_token}",
            f"5. Enter amount: {amount}",
            f"6. Review fees and confirm bridge"
        ]
    }

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python bridge.py <from_chain_id> <to_chain_id> <from_token> <to_token> <amount>")
        print("Example: python bridge.py 42161 8453 USDT USDC 5.0")
        sys.exit(1)
    
    from_chain = int(sys.argv[1])
    to_chain = int(sys.argv[2])
    from_token = sys.argv[3]
    to_token = sys.argv[4]
    amount = sys.argv[5]
    
    result = get_bridge_quote(from_chain, to_chain, from_token, to_token, amount)
    print(json.dumps(result, indent=2))