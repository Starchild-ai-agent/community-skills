# Backtest Notes — SOL 15M Scalping Strategy

## Data
- Exchange: Hyperliquid (SOL-PERP)
- Timeframe: 15M candles
- Period: 52 days (~5,000 candles)
- Entry: market on signal candle close
- Fees: 0.045% taker per side (conservative)

## Filter Evolution (cumulative results)

| Config | Trades | Win% | PF | Net% |
|--------|--------|------|----|------|
| Baseline (9/21 EMA + 50 + RSI + vol) | 38 | 34.2% | 1.85 | +2.80% |
| + 1H EMA alignment | 26 | 42.3% | 2.08 | +3.52% |
| + VWAP filter | 35 | 34.3% | 1.84 | +2.67% |
| **+ 1H EMA + VWAP (combined)** | **25** | **44.0%** | **2.20** | **+3.91%** |
| + 200 EMA regime gate | 22 | 53.8% | -- | -- |
| + RSI smoothed (5-MA) | 22 | **63.6%** | **1.96** | **+8.68%** |

## Filters Tested and Rejected

| Filter | Why Rejected |
|--------|-------------|
| OBV | Lagging — cut win rate from 34% to 11% |
| Bollinger Bands | Mean-reversion tool, kills momentum signals. Worst filter tested. |
| ATR dynamic stops | Same win rate but wider stops hurt R:R |
| StochRSI standalone | 72.7% win rate but filters too many valid trades (22→11) |
| ADX > 25 | Reduces trades too aggressively, lower net than ADX > 20 |

## Timeframe Comparison

| Timeframe | Trades | Win% | Net% |
|-----------|--------|------|------|
| 15M | 24 | **58.3%** | **+0.14%** |
| 30M | 11 | 27.3% | -1.89% |

30M rejected — EMA too slow, enters after moves complete.

## Position Sizing (Monte Carlo, 2000 sims × 100 trades, $10k start)

| Config | Median | P10 (worst) | Max DD P90 |
|--------|--------|-------------|------------|
| 0.5% / 1x | $14,110 | $12,706 | 4.0% |
| **1.0% / 1x** | **$19,784** | **$16,046** | **7.8%** ← RECOMMENDED |
| 1.0% / 2x | $15,818 | $12,823 | 10.8% |
| 2.0% / 2x | $24,459 | $17,069 | 20.6% |
| Half-Kelly / 2x | $27,754 | $18,351 | 23.4% |

**Winner: 1% flat risk at 1x leverage.** More leverage doesn't help — it amplifies fees
and slippage without improving returns on 15M scalping with 0.3–0.6% stops.

## Market Regime Sensitivity

Strategy is trend-following — performs best in trending conditions.

| Scenario | Win Rate |
|----------|----------|
| Uptrend  longs | ~70% |
| Downtrend shorts | ~60% |
| Ranging longs | ~30% |
| Ranging shorts | ~25% |

The 200 EMA regime gate exists specifically to block longs in downtrends (0% win rate
historically) and shorts in uptrends. This is the single most impactful filter.

## Entry/Exit Rules
- Entry: close of signal candle, or limit 1–2 ticks inside breakout for maker fill
- TP1: 1.5R → close 50%, move SL to breakeven
- TP2: 2.5R → close remaining
- Stop out: EMA cross reversal before TP1
- Time stop: if no progress after 8 candles (2 hours), exit at market

## Session Performance
- Best: US open (13:30–16:00 UTC)
- Good: Asia open (00:00–03:00 UTC)
- Worst: Low-volume weekend / Sunday Asia session
