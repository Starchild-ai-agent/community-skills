#!/usr/bin/env python3
"""
HL Copy Trader — Sync Script
Called by scheduled task every N minutes.
Reads state.json, syncs positions & orders, enforces risk controls.

Usage:
  python3 sync.py --state-dir /data/workspace/tasks/{job_id}
"""
import asyncio, sys, json, argparse
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, '/data/workspace')
from skills.hyperliquid.client import HyperliquidClient

MIN_BTC_SIZE = 0.001

parser = argparse.ArgumentParser()
parser.add_argument('--state-dir', required=True, help='Path to task state directory')
args = parser.parse_args()

STATE_FILE = Path(args.state_dir) / 'state.json'

def load_state():
    return json.loads(STATE_FILE.read_text())

def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2))

def scale_size(sz, ratio):
    return max(round(float(sz) * ratio, 3), MIN_BTC_SIZE)

def asset_allowed(coin, copy_assets):
    if copy_assets == 'all': return True
    return coin.upper() in [a.strip().upper() for a in copy_assets.split(',')]

def notify(msg, lang):
    """Print notification — task system will push if non-empty stdout."""
    now = datetime.now(timezone.utc).strftime('%H:%M UTC')
    print(f"[{now}] {msg}")

async def main():
    if not STATE_FILE.exists():
        print("ERROR: state.json not found. Run setup.py first.")
        sys.exit(1)

    state = load_state()
    lang = state.get('lang', 'zh')

    # ── Paused check ──────────────────────────────────────────────
    if state.get('paused'):
        # Silent — don't push noise when already paused
        return

    c = HyperliquidClient()
    my_addr = await c._get_address()
    target_addr = state['target_address']
    scale_ratio = state['scale_ratio']
    stop_value = state['stop_value']
    max_leverage = state.get('max_leverage', 10)
    min_order = state.get('min_order_size', 10)
    copy_assets = state.get('copy_assets', 'all')
    paul_orders_map = state.get('paul_orders', {})  # target_oid → my_oid

    # ── Fetch states ──────────────────────────────────────────────
    my_acct, target_acct = await asyncio.gather(
        c.get_account_state(my_addr),
        c.get_account_state(target_addr),
    )
    my_val = float(my_acct.get('marginSummary', {}).get('accountValue', 0))

    # ── Risk check ────────────────────────────────────────────────
    if my_val < stop_value:
        if lang == 'zh':
            msg = f"⚠️ 风控熔断触发！账户余额 ${my_val:.2f} 低于安全线 ${stop_value:.2f}。正在平仓所有仓位并停止跟单…"
        else:
            msg = f"⚠️ Risk stop triggered! Account ${my_val:.2f} below stop ${stop_value:.2f}. Closing all positions and stopping copy trade…"
        print(msg)

        try: await c.cancel_all_orders('BTC')
        except Exception as e: print(f"Cancel error: {e}")
        try: await c.market_close('BTC', my_addr)
        except Exception as e: print(f"Close error: {e}")

        state['paused'] = True
        save_state(state)

        if lang == 'zh':
            print(f"✅ 已停止跟单。当前余额 ${my_val:.2f}")
        else:
            print(f"✅ Copy trade stopped. Current balance ${my_val:.2f}")
        return

    # ── Fetch target orders ───────────────────────────────────────
    target_orders_raw = await c.get_open_orders(target_addr)
    target_orders = {str(o['oid']): o for o in target_orders_raw if asset_allowed(o.get('coin',''), copy_assets)}
    target_positions = {
        p['position']['coin']: p['position']
        for p in target_acct.get('assetPositions', [])
        if asset_allowed(p['position']['coin'], copy_assets)
    }

    # My orders
    my_orders_raw = await c.get_open_orders(my_addr)
    my_orders = {str(o['oid']): o for o in my_orders_raw}

    # My positions
    my_positions = {
        p['position']['coin']: p['position']
        for p in my_acct.get('assetPositions', [])
    }

    actions = []

    # ── Sync orders ───────────────────────────────────────────────
    # 1. Cancel orders target no longer has
    for target_oid, my_oid in list(paul_orders_map.items()):
        if target_oid not in target_orders:
            if my_oid in my_orders:
                try:
                    await c.cancel_order('BTC', int(my_oid))
                    if lang == 'zh':
                        actions.append(f"🗑 取消挂单 oid={my_oid}（目标已取消）")
                    else:
                        actions.append(f"🗑 Cancelled order oid={my_oid} (target cancelled)")
                except Exception as e:
                    actions.append(f"❌ Cancel failed {my_oid}: {e}")
                await asyncio.sleep(0.2)
            del paul_orders_map[target_oid]

    # 2. Place new orders target has that I don't
    for target_oid, o in target_orders.items():
        if target_oid not in paul_orders_map:
            coin = o.get('coin')
            is_buy = o.get('side') == 'B'
            my_sz = scale_size(float(o['sz']), scale_ratio)
            px = float(o['limitPx'])
            notional = my_sz * px

            if notional < min_order:
                continue  # silent skip

            try:
                r = await c.place_order(coin, is_buy=is_buy, size=my_sz, price=px, order_type='limit')
                statuses = r.get('response', {}).get('data', {}).get('statuses', [{}])
                st = statuses[0]
                if 'resting' in st:
                    my_oid = str(st['resting']['oid'])
                    paul_orders_map[target_oid] = my_oid
                    side_label = '买入' if is_buy else '卖出'
                    if lang == 'zh':
                        actions.append(f"➕ 新增挂单 {side_label} {my_sz} {coin} @ ${px:,.0f}")
                    else:
                        side_label = 'BUY' if is_buy else 'SELL'
                        actions.append(f"➕ New order {side_label} {my_sz} {coin} @ ${px:,.0f}")
                elif 'filled' in st:
                    my_oid = str(st['filled']['oid'])
                    paul_orders_map[target_oid] = my_oid
                    if lang == 'zh':
                        actions.append(f"✅ 成交 {my_sz} {coin} @ ${px:,.0f}")
                    else:
                        actions.append(f"✅ Filled {my_sz} {coin} @ ${px:,.0f}")
            except Exception as e:
                actions.append(f"❌ Order failed: {e}")
            await asyncio.sleep(0.3)

    # ── Sync positions ────────────────────────────────────────────
    # Close positions I have that target no longer has
    for coin, my_pos in my_positions.items():
        if coin not in target_positions:
            try:
                await c.market_close(coin, my_addr)
                if lang == 'zh':
                    actions.append(f"📉 平仓 {coin}（目标已平仓）")
                else:
                    actions.append(f"📉 Closed {coin} (target closed)")
            except Exception as e:
                actions.append(f"❌ Close {coin} failed: {e}")

    # Adjust positions that differ
    for coin, t_pos in target_positions.items():
        t_szi = float(t_pos.get('szi', 0))
        if t_szi == 0: continue
        t_lev = min(int(t_pos.get('leverage', {}).get('value', 1)), max_leverage)
        target_sz = scale_size(abs(t_szi), scale_ratio)
        my_pos = my_positions.get(coin)
        my_szi = float(my_pos.get('szi', 0)) if my_pos else 0.0
        diff = round(target_sz * (1 if t_szi > 0 else -1) - my_szi, 3)

        if abs(diff) >= MIN_BTC_SIZE:
            is_buy = diff > 0
            try:
                await c.update_leverage(coin, t_lev, is_cross=True)
                r = await c.market_open(coin, is_buy=is_buy, size=abs(diff))
                side_label = '加仓' if is_buy else '减仓'
                if lang == 'zh':
                    actions.append(f"📐 {side_label} {abs(diff)} {coin}")
                else:
                    side_label = 'Added' if is_buy else 'Reduced'
                    actions.append(f"📐 {side_label} {abs(diff)} {coin}")
            except Exception as e:
                actions.append(f"❌ Position adj {coin}: {e}")

    # ── Save state & report ───────────────────────────────────────
    state['paul_orders'] = paul_orders_map
    state['last_sync'] = datetime.utcnow().isoformat()
    state['last_account_value'] = my_val
    save_state(state)

    if actions:
        if lang == 'zh':
            print(f"💰 账户余额: ${my_val:.2f} | 距熔断线: ${my_val - stop_value:.2f}")
        else:
            print(f"💰 Account: ${my_val:.2f} | Buffer to stop: ${my_val - stop_value:.2f}")
        for a in actions:
            print(f"  {a}")
    # else: no output → no push notification (save cost)

asyncio.run(main())
