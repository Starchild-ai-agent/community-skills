# Backtest Scripts Guide

Run these in order to replicate the full research process. All scripts fetch
live data from Hyperliquid — no external API keys needed.

---

## 1. Baseline Backtest — SOL vs ETH
**Script:** `sol_eth_compare_chart.py`
Compares the 9/21 EMA crossover strategy on SOL and ETH over 30 days.
Shows why SOL outperforms ETH on this strategy.
```
python3 scripts/sol_eth_compare_chart.py
→ output: output/sol_vs_eth_backtest.png
```

---

## 2. OBV Filter Test
**Script:** `obv_backtest.py`
Tests whether adding OBV as a filter improves win rate.
Result: OBV hurts — skip it.
```
python3 scripts/obv_backtest.py
```

---

## 3. Filter Comparison (1H EMA + VWAP)
**Script:** `filter_backtest.py`  
**Chart:** `filter_comparison_chart.py`
Tests 1H EMA alignment and VWAP as signal gatekeepers.
Best combo: 1H EMA + VWAP → 44% WR, PF 2.20.
```
python3 scripts/filter_backtest.py
python3 scripts/filter_comparison_chart.py
→ output: output/filter_comparison.png
```

---

## 4. Timeframe Comparison (15M vs 30M)
**Script:** `timeframe_comparison.py`  
**Chart:** `tf_comparison_chart.py`
Proves 15M is optimal. 30M collapses win rate to 27%.
```
python3 scripts/timeframe_comparison.py
python3 scripts/tf_comparison_chart.py
→ output: output/tf_comparison.png
```

---

## 5. Indicator Candidates (ADX, StochRSI, BB, ATR)
**Script:** `indicator_backtest.py`  
**Chart:** `indicator_results_chart.py`
Tests 7 additional indicators. Baseline wins — don't add more filters.
```
python3 scripts/indicator_backtest.py
python3 scripts/indicator_results_chart.py
→ output: output/indicator_comparison.png
```

---

## 6. Position Sizing + Monte Carlo
**Script:** `position_sizing_backtest.py`  
**Chart:** `sizing_chart.py`
2000 Monte Carlo simulations across 8 sizing configs.
Optimal: 1% risk, 1x leverage. Max DD P90 = 7.8%.
```
python3 scripts/position_sizing_backtest.py
python3 scripts/sizing_chart.py
→ output: output/position_sizing.png
```

---

## 7. Advanced Indicators (RSI Smooth, 200 EMA, Supertrend)
**Script:** `advanced_indicator_backtest.py`  
**Chart:** `advanced_indicator_chart.py`
Tests regime-aware filters. RSI smoothing + 200 EMA gate are the final upgrades.
Win rate in uptrend: 78%. These are now baked into the live alert.
```
python3 scripts/advanced_indicator_backtest.py
python3 scripts/advanced_indicator_chart.py
→ output: output/advanced_indicator_comparison.png
```

---

## Final Strategy Stack (from all backtests)

| Layer | Filter | Impact |
|-------|--------|--------|
| Entry signal | 9/21 EMA crossover | Core |
| Bias | 50 EMA (15M) | Structural |
| Momentum | RSI 5-MA smoothed (45-65L / 35-55S) | +17% WR |
| Trend align | 1H EMA 50 | +8% WR |
| Price vs VWAP | Daily VWAP | +2% WR |
| Regime gate | 200 EMA (long above / short below) | Eliminates 0% WR trades |
| Confluence | Order block proximity | +conviction |
| Environment | Funding rate check | Fee/headwind gate |
| Volume | 1.3x avg spike | Entry timing |
| Sizing | 1% risk / 1x leverage | Survivability |

**Peak performance (uptrend):** 78% win rate | 2.5+ profit factor
