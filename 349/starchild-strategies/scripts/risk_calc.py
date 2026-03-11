#!/usr/bin/env python3
"""
Capital requirements and fee analysis for Starchild trading strategies.
"""

import json
import sys
from pathlib import Path

def calculate_trading_fees(strategy_id, volume_per_month, leverage=1):
    """Calculate expected trading fees based on strategy characteristics."""
    
    # Fee structures (maker/taker in bps)
    hyperliquid_fees = {"maker": 2, "taker": 5}
    orderly_fees = {"maker": 2, "taker": 5}
    
    # Strategy-specific trading frequency (trades per month)
    trading_frequency = {
        "rsi-reversal": 8,       # ~2 trades per week
        "zscore-reversion": 6,   # Less frequent, higher conviction
        "convergence-trade": 4,  # Monthly rebalancing
        "rsi-rotation": 2,       # Monthly rotation
        "volatility-breakout": 12, # More active
        "gap-continuation": 20,  # Intraday, high frequency
        "grid-bot": 60,         # Very high frequency
        "funding-arb": 8,       # Weekly rebalancing
        "overnight-drift": 22   # Daily entries
    }
    
    trades_per_month = trading_frequency.get(strategy_id, 10)
    
    # Assume 70% maker, 30% taker execution
    avg_fee_bps = (hyperliquid_fees["maker"] * 0.7 + hyperliquid_fees["taker"] * 0.3)
    
    monthly_fee_cost = volume_per_month * (avg_fee_bps / 10000)
    annual_fee_cost = monthly_fee_cost * 12
    
    return {
        "trades_per_month": trades_per_month,
        "avg_fee_bps": avg_fee_bps,
        "monthly_volume": volume_per_month,
        "monthly_fee_cost": monthly_fee_cost,
        "annual_fee_cost": annual_fee_cost,
        "break_even_return_monthly": (monthly_fee_cost / volume_per_month) * 100
    }

def calculate_funding_costs(strategy_id, notional_exposure, avg_funding_rate=0.01):
    """Calculate expected funding rate costs."""
    
    # Strategies that pay funding (net long bias)
    long_bias_strategies = ["rsi-reversal", "volatility-breakout", "gap-continuation", "overnight-drift"]
    
    # Market neutral strategies pay minimal funding
    neutral_strategies = ["grid-bot", "funding-arb", "convergence-trade", "zscore-reversion"]
    
    if strategy_id in neutral_strategies:
        net_funding_cost = 0  # Balanced or captures funding
    elif strategy_id in long_bias_strategies:
        net_funding_cost = notional_exposure * avg_funding_rate / 365  # Daily cost
    else:
        net_funding_cost = notional_exposure * (avg_funding_rate * 0.5) / 365  # Mixed exposure
    
    return {
        "daily_funding_cost": net_funding_cost,
        "monthly_funding_cost": net_funding_cost * 30,
        "annual_funding_cost": net_funding_cost * 365,
        "funding_drag_pct_annual": (net_funding_cost * 365 / notional_exposure) * 100
    }

def kelly_criterion(win_rate, avg_win, avg_loss):
    """Calculate optimal position size using Kelly criterion."""
    if avg_loss == 0:
        return 0
    
    win_prob = win_rate / 100
    lose_prob = 1 - win_prob
    win_loss_ratio = avg_win / abs(avg_loss)
    
    kelly_pct = (win_prob * win_loss_ratio - lose_prob) / win_loss_ratio
    
    # Apply 25% Kelly for practical risk management
    recommended_pct = max(0, kelly_pct * 0.25)
    
    return {
        "kelly_full": kelly_pct * 100,
        "kelly_quarter": recommended_pct * 100,
        "win_loss_ratio": win_loss_ratio
    }

def risk_metrics(capital, position_size_pct, max_positions, leverage, stop_loss_pct):
    """Calculate comprehensive risk metrics."""
    
    position_size = capital * (position_size_pct / 100)
    total_exposure = position_size * max_positions * leverage
    
    # Max single position loss (stop loss trigger)
    max_single_loss = position_size * leverage * (stop_loss_pct / 100)
    
    # Max portfolio loss (all positions hit stop losses)
    max_portfolio_loss = max_single_loss * max_positions
    
    # Portfolio heat (% of capital at risk)
    portfolio_heat = (max_portfolio_loss / capital) * 100
    
    return {
        "position_size": position_size,
        "total_exposure": total_exposure,
        "leverage_ratio": total_exposure / capital,
        "max_single_loss": max_single_loss,
        "max_portfolio_loss": max_portfolio_loss,
        "portfolio_heat": portfolio_heat,
        "positions_to_ruin": capital / max_single_loss if max_single_loss > 0 else float('inf')
    }

