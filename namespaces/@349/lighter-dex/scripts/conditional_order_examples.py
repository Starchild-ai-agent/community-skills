#!/usr/bin/env python3
"""
Conditional Orders Examples
Demonstrates all order types available on Lighter DEX
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools import (
    lighter_order, lighter_stop_loss, lighter_stop_limit,
    lighter_take_profit, lighter_take_profit_limit, lighter_twap_order,
    lighter_open_orders, lighter_cancel, lighter_account, lighter_positions,
    lighter_orderbook, lighter_market
)

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def example_basic_orders():
    """Basic limit and market orders"""
    print_section("1. BASIC ORDERS")
    
    # Check account first
    account = lighter_account()
    print(f"Account Balance: ${account['available_balance']:.2f}")
    
    # Example: Limit order (DOESN'T EXECUTE - just shows syntax)
    print("\n📌 Limit Order Example:")
    print("""
lighter_order(
    symbol="BTC",
    side="buy",
    size=0.01,
    order_type="LIMIT",
    price=94000  # Buy if BTC drops to $94k
)
    """)
    
    # Example: Market order (DOESN'T EXECUTE)
    print("\n📌 Market Order Example:")
    print("""
lighter_order(
    symbol="ETH",
    side="sell",
    size=0.5,
    order_type="MARKET"  # Sell immediately at best price
)
    """)

def example_stop_losses():
    """Stop loss examples"""
    print_section("2. STOP LOSS ORDERS")
    
    print("\n🛑 Stop Loss (Market) - Guaranteed Fill")
    print("""
Scenario: Long 0.1 BTC at $95,000, want to limit loss to 5%

lighter_stop_loss(
    symbol="BTC",
    side="sell",           # Sell to close long
    size=0.1,
    trigger_price=90250,   # Trigger at -5%
    reduce_only=True
)

✅ Pros: Guaranteed to fill even in crash
⚠️  Cons: May fill below trigger price (slippage)
    """)
    
    print("\n🛑 Stop Loss (Limit) - Price Control")
    print("""
Scenario: Long 0.1 BTC at $95,000, want controlled exit

lighter_stop_limit(
    symbol="BTC",
    side="sell",
    size=0.1,
    trigger_price=90250,   # Trigger at -5%
    limit_price=90000,     # Sell at $90k or better
    reduce_only=True
)

✅ Pros: Won't sell below $90k
⚠️  Cons: May not fill if price gaps down
    """)
    
    print("\n💡 When to use each:")
    print("   - STOP (market): High leverage, emergency exits, volatile markets")
    print("   - STOP_LIMIT:   Lower leverage, controlled exits, stable markets")

def example_take_profits():
    """Take profit examples"""
    print_section("3. TAKE PROFIT ORDERS")
    
    print("\n🎯 Take Profit (Market) - Guaranteed Exit")
    print("""
Scenario: Long 0.1 BTC at $95,000, target $100,000

lighter_take_profit(
    symbol="BTC",
    side="sell",
    size=0.1,
    trigger_price=100000,  # Trigger when BTC hits $100k
    reduce_only=True
)

✅ Pros: Guaranteed to take profit
⚠️  Cons: May fill slightly below target
    """)
    
    print("\n🎯 Take Profit (Limit) - Price Target")
    print("""
Scenario: Long 0.1 BTC at $95,000, want minimum $100k

lighter_take_profit_limit(
    symbol="BTC",
    side="sell",
    size=0.1,
    trigger_price=100000,  # Trigger at $100k
    limit_price=100500,    # Sell at $100.5k or better
    reduce_only=True
)

✅ Pros: Controls minimum exit price
⚠️  Cons: May miss move if price spikes and reverses
    """)

def example_bracket_order():
    """Bracket order (entry + SL + TP)"""
    print_section("4. BRACKET ORDER (Entry + SL + TP)")
    
    print("\n📊 Complete Bracket Setup:")
    print("""
Step 1: Enter Position
lighter_order(
    symbol="BTC",
    side="buy",
    size=0.1,
    order_type="MARKET"
)

