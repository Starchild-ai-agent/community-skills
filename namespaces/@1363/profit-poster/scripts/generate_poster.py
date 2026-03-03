#!/usr/bin/env python3
"""
Profit Poster Generator — TradingView-style trade summary card.
Usage: python3 generate_poster.py --config '{"coin":"BTC","entry":65806,"exit":69354,"size":0.00016,"side":"long","leverage":10}'
Or import and call generate_poster(config) directly.
"""

import json
import sys
import argparse
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont

# ── Config ──────────────────────────────────────────────────────────────
CARD_WIDTH = 800
CARD_HEIGHT = 520
BG_COLOR = (22, 26, 37)          # Dark TradingView background
CARD_BG = (30, 35, 50)           # Slightly lighter card
GREEN = (38, 166, 91)            # Profit green
RED = (234, 57, 67)              # Loss red
ACCENT_BLUE = (55, 135, 235)     # Header accent
TEXT_WHITE = (230, 230, 230)
TEXT_GRAY = (140, 145, 160)
TEXT_DIM = (90, 95, 110)
BORDER_RADIUS = 16


def get_font(size, bold=False):
    """Try to load a clean font, fall back to default."""
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def format_price(price):
    if price >= 1000:
        return f"${price:,.2f}"
    elif price >= 1:
        return f"${price:.4f}"
    else:
        return f"${price:.6f}"


def format_pnl(pnl):
    sign = "+" if pnl >= 0 else ""
    return f"{sign}${pnl:,.2f}"


def format_pct(pct):
    sign = "+" if pct >= 0 else ""
    return f"{sign}{pct:.2f}%"


