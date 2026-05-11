#!/usr/bin/env python3
"""
HL Copy Trader — Setup Script
Initializes copy trade: reads target, computes scale, deposits if needed,
mirrors current positions+orders, registers the sync scheduled task.

Usage (called by agent after user confirms):
  python3 setup.py \
    --target 0xdAe4... \
    --capital 1000 \
    --risk-stop 40 \
    --interval 5 \
    --max-leverage 10 \
    --assets all \
    --min-order 10 \
    --lang zh \
    --job-id <scheduled_task_job_id>
"""
import asyncio, sys, json, argparse, os
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/data/workspace')
from skills.hyperliquid.client import HyperliquidClient

MIN_BTC_SIZE = 0.001
HL_INFO = 'https://api.hyperliquid.xyz/info'

# ── Args ──────────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument('--target',       required=True)
parser.add_argument('--capital',      type=float, required=True)
parser.add_argument('--risk-stop',    type=float, default=40)
parser.add_argument('--interval',     type=int,   default=5)
parser.add_argument('--max-leverage', type=int,   default=10)
parser.add_argument('--assets',       default='all')
parser.add_argument('--min-order',    type=float, default=10)
parser.add_argument('--lang',         default='zh')
parser.add_argument('--job-id',       default='')
parser.add_argument('--dry-run',      action='store_true')
args = parser.parse_args()

STOP_VALUE = args.capital * (1 - args.risk_stop / 100)

# ── Helpers ───────────────────────────────────────────────────────────────────
def fmtUSD(v): return f"${float(v):,.2f}"
def scale_size(sz, ratio): return max(round(float(sz) * ratio, 3), MIN_BTC_SIZE)
def asset_allowed(coin):
    if args.assets == 'all': return True
    return coin.upper() in [a.strip().upper() for a in args.assets.split(',')]

# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    c = HyperliquidClient()
    my_addr = await c._get_address()

    # 1. Read target state
    print(f"\nReading target trader: {args.target[:10]}…{args.target[-6:]}")
    target_acct = await c.get_account_state(args.target)
    target_margin = target_acct.get('marginSummary', {})
    target_val = float(target_margin.get('accountValue', 0))
    if target_val == 0:
        print("ERROR: Target account not found or has zero value.")
        sys.exit(1)

    scale_ratio = args.capital / target_val
    target_positions = target_acct.get('assetPositions', [])
    target_orders = await c.get_open_orders(args.target)

    # 2. Print confirmation summary
    print(f"""
╔══════════════════════════════════════════════╗
║          HL COPY TRADER — Setup              ║
╠══════════════════════════════════════════════╣
║ Target:       {args.target[:12]}…{args.target[-6:]}   ║
║ Target value: {fmtUSD(target_val):<36} ║
║ Your capital: {fmtUSD(args.capital):<36} ║
║ Scale ratio:  1 : {1/scale_ratio:.1f:<31} ║
║ Stop-loss:    {fmtUSD(STOP_VALUE)} (−{args.risk_stop}%){'':<22} ║
║ Sync:         every {args.interval} min{'':<29} ║
║ Assets:       {args.assets:<36} ║
║ Max leverage: {args.max_leverage}x{'':<35} ║
║ Positions:    {len(target_positions)} open{'':<32} ║
║ Orders:       {len(target_orders)} open{'':<32} ║
╚══════════════════════════════════════════════╝
    """)

    if args.dry_run:
        print("[DRY RUN] Stopping here — no trades executed.")
        return

    # 3. Read my current HL balance
    my_acct = await c.get_account_state(my_addr)
    my_val = float(my_acct.get('marginSummary', {}).get('accountValue', 0))
    if my_val < args.capital * 0.95:
        needed = args.capital - my_val
        print(f"\nDepositing ${needed:.2f} USDC to Hyperliquid…")
        dep = await c.deposit_usdc(needed)
        print(f"Deposit: {dep}")
        await asyncio.sleep(15)  # wait for bridge

    # 4. Mirror positions
    print("\n── Mirroring positions ──")
    for p in target_positions:
        pos = p.get('position', {})
        coin = pos.get('coin')
        if not asset_allowed(coin): continue
        szi = float(pos.get('szi', 0))
        if szi == 0: continue
        lev = min(int(pos.get('leverage', {}).get('value', 1)), args.max_leverage)
        my_sz = scale_size(abs(szi), scale_ratio)
        is_buy = szi > 0

        # Set leverage
        try:
            await c.update_leverage(coin, lev, is_cross=True)
        except Exception as e:
            print(f"  Leverage warn ({coin}): {e}")

        # Open position
        try:
            r = await c.market_open(coin, is_buy=is_buy, size=my_sz)
            statuses = r.get('response', {}).get('data', {}).get('statuses', [{}])
            st = statuses[0]
            if 'filled' in st:
                side = 'LONG' if is_buy else 'SHORT'
                print(f"  ✅ {side} {my_sz} {coin} @ avg ${st['filled']['avgPx']}")
            else:
                print(f"  ⚠️  {coin}: {st}")
        except Exception as e:
            print(f"  ❌ {coin}: {e}")
        await asyncio.sleep(0.4)

    # 5. Mirror orders
    print("\n── Mirroring orders ──")
    paul_orders_map = {}  # target_oid → my_oid
    placed = 0
    skipped = 0
    for o in target_orders:
        coin = o.get('coin')
        if not asset_allowed(coin): continue
        side = o.get('side')
        sz = float(o.get('sz', 0))
        px = float(o.get('limitPx', 0))
        target_oid = str(o.get('oid'))
        my_sz = scale_size(sz, scale_ratio)
        notional = my_sz * px

        if notional < args.min_order:
            print(f"  ⏭  Skip {side} {my_sz} {coin} @ {px:.0f} — notional ${notional:.1f} < ${args.min_order}")
            skipped += 1
            continue

        is_buy = side == 'B'
        try:
            r = await c.place_order(coin, is_buy=is_buy, size=my_sz, price=px, order_type='limit')
            statuses = r.get('response', {}).get('data', {}).get('statuses', [{}])
            st = statuses[0]
            if 'resting' in st:
                my_oid = str(st['resting']['oid'])
                paul_orders_map[target_oid] = my_oid
                side_label = 'BUY ' if is_buy else 'SELL'
                print(f"  ✅ {side_label} {my_sz} {coin} @ ${px:,.0f}")
                placed += 1
            elif 'filled' in st:
                my_oid = str(st['filled']['oid'])
                paul_orders_map[target_oid] = my_oid
                print(f"  ✅ FILLED {my_sz} {coin} @ ${px:,.0f}")
                placed += 1
            else:
                print(f"  ⚠️  {coin}: {st}")
        except Exception as e:
            print(f"  ❌ {coin} @ {px:.0f}: {e}")
        await asyncio.sleep(0.3)

    print(f"\nOrders: {placed} placed, {skipped} skipped (below min size)")

    # 6. Save state
    state_dir = Path(f'/data/workspace/tasks/{args.job_id}') if args.job_id else Path('/data/workspace/tasks/hl-copy-trader-state')
    state_dir.mkdir(parents=True, exist_ok=True)
    state = {
        'paused': False,
        'target_address': args.target,
        'my_capital': args.capital,
        'scale_ratio': scale_ratio,
        'stop_value': STOP_VALUE,
        'sync_interval': args.interval,
        'max_leverage': args.max_leverage,
        'copy_assets': args.assets,
        'min_order_size': args.min_order,
        'lang': args.lang,
        'paul_orders': paul_orders_map,
        'started_at': datetime.utcnow().isoformat(),
        'job_id': args.job_id,
    }
    (state_dir / 'state.json').write_text(json.dumps(state, indent=2))
    print(f"\n✅ State saved to {state_dir}/state.json")
    print(f"✅ Setup complete. Sync monitor will run every {args.interval} minutes.")

asyncio.run(main())
