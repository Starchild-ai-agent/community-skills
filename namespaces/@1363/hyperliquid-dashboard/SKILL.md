---
name: hyperliquid-dashboard
version: 2.0.0
description: "Real-time Hyperliquid wallet monitoring dashboard — positions, orders, and account stats in your browser. Supports native perps + all HIP-3 builder dex markets (stocks, RWA, commodities)."
author: dub
tags: [hyperliquid, dashboard, trading, monitoring, hip3, positions]
---

# 📊 Hyperliquid Dashboard — Position Monitor

**Real-time Hyperliquid wallet monitoring dashboard — positions, orders, and account stats in your browser.**

---

## 🎯 What It Does

Generates a clean, auto-refreshing dashboard showing:
- **Account Summary** — Total value, uPnL, margin used/available, open positions/orders count
- **Open Positions** — All active perps with entry, mark, liq price, PnL, ROE%
- **Open Orders** — All resting limit orders with prices, sizes, reduce-only status
- **HIP-3 Builder Dex Markets** — Full support for xyz (stocks/RWA), Felix, Ventuals, and all builder-deployed perps
- **Dex Filter Tabs** — View all markets combined or filter by specific dex (Native, xyz, flx, etc.)
- **Auto-Refresh** — Configurable intervals (5s, 10s, 30s default, 1m, or off) — no loading flicker on refresh
- **Any Wallet** — Works for any Hyperliquid wallet address (not just yours)

**Zero backend required** — runs entirely in the browser using Hyperliquid's public API.

---

## 🚀 Quick Start

### Option 1: Run Locally (Workspace Preview)
```bash
# From workspace root
cd skills/hyperliquid-dashboard
# Open index.html in browser or use preview_serve
```

### Option 2: Deploy to Vercel (Recommended)
```bash
# Install Vercel CLI (if needed)
npm i -g vercel

# Deploy
cd skills/hyperliquid-dashboard
vercel deploy --prod
```

**Or:** Drag the folder into [vercel.com](https://vercel.com) for one-click deploy.

### Option 3: GitHub + Vercel Auto-Deploy
```bash
# Push to GitHub
git add skills/hyperliquid-dashboard
git commit -m "Add HL dashboard"
git push

# Connect repo to Vercel for auto-deploys on push
```

---

## 📋 Usage

1. **Open the dashboard** (local preview or deployed URL)
2. **Enter wallet address** — Your Hyperliquid wallet or any address to monitor
3. **Click "Load Dashboard"** — Fetches live data
4. **Set refresh interval** — Choose auto-refresh rate or turn off
5. **Monitor** — Watch positions and orders update in real-time

**Pro tip:** Deploy to Vercel, bookmark the URL on your phone, and you've got a mobile position monitor.

---

## 🛠️ How It Works

- **Data Source:** Hyperliquid public info API (`https://api.hyperliquid.xyz/info`)
- **Queries:** `clearinghouseState` + `openOrders` for native perps, plus same for each builder dex (xyz, flx, vntl, etc.)
- **Builder Dex Discovery:** Auto-discovers all active HIP-3 dexes via `perpDexs` endpoint
- **No Auth Needed:** Uses public API — no API keys, no backend
- **Single File:** `index.html` contains everything (HTML, CSS, JS)
- **Zero Dependencies:** No npm, no build step, no framework
- **Smart Refresh:** Full loading spinner only on first load; silent background updates on auto-refresh

---

## 📦 Files Included

```
skills/hyperliquid-dashboard/
├── SKILL.md           # This file
├── index.html         # The dashboard (single-file app)
├── README.md          # Deployment guide
└── vercel.json        # Vercel config (optional)
```

---

## 🔧 Customization

**Edit `index.html` directly to:**
- Change refresh intervals
- Adjust theme colors
- Add/remove columns from tables
- Add PnL charts (integrate with charting skill)
- Add position history
- Add alerts (email/Telegram webhook on PnL thresholds)

---

## 🎯 Use Cases

- **Personal monitoring** — Quick position checks without opening HL UI
- **Copy-trade oversight** — Monitor wallets you're copying
- **Whale watching** — Track large accounts in real-time
- **Multi-account management** — Switch between wallets instantly
- **Mobile access** — Deployed URL works on any device

---

## 📈 Example Output

**Account Summary:**
| Metric | Value |
|--------|-------|
| Account Value | $214.52 |
| Unrealized PnL | +$22.15 |
| Margin Used | $25.10 |
| Available Margin | $189.42 |
| Leverage | 1.12x |

**Positions Table:**
| Coin | Side | Size | Entry | Mark | Liq Price | uPnL | ROE% |
|------|------|------|-------|------|-----------|------|------|
| BTC | Short | 0.01286 | $72,837 | $71,231 | $132,641 | +$21.73 | +23.2% |

**Orders Table:**
| Coin | Side | Size | Limit Price | Reduce Only | Order ID |
|------|------|------|-------------|-------------|----------|
| BTC | Sell | 0.00235 | $73,800 | No | 1234567890 |
| BTC | Sell | 0.00235 | $74,100 | No | 1234567891 |

---

## 🔗 Related Skills

- **`@1363/position-snapshot`** — Generate OHLC charts with position overlays
- **`@1363/profit-poster`** — Create trade recap images with PnL summary
- **`@1363/hl-trader-rankings`** — Analyze and rank Hyperliquid traders
- **`@1363/copy-trade`** — Auto-mirror profitable trader positions

---

## ⚠️ Notes

- **Public API only** — Can't place orders, only view data
- **Rate limits** — Hyperliquid may rate-limit frequent requests (use 10s+ refresh). HIP-3 adds extra API calls per dex.
- **Perp accounts only** — Shows perpetual futures (native + builder dexes), not spot balances
- **Unified account mode** — If using unified margin, shows combined account state
- **HIP-3 labels** — Builder dex positions/orders are tagged with their dex name (e.g. "xyz") for clarity

---

## 🐛 Troubleshooting

**Blank screen / loading forever:**
- Check browser console for errors
- Verify wallet address is valid Hyperliquid address
- Hyperliquid API may be temporarily down

**No positions showing:**
- Wallet may have no open positions
- Try refreshing manually
- Check if address is correct (0x...)

**Rate limit errors:**
- Increase refresh interval to 30s or 1m
- You're hitting Hyperliquid's public API limits

---

**Install:** `Install @1363/hyperliquid-dashboard`

**Author:** @1363  
**Version:** 2.0.0  
**Last Updated:** 2026-03-06
