#!/usr/bin/env python3
"""
Market Lookup Tool for Lighter DEX
Find any market by symbol, name, or category
"""

import os
import sys
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import lighter_markets_list, lighter_market

def print_market(m):
    """Format and print a single market"""
    status_emoji = "✅" if m['status'] == 'ACTIVE' else "⏸️"
    print(f"  {status_emoji} {m['symbol']:12} | {m['base']:8} / {m['quote']:6} | "
          f"Min: {m['min_size']:<10} | Tick: {m['tick_size']:<10} | "
          f"Max Lev: {m['max_leverage']:3}x")

def search_markets(query=None, category=None, show_all=False):
    """Search and display markets"""
    
    print("\n" + "="*80)
    print("  LIGHTER DEX MARKET LOOKUP")
    print("="*80)
    
    if query:
        print(f"\n🔍 Search: '{query}'")
    if category:
        print(f"\n📁 Category: {category.upper()}")
    
    try:
        result = lighter_markets_list(search=query, category=category)
        
        print(f"\n📊 Found {result['count']} markets\n")
        
        if result['count'] == 0:
            print("  No markets found. Try:")
            print("    - Different search term (e.g., 'gold' instead of 'XAU')")
            print("    - Category filter: --category crypto|stocks|forex|commodities")
            print("    - No filters to see all markets")
            return
        
        # Group by category for better display
        markets = result['markets']
        
        if show_all or len(markets) <= 30:
            # Show all
            for m in markets:
                print_market(m)
        else:
            # Show first 30
            print(f"Showing first 30 of {len(markets)} markets:\n")
            for m in markets[:30]:
                print_market(m)
            print(f"\n  ... and {len(markets) - 30} more")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure LIGHTER_API_KEY is set in your .env file")

def get_market_details(symbol):
    """Get detailed info for a specific market"""
    
    print("\n" + "="*80)
    print(f"  MARKET DETAILS: {symbol}")
    print("="*80 + "\n")
    
    try:
        m = lighter_market(symbol)
        
        print(f"  Symbol:       {m['symbol']}")
        print(f"  Base Asset:   {m['base']}")
        print(f"  Quote Asset:  {m['quote']}")
        print(f"  Status:       {m['status']}")
        print(f"  Min Size:     {m['min_size']}")
        print(f"  Tick Size:    {m['tick_size']}")
        print(f"  Max Leverage: {m['max_leverage']}x")
        
        # Get current orderbook
        from tools import lighter_orderbook
        ob = lighter_orderbook(symbol, levels=5)
        
        print(f"\n  📊 Current Orderbook:")
        print(f"     Spread: {ob['spread']:.4f} ({(ob['spread']/ob['mid_price']*100):.4f}%)")
        print(f"     Mid:    ${ob['mid_price']:.4f}")
        print(f"\n     Top 5 Bids:")
        for bid in ob['bids'][:5]:
            print(f"       ${bid[0]:,.2f} × {bid[1]:.4f}")
        print(f"\n     Top 5 Asks:")
        for ask in ob['asks'][:5]:
            print(f"       ${ask[0]:,.2f} × {ask[1]:.4f}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\nSymbol '{symbol}' not found. Try:")
        print("  - Check spelling (e.g., 'XAU' for gold, 'BTC' for bitcoin)")
        print("  - Use search: python3 market_lookup.py --search {symbol}")

def list_categories():
    """Show available categories and examples"""
    
    print("\n" + "="*80)
    print("  LIGHTER DEX MARKET CATEGORIES")
    print("="*80 + "\n")
    
    categories = {
        "crypto": [
            "BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LINK", 
            "MATIC", "DOT", "UNI", "ATOM", "LTC", "BCH", "NEAR", "APT",
            "ARB", "OP", "INJ", "TAO", "SUI", "SEI", "TIA", "WIF", "PEPE", "BONK"
        ],
        "stocks": [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B",
            "V", "JPM", "WMT", "JNJ", "PG", "MA", "HD", "DIS", "PYPL", "BAC",
            "ADBE", "CRM", "NFLX", "XOM", "KO", "PFE", "INTC", "CSCO"
        ],
        "forex": [
            "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD",
            "NZDUSD", "EURGBP", "EURJPY", "GBPJPY"
        ],
        "commodities": [
            "XAU (Gold)", "XAG (Silver)", "XPT (Platinum)", "XPD (Palladium)",
            "USOIL (Crude Oil)", "UKOIL (Brent Oil)", "NATGAS (Natural Gas)",
            "CORN", "WHEAT", "SOYBEAN", "SUGAR", "COFFEE", "COTTON"
        ]
    }
    
    for cat, examples in categories.items():
        print(f"\n📁 {cat.upper()}")
        print(f"   Command: python3 market_lookup.py --category {cat}")
        print(f"   Examples: {', '.join(examples[:10])}")
        if len(examples) > 10:
            print(f"             ... and {len(examples) - 10} more")
    
    print("\n" + "="*80)
    print("\n💡 Quick Start:")
    print("   python3 market_lookup.py --category crypto     # All crypto")
    print("   python3 market_lookup.py --search gold         # Find gold")
    print("   python3 market_lookup.py --search BTC          # Find Bitcoin")
    print("   python3 market_lookup.py --details XAU         # Gold market details")
    print()

def main():
    parser = argparse.ArgumentParser(description="Lighter DEX Market Lookup")
    parser.add_argument("--search", "-s", type=str, help="Search by symbol or name")
    parser.add_argument("--category", "-c", type=str, 
                       choices=["crypto", "stocks", "forex", "commodities"],
                       help="Filter by category")
    parser.add_argument("--details", "-d", type=str, help="Show details for specific symbol")
    parser.add_argument("--all", "-a", action="store_true", help="Show all results (no limit)")
    parser.add_argument("--categories", action="store_true", help="List all categories")
    
    args = parser.parse_args()
    
    if args.categories:
        list_categories()
    elif args.details:
        get_market_details(args.details)
    else:
        search_markets(
            query=args.search,
            category=args.category,
            show_all=args.all
        )

if __name__ == "__main__":
    main()