def draw_rounded_rect(draw, xy, fill, radius=16):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def generate_poster(config, output_path=None):
    """
    config keys:
      coin: str (e.g. "BTC")
      entry: float
      exit: float (or current price if still open)
      size: float
      side: "long" or "short"
      leverage: int
      status: "closed" or "open" (default: "closed")
      entry_time: str ISO (optional)
      exit_time: str ISO (optional)
      account: float (optional, total account value)
      notes: str (optional, e.g. "VAL → VAH rotation")
    """
    coin = config.get("coin", "BTC")
    entry = config["entry"]
    exit_price = config["exit"]
    size = config["size"]
    side = config.get("side", "long")
    leverage = config.get("leverage", 1)
    status = config.get("status", "closed")
    notes = config.get("notes", "")
    
    # Calculate PnL
    if side.lower() == "long":
        pnl = (exit_price - entry) * size
        pnl_pct = ((exit_price - entry) / entry) * 100
    else:
        pnl = (entry - exit_price) * size
        pnl_pct = ((entry - exit_price) / entry) * 100
    
    roe = pnl_pct * leverage
    is_profit = pnl >= 0
    accent = GREEN if is_profit else RED
    
    # Notional
    notional = entry * size
    
    # ── Draw ────────────────────────────────────────────────────────────
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_title = get_font(28, bold=True)
    font_large = get_font(42, bold=True)
    font_medium = get_font(18, bold=True)
    font_small = get_font(15)
    font_tiny = get_font(12)
    
    # ── Main card background ────────────────────────────────────────────
    card_margin = 24
    draw_rounded_rect(draw,
        (card_margin, card_margin, CARD_WIDTH - card_margin, CARD_HEIGHT - card_margin),
        fill=CARD_BG, radius=BORDER_RADIUS)
    
    # ── Header bar ──────────────────────────────────────────────────────
    header_y = card_margin
    draw_rounded_rect(draw,
        (card_margin, header_y, CARD_WIDTH - card_margin, header_y + 64),
        fill=(25, 30, 42), radius=BORDER_RADIUS)
    # Fix bottom corners of header (overlap with card)
    draw.rectangle((card_margin, header_y + 48, CARD_WIDTH - card_margin, header_y + 64), fill=(25, 30, 42))
    
    # Coin name + side badge
    side_text = side.upper()
    side_color = GREEN if side.lower() == "long" else RED
    
    draw.text((48, header_y + 16), f"{coin}/USDC", fill=TEXT_WHITE, font=font_title)
    
    # Side badge
    badge_x = 48 + draw.textlength(f"{coin}/USDC", font=font_title) + 16
    badge_w = draw.textlength(side_text, font=font_medium) + 20
    draw_rounded_rect(draw,
        (badge_x, header_y + 18, badge_x + badge_w, header_y + 44),
        fill=side_color, radius=8)
    draw.text((badge_x + 10, header_y + 20), side_text, fill=(255,255,255), font=font_medium)
    
    # Leverage badge
    lev_text = f"{leverage}×"
    lev_x = badge_x + badge_w + 10
    lev_w = draw.textlength(lev_text, font=font_medium) + 20
    draw_rounded_rect(draw,
        (lev_x, header_y + 18, lev_x + lev_w, header_y + 44),
        fill=ACCENT_BLUE, radius=8)
    draw.text((lev_x + 10, header_y + 20), lev_text, fill=(255,255,255), font=font_medium)
    
    # Status badge (right side)
    status_text = "OPEN" if status == "open" else "CLOSED"
    status_w = draw.textlength(status_text, font=font_medium) + 20
    status_x = CARD_WIDTH - card_margin - status_w - 24
    status_color = ACCENT_BLUE if status == "open" else TEXT_DIM
    draw_rounded_rect(draw,
        (status_x, header_y + 18, status_x + status_w, header_y + 44),
        fill=status_color, radius=8)
    draw.text((status_x + 10, header_y + 20), status_text, fill=TEXT_WHITE, font=font_medium)
    
    # ── ROE (big number) ────────────────────────────────────────────────
    roe_y = header_y + 88
    roe_text = format_pct(roe)
    draw.text((48, roe_y), "ROE", fill=TEXT_GRAY, font=font_medium)
    draw.text((48, roe_y + 26), roe_text, fill=accent, font=font_large)
    
    # PnL next to ROE
    pnl_x = 320
    draw.text((pnl_x, roe_y), "PnL", fill=TEXT_GRAY, font=font_medium)
    draw.text((pnl_x, roe_y + 26), format_pnl(pnl), fill=accent, font=font_large)
    
    # Price change % (unlevered)
    pct_x = 580
    draw.text((pct_x, roe_y), "Price Δ", fill=TEXT_GRAY, font=font_medium)
    draw.text((pct_x, roe_y + 30), format_pct(pnl_pct), fill=accent, font=font_title)
    
    # ── Divider ─────────────────────────────────────────────────────────
    div_y = roe_y + 90
    draw.line((48, div_y, CARD_WIDTH - 48, div_y), fill=TEXT_DIM, width=1)
    
    # ── Details grid ────────────────────────────────────────────────────
    grid_y = div_y + 16
    col1_x, col2_x, col3_x = 48, 300, 560
    row_height = 48
    
    details = [
        [("Entry Price", format_price(entry)), ("Exit Price", format_price(exit_price)), ("Size", f"{size} {coin}")],
        [("Notional", f"${notional:,.2f}"), ("Leverage", f"{leverage}×"), ("Side", side.capitalize())],
    ]
    
    for row_idx, row in enumerate(details):
        y = grid_y + row_idx * row_height
        for col_idx, (label, value) in enumerate(row):
            x = [col1_x, col2_x, col3_x][col_idx]
            draw.text((x, y), label, fill=TEXT_GRAY, font=font_small)
            draw.text((x, y + 18), value, fill=TEXT_WHITE, font=font_medium)
    
    # ── Notes / trade description ───────────────────────────────────────
    if notes:
        notes_y = grid_y + len(details) * row_height + 12
        draw.line((48, notes_y, CARD_WIDTH - 48, notes_y), fill=TEXT_DIM, width=1)
        draw.text((48, notes_y + 10), notes, fill=TEXT_GRAY, font=font_small)
    
    # ── Footer ──────────────────────────────────────────────────────────
    footer_y = CARD_HEIGHT - card_margin - 36
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    draw.text((48, footer_y), f"Hyperliquid  •  {timestamp}", fill=TEXT_DIM, font=font_tiny)
    draw.text((CARD_WIDTH - 48 - draw.textlength("★ Star Child", font=font_tiny), footer_y),
              "★ Star Child", fill=TEXT_DIM, font=font_tiny)
    
    # ── Save ────────────────────────────────────────────────────────────
    if output_path is None:
        output_path = f"output/{coin}_{side}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.png"
    
    img.save(output_path, "PNG", quality=95)
    print(f"✅ Poster saved: {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate trade profit poster")
    parser.add_argument("--config", type=str, required=True, help="JSON config string")
    parser.add_argument("--output", type=str, default=None, help="Output path (optional)")
    args = parser.parse_args()
    
    config = json.loads(args.config)
    generate_poster(config, args.output)