Step 2: Set Stop Loss (-5%)
lighter_stop_loss(
    symbol="BTC",
    side="sell",
    size=0.1,
    trigger_price=90250,
    reduce_only=True
)

Step 3: Set Take Profit (+10%)
lighter_take_profit(
    symbol="BTC",
    side="sell",
    size=0.1,
    trigger_price=104500,
    reduce_only=True
)

⚠️  IMPORTANT: Lighter doesn't have OCO (One-Cancels-Other)
    When one order fills, manually cancel the other:
    
    orders = lighter_open_orders(symbol="BTC")
    lighter_cancel(symbol="BTC", order_id=REMAINING_ORDER_ID)
    """)

def example_twap():
    """TWAP order examples"""
    print_section("5. TWAP ORDERS (Time-Weighted Average Price)")
    
    print("\n⏱️  TWAP Example: Accumulate 1 BTC over 4 hours")
    print("""
lighter_twap_order(
    symbol="BTC",
    side="buy",
    total_amount=1.0,
    duration_seconds=14400,   # 4 hours
    slice_interval=60         # Execute slice every 60 seconds
)

How it works:
- Total: 1.0 BTC over 4 hours
- Slices: 14400 / 60 = 240 slices
- Per slice: 1.0 / 240 = 0.00417 BTC every minute
- Execution: Market orders at each interval

✅ Pros: Reduces slippage, doesn't move market
⚠️  Cons: Takes time, average price uncertain
    """)
    
    print("\n📦 Large Order Example: Exit 50 ETH over 8 hours")
    print("""
lighter_twap_order(
    symbol="ETH",
    side="sell",
    total_amount=50.0,
    duration_seconds=28800,   # 8 hours
    slice_interval=120        # Every 2 minutes
)

Use TWAP for:
- Orders >1% of daily volume
- Illiquid markets
- Building/reducing large positions
    """)

def example_time_in_force():
    """Time-in-force options"""
    print_section("6. TIME-IN-FORCE OPTIONS")
    
    print("\n⏰ GTC (Good 'Til Cancelled) - Default")
    print("""
lighter_order(
    symbol="BTC",
    side="buy",
    size=0.1,
    order_type="LIMIT",
    price=94000,
    time_in_force="GTC"  # Stays until filled or cancelled
)
    """)
    
    print("\n⏰ GTT (Good 'Til Time) - Expires")
    print("""
lighter_order(
    symbol="BTC",
    side="buy",
    size=0.1,
    order_type="LIMIT",
    price=94000,
    time_in_force="GTT",
    expiry_time="2024-12-31T23:59:59Z"  # ISO 8601 format
)

Use for: Day trades, don't leave orders overnight
    """)
    
    print("\n⏰ IOC (Immediate or Cancel)")
    print("""
lighter_order(
    symbol="BTC",
    side="buy",
    size=1.0,
    order_type="LIMIT",
    price=95000,
    time_in_force="IOC"  # Fill what's available, cancel rest
)

Use for: Testing liquidity, quick partial fills
    """)
    
    print("\n⏰ POST_ONLY (Maker Only)")
    print("""
lighter_order(
    symbol="BTC",
    side="buy",
    size=0.1,
    order_type="LIMIT",
    price=94500,
    time_in_force="POST_ONLY"  # Rejects if would immediately fill
)

Use for: Market making, earning maker rebates
    """)

def example_risk_management():
    """Risk management workflow"""
    print_section("7. RISK MANAGEMENT WORKFLOW")
    
    print("\n⚠️  Step 1: Check Liquidation Risk")
    print("""
lighter_liquidation()

Output:
[
  {
    "symbol": "BTC",
    "side": "LONG",
    "leverage": 10,
    "entry_price": 95000,
    "liquidation_price": 86350,
    "distance_to_liquidation": "10.52%"
  }
]

Rule: Distance to liq should be > 2x your stop loss
    """)
    
    print("\n📊 Step 2: Set Conservative Leverage")
    print("""
lighter_leverage(symbol="BTC", leverage=5)

