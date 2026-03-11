---
name: "@1363/profit-poster"
version: 1.0.0
description: "Generate TradingView-style trade summary cards (PNG). Use when user wants a visual trade recap, profit poster, or shareable trade image."
author: Star Child
tags: [trading, visualization, hyperliquid, poster]

metadata:
  starchild:
    emoji: "🖼️"
    skillKey: profit-poster
    requires:
      bins: [python]
      pip: [Pillow]

user-invocable: true
---

# Profit Poster Generator

## Overview

Generates professional dark-themed trade summary cards as PNG images. Styled after TradingView/Hyperliquid aesthetics — coin, side, leverage, entry/exit, PnL, ROE.

## Usage

### From Agent Code

```python
import sys
sys.path.insert(0, "skills/profit-poster/scripts")
from generate_poster import generate_poster

config = {
    "coin": "BTC",
    "entry": 65806.0,
    "exit": 69354.0,
    "size": 0.00016,
    "side": "long",
    "leverage": 10,
    "status": "closed",       # "open" or "closed"
    "notes": "VAL → VAH rotation — textbook range trade"
}

path = generate_poster(config, "output/btc_trade.png")
```

### From CLI

```bash
python3 skills/profit-poster/scripts/generate_poster.py \
  --config '{"coin":"BTC","entry":65806,"exit":69354,"size":0.00016,"side":"long","leverage":10,"status":"closed","notes":"VAL → VAH range rotation"}' \
  --output output/btc_trade.png
```

### Config Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| coin | str | ✅ | Asset symbol (BTC, ETH) |
| entry | float | ✅ | Entry price |
| exit | float | ✅ | Exit/current price |
| size | float | ✅ | Position size in base asset |
| side | str | ✅ | "long" or "short" |
| leverage | int | ❌ | Leverage multiplier (default: 1) |
| status | str | ❌ | "open" or "closed" (default: "closed") |
| notes | str | ❌ | Trade description / strategy note |

### Output

- PNG image saved to `output/` directory
- Filename: `{coin}_{side}_{timestamp}.png` (auto-generated) or custom path
- Resolution: 800×520px, dark theme

## Workflow

1. Gather trade data (from `hl_account`, `hl_fills`, or user input)
2. Build config dict
3. Call `generate_poster(config)`
4. Image saved to `output/`

## Dependencies

- `Pillow` (PIL) — install with `pip install Pillow --break-system-packages`
- Fonts: DejaVu Sans (pre-installed on most Linux)
