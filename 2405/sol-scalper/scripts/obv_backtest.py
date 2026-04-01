import requests, json, time, pandas as pd, numpy as np

def fetch_candles(coin, interval, hours=720):
    end = int(time.time() * 1000)
    start = end - hours * 3600 * 1000
    url = "https://api.hyperliquid.xyz/info"
    payload = {"type": "candleSnapshot", "req": {"coin": coin, "interval": interval, "startTime": start, "endTime": end}}
    r = requests.post(url, json=payload, timeout=15)
    data = r.json()
    rows = []
    for c in data:
        rows.append({
            'ts':     c['t'],
            'open':   float(c['o']),
            'high':   float(c['h']),
            'low':    float(c['l']),
            'close':  float(c['c']),
            'volume': float(c['v']),
        })
    df = pd.DataFrame(rows)
    df['ts'] = pd.to_datetime(df['ts'], unit='ms')
    return df.reset_index(drop=True)

def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()

def rsi(s, n=14):
    d = s.diff()
    g = d.clip(lower=0).ewm(span=n, adjust=False).mean()
    l = (-d.clip(upper=0)).ewm(span=n, adjust=False).mean()
    return 100 - 100 / (1 + g / l.replace(0, 1e-9))

def calc_obv(close, volume):
    o = [0.0]
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            o.append(o[-1] + volume.iloc[i])
        elif close.iloc[i] < close.iloc[i-1]:
            o.append(o[-1] - volume.iloc[i])
        else:
            o.append(o[-1])
    return pd.Series(o, index=close.index)

print("Fetching SOL 15M candles (30 days)...")
df = fetch_candles("SOL", "15m", hours=720)
print(f"Loaded: {len(df)} candles")

# --- Indicators ---
df['ema9']     = ema(df['close'], 9)
df['ema21']    = ema(df['close'], 21)
df['ema50']    = ema(df['close'], 50)
df['rsi']      = rsi(df['close'])
df['vol_avg']  = df['volume'].rolling(5).mean()
df['vol_spike']= df['volume'] > df['vol_avg'] * 1.3
df['obv']      = calc_obv(df['close'], df['volume'])
df['obv_ema20']= ema(df['obv'], 20)
df['obv_bull'] = df['obv'] > df['obv_ema20']
df['obv_bear'] = df['obv'] < df['obv_ema20']

df['cross_up']   = (df['ema9'] > df['ema21']) & (df['ema9'].shift(1) <= df['ema21'].shift(1))
df['cross_down'] = (df['ema9'] < df['ema21']) & (df['ema9'].shift(1) >= df['ema21'].shift(1))
df['above50']    = df['close'] > df['ema50']

def backtest(df, use_obv=False):
    trades = []
    in_trade = False
    direction = None
    entry = sl = tp1 = tp2 = 0.0
    tp1_hit = False

    for i in range(52, len(df) - 1):
        row  = df.iloc[i]
        next_row = df.iloc[i + 1]

        if in_trade:
            hi = next_row['high']
            lo = next_row['low']

            if direction == 'long':
                if lo <= sl:
                    pnl = (sl - entry) / entry
                    trades.append({'result': 'loss', 'pnl': pnl})
                    in_trade = False
                elif hi >= tp2:
                    # TP1 half (1.5R) + TP2 half (2.5R) = avg 2R
                    pnl = ((tp1 - entry) / entry * 0.5) + ((tp2 - entry) / entry * 0.5)
                    trades.append({'result': 'tp2', 'pnl': pnl})
                    in_trade = False
                elif hi >= tp1 and not tp1_hit:
                    tp1_hit = True
                    sl = entry  # move SL to breakeven
            else:
                if hi >= sl:
                    pnl = (entry - sl) / entry
                    trades.append({'result': 'loss', 'pnl': pnl})
                    in_trade = False
                elif lo <= tp2:
                    pnl = ((entry - tp1) / entry * 0.5) + ((entry - tp2) / entry * 0.5)
                    trades.append({'result': 'tp2', 'pnl': pnl})
                    in_trade = False
                elif lo <= tp1 and not tp1_hit:
                    tp1_hit = True
                    sl = entry
            continue

        rsi_val = row['rsi']

        # LONG signal
        if (row['cross_up'] and row['above50'] and
                45 <= rsi_val <= 65 and row['vol_spike']):
            if use_obv and not row['obv_bull']:
                continue
            in_trade  = True
            direction = 'long'
            entry     = row['close']
            atr = (df.iloc[i-14:i]['high'] - df.iloc[i-14:i]['low']).mean()
            sl  = entry - atr * 0.8
            tp1 = entry + (entry - sl) * 1.5
            tp2 = entry + (entry - sl) * 2.5
            tp1_hit = False

        # SHORT signal
        elif (row['cross_down'] and not row['above50'] and
              35 <= rsi_val <= 55 and row['vol_spike']):
            if use_obv and not row['obv_bear']:
                continue
            in_trade  = True
            direction = 'short'
            entry     = row['close']
            atr = (df.iloc[i-14:i]['high'] - df.iloc[i-14:i]['low']).mean()
            sl  = entry + atr * 0.8
            tp1 = entry - (sl - entry) * 1.5
            tp2 = entry - (sl - entry) * 2.5
            tp1_hit = False

    total    = len(trades)
    winners  = [t for t in trades if t['result'] == 'tp2']
    losses   = [t for t in trades if t['result'] == 'loss']
    win_rate = len(winners) / total * 100 if total else 0
    avg_win  = np.mean([t['pnl'] for t in winners]) * 100 if winners else 0
    avg_loss = abs(np.mean([t['pnl'] for t in losses]) * 100) if losses else 0
    pf       = (len(winners) * avg_win) / (len(losses) * avg_loss) if losses and avg_loss else 0
    net      = sum(t['pnl'] for t in trades) * 100
    # Assume 1% risk per trade, fees ~0.045% taker per side
    fee_drag = total * 0.09  # 0.045% in + 0.045% out
    net_after_fees = net - fee_drag

    return {
        'total': total,
        'winners': len(winners),
        'losses': len(losses),
        'win_rate': round(win_rate, 1),
        'avg_win_pct': round(avg_win, 3),
        'avg_loss_pct': round(avg_loss, 3),
        'profit_factor': round(pf, 2),
        'net_pnl_pct': round(net, 2),
        'fee_drag_pct': round(fee_drag, 2),
        'net_after_fees': round(net_after_fees, 2),
    }

base    = backtest(df, use_obv=False)
with_obv = backtest(df, use_obv=True)

print("\n=== BASELINE (no OBV) ===")
for k, v in base.items():
    print(f"  {k:25s}: {v}")

print("\n=== + OBV TREND FILTER ===")
for k, v in with_obv.items():
    print(f"  {k:25s}: {v}")

print("\n=== DELTA (OBV - Baseline) ===")
for k in base:
    delta = round(with_obv[k] - base[k], 2) if isinstance(base[k], (int, float)) else "n/a"
    print(f"  {k:25s}: {delta:+}")
