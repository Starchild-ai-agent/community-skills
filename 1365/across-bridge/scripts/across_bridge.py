#!/usr/bin/env python3

import requests
import json

def get_across_quote(input_token, output_token, amount, origin_chain, dest_chain, depositor):
    """Get quote and transaction data from Across API"""
    
    url = "https://app.across.to/api/swap"
    
    params = {
        'inputToken': input_token,
        'outputToken': output_token, 
        'amount': amount,
        'originChainId': origin_chain,
        'destinationChainId': dest_chain,
        'depositor': depositor,
        'recipient': depositor
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"API Error: {e}")
        return None

if __name__ == "__main__":
    # Bridge ETH from Base to Arbitrum
    # ETH on Base: 0x0000000000000000000000000000000000000000 (native)
    # WETH on Arbitrum: 0x82aF49447D8a07e3bd95BD0d56f35241523fBab1 
    
    wallet_address = "0xE09ef4a2CcB5fCD88AA3aE51970BCc17884811de"
    amount = "4624539426727526"  # Current balance in wei
    
    quote = get_across_quote(
        input_token="0x0000000000000000000000000000000000000000",  # ETH on Base
        output_token="0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",   # WETH on Arbitrum  
        amount=amount,
        origin_chain=8453,   # Base
        dest_chain=42161,    # Arbitrum
        depositor=wallet_address
    )
    
    if quote:
        print("Bridge Quote:")
        print(json.dumps(quote, indent=2))
    else:
        print("Failed to get quote")