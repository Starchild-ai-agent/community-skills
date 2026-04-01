import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs('output', exist_ok=True)

configs = [
    "Baseline\n(1H EMA+VWAP)",
    "+ ADX > 20",
    "+ ADX > 25",
    "+ Stoch RSI",
    "+ BB\nMid-Zone",
    "+ ATR\nDyn Stops",
    "ADX>20\n+StochRSI",
    "ADX>20+StochRSI\n+ATR",
]

trades  = [22, 15,  9, 11,  4, 22,  7,  7]
winrate = [63.6, 60.0, 55.6, 72.7, 25.0, 59.1, 57.1, 42.9]
pf      = [1.96, 2.05, 1.64, 1.77, 0.22, 1.39, 0.89, 0.48]
net     = [8.68, 7.16, 2.79, 2.50, -2.42, 6.11, -0.34, -4.30]

BG   = '#0d1117'
CARD = '#161b22'
GREEN = '#39d353'
RED   = '#f85149'
GOLD  = '#f0c040'
BLUE  = '#58a6ff'
GRAY  = '#8b949e'
WHITE = '#e6edf3'

fig, axes = plt.subplots(1, 3, figsize=(18, 7))
fig.patch.set_facecolor(BG)
fig.suptitle('SOL 15M — Indicator Filter Comparison (52 days)', color=WHITE, fontsize=15, fontweight='bold', y=1.0)

x = np.arange(len(configs))
bar_colors = [GREEN if n >= 0 else RED for n in net]
bar_colors[0] = BLUE  # baseline

for ax in axes:
    ax.set_facecolor(CARD)
    ax.tick_params(colors=GRAY, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#30363d')
    ax.set_xticks(x)
    ax.set_xticklabels(configs, color=GRAY, fontsize=7.5)
    ax.yaxis.label.set_color(GRAY)
    ax.grid(axis='y', color='#21262d', linewidth=0.6)

# Win Rate
bars0 = axes[0].bar(x, winrate, color=bar_colors, width=0.6, zorder=3)
axes[0].axhline(50, color=GRAY, linestyle='--', linewidth=0.8, alpha=0.6, label='50% threshold')
axes[0].set_title('Win Rate (%)', color=WHITE, fontsize=11, pad=8)
axes[0].set_ylim(0, 90)
for bar, v in zip(bars0, winrate):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                 f'{v:.0f}%', ha='center', va='bottom', color=WHITE, fontsize=8, fontweight='bold')

# Profit Factor
bars1 = axes[1].bar(x, pf, color=bar_colors, width=0.6, zorder=3)
axes[1].axhline(1.0, color=GRAY, linestyle='--', linewidth=0.8, alpha=0.6, label='Breakeven PF=1')
axes[1].set_title('Profit Factor', color=WHITE, fontsize=11, pad=8)
axes[1].set_ylim(0, 2.8)
for bar, v in zip(bars1, pf):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
                 f'{v:.2f}', ha='center', va='bottom', color=WHITE, fontsize=8, fontweight='bold')

# Net P&L
bars2 = axes[2].bar(x, net, color=bar_colors, width=0.6, zorder=3)
axes[2].axhline(0, color=GRAY, linestyle='--', linewidth=0.8, alpha=0.6)
axes[2].set_title('Net P&L % (after fees)', color=WHITE, fontsize=11, pad=8)
axes[2].set_ylim(-7, 12)
for bar, v in zip(bars2, net):
    offset = 0.2 if v >= 0 else -0.6
    axes[2].text(bar.get_x() + bar.get_width()/2, v + offset,
                 f'{v:+.1f}%', ha='center', va='bottom', color=WHITE, fontsize=8, fontweight='bold')

# Annotation boxes
for ax, col, data in [(axes[0], GREEN, winrate), (axes[1], GOLD, pf), (axes[2], GREEN, net)]:
    best_i = int(np.argmax(data))
    bar = ax.patches[best_i]
    ax.annotate('BEST', xy=(bar.get_x() + bar.get_width()/2, bar.get_height()),
                xytext=(0, 14), textcoords='offset points',
                ha='center', color=GOLD, fontsize=7.5, fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.0))

# Trade count below x-axis
for ax in axes:
    for xi, t in zip(x, trades):
        ax.text(xi, -6.5 if ax == axes[2] else -8,
                f'n={t}', ha='center', color=GRAY, fontsize=7, transform=ax.get_xaxis_transform())

# Legend box
legend_text = (
    "  Blue = Baseline  |  Green = Profitable  |  Red = Unprofitable  |  BEST = highest in category\n"
    "  n = number of trades over 52 days  |  52-day SOL backtest with 1H EMA + VWAP already applied"
)
fig.text(0.5, -0.04, legend_text, ha='center', color=GRAY, fontsize=8.5)

plt.tight_layout(rect=[0, 0.04, 1, 0.97])
plt.savefig('output/indicator_comparison.png', dpi=150, bbox_inches='tight',
            facecolor=BG, edgecolor='none')
print("Chart saved.")
