#!/usr/bin/env python3
"""Test Lighter DEX API connection"""

import os
import sys
import asyncio
import logging

# Add workspace to path
sys.path.insert(0, '/data/workspace')

from dotenv import load_dotenv
load_dotenv('/data/workspace/.env')

logging.basicConfig(level=logging.INFO)

async def test_lighter_connection():
    """Test connection to Lighter DEX"""
    
    api_key = os.getenv("LIGHTER_API_KEY")
    api_address = os.getenv("LIGHTER_API_ADDRESS")
    network = os.getenv("LIGHTER_NETWORK", "testnet")
    
    if not api_key or not api_address:
        print("❌ Missing LIGHTER_API_KEY or LIGHTER_API_ADDRESS in .env")
        print("\nSetup instructions:")
        print("1. Run: python skills/lighter-dex/scripts/generate_keys.py")
        print("2. Register the API address with Lighter (via testnet.zklighter.elliot.ai)")
        print("3. Update workspace/.env with the keys")
        return False
    
    try:
        import lighter
        
        base_url = "https://testnet.zklighter.elliot.ai" if network == "testnet" else "https://mainnet.zklighter.elliot.ai"
        
        print(f"🔗 Connecting to Lighter {network}...")
        print(f"   API Address: {api_address}")
        print(f"   Base URL: {base_url}")
        
        # Create API client
        api_client = lighter.ApiClient(configuration=lighter.Configuration(host=base_url))
        
        # Check if account exists
        print("\n📊 Checking if account exists...")
        try:
            account_api = lighter.AccountApi(api_client)
            response = await account_api.accounts_by_l1_address(l1_address=api_address)
            
            if response.sub_accounts:
                account_index = response.sub_accounts[0].index
                print(f"✅ Account found! Index: {account_index}")
                
                # Create SignerClient
                print("\n🔑 Creating SignerClient...")
                private_keys = {3: api_key}  # Use API key index 3
                signer = lighter.SignerClient(
                    url=base_url,
                    account_index=account_index,
                    api_private_keys=private_keys,
                )
                
                # Check client
                print("🔍 Verifying API key...")
                err = signer.check_client()
                if err:
                    print(f"❌ API key verification failed: {err}")
                    print("\n⚠️  Your API key needs to be registered with Lighter!")
                    print("\nNext steps:")
                    print("1. Go to testnet.zklighter.elliot.ai")
                    print("2. Connect your wallet")
                    print("3. Navigate to Settings > API")
                    print("4. Register your API address: " + api_address)
                    await api_client.close()
                    await signer.close()
                    return False
                
                print("✅ API key verified!")
                
                # Get account info
                print("\n📈 Fetching account info...")
                account = await account_api.account(by="index", value=str(account_index))
                print(f"\nAccount Summary:")
                print(f"  Account Index: {account.index}")
                print(f"  L1 Address: {account.l1_address}")
                
                # Get order books
                print("\n📚 Fetching order books...")
                order_api = lighter.OrderApi(api_client)
                order_books = await order_api.order_books()
                print(f"  Found {len(order_books)} markets:")
                for ob in order_books[:5]:
                    print(f"    Market {ob.market_id}: {ob.name if hasattr(ob, 'name') else 'N/A'}")
                if len(order_books) > 5:
                    print(f"    ... and {len(order_books) - 5} more")
                
                # Get exchange stats
                print("\n📊 Exchange Stats...")
                stats = await order_api.exchange_stats()
                print(f"  Status: {stats.status if hasattr(stats, 'status') else 'N/A'}")
                
                await api_client.close()
                await signer.close()
                
                print("\n✅ Successfully connected to Lighter!")
                return True
            else:
                print(f"❌ No account found for address {api_address}")
                print("\n⚠️  You need to create an account on Lighter first!")
                print("\nNext steps:")
                print("1. Go to testnet.zklighter.elliot.ai")
                print("2. Connect your wallet")
                print("3. Complete account setup")
                print("4. Your account will be linked to your L1 address")
                await api_client.close()
                return False
                
        except lighter.ApiException as e:
            if "account not found" in str(e).lower():
                print(f"❌ Account not found for {api_address}")
                print("\n⚠️  You need to create an account on Lighter first!")
                print("\nNext steps:")
                print("1. Go to testnet.zklighter.elliot.ai")
                print("2. Connect your wallet")
                print("3. Complete account setup")
            else:
                print(f"❌ API Error: {e}")
            await api_client.close()
            return False
        
    except ImportError as e:
        print(f"❌ Error importing lighter SDK: {e}")
        print("\nMake sure lighter-sdk is installed: pip install lighter-sdk")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Lighter: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_lighter_connection())
    sys.exit(0 if success else 1)
