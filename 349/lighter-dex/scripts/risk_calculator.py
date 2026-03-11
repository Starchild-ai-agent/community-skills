#!/usr/bin/env python3
"""
Risk Calculator for Lighter DEX
Calculate liquidation price, position risk, and recommended stop losses
"""

import argparse
import sys

def calculate_liquidation_price(entry_price, side, leverage, balance=None, position_size=None):
    """
    Calculate liquidation price for a perpetual position
    
    Args:
        entry_price: Entry price
        side: "long" or "short"
        leverage: Leverage multiplier (e.g., 10 for 10x)
        balance: Account balance in USDC (optional, for more accurate calc)
        position_size: Position size in base asset (optional)
    
    Returns:
        Liquidation price
    """
    
    # Simplified liquidation calculation (Lighter uses isolated margin by default)
    # Liquidation occurs when: Loss = Initial Margin - Maintenance Margin
    # Assuming maintenance margin is ~0.5% of position
    
    initial_margin_pct = 1.0 / leverage
    maintenance_margin_pct = 0.005  # 0.5% maintenance margin (typical)
    
    if side.lower() == "long":
        # Long: Liquidation when price drops
        # Liq Price = Entry × (1 - Initial Margin + Maintenance Margin)
        liq_price = entry_price * (1 - initial_margin_pct + maintenance_margin_pct)
    else:  # short
        # Short: Liquidation when price rises
        # Liq Price = Entry × (1 + Initial Margin - Maintenance Margin)
        liq_price = entry_price * (1 + initial_margin_pct - maintenance_margin_pct)
    
    return liq_price

def calculate_position_risk(entry_price, current_price, side, leverage, position_size):
    """
    Calculate current position risk metrics
    
    Returns:
        Dictionary with PnL, ROE, distance to liquidation
    """
    
    if side.lower() == "long":
        pnl_pct = (current_price - entry_price) / entry_price * 100
        price_to_liq = current_price - calculate_liquidation_price(entry_price, "long", leverage)
    else:  # short
        pnl_pct = (entry_price - current_price) / entry_price * 100
        price_to_liq = calculate_liquidation_price(entry_price, "short", leverage) - current_price
    
    # ROE = PnL % × Leverage
    roe = pnl_pct * leverage
    
    # Distance to liquidation as percentage
    liq_price = calculate_liquidation_price(entry_price, side, leverage)
    dist_to_liq_pct = abs(current_price - liq_price) / current_price * 100
    
    return {
        "pnl_percent": pnl_pct,
        "roe": roe,
        "liquidation_price": liq_price,
        "price_to_liquidation": price_to_liq,
        "distance_to_liquidation_pct": dist_to_liq_pct
    }

def recommend_stop_loss(entry_price, side, leverage, risk_reward=2.0):
    """
    Recommend stop loss price based on leverage and risk/reward ratio
    
    Args:
        entry_price: Entry price
        side: "long" or "short"
        leverage: Current leverage
        risk_reward: Target risk/reward ratio (default 2.0)
    
    Returns:
        Recommended stop loss price
    """
    
    # Conservative: Stop loss at 50% of liquidation distance
    liq_price = calculate_liquidation_price(entry_price, side, leverage)
    
    if side.lower() == "long":
        liq_distance = entry_price - liq_price
        sl_distance = liq_distance * 0.5  # Stop at 50% of liq distance
        sl_price = entry_price - sl_distance
    else:  # short
        liq_distance = liq_price - entry_price
        sl_distance = liq_distance * 0.5
        sl_price = entry_price + sl_distance
    
    return sl_price

def format_currency(value, symbol="$"):
    """Format as currency"""
    if value >= 1000:
        return f"{symbol}{value:,.2f}"
    else:
        return f"{symbol}{value:.4f}"

