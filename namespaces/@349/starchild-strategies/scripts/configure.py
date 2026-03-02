#!/usr/bin/env python3
"""
Interactive strategy configurator for Starchild trading strategies.
"""

import json
import os
import sys
from pathlib import Path

def load_catalog():
    """Load the strategy catalog."""
    catalog_path = Path(__file__).parent.parent / "catalog.json"
    with open(catalog_path) as f:
        return json.load(f)

def load_strategy_template(strategy_id):
    """Load strategy template from assets directory."""
    template_path = Path(__file__).parent.parent / "assets" / f"{strategy_id}.json"
    if template_path.exists():
        with open(template_path) as f:
            return json.load(f)
    else:
        # Return basic template if file doesn't exist
        return {
            "strategy_id": strategy_id,
            "name": strategy_id.replace("-", " ").title(),
            "parameters": {},
            "risk_management": {
                "stop_loss_pct": 5,
                "take_profit_pct": 25,
                "max_drawdown_pct": 10,
                "daily_loss_limit_pct": 2
            }
        }

def calculate_requirements(strategy_id, capital, leverage=1):
    """Calculate capital requirements and risk metrics."""
    min_requirements = {
        "rsi-reversal": 500, "zscore-reversion": 1000, "convergence-trade": 2000,
        "rsi-rotation": 3000, "volatility-breakout": 1000, "gap-continuation": 500,
        "grid-bot": 1500, "funding-arb": 5000, "overnight-drift": 1000
    }
    
    min_capital = min_requirements.get(strategy_id, 1000)
    position_size = capital * 0.10  # Default 10% per position
    max_positions = min(8, capital // (min_capital // 10))
    
    return {
        "min_capital_required": min_capital,
        "suggested_position_size": position_size,
        "max_positions": max_positions,
        "total_exposure": position_size * max_positions * leverage,
        "risk_ratio": (position_size * max_positions * leverage) / capital
    }

def configure_strategy(strategy_id, capital=None, interactive=True):
    """Interactive configuration for a trading strategy."""
    catalog = load_catalog()
    
    # Find strategy in catalog
    strategy_info = None
    for category in catalog["tree"].values():
        for strategy in category["strategies"]:
            if strategy["id"] == strategy_id:
                strategy_info = strategy
                break
        if strategy_info:
            break
    
    if not strategy_info:
        print(f"❌ Strategy '{strategy_id}' not found in catalog")
        return None
    
    print(f"🎯 Configuring: {strategy_info['name']}")
    print(f"📝 Summary: {strategy_info['summary']}")
    print(f"📊 Complexity: {strategy_info['complexity']}")
    print(f"💰 Min Capital: ${strategy_info['min_capital']:,}")
    print()
    
    # Load template
    config = load_strategy_template(strategy_id)
    
    # Get capital input
    if capital is None and interactive:
        capital = float(input(f"💵 Trading capital (min ${strategy_info['min_capital']:,}): $"))
    elif capital is None:
        capital = strategy_info['min_capital']
    
    # Calculate requirements
    requirements = calculate_requirements(strategy_id, capital)
    
    print(f"\n📈 Capital Analysis:")
    print(f"  • Position size: ${requirements['suggested_position_size']:.0f}")
    print(f"  • Max positions: {requirements['max_positions']}")
    print(f"  • Total exposure: ${requirements['total_exposure']:.0f}")
    print(f"  • Risk ratio: {requirements['risk_ratio']:.1%}")
    
    if capital < requirements['min_capital_required']:
        print(f"⚠️  Warning: Capital below minimum (${requirements['min_capital_required']:,})")
    
    # Update config with calculated values
    config.update({
        "capital": capital,
        "position_size_usd": requirements['suggested_position_size'],
        "max_positions": requirements['max_positions'],
        "requirements": requirements
    })
    
    return config

def main():
    if len(sys.argv) != 2:
        print("Usage: python configure.py <strategy-id>")
        print("\nAvailable strategies:")
        catalog = load_catalog()
        for category_name, category in catalog["tree"].items():
            print(f"\n{category['label']}:")
            for strategy in category["strategies"]:
                print(f"  • {strategy['id']} ({strategy['complexity']})")
        sys.exit(1)
    
    strategy_id = sys.argv[1]
    config = configure_strategy(strategy_id)
    
    if config:
        output_file = f"{strategy_id}-config.json"
        with open(output_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"\n✅ Configuration saved to {output_file}")

if __name__ == "__main__":
    main()