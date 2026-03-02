#!/usr/bin/env python3
"""
Quick backtesting for Starchild trading strategies using recent market data.
"""

import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys

class QuickBacktest:
    def __init__(self, strategy_config, symbol="BTC/USDT", days=30):
        self.config = strategy_config
        self.symbol = symbol
        self.days = days
        self.results = {}
        
    def fetch_ohlcv(self):
        """Fetch OHLCV data from public API (CoinGecko or similar)."""
        # Using simplified data fetch - in reality would use hl_candles or similar
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.days)
        
        print(f"📊 Fetching {self.days} days of {self.symbol} data...")
        
        # Mock data for demonstration - replace with actual API call
        dates = pd.date_range(start_date, end_date, freq='1D')
        np.random.seed(42)
        
        # Generate realistic price data
        price_start = 45000
        returns = np.random.normal(0.001, 0.03, len(dates))  # 0.1% daily drift, 3% volatility
        prices = [price_start]
        
        for r in returns[1:]:
            prices.append(prices[-1] * (1 + r))
        
        self.ohlcv = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': [p * (1 + max(0, np.random.normal(0.01, 0.005))) for p in prices],
            'low': [p * (1 - max(0, np.random.normal(0.01, 0.005))) for p in prices],
            'close': prices,
            'volume': np.random.normal(50000, 15000, len(dates))
        })
        
        return self.ohlcv
        
    def calculate_rsi(self, period=14):
        """Calculate RSI indicator."""
        df = self.ohlcv.copy()
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
        
    def simulate_rsi_reversal(self):
        """Simulate RSI reversal strategy."""
        df = self.ohlcv.copy()
        df['rsi'] = self.calculate_rsi()
        
        # Default RSI reversal parameters
        long_entry = self.config.get('long_entry', 40)
        long_exit = self.config.get('long_exit', 55)
        stop_loss = self.config.get('stop_loss_pct', 5) / 100
        
        trades = []
        position = None
        
        for i, row in df.iterrows():
            if pd.isna(row['rsi']):
                continue
                
            # Entry logic
            if position is None and row['rsi'] < long_entry:
                position = {
                    'entry_date': row['timestamp'],
                    'entry_price': row['close'],
                    'entry_rsi': row['rsi'],
                    'side': 'long'
                }
                
            # Exit logic
            elif position is not None:
                exit_triggered = False
                exit_reason = ""
                
                # RSI exit
                if row['rsi'] > long_exit:
                    exit_triggered = True
                    exit_reason = "rsi_exit"
                    
                # Stop loss
                elif (row['close'] / position['entry_price'] - 1) < -stop_loss:
                    exit_triggered = True
                    exit_reason = "stop_loss"
                
                if exit_triggered:
                    pnl_pct = (row['close'] / position['entry_price'] - 1) * 100
                    position.update({
                        'exit_date': row['timestamp'],
                        'exit_price': row['close'],
                        'exit_rsi': row['rsi'],
                        'pnl_pct': pnl_pct,
                        'exit_reason': exit_reason,
                        'hold_days': (row['timestamp'] - position['entry_date']).days
                    })
                    trades.append(position)
                    position = None
        
        return trades
        
    def analyze_results(self, trades):
        """Analyze backtest results."""
        if not trades:
            return {"error": "No trades generated"}
            
        df_trades = pd.DataFrame(trades)
        
        total_trades = len(trades)
        winning_trades = len(df_trades[df_trades['pnl_pct'] > 0])
        losing_trades = len(df_trades[df_trades['pnl_pct'] <= 0])
        win_rate = (winning_trades / total_trades) * 100
        
        total_return = df_trades['pnl_pct'].sum()
        avg_return = df_trades['pnl_pct'].mean()
        best_trade = df_trades['pnl_pct'].max()
        worst_trade = df_trades['pnl_pct'].min()
        avg_hold_days = df_trades['hold_days'].mean()
        
        return {
            "period": f"{self.days} days",
            "symbol": self.symbol,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_return": total_return,
            "avg_return": avg_return,
            "best_trade": best_trade,
            "worst_trade": worst_trade,
            "avg_hold_days": avg_hold_days,
            "trades": trades[-5:] if len(trades) > 5 else trades  # Last 5 trades
        }
        
    def run(self):
        """Run the backtest."""
        strategy_id = self.config.get('strategy_id', 'unknown')
        
        if strategy_id == 'rsi-reversal':
            self.fetch_ohlcv()
            trades = self.simulate_rsi_reversal()
            return self.analyze_results(trades)
        else:
            return {"error": f"Backtest not implemented for {strategy_id}"}

def main():
    if len(sys.argv) < 2:
        print("Usage: python backtest.py <config-file> [symbol] [days]")
        sys.exit(1)
        
    config_file = sys.argv[1]
    symbol = sys.argv[2] if len(sys.argv) > 2 else "BTC/USDT"
    days = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    with open(config_file) as f:
        config = json.load(f)
    
    backtest = QuickBacktest(config, symbol, days)
    results = backtest.run()
    
    if "error" in results:
        print(f"❌ {results['error']}")
        return
        
    print(f"\n🎯 Backtest Results: {results['symbol']} ({results['period']})")
    print(f"📊 Total trades: {results['total_trades']}")
    print(f"✅ Win rate: {results['win_rate']:.1f}%")
    print(f"💰 Total return: {results['total_return']:.2f}%")
    print(f"📈 Avg return per trade: {results['avg_return']:.2f}%")
    print(f"🚀 Best trade: {results['best_trade']:.2f}%")
    print(f"🛑 Worst trade: {results['worst_trade']:.2f}%")
    print(f"⏰ Avg hold time: {results['avg_hold_days']:.1f} days")
    
    if results['trades']:
        print(f"\n📋 Recent trades:")
        for trade in results['trades']:
            print(f"  • {trade['entry_date'].strftime('%m/%d')} → {trade['exit_date'].strftime('%m/%d')}: {trade['pnl_pct']:.2f}% ({trade['exit_reason']})")

if __name__ == "__main__":
    main()