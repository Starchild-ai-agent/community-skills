import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import json, os

with open('/tmp/mc_results.json') as f:
    data = json.load(f)

os.makedirs('output', exist_ok=True)

BG   = '#0d1117'
CARD = '#161b22'
GRN  = '#39d353'
RED  = '#f85149'
BLU  = '#58a6ff'
YEL  = '#f0e68c'
GRY  = '#8b949e'
WHT  = '#e6edf3'

configs = list(data.keys())
medians = [data[c]['median'] for c in configs]
p10s    = [data[c]['p10']    for c in configs]
p90s    = [data[c]['p90']    for c in configs]
avg_dds = [data[c]['avg_dd'] for c in configs]
dd_p90s = [data[c]['max_dd_p90'] for c in configs]

# Short labels
short = ['0.5%|1x','1.0%|1x','0.5%|2x','1.0%|2x','1.5%|2x','2.0%|2x','1.0%|3x','HalfKelly|2x']

fig = plt.figure(figsize=(16,10), facecolor=BG)
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.32,
                         left=0.07, right=0.97, top=0.90, bottom=0.10)

# --- Chart 1: Median final equity (bar) ---
ax1 = fig.add_subplot(gs[0,0])
ax1.set_facecolor(CARD)
colors = [GRN if m > 15000 else BLU if m > 12000 else GRY for m in medians]
bars = ax1.bar(short, medians, color=colors, width=0.6, zorder=3)
ax1.errorbar(short, medians,
             yerr=[np.array(medians)-np.array(p10s), np.array(p90s)-np.array(medians)],
             fmt='none', color=WHT, capsize=4, linewidth=1.2, zorder=4)
ax1.axhline(10000, color=RED, linestyle='--', linewidth=1, alpha=0.7, label='Start $10k')
ax1.set_title('Median Final Equity (100 trades)', color=WHT, fontsize=11, pad=8)
ax1.set_ylabel('Portfolio Value ($)', color=GRY, fontsize=9)
ax1.tick_params(colors=GRY, labelsize=7.5)
ax1.set_xticklabels(short, rotation=30, ha='right', fontsize=7.5)
for spine in ax1.spines.values(): spine.set_edgecolor(GRY)
ax1.yaxis.label.set_color(GRY)
ax1.tick_params(axis='y', colors=GRY)
ax1.tick_params(axis='x', colors=GRY)
ax1.set_facecolor(CARD); ax1.grid(axis='y', color=GRY, alpha=0.15, zorder=0)
ax1.legend(fontsize=8, labelcolor=GRY, facecolor=BG, edgecolor=GRY)
for bar, val in zip(bars, medians):
    ax1.text(bar.get_x()+bar.get_width()/2, bar.get_height()+200,
             f'${val:,.0f}', ha='center', va='bottom', color=WHT, fontsize=7.5, fontweight='bold')

# --- Chart 2: Max drawdown P90 ---
ax2 = fig.add_subplot(gs[0,1])
ax2.set_facecolor(CARD)
dd_colors = [GRN if d < 8 else YEL if d < 15 else RED for d in dd_p90s]
bars2 = ax2.bar(short, dd_p90s, color=dd_colors, width=0.6, zorder=3)
ax2.axhline(10, color=YEL, linestyle='--', linewidth=1, alpha=0.7, label='10% caution')
ax2.axhline(20, color=RED, linestyle='--', linewidth=1, alpha=0.7, label='20% danger')
ax2.set_title('Max Drawdown P90 (worst 10% of runs)', color=WHT, fontsize=11, pad=8)
ax2.set_ylabel('Max Drawdown (%)', color=GRY, fontsize=9)
ax2.tick_params(colors=GRY, labelsize=7.5)
ax2.set_xticklabels(short, rotation=30, ha='right', fontsize=7.5)
for spine in ax2.spines.values(): spine.set_edgecolor(GRY)
ax2.tick_params(axis='y', colors=GRY)
ax2.tick_params(axis='x', colors=GRY)
ax2.grid(axis='y', color=GRY, alpha=0.15, zorder=0)
ax2.legend(fontsize=8, labelcolor=GRY, facecolor=BG, edgecolor=GRY)
for bar, val in zip(bars2, dd_p90s):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3,
             f'{val:.1f}%', ha='center', va='bottom', color=WHT, fontsize=7.5, fontweight='bold')

# --- Chart 3: Return vs Risk scatter ---
ax3 = fig.add_subplot(gs[1,0])
ax3.set_facecolor(CARD)
returns_pct = [(m-10000)/10000*100 for m in medians]
ax3.scatter(avg_dds, returns_pct, c=BLU, s=120, zorder=5, edgecolors=WHT, linewidths=0.8)
for i, s in enumerate(short):
    ax3.annotate(s, (avg_dds[i], returns_pct[i]),
                 textcoords='offset points', xytext=(6,4),
                 color=WHT, fontsize=7.5)
# Highlight sweet spot
ax3.axvspan(0, 8, alpha=0.08, color=GRN, label='Sweet spot')
ax3.set_xlabel('Avg Max Drawdown (%)', color=GRY, fontsize=9)
ax3.set_ylabel('Median Net Return (%)', color=GRY, fontsize=9)
ax3.set_title('Return vs Risk (Efficient Frontier)', color=WHT, fontsize=11, pad=8)
for spine in ax3.spines.values(): spine.set_edgecolor(GRY)
ax3.tick_params(colors=GRY, labelsize=8)
ax3.grid(color=GRY, alpha=0.15)
ax3.legend(fontsize=8, labelcolor=GRY, facecolor=BG, edgecolor=GRY)

# --- Chart 4: Distribution of outcomes for recommended config ---
ax4 = fig.add_subplot(gs[1,1])
ax4.set_facecolor(CARD)
# Recommended: 1.0% | 1x
rec_finals = data['1.0% risk | 1x lev']['finals']
ax4.hist(rec_finals, bins=40, color=GRN, alpha=0.7, edgecolor=BG, linewidth=0.5)
ax4.axvline(10000, color=RED,  linestyle='--', linewidth=1.5, label='Start $10k')
ax4.axvline(np.median(rec_finals), color=YEL, linestyle='-', linewidth=1.5, label=f'Median ${np.median(rec_finals):,.0f}')
ax4.axvline(np.percentile(rec_finals, 10), color=GRY, linestyle=':', linewidth=1.2, label=f'P10 ${np.percentile(rec_finals,10):,.0f}')
ax4.set_title('Outcome Distribution — Recommended (1% | 1x)', color=WHT, fontsize=11, pad=8)
ax4.set_xlabel('Final Portfolio Value ($)', color=GRY, fontsize=9)
ax4.set_ylabel('Frequency', color=GRY, fontsize=9)
for spine in ax4.spines.values(): spine.set_edgecolor(GRY)
ax4.tick_params(colors=GRY, labelsize=8)
ax4.grid(axis='y', color=GRY, alpha=0.15)
ax4.legend(fontsize=8, labelcolor=GRY, facecolor=BG, edgecolor=GRY)

fig.suptitle('SOL 15M Scalp — Position Sizing & Leverage Monte Carlo (2000 sims × 100 trades)',
             color=WHT, fontsize=13, fontweight='bold', y=0.96)

plt.savefig('output/position_sizing.png', dpi=130, facecolor=BG, bbox_inches='tight')
print("Chart saved.")
