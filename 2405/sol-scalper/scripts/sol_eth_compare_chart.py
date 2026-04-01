import pandas as pd, numpy as np, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

os.makedirs('output', exist_ok=True)

BG     = '#131722'
GRID   = '#1e222d'
TEXT   = '#d1d4dc'
GREEN  = '#26a69a'
RED    = '#ef5350'

sol_eq = pd.read_csv('/tmp/equity_curve.csv', header=0, names=['eq'])['eq']
eth_eq = pd.read_csv('/tmp/eth_equity.csv',   header=0, names=['eq'])['eq']
sol_tr = pd.read_csv('/tmp/trades.csv')
eth_tr = pd.read_csv('/tmp/eth_trades.csv')

fig = plt.figure(figsize=(16, 12), facecolor=BG)
fig.patch.set_facecolor(BG)
gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.5, wspace=0.35)

def style(ax, title):
    ax.set_facecolor(BG)
    ax.set_title(title, color=TEXT, fontsize=10, pad=6)
    ax.tick_params(colors=TEXT, labelsize=8)
    for s in ax.spines.values(): s.set_edgecolor(GRID)
    ax.grid(True, color=GRID, linestyle=':', alpha=0.5)

# Row 1: Equity curves
ax1 = fig.add_subplot(gs[0, 0])
style(ax1, '\nSOL — Equity Curve')
v = sol_eq.values
x = range(len(v))
ax1.plot(x, v, color=GREEN, lw=1.8)
ax1.fill_between(x, 10000, v, where=(v >= 10000), alpha=0.12, color=GREEN)
ax1.fill_between(x, 10000, v, where=(v < 10000),  alpha=0.12, color=RED)
ax1.axhline(10000, color=TEXT, lw=0.5, ls='--', alpha=0.4)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f'${val:,.0f}'))
ax1.set_ylabel('Account ($)', color=TEXT, fontsize=8)
ax1.annotate('+7.80%  10,780', xy=(len(v)-1, v[-1]),
             xytext=(len(v)-300, v[-1]+80), color=GREEN, fontsize=8, fontweight='bold')

ax2 = fig.add_subplot(gs[0, 1])
style(ax2, '\nETH — Equity Curve')
v2 = eth_eq.values
x2 = range(len(v2))
ax2.plot(x2, v2, color=RED, lw=1.8)
ax2.fill_between(x2, 10000, v2, where=(v2 >= 10000), alpha=0.12, color=GREEN)
ax2.fill_between(x2, 10000, v2, where=(v2 < 10000),  alpha=0.12, color=RED)
ax2.axhline(10000, color=TEXT, lw=0.5, ls='--', alpha=0.4)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda val, _: f'${val:,.0f}'))
ax2.set_ylabel('Account ($)', color=TEXT, fontsize=8)
ax2.annotate('-12.13%  8,787', xy=(len(v2)-1, v2[-1]),
             xytext=(len(v2)-300, v2[-1]-200), color=RED, fontsize=8, fontweight='bold')

# Row 2: Drawdowns
ax3 = fig.add_subplot(gs[1, 0])
style(ax3, 'SOL — Drawdown (%)')
sol_dd = (sol_eq - sol_eq.cummax()) / sol_eq.cummax() * 100
ax3.fill_between(range(len(sol_dd)), sol_dd.values, 0, color=RED, alpha=0.5)
ax3.plot(range(len(sol_dd)), sol_dd.values, color=RED, lw=1)
ax3.set_ylabel('%', color=TEXT, fontsize=8)
idx = int(sol_dd.idxmin())
ax3.annotate(f'Max: {sol_dd.min():.1f}%', xy=(idx, sol_dd.min()),
             xytext=(idx+100, sol_dd.min()+2.5),
             color=RED, fontsize=8, arrowprops=dict(arrowstyle='->', color=RED, lw=0.8))

ax4 = fig.add_subplot(gs[1, 1])
style(ax4, 'ETH — Drawdown (%)')
eth_dd = (eth_eq - eth_eq.cummax()) / eth_eq.cummax() * 100
ax4.fill_between(range(len(eth_dd)), eth_dd.values, 0, color=RED, alpha=0.5)
ax4.plot(range(len(eth_dd)), eth_dd.values, color=RED, lw=1)
ax4.set_ylabel('%', color=TEXT, fontsize=8)
idx2 = int(eth_dd.idxmin())
ax4.annotate(f'Max: {eth_dd.min():.1f}%', xy=(idx2, eth_dd.min()),
             xytext=(idx2+100, eth_dd.min()+3),
             color=RED, fontsize=8, arrowprops=dict(arrowstyle='->', color=RED, lw=0.8))

# Row 3: P&L per trade
ax5 = fig.add_subplot(gs[2, 0])
style(ax5, 'SOL — P&L per Trade ($)')
sol_pnl = sol_tr.sort_values('time')['pnl'].values
cols = [GREEN if p > 0 else RED for p in sol_pnl]
ax5.bar(range(len(sol_pnl)), sol_pnl, color=cols, edgecolor='none', width=0.85)
ax5.axhline(0, color=TEXT, lw=0.5, ls='--', alpha=0.5)
ax5.set_xlabel('Trade #', color=TEXT, fontsize=8)
ax5.set_ylabel('P&L ($)', color=TEXT, fontsize=8)

ax6 = fig.add_subplot(gs[2, 1])
style(ax6, 'ETH — P&L per Trade ($)')
eth_pnl = eth_tr.sort_values('time')['pnl'].values
cols2 = [GREEN if p > 0 else RED for p in eth_pnl]
ax6.bar(range(len(eth_pnl)), eth_pnl, color=cols2, edgecolor='none', width=0.85)
ax6.axhline(0, color=TEXT, lw=0.5, ls='--', alpha=0.5)
ax6.set_xlabel('Trade #', color=TEXT, fontsize=8)
ax6.set_ylabel('P&L ($)', color=TEXT, fontsize=8)

fig.suptitle('\n15M Scalping Backtest — SOL vs ETH  (30 Days, $10k Start, 1% Risk/Trade)',
             color=TEXT, fontsize=13, fontweight='bold')

footer = (
    "SOL: Signals 43 | Completed 34 | Win 32.4% | PF 1.39 | Net +780 (+7.8%) | MaxDD -6.4%"
    "          ||          "
    "ETH: Signals 35 | Completed 31 | Win 12.9% | PF 0.48 | Net -1,213 (-12.1%) | MaxDD -13.9%"
)
fig.text(0.5, 0.005, footer, ha='center', color=TEXT, fontsize=8.5,
         math_fontfamily='dejavusans', usetex=False,
         bbox=dict(boxstyle='round,pad=0.4', facecolor=GRID, edgecolor=GRID))

plt.savefig('output/sol_vs_eth_backtest.png', facecolor=BG, edgecolor=BG, dpi=140, bbox_inches='tight')
print("Chart saved.")
