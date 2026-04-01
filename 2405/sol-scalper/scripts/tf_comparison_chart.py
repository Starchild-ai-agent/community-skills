import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import pickle
import numpy as np
import os

with open('/tmp/tf_results.pkl', 'rb') as f:
    data = pickle.load(f)

r15 = data['r15']
r30 = data['r30']

BG   = '#0d1117'
CARD = '#161b22'
GRN  = '#39d353'
RED  = '#f85149'
YLW  = '#e3b341'
BLUE = '#58a6ff'
TXT  = '#c9d1d9'
MUT  = '#8b949e'

fig = plt.figure(figsize=(14, 9), facecolor=BG)
gs  = gridspec.GridSpec(2, 2, figure=fig, hspace=0.55, wspace=0.35,
                        left=0.07, right=0.97, top=0.88, bottom=0.08)

# ── Equity curves ──────────────────────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :])
ax1.set_facecolor(CARD)

eq15 = r15.get('equity', [1])
eq30 = r30.get('equity', [1])

x15 = np.linspace(0, 100, len(eq15))
x30 = np.linspace(0, 100, len(eq30))

ax1.plot(x15, [v * 10000 for v in eq15], color=BLUE, lw=2.2, label='15M (+0.14%)', zorder=3)
ax1.plot(x30, [v * 10000 for v in eq30], color=RED,  lw=2.2, label='30M (-1.89%)', zorder=3, linestyle='--')
ax1.axhline(10000, color=MUT, lw=0.8, linestyle=':')
ax1.fill_between(x15, 10000, [v * 10000 for v in eq15],
                 where=[v >= 1 for v in eq15], alpha=0.12, color=BLUE)
ax1.fill_between(x30, 10000, [v * 10000 for v in eq30],
                 where=[v < 1 for v in eq30], alpha=0.12, color=RED)

ax1.set_title('Equity Curve — 15M vs 30M  |  SOL SCALP  |  30 Days', color=TXT, fontsize=13, pad=10)
ax1.set_ylabel('Account Value ($)', color=MUT, fontsize=9)
ax1.set_xlabel('Trade Progression (%)', color=MUT, fontsize=9)
ax1.tick_params(colors=MUT)
ax1.legend(fontsize=10, facecolor=CARD, labelcolor=TXT, edgecolor=MUT)
for sp in ax1.spines.values():
    sp.set_edgecolor(MUT)
ax1.yaxis.label.set_color(MUT)

# ── Bar: Win Rate ───────────────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, 0])
ax2.set_facecolor(CARD)
bars = ax2.bar(['15M', '30M'], [r15['win_rate'], r30['win_rate']],
               color=[BLUE, RED], width=0.45, zorder=3)
ax2.axhline(50, color=MUT, linestyle='--', lw=0.8)
for bar, val in zip(bars, [r15['win_rate'], r30['win_rate']]):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
             f'{val:.1f}%', ha='center', color=TXT, fontsize=12, fontweight='bold')
ax2.set_title('Win Rate', color=TXT, fontsize=11)
ax2.set_ylim(0, 80)
ax2.tick_params(colors=MUT)
for sp in ax2.spines.values():
    sp.set_edgecolor(MUT)
ax2.set_facecolor(CARD)

# ── Bar: Profit Factor ──────────────────────────────────────────────────────────
ax3 = fig.add_subplot(gs[1, 1])
ax3.set_facecolor(CARD)
bars2 = ax3.bar(['15M', '30M'], [r15['pf'], r30['pf']],
                color=[BLUE, RED], width=0.45, zorder=3)
ax3.axhline(1.0, color=YLW, linestyle='--', lw=0.8, label='Break-even')
for bar, val in zip(bars2, [r15['pf'], r30['pf']]):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
             f'{val:.2f}', ha='center', color=TXT, fontsize=12, fontweight='bold')
ax3.set_title('Profit Factor', color=TXT, fontsize=11)
ax3.set_ylim(0, 2.5)
ax3.tick_params(colors=MUT)
ax3.legend(fontsize=8, facecolor=CARD, labelcolor=TXT, edgecolor=MUT)
for sp in ax3.spines.values():
    sp.set_edgecolor(MUT)

# ── Stats table ─────────────────────────────────────────────────────────────────
stats = [
    ('Timeframe',       '15M',                    '30M'),
    ('Trades',          str(r15['trades']),        str(r30['trades'])),
    ('Win Rate',        f"{r15['win_rate']:.1f}%", f"{r30['win_rate']:.1f}%"),
    ('Profit Factor',   f"{r15['pf']:.2f}",        f"{r30['pf']:.2f}"),
    ('Net P&L (fees)',  f"+{r15['net']:.2f}%",     f"{r30['net']:.2f}%"),
    ('Avg Winner',      f"{r15['avg_win']:.3f}%",  f"{r30['avg_win']:.3f}%"),
    ('Avg Loser',       f"{r15['avg_loss']:.3f}%", f"{r30['avg_loss']:.3f}%"),
    ('Verdict',         'KEEP',                    'SKIP'),
]

fig.text(0.5, 0.965,
         '15M wins on win rate, profit factor & net P&L — 30M is NOT an improvement',
         ha='center', color=YLW, fontsize=10)

os.makedirs('output', exist_ok=True)
plt.savefig('output/tf_comparison.png', dpi=150, bbox_inches='tight', facecolor=BG)
print("Chart saved.")
