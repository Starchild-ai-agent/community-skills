#!/usr/bin/env python3
"""Generate Lighter DEX API keys"""

from eth_account import Account

def generate_api_keys():
    """Generate a new API key pair for Lighter DEX"""
    
    print("🔑 Generating Lighter DEX API Keys...\n")
    
    # Create new account for API access
    api_account = Account.create()
    
    print(f"✅ New API Account Created!")
    print(f"\n📝 Add these to your workspace/.env file:\n")
    print(f"LIGHTER_API_KEY={api_account.key.hex()}")
    print(f"LIGHTER_API_ADDRESS={api_account.address}")
    print(f"LIGHTER_NETWORK=testnet  # Change to 'mainnet' when ready\n")
    
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("  1. Save the private key securely - it cannot be recovered if lost")
    print("  2. Never commit this to git or share it publicly")
    print("  3. This key is SEPARATE from your main wallet key (safer for API access)")
    print("  4. You can generate multiple API keys and revoke them individually\n")
    
    print("📋 Next Steps:")
    print("  1. Copy the LIGHTER_API_KEY and LIGHTER_API_ADDRESS above to workspace/.env")
    print("  2. Go to app.lighter.xyz (or testnet.lighter.xyz)")
    print("  3. Connect your main wallet")
    print("  4. Navigate to Settings > API")
    print("  5. Register/whitelist your API address (LIGHTER_API_ADDRESS)")
    print("  6. Run: python skills/lighter-dex/scripts/test_connection.py\n")

if __name__ == "__main__":
    generate_api_keys()