Recommended Max Leverage:
- Major Crypto (BTC, ETH): 5-10x
- Altcoins:               3-5x
- Stocks (AAPL, NVDA):    10-20x
- Forex (EURUSD):         20-50x
- Commodities (Gold):     10-20x
    """)
    
    print("\n🎯 Step 3: Place Order with Stop Loss")
    print("""
# Always set stop loss BEFORE or immediately after entry
lighter_order(
    symbol="BTC",
    side="buy",
    size=0.1,
    order_type="MARKET"
)

lighter_stop_limit(
    symbol="BTC",
    side="sell",
    size=0.1,
    trigger_price=90000,
    limit_price=89500,
    reduce_only=True
)
    """)
    
    print("\n📈 Step 4: Monitor Position")
    print("""
lighter_positions()      # Check PnL
lighter_liquidation()    # Verify liquidation price
lighter_open_orders()    # Check active SL/TP
    """)

def example_real_strategies():
    """Real trading strategies"""
    print_section("8. REAL TRADING STRATEGIES")
    
    print("\n📈 Strategy 1: Swing Trade")
    print("""
Setup: BTC at $95k, support $93k, resistance $100k

Entry (limit at support):
lighter_order(
    symbol="BTC", side="buy", size=0.5,
    order_type="LIMIT", price=93000
)

Stop loss (5% below entry):
lighter_stop_limit(
    symbol="BTC", side="sell", size=0.5,
    trigger_price=88350, limit_price=88000,
    reduce_only=True
)

Take profit (7.5% above):
lighter_take_profit_limit(
    symbol="BTC", side="sell", size=0.5,
    trigger_price=100000, limit_price=100500,
    reduce_only=True
)

Risk/Reward: 1:1.5
    """)
    
    print("\n⚡ Strategy 2: Scalping")
    print("""
Setup: ETH ranging $3400-3450, quick momentum

Entry (market for speed):
lighter_order(
    symbol="ETH", side="buy", size=5.0,
    order_type="MARKET"
)

Tight stop (1% below):
lighter_stop_loss(
    symbol="ETH", side="sell", size=5.0,
    trigger_price=3366, reduce_only=True
)

Quick target (1.5% above):
lighter_take_profit(
    symbol="ETH", side="sell", size=5.0,
    trigger_price=3451, reduce_only=True
)

Risk/Reward: 1:1.5
Note: Requires tight spreads, low fees
    """)
    
    print("\n📦 Strategy 3: Accumulation")
    print("""
Goal: Accumulate 10 BTC over 3 days

TWAP order:
lighter_twap_order(
    symbol="BTC",
    side="buy",
    total_amount=10.0,
    duration_seconds=259200,  # 72 hours
    slice_interval=300        # Every 5 minutes
)

After completion, set stop loss at -10% from average entry
    """)

def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("  LIGHTER DEX CONDITIONAL ORDERS EXAMPLES")
    print("="*60)
    
    try:
        # Show account info (read-only)
        account = lighter_account()
        print(f"\n✅ Connected to Lighter DEX")
        print(f"   Address: {account['address'][:10]}...")
        print(f"   Balance: ${account['available_balance']:.2f}")
    except Exception as e:
        print(f"\n⚠️  Not connected: {e}")
        print("   Set LIGHTER_API_KEY in .env to execute orders\n")
    
    # Show all examples (none execute trades)
    example_basic_orders()
    example_stop_losses()
    example_take_profits()
    example_bracket_order()
    example_twap()
    example_time_in_force()
    example_risk_management()
    example_real_strategies()
    
    print("\n" + "="*60)
    print("  EXAMPLES COMPLETE")
    print("="*60)
    print("\n💡 To execute any example:")
    print("   1. Copy the code block")
    print("   2. Adjust parameters (symbol, size, prices)")
    print("   3. Run in Python or via agent command")
    print("   4. Always verify with lighter_open_orders() after placing")
    print("\n⚠️  Trading involves risk. Start small!")
    print()

if __name__ == "__main__":
    main()
