#!/usr/bin/env python3
"""
Position Snapshot — OHLC chart with position overlay.
Renders entry, current price, open orders, PnL, and custom zones on a candlestick chart.

Usage:
  python render_position_chart.py \
    --coin BTC --side short --entry 72837 --size 0.01286 \
    --leverage 10 --pnl 21.73 --roe 23.2 --current-price 71231 \
    --candles candles.json --orders orders.json \
    --zones '{"External Range Liq": [72600, 75300]}' \
    --output output/position_snapshot.png
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


# ── Theme ───────────────────────────────────────────────────────────

BG = '#1a1a2e'
CANDLE_UP = '#00c853'
CANDLE_DOWN = '#ff5252'
ENTRY_COLOR = '#ffd700'
CURRENT_COLOR = '#00e5ff'
ORDER_COLOR = '#ff9800'
ZONE_COLOR = '#ff9800'
LIQ_COLOR = '#ff1744'
BOX_BG = '#16213e'
BOX_EDGE = '#00e5ff'
TEXT_COLOR = 'white'
GRID_ALPHA = 0.2
ZONE_ALPHA = 0.12


def parse_args():
    p = argparse.ArgumentParser(description='Position Snapshot Chart')
    p.add_argument('--coin', required=True, help='Asset symbol (BTC, ETH)')
    p.add_argument('--side', required=True, choices=['long', 'short'])
    p.add_argument('--entry', type=float, required=True, help='Entry price')
    p.add_argument('--size', type=float, required=True, help='Position size')
    p.add_argument('--leverage', type=int, required=True)
    p.add_argument('--pnl', type=float, required=True, help='Unrealized PnL USD')
    p.add_argument('--roe', type=float, required=True, help='ROE %')
    p.add_argument('--current-price', type=float, required=True)
    p.add_argument('--liq-price', type=float, default=None)
    p.add_argument('--candles', required=True, help='Path to candle JSON [{t,o,h,l,c}]')
    p.add_argument('--orders', default=None, help='Path to orders JSON [{price,size,side}]')
    p.add_argument('--zones', default=None, help='JSON string: {"name": [low, high]}')
    p.add_argument('--output', default='output/position_snapshot.png')
    p.add_argument('--interval', default='4H', help='Candle interval label')
    p.add_argument('--title', default=None, help='Custom chart title')
    return p.parse_args()


def load_candles(path):
    with open(path) as f:
        data = json.load(f)
    candles = []
    for c in data:
        # Support both seconds and milliseconds timestamps
        ts = c['t']
        if ts > 1e12:
            ts = ts / 1000
        candles.append({
            'dt': datetime.fromtimestamp(ts, tz=timezone.utc),
            'o': float(c['o']),
            'h': float(c['h']),
            'l': float(c['l']),
            'c': float(c['c']),
        })
    return candles


def load_orders(path):
    if not path:
        return []
    with open(path) as f:
        return json.load(f)


def render(args):
    candles = load_candles(args.candles)
    orders = load_orders(args.orders)
    zones = json.loads(args.zones) if args.zones else {}

    dates = [c['dt'] for c in candles]
    opens = [c['o'] for c in candles]
    highs = [c['h'] for c in candles]
    lows = [c['l'] for c in candles]
    closes = [c['c'] for c in candles]

    # ── Figure ──
    fig, ax = plt.subplots(figsize=(16, 10))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    # ── Candlesticks ──
    body_width = (dates[1] - dates[0]).total_seconds() / 86400 * 0.6 if len(dates) > 1 else 0.02
    for i, c in enumerate(candles):
        color = CANDLE_UP if c['c'] >= c['o'] else CANDLE_DOWN
        d = mdates.date2num(c['dt'])
        # Wick
        ax.plot([d, d], [c['l'], c['h']], color=color, linewidth=1, zorder=2)
        # Body
        body_low = min(c['o'], c['c'])
        body_h = abs(c['c'] - c['o']) or (c['h'] - c['l']) * 0.01
        rect = plt.Rectangle((d - body_width / 2, body_low), body_width, body_h,
                              facecolor=color, edgecolor=color, zorder=3)
        ax.add_patch(rect)

    ax.xaxis_date()

    # ── Zones (behind everything) ──
    zone_colors = ['#ff9800', '#9c27b0', '#2196f3', '#4caf50', '#e91e63']
    for idx, (name, (lo, hi)) in enumerate(zones.items()):
        zc = zone_colors[idx % len(zone_colors)]
        ax.axhspan(lo, hi, alpha=ZONE_ALPHA, color=zc, zorder=1, label=name)

    # ── Entry line ──
    ax.axhline(y=args.entry, color=ENTRY_COLOR, linestyle='--', linewidth=2, 
               label=f'Entry: ${args.entry:,.0f}', zorder=5)

    # ── Current price line ──
    ax.axhline(y=args.current_price, color=CURRENT_COLOR, linestyle='-', linewidth=2,
               label=f'Current: ${args.current_price:,.0f}', zorder=5)

    # ── Liquidation price ──
    if args.liq_price and args.liq_price < max(highs) * 3:
        ax.axhline(y=args.liq_price, color=LIQ_COLOR, linestyle='-.', linewidth=1.5,
                   alpha=0.7, label=f'Liq: ${args.liq_price:,.0f}', zorder=5)

    # ── Open limit orders ──
    order_prices = []
    for order in orders:
        px = float(order['price'])
        order_prices.append(px)
        ax.axhline(y=px, color=ORDER_COLOR, linestyle=':', linewidth=1, alpha=0.7, zorder=4)

    if order_prices:
        # Add a single legend entry for all orders
        ax.plot([], [], color=ORDER_COLOR, linestyle=':', linewidth=1,
                label=f'Limit Orders ({len(orders)}): ${min(order_prices):,.0f}–${max(order_prices):,.0f}')

    # ── PnL shading between entry and current ──
    pnl_color = CANDLE_UP if args.pnl >= 0 else CANDLE_DOWN
    shade_lo = min(args.entry, args.current_price)
    shade_hi = max(args.entry, args.current_price)
    ax.axhspan(shade_lo, shade_hi, alpha=0.08, color=pnl_color, zorder=1)

    # ── Title ──
    title = args.title or f'{args.coin}/USD {args.interval} — {"Short" if args.side == "short" else "Long"} Position Snapshot'
    ax.set_title(title, fontsize=18, fontweight='bold', color=TEXT_COLOR, pad=20)
    ax.set_ylabel('Price (USD)', fontsize=12, color=TEXT_COLOR)

    # ── Grid ──
    ax.grid(True, alpha=GRID_ALPHA, color='white')

    # ── Info box ──
    pnl_sign = '+' if args.pnl >= 0 else ''
    roe_sign = '+' if args.roe >= 0 else ''

    info_lines = [
        f'POSITION SUMMARY',
        f'━━━━━━━━━━━━━━━━━━━',
        f'Side: {args.side.upper()}',
        f'Size: {args.size} {args.coin}',
        f'Leverage: {args.leverage}x',
        f'Entry: ${args.entry:,.0f}',
        f'Current: ${args.current_price:,.0f}',
        f'PnL: {pnl_sign}${args.pnl:.2f} ({roe_sign}{args.roe:.1f}% ROE)',
    ]
    if args.liq_price:
        info_lines.append(f'Liq Price: ${args.liq_price:,.0f}')
    if orders:
        total_order_size = sum(float(o.get('size', 0)) for o in orders)
        info_lines.append(f'')
        info_lines.append(f'OPEN LIMITS: {len(orders)} orders')
        info_lines.append(f'Range: ${min(order_prices):,.0f} – ${max(order_prices):,.0f}')
        info_lines.append(f'Total size: {total_order_size:.4f} {args.coin}')
    for name, (lo, hi) in zones.items():
        info_lines.append(f'')
        info_lines.append(f'ZONE: {name}')
        info_lines.append(f'${lo:,.0f} – ${hi:,.0f}')

    info_text = '\n'.join(info_lines)
    props = dict(boxstyle='round', facecolor=BOX_BG, alpha=0.9, edgecolor=BOX_EDGE)
    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', fontfamily='monospace', color=TEXT_COLOR, bbox=props, zorder=10)

    # ── Legend ──
    legend = ax.legend(loc='upper right', facecolor=BOX_BG, edgecolor='white',
                       labelcolor='white', fontsize=10)
    legend.set_zorder(10)

    # ── Axis styling ──
    ax.tick_params(axis='x', colors=TEXT_COLOR)
    ax.tick_params(axis='y', colors=TEXT_COLOR)
    fig.autofmt_xdate()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    # ── Y-axis range: show all orders + some padding ──
    all_prices = highs + lows + [args.entry, args.current_price] + order_prices
    if args.liq_price and args.liq_price < max(highs) * 3:
        all_prices.append(args.liq_price)
    price_range = max(all_prices) - min(all_prices)
    ax.set_ylim(min(all_prices) - price_range * 0.05, max(all_prices) + price_range * 0.05)

    # ── Save ──
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(str(out), dpi=150, facecolor=BG)
    plt.close()
    print(f'Chart saved to {out}')


if __name__ == '__main__':
    render(parse_args())
