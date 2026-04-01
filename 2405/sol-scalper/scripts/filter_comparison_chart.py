import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

os.makedirs('output', exist_ok=True)

BG    = '#0d1117'
CARD  = '#161b22'
GREEN = '#3fb950'
RED   = '#f85149'
BLUE  = '#58a6ff'
GOLD  = '#e3b341'
GRAY  = '#8b949e'
WHITE = '#e6edf3'

labels  = ['Baseline\n(current)', '+1H EMA\nfilter', '+VWAP\nfilter', '+1H EMA\n+VWAP']
trades  = [38, 26, 35, 25]
wins    = [13, 11, 12, 11]
losses  = [25, 15, 23, 14]
wr      = [34.2, 42.3, 34.3, 44.0]
pf      = [1.85, 2.08, 1.84, 2.20]
net_fee = [2.80, 3.52, 2.67, 3.91]

x = np.arange(len(labels))
w = 0.35

fig, axes = plt.subplots(1, 3, figsize=(16, 7))
fig.patch.set_facecolor(BG)
for ax in axes:
    ax.set_facecolor(CARD)
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.spines['bottom'].set_color('#30363d')
    ax.spines['left'].set_color('#30363d')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# ---------- Chart 1: Win rate ----------
colors_wr = [GREEN if v > 34.2 else BLUE for v in wr]
bars = axes[0].bar(x, wr, color=colors_wr, width=0.55, zorder=3, edgecolor='none')
axes[0].set_xticks(x)
axes[0].set_xticklabels(labels, color=WHITE, fontsize=8.5)
axes[0].set_ylabel('Win Rate %', color=GRAY, fontsize=9)
axes[0].set_title('Win Rate', color=WHITE, fontsize=12, pad=10)
axes[0].axhline(34.2, color=GRAY, linewidth=1, linestyle='--', zorder=2, alpha=0.5)
axes[0].set_ylim(0, 55)
axes[0].yaxis.label.set_color(GRAY)
axes[0].grid(axis='y', color='#30363d', linewidth=0.5, zorder=1)
for bar, val in zip(bars, wr):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
                 f'{val:.1f}%', ha='center', va='bottom', color=WHITE, fontsize=10, fontweight='bold')

# ---------- Chart 2: Profit Factor ----------
colors_pf = [GREEN if v > 1.85 else BLUE for v in pf]
bars2 = axes[1].bar(x, pf, color=colors_pf, width=0.55, zorder=3, edgecolor='none')
axes[1].set_xticks(x)
axes[1].set_xticklabels(labels, color=WHITE, fontsize=8.5)
axes[1].set_ylabel('Profit Factor', color=GRAY, fontsize=9)
axes[1].set_title('Profit Factor', color=WHITE, fontsize=12, pad=10)
axes[1].axhline(1.85, color=GRAY, linewidth=1, linestyle='--', zorder=2, alpha=0.5)
axes[1].set_ylim(0, 2.8)
axes[1].grid(axis='y', color='#30363d', linewidth=0.5, zorder=1)
for bar, val in zip(bars2, pf):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
                 f'{val:.2f}', ha='center', va='bottom', color=WHITE, fontsize=10, fontweight='bold')

# ---------- Chart 3: Net P&L after fees ----------
colors_nl = [GREEN if v >= max(net_fee) else (GOLD if v > net_fee[0] else BLUE) for v in net_fee]
bars3 = axes[2].bar(x, net_fee, color=colors_nl, width=0.55, zorder=3, edgecolor='none')
axes[2].set_xticks(x)
axes[2].set_xticklabels(labels, color=WHITE, fontsize=8.5)
axes[2].set_ylabel('Net P&L after fees %', color=GRAY, fontsize=9)
axes[2].set_title('Net P&L (after fees)', color=WHITE, fontsize=12, pad=10)
axes[2].axhline(net_fee[0], color=GRAY, linewidth=1, linestyle='--', zorder=2, alpha=0.5)
axes[2].set_ylim(0, 5.5)
axes[2].grid(axis='y', color='#30363d', linewidth=0.5, zorder=1)
for bar, val in zip(bars3, net_fee):
    axes[2].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                 f'+{val:.2f}%', ha='center', va='bottom', color=WHITE, fontsize=10, fontweight='bold')

# W/L trade count overlay on chart 1
for i, (w_count, l_count) in enumerate(zip(wins, losses)):
    axes[0].text(x[i], 1.5, f'{w_count}W/{l_count}L', ha='center', va='bottom',
                 color=BG, fontsize=8, fontweight='bold')

# ---------- Legend / title ----------
baseline_patch = mpatches.Patch(color=BLUE, label='Baseline level')
improved_patch  = mpatches.Patch(color=GREEN, label='Best result')
gold_patch      = mpatches.Patch(color=GOLD, label='Improved')
fig.legend(handles=[baseline_patch, gold_patch, improved_patch],
           loc='lower center', ncol=3, frameon=False,
           labelcolor=WHITE, fontsize=9, bbox_to_anchor=(0.5, -0.02))

fig.suptitle('SOL 15M Scalping — Filter Comparison (30-day backtest)',
             color=WHITE, fontsize=14, fontweight='bold', y=1.01)

plt.tight_layout()
plt.savefig('output/filter_comparison.png', dpi=150, bbox_inches='tight',
            facecolor=BG)
print("Chart saved.")