def comprehensive_analysis(strategy_id, capital, leverage=1):
    """Comprehensive risk and cost analysis."""
    
    # Load strategy defaults
    defaults = {
        "position_size_pct": 10,
        "max_positions": 8,
        "stop_loss_pct": 5,
        "leverage": leverage
    }
    
    # Calculate monthly volume (assumes full position turnover)
    monthly_volume = capital * (defaults["position_size_pct"] / 100) * defaults["max_positions"] * leverage * 2
    
    # Risk analysis
    risk = risk_metrics(
        capital=capital,
        position_size_pct=defaults["position_size_pct"],
        max_positions=defaults["max_positions"],
        leverage=leverage,
        stop_loss_pct=defaults["stop_loss_pct"]
    )
    
    # Cost analysis
    fees = calculate_trading_fees(strategy_id, monthly_volume, leverage)
    funding = calculate_funding_costs(strategy_id, risk["total_exposure"])
    
    # Kelly analysis (using historical estimates)
    historical_stats = {
        "rsi-reversal": {"win_rate": 65, "avg_win": 3.2, "avg_loss": -2.1},
        "grid-bot": {"win_rate": 85, "avg_win": 0.8, "avg_loss": -3.5},
        "funding-arb": {"win_rate": 90, "avg_win": 1.2, "avg_loss": -0.8}
    }
    
    stats = historical_stats.get(strategy_id, {"win_rate": 60, "avg_win": 2.5, "avg_loss": -2.0})
    kelly = kelly_criterion(stats["win_rate"], stats["avg_win"], stats["avg_loss"])
    
    return {
        "strategy_id": strategy_id,
        "capital": capital,
        "risk_metrics": risk,
        "cost_analysis": {
            "trading_fees": fees,
            "funding_costs": funding,
            "total_monthly_cost": fees["monthly_fee_cost"] + funding["monthly_funding_cost"]
        },
        "kelly_sizing": kelly,
        "recommendations": {
            "suggested_position_size": min(defaults["position_size_pct"], kelly["kelly_quarter"]),
            "risk_warnings": []
        }
    }

def main():
    if len(sys.argv) < 3:
        print("Usage: python risk_calc.py <strategy-id> <capital> [leverage]")
        print("\nExamples:")
        print("  python risk_calc.py rsi-reversal 10000")
        print("  python risk_calc.py grid-bot 5000 2")
        sys.exit(1)
    
    strategy_id = sys.argv[1]
    capital = float(sys.argv[2])
    leverage = float(sys.argv[3]) if len(sys.argv) > 3 else 1
    
    analysis = comprehensive_analysis(strategy_id, capital, leverage)
    
    print(f"\n🎯 Risk Analysis: {strategy_id}")
    print(f"💰 Capital: ${capital:,.0f}")
    print(f"📊 Leverage: {leverage}x")
    print()
    
    risk = analysis["risk_metrics"]
    print(f"🎲 Risk Metrics:")
    print(f"  • Position size: ${risk['position_size']:,.0f}")
    print(f"  • Total exposure: ${risk['total_exposure']:,.0f}")
    print(f"  • Portfolio heat: {risk['portfolio_heat']:.1f}%")
    print(f"  • Max single loss: ${risk['max_single_loss']:,.0f}")
    print(f"  • Positions to ruin: {risk['positions_to_ruin']:.0f}")
    print()
    
    costs = analysis["cost_analysis"]
    print(f"💸 Monthly Costs:")
    print(f"  • Trading fees: ${costs['trading_fees']['monthly_fee_cost']:,.0f}")
    print(f"  • Funding costs: ${costs['funding_costs']['monthly_funding_cost']:,.0f}")
    print(f"  • Total: ${costs['total_monthly_cost']:,.0f}")
    print(f"  • Break-even return: {costs['trading_fees']['break_even_return_monthly']:.2f}%")
    print()
    
    kelly = analysis["kelly_sizing"]
    print(f"📏 Kelly Sizing:")
    print(f"  • Full Kelly: {kelly['kelly_full']:.1f}%")
    print(f"  • Conservative (1/4): {kelly['kelly_quarter']:.1f}%")
    print(f"  • Win/Loss ratio: {kelly['win_loss_ratio']:.2f}")

if __name__ == "__main__":
    main()