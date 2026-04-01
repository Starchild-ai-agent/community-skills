import requests, json, time, pandas as pd, numpy as np

def fetch_candles(coin, interval, hours=1440):
    end = int(time.time() * 1000)
    start = end - hours * 3600 * 1000
    url = "https://api.hyperliquid.xyz/info"
    payload = {"type": "candleSnapshot", "req": {"coin": coin, "interval": interval, "startTime": start, "endTime": end}}
    r = requests.post(url, json=payload, timeout=15)
    data = r.json()
    if not data: return None
    cols = ['t','T','s','i','o','c','h','l','v','n']
    df = pd.DataFrame(data, columns=cols)
    df['open']   = df['o'].astype(float)
    df['close']  = df['c'].astype(float)
    df['high']   = df['h'].astype(float)
    df['low']    = df['l'].astype(float)
    df['volume'] = df['v'].astype(float)
    return df.reset_index(drop=True)

def ema(s, n): return s.ewm(span=n, adjust=False).mean()
def rsi(s, n=14):
    d = s.diff(); g = d.clip(lower=0); l = (-d).clip(lower=0)
    return 100 - 100/(1 + g.ewm(span=n).mean()/l.ewm(span=n).mean())
def vwap(df):
    tp = (df['high'] + df['low'] + df['close']) / 3
    return (tp * df['volume']).cumsum() / df['volume'].cumsum()

def run_backtest(df, account_size, risk_pct, leverage, use_kelly=False, kelly_f=None):
    c = df['close']
    e9 = ema(c, 9); e21 = ema(c, 21); e50 = ema(c, 50)
    e9_1h = ema(c, 36); e21_1h = ema(c, 84)  # 1H proxy on 15M
    rsi_v = rsi(c)
    vol_avg = df['volume'].rolling(5).mean()
    vwap_v = vwap(df)

    trades = []
    equity = account_size
    equity_curve = [account_size]
    peak = account_size
    max_dd = 0.0
    consecutive_losses = 0
    max_consec_losses = 0

    i = 50
    while i < len(df) - 3:
        cross_up   = e9.iloc[i] > e21.iloc[i] and e9.iloc[i-1] <= e21.iloc[i-1]
        cross_down = e9.iloc[i] < e21.iloc[i] and e9.iloc[i-1] >= e21.iloc[i-1]
        above_50   = c.iloc[i] > e50.iloc[i]
        below_50   = c.iloc[i] < e50.iloc[i]
        rsi_long   = 45 <= rsi_v.iloc[i] <= 65
        rsi_short  = 35 <= rsi_v.iloc[i] <= 55
        vol_spike  = df['volume'].iloc[i] >= 1.3 * vol_avg.iloc[i]
        above_vwap = c.iloc[i] > vwap_v.iloc[i]
        below_vwap = c.iloc[i] < vwap_v.iloc[i]
        h1_bull    = e9_1h.iloc[i] > e21_1h.iloc[i]
        h1_bear    = e9_1h.iloc[i] < e21_1h.iloc[i]

        long_sig  = cross_up  and above_50  and rsi_long  and vol_spike and above_vwap and h1_bull
        short_sig = cross_down and below_50 and rsi_short and vol_spike and below_vwap and h1_bear

        direction = None
        if long_sig:  direction = 'long'
        if short_sig: direction = 'short'

        if direction:
            entry = c.iloc[i]
            atr = (df['high'].iloc[i-14:i] - df['low'].iloc[i-14:i]).mean()
            sl_pct  = max(atr / entry, 0.003)
            tp1_pct = sl_pct * 1.5
            tp2_pct = sl_pct * 2.5

            if direction == 'long':
                sl  = entry * (1 - sl_pct)
                tp1 = entry * (1 + tp1_pct)
                tp2 = entry * (1 + tp2_pct)
            else:
                sl  = entry * (1 + sl_pct)
                tp1 = entry * (1 - tp1_pct)
                tp2 = entry * (1 - tp2_pct)

            # Position sizing
            if use_kelly and kelly_f:
                risk_used = min(kelly_f, 0.03)  # cap Kelly at 3%
            else:
                risk_used = risk_pct

            risk_dollars   = equity * risk_used
            position_value = (risk_dollars / sl_pct) * leverage
            fee_in  = position_value * 0.00045
            fee_out = position_value * 0.00045

            # Simulate outcome
            result = 'sl'
            for j in range(i+1, min(i+20, len(df))):
                hi = df['high'].iloc[j]; lo = df['low'].iloc[j]
                if direction == 'long':
                    if lo <= sl:   result = 'sl';  break
                    if hi >= tp2:  result = 'tp2'; break
                    if hi >= tp1:  result = 'tp1'; break
                else:
                    if hi >= sl:   result = 'sl';  break
                    if lo <= tp2:  result = 'tp2'; break
                    if lo <= tp1:  result = 'tp1'; break

            if result == 'tp2':
                pnl = risk_dollars * 2.5 - fee_in - fee_out
                consecutive_losses = 0
            elif result == 'tp1':
                pnl = risk_dollars * 1.5 * 0.5 - fee_in - fee_out * 0.5
                consecutive_losses = 0
            else:
                pnl = -risk_dollars - fee_in - fee_out
                consecutive_losses += 1

            max_consec_losses = max(max_consec_losses, consecutive_losses)
            equity += pnl
            peak = max(peak, equity)
            dd = (peak - equity) / peak
            max_dd = max(max_dd, dd)
            equity_curve.append(equity)
            trades.append({'dir': direction, 'result': result, 'pnl': pnl, 'equity': equity})
            i += 4  # skip forward to avoid re-entry on same move
        else:
            i += 1

    t = pd.DataFrame(trades)
    if t.empty:
        return {'trades': 0}
    wins = len(t[t['result'].isin(['tp1','tp2'])])
    return {
        'trades':       len(t),
        'win_rate':     wins / len(t) * 100,
        'net_pnl_pct':  (equity - account_size) / account_size * 100,
        'final_equity': equity,
        'max_dd':       max_dd * 100,
        'max_consec_l': max_consec_losses,
        'equity_curve': equity_curve,
        'pf':           t[t['pnl']>0]['pnl'].sum() / abs(t[t['pnl']<0]['pnl'].sum()) if len(t[t['pnl']<0]) else 0,
    }

