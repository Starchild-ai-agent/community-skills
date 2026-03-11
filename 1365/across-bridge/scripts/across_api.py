#!/usr/bin/env python3
"""
Across Protocol Bridge API Helper
Fast cross-chain token bridging with 1-3 minute settlement
"""

import requests
import json

def get_across_quote(input_token, output_token, amount, origin_chain, dest_chain, depositor):
    """
    Get a complete bridge quote from Across Protocol
    
    Args:
        input_token: Contract address of input token
        output_token: Contract address of output token  
        amount: Amount in wei (string)
        origin_chain: Origin chain ID
        dest_chain: Destination chain ID
        depositor: Wallet address
        
    Returns:
        dict: Complete quote with transaction data
    """
    url = "https://app.across.to/api/swap"
    
    params = {
        'inputToken': input_token,
        'outputToken': output_token,
        'amount': str(amount),
        'originChainId': origin_chain,
        'destinationChainId': dest_chain,
        'depositor': depositor
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Calculate fee percentage
        if 'fees' in data and 'total' in data['fees']:
            input_amount = float(amount)
            fee_total = data['fees']['total']
            if isinstance(fee_total, dict) and 'amount' in fee_total:
                fee_amount = float(fee_total['amount'])
            else:
                fee_amount = float(fee_total)
            fee_pct = (fee_amount / input_amount) * 100 if input_amount > 0 else 0
            data['fees']['totalFeePct'] = fee_pct
            
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None
    except (ValueError, KeyError) as e:
        print(f"Parse Error: {e}")
        return None

def execute_across_bridge(quote_data, wallet_transfer_func):
    """
    Execute the bridge using quote data and wallet transfer function
    
    Args:
        quote_data: Result from get_across_quote()
        wallet_transfer_func: Function to call for sending transactions
        
    Returns:
        list: Transaction hashes of executed transactions
    """
    tx_hashes = []
    
    # Send approval transactions first (if any)
    if 'approvalTxns' in quote_data and quote_data['approvalTxns']:
        for approval_tx in quote_data['approvalTxns']:
            tx_hash = wallet_transfer_func(
                to=approval_tx['to'],
                amount=approval_tx.get('value', '0'),
                data=approval_tx['data'],
                chain_id=int(approval_tx['chainId'])
            )
            tx_hashes.append(('approval', tx_hash))
    
    # Send the main bridge transaction
    if 'swapTx' in quote_data:
        swap_tx = quote_data['swapTx']
        tx_hash = wallet_transfer_func(
            to=swap_tx['to'],
            amount=swap_tx.get('value', '0'),
            data=swap_tx['data'],
            chain_id=int(swap_tx['chainId'])
        )
        tx_hashes.append(('bridge', tx_hash))
    
    return tx_hashes

# Chain IDs for reference
CHAIN_IDS = {
    'ethereum': 1,
    'arbitrum': 42161,
    'base': 8453,
    'optimism': 10,
    'polygon': 137
}

# Common token addresses
TOKEN_ADDRESSES = {
    'ethereum': {
        'ETH': '0x0000000000000000000000000000000000000000',
        'WETH': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
        'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7'
    },
    'arbitrum': {
        'ETH': '0x0000000000000000000000000000000000000000',
        'WETH': '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1',
        'USDC': '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
        'USDT': '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'
    },
    'base': {
        'ETH': '0x4200000000000000000000000000000000000006',
        'WETH': '0x4200000000000000000000000000000000000006',
        'USDC': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
        'USDT': '0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2'
    },
    'optimism': {
        'ETH': '0x0000000000000000000000000000000000000000',
        'WETH': '0x4200000000000000000000000000000000000006',
        'USDC': '0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85',
        'USDT': '0x94b008aA00579c1307B0EF2c499aD98a8ce58e58'
    }
}