def print_risk_analysis(entry_price, side, leverage, current_price=None):
    """Print comprehensive risk analysis"""
    
    liq_price = calculate_liquidation_price(entry_price, side, leverage)
    sl_recommended = recommend_stop_loss(entry_price, side, leverage)
    
    print("\n" + "="*70)
    print(f"  RISK ANALYSIS: {side.upper()} {format_currency(entry_price)} @ {leverage}x")
    print("="*70 + "\n")
    
    # Position metrics
    print("📊 Position Metrics:")
    print(f"   Entry Price:       {format_currency(entry_price)}")
    print(f"   Side:              {side.upper()}")
    print(f"   Leverage:          {leverage}x")
    print(f"   Initial Margin:    {100/leverage:.1f}% of position")
    
    # Liquidation
    print(f"\n⚠️  Liquidation:")
    print(f"   Liquidation Price: {format_currency(liq_price)}")
    
    if side.lower() == "long":
        liq_distance_pct = (entry_price - liq_price) / entry_price * 100
        print(f"   Distance:          {format_currency(liq_distance_pct)}% below entry")
    else:
        liq_distance_pct = (liq_price - entry_price) / entry_price * 100
        print(f"   Distance:          {format_currency(liq_distance_pct)}% above entry")
    
    # Stop loss recommendation
    print(f"\n🛑 Stop Loss Recommendation:")
    print(f"   Recommended SL:    {format_currency(sl_recommended)}")
    
    if side.lower() == "long":
        sl_risk_pct = (entry_price - sl_recommended) / entry_price * 100
    else:
        sl_risk_pct = (sl_recommended - entry_price) / entry_price * 100
    
    print(f"   Risk:              {sl_risk_pct:.2f}% of entry")
    print(f"   Safety Buffer:     {(liq_distance_pct - sl_risk_pct):.2f}% to liquidation")
    
    # Current price analysis (if provided)
    if current_price:
        print(f"\n📈 Current Market: {format_currency(current_price)}")
        
        risk = calculate_position_risk(entry_price, current_price, side, leverage, 1.0)
        
        print(f"\n   PnL:               {risk['pnl_percent']:+.2f}%")
        print(f"   ROE:               {risk['roe']:+.2f}%")
        print(f"   Distance to Liq:   {risk['distance_to_liquidation_pct']:.2f}%")
        
        # Risk assessment
        print(f"\n🎯 Risk Assessment:")
        if risk['distance_to_liquidation_pct'] > 50:
            print("   ✅ LOW RISK - Comfortable distance to liquidation")
        elif risk['distance_to_liquidation_pct'] > 20:
            print("   ⚠️  MEDIUM RISK - Monitor closely")
        else:
            print("   ❌ HIGH RISK - Consider reducing position or adding margin")
    
    # Leverage recommendation
    print(f"\n💡 Leverage Recommendation:")
    if leverage > 20:
        print("   ⚠️  VERY HIGH - Consider reducing to 5-10x for crypto")
    elif leverage > 10:
        print("   ⚠️  HIGH - Consider reducing to 5-8x for safer trading")
    elif leverage > 5:
        print("   ✅ MODERATE - Reasonable for experienced traders")
    else:
        print("   ✅ CONSERVATIVE - Good for beginners or volatile markets")
    
    print("\n" + "="*70)
    
    # Trading example
    print("\n📚 Example Trade Setup:")
    print(f"   Entry:    {format_currency(entry_price)}")
    
    if side.lower() == "long":
        tp_price = entry_price * (1 + sl_risk_pct/100 * 2)  # 2:1 R/R
        print(f"   Stop:     {format_currency(sl_recommended)} (-{sl_risk_pct:.2f}%)")
        print(f"   Target:   {format_currency(tp_price)} (+{sl_risk_pct*2:.2f}%)")
        print(f"   R/R:      1:2 (Risk $1 to make $2)")
    else:
        tp_price = entry_price * (1 - sl_risk_pct/100 * 2)
        print(f"   Stop:     {format_currency(sl_recommended)} (+{sl_risk_pct:.2f}%)")
        print(f"   Target:   {format_currency(tp_price)} (-{sl_risk_pct*2:.2f}%)")
        print(f"   R/R:      1:2 (Risk $1 to make $2)")
    
    print()

def main():
    parser = argparse.ArgumentParser(description="Lighter DEX Risk Calculator")
    parser.add_argument("symbol", nargs="?", help="Symbol (e.g., BTC, XAU)")
    parser.add_argument("side", nargs="?", choices=["long", "short"], help="Position side")
    parser.add_argument("entry", nargs="?", type=float, help="Entry price")
    parser.add_argument("leverage", nargs="?", type=int, help="Leverage (1-100)")
    parser.add_argument("--current", "-c", type=float, help="Current price (for PnL calc)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive or not all([args.symbol, args.side, args.entry, args.leverage]):
        # Interactive mode
        print("\n" + "="*70)
        print("  LIGHTER DEX RISK CALCULATOR")
        print("="*70 + "\n")
        
        symbol = input("Symbol (e.g., BTC, XAU, AAPL): ").strip().upper()
        side = input("Side (long/short): ").strip().lower()
        entry = float(input("Entry price: ").strip())
        leverage = int(input("Leverage (1-100): ").strip())
        
        current = None
        current_input = input("Current price (optional, press Enter to skip): ").strip()
        if current_input:
            current = float(current_input)
        
        print_risk_analysis(entry, side, leverage, current)
        
    else:
        # Command line mode
        print_risk_analysis(args.entry, args.side, args.leverage, args.current)

if __name__ == "__main__":
    main()
