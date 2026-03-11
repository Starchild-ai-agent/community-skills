---
name: "@1363/position-snapshot"
version: 1.0.0
description: "Generate OHLC candlestick charts with position overlays — entry price, open limit orders, PnL, and liquidity zones. Use when the user wants a visual snapshot of their current trading position on a price chart."
author: dub
tags: [trading, charting, hyperliquid, positions, visualization]

metadata:
  starchild:
    emoji: "📸"
    skillKey: position-snapshot
    install:
      - kind: pip
        package: matplotlib

user-invocable: true
---

# Position Snapshot

Generate OHLC candlestick charts overlaid with live position data — entries, limit orders, PnL, and custom zones.

## When To Use

- User asks to see their position on a chart
- User wants a visual of where their orders are relative to price action
- User says "show me where we are" or "chart my position"

## Workflow

1. **Gather position data** — call `hl_account()` (or `orderly_positions()`) to get current position: entry price, size, side, uPnL, leverage, liquidation price
2. **Gather open orders** — call `hl_open_orders()` to get resting limit orders
3. **Fetch OHLC data** — call `hl_candles(coin=ASSET, interval="4h", lookback=336)` for 14 days of 4H candles (adjust interval/lookback to user preference)
4. **Run the render script** — pass data as JSON args to `scripts/render_position_chart.py`
5. **Present the chart** — display from `output/` directory

## Render Script

```bash
python skills/position-snapshot/scripts/render_position_chart.py \
  --coin BTC \
  --side short \
  --entry 72837 \
  --size 0.01286 \
  --leverage 10 \
  --pnl 21.73 \
  --roe 23.2 \
  --current-price 71231 \
  --liq-price 132641 \
  --candles candles.json \
  --orders orders.json \
  --zones '{"External Range Liq": [72600, 75300]}' \
  --output output/position_snapshot.png
```

### Parameters

| Param | Required | Description |
|-------|----------|-------------|
| `--coin` | ✅ | Asset symbol (BTC, ETH, etc.) |
| `--side` | ✅ | Position side: `long` or `short` |
| `--entry` | ✅ | Entry price |
| `--size` | ✅ | Position size in base asset |
| `--leverage` | ✅ | Leverage multiplier |
| `--pnl` | ✅ | Unrealized PnL in USD |
| `--roe` | ✅ | Return on equity % |
| `--current-price` | ✅ | Current mark price |
| `--liq-price` | No | Liquidation price (shown if provided) |
| `--candles` | ✅ | Path to JSON file with OHLC candle data (array of `{t, o, h, l, c}`) |
| `--orders` | No | Path to JSON file with open orders (array of `{price, size, side}`) |
| `--zones` | No | JSON string of named price zones: `{"name": [low, high]}` |
| `--output` | No | Output path (default: `output/position_snapshot.png`) |
| `--interval` | No | Label for candle interval (default: `4H`) |
| `--title` | No | Custom chart title |

### Candle JSON format
```json
[{"t": 1772740800, "o": 70875.5, "h": 71530.4, "l": 70805.9, "c": 71231.2}, ...]
```

### Orders JSON format
```json
[{"price": 73800, "size": 0.00235, "side": "sell"}, ...]
```

## Customization

- **Colors**: Dark theme by default. Green/red candles, gold entry, cyan current price, orange limit orders.
- **Zones**: Pass named zones as JSON — they render as shaded regions with labels.
- **Side-aware**: Long positions show entry below current (green PnL arrow), short positions show entry above.
- **Info box**: Auto-generated summary panel with position details, open order count, and zone labels.

## Notes

- Works with any exchange data — just needs candles in `{t, o, h, l, c}` format
- Hyperliquid candles from `hl_candles()` use this format natively
- For Orderly/other exchanges, transform to same schema before passing
- The script is self-contained — no network calls, all data passed via args/files