print("Fetching SOL 15M candles (52 days)...")
df = fetch_candles("SOL", "15m", hours=1248)
print(f"Loaded {len(df)} candles\n")

ACCOUNT = 10000

configs = [
    # label,                  risk,   lev,  kelly,  kf
    ("Flat 1% | 3x lev",      0.010,  3,    False,  None),
    ("Flat 0.5% | 3x lev",   0.005,  3,    False,  None),
    ("Flat 1% | 2x lev",      0.010,  2,    False,  None),
    ("Flat 0.5% | 2x lev",   0.005,  2,    False,  None),
    ("Flat 0.25% | 2x lev",  0.0025, 2,    False,  None),
    ("Flat 1% | 1x lev",      0.010,  1,    False,  None),
    ("Flat 0.5% | 1x lev",   0.005,  1,    False,  None),
    ("Kelly 25% | 2x lev",   0.010,  2,    True,   0.025),
    ("Kelly 50% | 2x lev",   0.010,  2,    True,   0.050),
]

print(f"{'Config':<26} {'Trades':>7} {'Win%':>6} {'PF':>5} {'Net%':>7} {'MaxDD%':>8} {'MaxL':>5} {'Final $':>10}")
print("-"*80)

results = {}
for label, risk, lev, kelly, kf in configs:
    r = run_backtest(df, ACCOUNT, risk, lev, kelly, kf)
    if r['trades'] == 0: continue
    print(f"{label:<26} {r['trades']:>7} {r['win_rate']:>5.1f}% {r['pf']:>5.2f} {r['net_pnl_pct']:>6.2f}% {r['max_dd']:>7.2f}% {r['max_consec_l']:>5}  ${r['final_equity']:>9,.0f}")
    results[label] = r
