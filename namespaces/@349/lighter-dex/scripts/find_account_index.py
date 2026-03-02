#!/usr/bin/env python3
"""
Find your Lighter account index and verify API keys.

This script helps you discover:
1. Your account index on Lighter (required for API calls)
2. Which API key indexes are registered to your account
3. Verify your API key is working

Usage:
    python3 scripts/find_account_index.py

You'll be prompted to:
1. Enter your wallet address (the one you use on app.lighter.xyz)
2. Sign a message with MetaMask (proves ownership)
3. Enter your API key private key (to verify it works)

The script will output:
- Your account index
- All registered API keys
- Whether your API key is valid
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lighter_sdk import LighterClient, Wallet
from eth_account import Account
from eth_account.messages import encode_defunct
import json

def main():
    print("🏮 Lighter Account Index Finder\n")
    print("This will help you find your account index and verify API keys.\n")
    
    # Step 1: Get wallet address
    wallet_address = input("1. Enter your wallet address (0x... from app.lighter.xyz): ").strip()
    
    if not wallet_address.startswith("0x"):
        wallet_address = "0x" + wallet_address
    
    print(f"   → Wallet: {wallet_address}\n")
    
    # Step 2: Sign message to prove ownership
    print("2. You need to sign a message to prove you own this wallet.")
    print("   Copy this message and sign it in MetaMask:\n")
    
    message = f"I own {wallet_address} and want to access my Lighter account."
    print(f"   \"{message}\"\n")
    
    signature = input("3. Paste the signature here: ").strip()
    print()
    
    # Step 3: Initialize client
    print("🔍 Looking up your account...\n")
    
    try:
        client = LighterClient("https://mainnet.zklighter.elliot.ai")
        
        # Use the wallet address and signature to authenticate
        # This will return your account index
        account_info = client.get_account(wallet_address, signature)
        
        account_index = account_info.get("account_index")
        registered_keys = account_info.get("api_keys", [])
        
        print(f"✅ FOUND YOUR ACCOUNT!")
        print(f"   Account Index: {account_index}")
        print(f"   Wallet: {wallet_address}")
        print(f"\n📋 Registered API Keys:")
        
        if registered_keys:
            for key_info in registered_keys:
                key_index = key_info.get("index")
                public_key = key_info.get("public_key", "")[:20] + "..."
                print(f"   - Index {key_index}: {public_key}")
        else:
            print("   No API keys registered yet!")
            print("   Go to https://app.lighter.xyz/apikeys to create one.")
        
        print(f"\n💾 SAVE THIS:")
        print(f"   ACCOUNT_INDEX={account_index}")
        
        # Step 4: Verify API key (optional)
        if registered_keys:
            print(f"\n🔑 Want to verify an API key works?")
            verify = input("   Enter your API key private key (or press Enter to skip): ").strip()
            
            if verify:
                print("\n   Testing API key...")
                try:
                    # Try to get account balance with the API key
                    # This proves the key works
                    test_client = LighterClient(
                        "https://mainnet.zklighter.elliot.ai",
                        account_index=account_index,
                        api_key=verify
                    )
                    
                    holdings = test_client.get_holdings()
                    balance = holdings.get("usdc", {}).get("available", 0)
                    
                    print(f"   ✅ API KEY WORKS!")
                    print(f"   USDC Balance: ${balance:.2f}")
                    
                except Exception as e:
                    print(f"   ❌ API Key failed: {str(e)}")
                    print("   Make sure you copied the full private key correctly.")
        
        print(f"\n📝 Next steps:")
        print(f"   1. Copy ACCOUNT_INDEX={account_index}")
        print(f"   2. Add to your .env file:")
        print(f"      LIGHTER_ACCOUNT_INDEX={account_index}")
        print(f"      LIGHTER_API_KEY=your_private_key_here")
        print(f"   3. Run: lighter_account() to test\n")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print(f"\nTroubleshooting:")
        print(f"   - Make sure your wallet address is correct")
        print(f"   - Make sure the signature is from that wallet")
        print(f"   - Try again or contact Lighter support")

if __name__ == "__main__":
    main()
