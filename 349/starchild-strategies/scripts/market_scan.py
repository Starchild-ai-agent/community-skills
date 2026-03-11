#!/usr/bin/env python3
"""
Market regime assessment to help select appropriate trading strategies.
"""

import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def get_market_data(symbol="bitcoin", days=30):
    """Fetch market data from CoinGecko."""
    url = f"https://api.coingecko.com/api/v3/coins/{symbol}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        prices = data["prices"]
        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def calculate_volatility(prices, window=14):
    """Calculate rolling volatility."""
    returns = prices.pct_change()
    volatility = returns.rolling(window=window).std() * np.sqrt(365) * 100
    return volatility

def detect_trend_strength(prices, window=14):
    """Calculate ADX-like trend strength indicator."""
    high = prices.rolling(window=3).max()
    low = prices.rolling(window=3).min()
    
    # Simplified directional movement
    dm_plus = np.where(high.diff() > low.diff().abs(), high.diff(), 0)
    dm_minus = np.where(low.diff().abs() > high.diff(), low.diff().abs(), 0)
    
    # Smooth the directional movements
    dm_plus_smooth = pd.Series(dm_plus).rolling(window=window).mean()
    dm_minus_smooth = pd.Series(dm_minus).rolling(window=window).mean()
    
    # Calculate trend strength (simplified ADX)
    dx = abs(dm_plus_smooth - dm_minus_smooth) / (dm_plus_smooth + dm_minus_smooth + 1e-10)
    trend_strength = dx.rolling(window=window).mean() * 100
    
    return trend_strength

def analyze_market_regime(df):
    """Analyze current market regime."""
    prices = df["price"]
    
    # Current metrics
    current_price = prices.iloc[-1]
    price_30d_ago = prices.iloc[0] if len(prices) > 30 else prices.iloc[0]
    return_30d = (current_price / price_30d_ago - 1) * 100
    
    # Calculate indicators
    volatility = calculate_volatility(prices)
    trend_strength = detect_trend_strength(prices)
    
    current_vol = volatility.iloc[-1] if not pd.isna(volatility.iloc[-1]) else 50
    current_trend = trend_strength.iloc[-1] if not pd.isna(trend_strength.iloc[-1]) else 25
    
    # Price action analysis
    recent_high = prices.tail(7).max()
    recent_low = prices.tail(7).min()
    range_pct = (recent_high / recent_low - 1) * 100
    
    # Moving average analysis
    ma_20 = prices.rolling(20).mean().iloc[-1]
    ma_50 = prices.rolling(50).mean().iloc[-1] if len(prices) >= 50 else ma_20
    
    above_ma20 = current_price > ma_20
    ma_slope = (ma_20 / prices.rolling(20).mean().iloc[-5] - 1) * 100 if len(prices) >= 25 else 0
    
    return {
        "current_price": current_price,
        "return_30d": return_30d,
        "volatility": current_vol,
        "trend_strength": current_trend,
        "range_pct_7d": range_pct,
        "above_ma20": above_ma20,
        "ma_slope": ma_slope,
        "timestamp": df["timestamp"].iloc[-1]
    }

def recommend_strategies(regime_data):
    """Recommend strategies based on market regime."""
    vol = regime_data["volatility"]
    trend = regime_data["trend_strength"]
    return_30d = regime_data["return_30d"]
    range_pct = regime_data["range_pct_7d"]
    
    recommendations = []
    
    # Trending market (high trend strength, directional move)
    if trend > 40 and abs(return_30d) > 15:
        if return_30d > 0:
            recommendations.extend([
                {"category": "momentum", "strategy": "volatility-breakout", "confidence": 85},
                {"category": "momentum", "strategy": "gap-continuation", "confidence": 70}
            ])
        else:
            recommendations.extend([
                {"category": "mean-reversion", "strategy": "rsi-reversal", "confidence": 75},
                {"category": "momentum", "strategy": "volatility-breakout", "confidence": 60}
            ])
    
    # Choppy market (low trend strength, sideways)
    elif trend < 25 and abs(return_30d) < 10:
        recommendations.extend([
            {"category": "mean-reversion", "strategy": "rsi-reversal", "confidence": 90},
            {"category": "market-neutral", "strategy": "grid-bot", "confidence": 85},
            {"category": "mean-reversion", "strategy": "zscore-reversion", "confidence": 70}
        ])
    
    # High volatility environment
    if vol > 80:
        recommendations.extend([
            {"category": "momentum", "strategy": "volatility-breakout", "confidence": 80},
            {"category": "market-neutral", "strategy": "funding-arb", "confidence": 75}
        ])
    
    # Low volatility (compression)
    elif vol < 40:
        recommendations.extend([
            {"category": "market-neutral", "strategy": "overnight-drift", "confidence": 80},
            {"category": "market-neutral", "strategy": "grid-bot", "confidence": 85}
        ])
    
    # Always suitable strategies
    recommendations.extend([
        {"category": "market-neutral", "strategy": "funding-arb", "confidence": 60},
        {"category": "market-neutral", "strategy": "overnight-drift", "confidence": 65}
    ])
    
    # Sort by confidence and remove duplicates
    seen = set()
    unique_recs = []
    for rec in sorted(recommendations, key=lambda x: x["confidence"], reverse=True):
        key = (rec["category"], rec["strategy"])
        if key not in seen:
            seen.add(key)
            unique_recs.append(rec)
    
    return unique_recs[:5]  # Top 5 recommendations

def market_summary(regime_data):
    """Generate human-readable market summary."""
    vol = regime_data["volatility"]
    trend = regime_data["trend_strength"]
    return_30d = regime_data["return_30d"]
    
    # Volatility assessment
    if vol > 80:
        vol_desc = "high volatility"
    elif vol < 40:
        vol_desc = "low volatility"
    else:
        vol_desc = "normal volatility"
    
    # Trend assessment
    if trend > 40:
        trend_desc = "strong trend"
    elif trend < 25:
        trend_desc = "sideways/choppy"
    else:
        trend_desc = "weak trend"
    
    # Direction assessment
    if return_30d > 15:
        direction = "strong uptrend"
    elif return_30d < -15:
        direction = "strong downtrend"
    elif return_30d > 5:
        direction = "mild uptrend"
    elif return_30d < -5:
        direction = "mild downtrend"
    else:
        direction = "sideways"
    
    return f"{direction}, {trend_desc}, {vol_desc}"

def main():
    print("🔍 Scanning market conditions...")
    
    # Fetch BTC data as proxy for overall crypto market
    df = get_market_data("bitcoin", 60)
    
    if df is None:
        print("❌ Failed to fetch market data")
        return
    
    regime = analyze_market_regime(df)
    summary = market_summary(regime)
    recommendations = recommend_strategies(regime)
    
    print(f"\n📊 Market Analysis (BTC as proxy)")
    print(f"⏰ As of: {regime['timestamp'].strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"💰 Current price: ${regime['current_price']:,.0f}")
    print(f"📈 30d return: {regime['return_30d']:.1f}%")
    print(f"📊 Volatility: {regime['volatility']:.1f}%")
    print(f"🎯 Trend strength: {regime['trend_strength']:.1f}")
    print()
    
    print(f"🏷️  Market Regime: {summary}")
    print()
    
    print("🎯 Strategy Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec['strategy']} ({rec['category']}) - {rec['confidence']}% confidence")
    
    print(f"\n💡 Use 'python configure.py <strategy-id>' to set up a specific strategy")

if __name__ == "__main__":
    main()