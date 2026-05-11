#!/usr/bin/env python3
"""
HL Copy Trader — Weekly Report
Called by a separate scheduled task every Sunday UTC 00:00.

Usage:
  python3 weekly_report.py --state-dir /data/workspace/tasks/{job_id}
"""
import asyncio, sys, json, argparse
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, '/data/workspace')
from skills.hyperliquid.client import HyperliquidClient

parser = argparse.ArgumentParser()
parser.add_argument('--state-dir', required=True)
args = parser.parse_args()
STATE_FILE = Path(args.state_dir) / 'state.json'

async def main():
    if not STATE_FILE.exists():
        print("No state file found.")
        return

    state = json.loads(STATE_FILE.read_text())
    lang = state.get('lang', 'zh')
    c = HyperliquidClient()
    my_addr = await c._get_address()
    target_addr = state['target_address']
    my_capital = state['my_capital']
    stop_value = state['stop_value']

    # Fetch current states
    my_acct, target_acct = await asyncio.gather(
        c.get_account_state(my_addr),
        c.get_account_state(target_addr),
    )
    my_val = float(my_acct.get('marginSummary', {}).get('accountValue', 0))
    target_val = float(target_acct.get('marginSummary', {}).get('accountValue', 0))

    # Fills this week
    now = datetime.now(timezone.utc)
    week_ago = int((now - timedelta(days=7)).timestamp() * 1000)
    my_fills = await c._info('userFills', user=my_addr)

    if isinstance(my_fills, list):
        week_fills = [f for f in my_fills if f.get('time', 0) >= week_ago]
        week_pnl = sum(float(f.get('closedPnl', 0)) for f in week_fills)
        week_trades = len(week_fills)
    else:
        week_pnl = 0
        week_trades = 0

    my_pct = ((my_val - my_capital) / my_capital * 100)
    week_pct = (week_pnl / my_capital * 100)

    if lang == 'zh':
        print(f"""
📊 每周跟单报告 — {now.strftime('%Y-%m-%d')}
{'='*45}
本周收益:    ${week_pnl:+.2f} ({week_pct:+.2f}%)
本周交易次数: {week_trades} 笔
{'─'*45}
账户总值:    ${my_val:,.2f}
起始本金:    ${my_capital:,.2f}
总收益率:    {my_pct:+.2f}%
距熔断线:    ${my_val - stop_value:,.2f}（安全线 ${stop_value:,.2f}）
{'─'*45}
目标交易员账户: ${target_val:,.2f}
缩放比例:       1 : {1/state['scale_ratio']:.0f}
{'='*45}
💡 建议: {'策略运行正常，继续监控' if my_pct > -10 else '注意回撤，考虑减少仓位或暂停跟单'}
        """)
    else:
        print(f"""
📊 Weekly Copy Trade Report — {now.strftime('%Y-%m-%d')}
{'='*45}
Week PnL:      ${week_pnl:+.2f} ({week_pct:+.2f}%)
Week trades:   {week_trades}
{'─'*45}
Account value: ${my_val:,.2f}
Starting cap:  ${my_capital:,.2f}
Total return:  {my_pct:+.2f}%
Buffer to stop: ${my_val - stop_value:,.2f} (stop at ${stop_value:,.2f})
{'─'*45}
Target account: ${target_val:,.2f}
Scale ratio:    1 : {1/state['scale_ratio']:.0f}
{'='*45}
💡 Suggestion: {'Strategy running well, continue monitoring' if my_pct > -10 else 'Watch drawdown — consider reducing size or pausing'}
        """)

asyncio.run(main())
