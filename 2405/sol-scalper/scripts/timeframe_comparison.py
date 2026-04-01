import requests, json, time, pandas as pd, numpy as np

def fetch_candles(coin, interval, n=2000):
    url = "https://api.hyperliquid.xyz/info"
    end = int(time.time() * 1000)
    # for 30m we need more time coverage
    if interval == "30m":
        start = end - 60 * 24 * 3600 * 1000  # 60 days to get ~2880 30m candles
    else:
        start = end - 30 * 24 * 3600 * 1000  # 30 days
    payload = {"type": "candleSnapshot", "req": {"coin": coin, "interval": interval, "startTime": start, "endTime": end}}
    r = requests.post(url, json=payload, timeout=20)
    data = r.json()
    if not data:
        return None
    df = pd.DataFrame(data)
    if df.shape[1] == 10:
        df.columns = ['t','T','s','i','o','c','h','l','v','n']
    else:
        df = pd.DataFrame(data, columns=['t','T','s','i','o','c','h','l','v','n'])
    for col in ['o','c','h','l','v']:
        df[col] = pd.to_numeric(df[col])
    df['t'] = pd.to_datetime(df['t'], unit='ms')
    df = df.sort_values('t').reset_index(drop=True)
    # trim to last 30 days
    cutoff = df['t'].max() - pd.Timedelta(days=30)
    df = df[df['t'] >= cutoff].reset_index(drop=True)
    return df

def compute_indicators(df):
    df['ema9']  = df['c'].ewm(span=9, adjust=False).mean()
    df['ema21'] = df['c'].ewm(span=21, adjust=False).mean()
    df['ema50'] = df['c'].ewm(span=50, adjust=False).mean()
    # RSI
    delta = df['c'].diff()
    gain = delta.clip(lower=0).ewm(span=14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(span=14, adjust=False).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss.replace(0, np.nan)))
    # Volume MA
    df['vol_ma'] = df['v'].rolling(5).mean()
    # VWAP (daily reset)
    df['date'] = df['t'].dt.date
    df['tp'] = (df['h'] + df['l'] + df['c']) / 3
    df['tp_vol'] = df['tp'] * df['v']
    df['cum_tp_vol'] = df.groupby('date')['tp_vol'].cumsum()
    df['cum_vol']    = df.groupby('date')['v'].cumsum()
    df['vwap'] = df['cum_tp_vol'] / df['cum_vol']
    # 1H EMA50 — use rolling approx from the base timeframe
    df['ema50_1h'] = df['c'].ewm(span=50, adjust=False).mean()  # proxy
    # OB detection
    df['body'] = abs(df['c'] - df['o'])
    df['avg_body'] = df['body'].rolling(20).mean()
    df['bull_impulse'] = (df['c'] > df['o']) & (df['body'] > 1.5 * df['avg_body'])
    df['bear_impulse'] = (df['c'] < df['o']) & (df['body'] > 1.5 * df['avg_body'])
    return df

def get_ob_zone(df, idx, direction, lookback=5):
    if idx < lookback:
        return None, None
    if direction == 'long':
        for i in range(idx-1, max(idx-lookback, 0), -1):
            if df['bear_impulse'].iloc[i+1] if i+1 < len(df) else False:
                return df['l'].iloc[i], df['h'].iloc[i]
    else:
        for i in range(idx-1, max(idx-lookback, 0), -1):
            if df['bull_impulse'].iloc[i+1] if i+1 < len(df) else False:
                return df['l'].iloc[i], df['h'].iloc[i]
    return None, None

def run_backtest(df, label):
    results = []
    in_trade = False

    for i in range(52, len(df) - 1):
        row  = df.iloc[i]
        prev = df.iloc[i-1]

        # --- 1H EMA filter (approximate: price vs own ema50)
        above_1h = row['c'] > row['ema50_1h']
        # --- VWAP filter
        above_vwap = row['c'] > row['vwap']
        # --- volume spike
        vol_spike = row['v'] > 1.3 * row['vol_ma']
        # --- EMA cross
        long_cross  = (prev['ema9'] <= prev['ema21']) and (row['ema9'] > row['ema21'])
        short_cross = (prev['ema9'] >= prev['ema21']) and (row['ema9'] < row['ema21'])
        # --- RSI gates
        rsi_long  = 42 <= row['rsi'] <= 68
        rsi_short = 32 <= row['rsi'] <= 58
        # --- above 50 EMA
        above50 = row['c'] > row['ema50']

        if in_trade:
            continue

        # LONG signal
        if long_cross and above50 and rsi_long and vol_spike and above_1h and above_vwap:
            entry  = df.iloc[i+1]['o']
            sl     = entry * (1 - 0.004)
            risk   = entry - sl
            tp1    = entry + risk * 1.5
            tp2    = entry + risk * 2.5
            # sim next 20 candles
            outcome = 'loss'
            exit_p  = sl
            for j in range(i+2, min(i+22, len(df))):
                c = df.iloc[j]
                if c['l'] <= sl:
                    outcome, exit_p = 'loss', sl; break
                if c['h'] >= tp2:
                    outcome, exit_p = 'tp2', tp2; break
                if c['h'] >= tp1:
                    outcome, exit_p = 'tp1', tp1; break
            results.append({'dir':'long','entry':entry,'exit':exit_p,'outcome':outcome,'sl':sl,'tp1':tp1,'tp2':tp2})

        # SHORT signal
        elif short_cross and not above50 and rsi_short and vol_spike and not above_1h and not above_vwap:
            entry  = df.iloc[i+1]['o']
            sl     = entry * (1 + 0.004)
            risk   = sl - entry
            tp1    = entry - risk * 1.5
            tp2    = entry - risk * 2.5
            outcome = 'loss'
            exit_p  = sl
            for j in range(i+2, min(i+22, len(df))):
                c = df.iloc[j]
                if c['h'] >= sl:
                    outcome, exit_p = 'loss', sl; break
                if c['l'] <= tp2:
                    outcome, exit_p = 'tp2', tp2; break
                if c['l'] <= tp1:
                    outcome, exit_p = 'tp1', tp1; break
            results.append({'dir':'short','entry':entry,'exit':exit_p,'outcome':outcome,'sl':sl,'tp1':tp1,'tp2':tp2})

    if not results:
        print(f"{label}: No trades generated.")
        return {}

    df_r = pd.DataFrame(results)
    
    def pnl(row):
        if row['outcome'] == 'tp2':
            return abs(row['tp2'] - row['entry']) / row['entry']
        elif row['outcome'] == 'tp1':
            return abs(row['tp1'] - row['entry']) / row['entry'] * 0.5  # 50% close
        else:
            return -(abs(row['entry'] - row['sl']) / row['entry'])

    df_r['pnl'] = df_r.apply(pnl, axis=1)
    df_r['pnl_fee'] = df_r['pnl'] - 0.0009  # round-trip fees
    
    wins   = df_r[df_r['outcome'].isin(['tp1','tp2'])]
    losses = df_r[df_r['outcome'] == 'loss']
    win_rate = len(wins) / len(df_r) * 100
    gross_win  = wins['pnl'].sum() if len(wins) else 0
    gross_loss = abs(losses['pnl'].sum()) if len(losses) else 0.001
    pf   = gross_win / gross_loss
    net  = df_r['pnl_fee'].sum() * 100

    print(f"\n{'='*45}")
    print(f"  {label}")
    print(f"{'='*45}")
    print(f"  Trades         : {len(df_r)}  ({len(wins)}W / {len(losses)}L)")
    print(f"  Win Rate       : {win_rate:.1f}%")
    print(f"  Profit Factor  : {pf:.2f}")
    print(f"  Net P&L        : {net:+.2f}% (after fees)")
    print(f"  Avg winner     : {wins['pnl'].mean()*100:.3f}%") if len(wins) else None
    print(f"  Avg loser      : {losses['pnl'].mean()*100:.3f}%") if len(losses) else None
    print(f"  Longs / Shorts : {len(df_r[df_r['dir']=='long'])} / {len(df_r[df_r['dir']=='short'])}")

    return {
        'label': label,
        'trades': len(df_r),
        'wins': len(wins),
        'losses': len(losses),
        'win_rate': win_rate,
        'pf': pf,
        'net': net,
        'avg_win': wins['pnl'].mean()*100 if len(wins) else 0,
        'avg_loss': losses['pnl'].mean()*100 if len(losses) else 0,
        'equity': (1 + df_r['pnl_fee']).cumprod().tolist()
    }

print("Fetching SOL 15M candles...")
df15 = fetch_candles("SOL", "15m")
df15 = compute_indicators(df15)
r15  = run_backtest(df15, "15M — 1H EMA + VWAP (current best)")

print("\nFetching SOL 30M candles...")
df30 = fetch_candles("SOL", "30m")
df30 = compute_indicators(df30)
r30  = run_backtest(df30, "30M — 1H EMA + VWAP (same rules)")

# Save equity curves for charting
import pickle
with open('/tmp/tf_results.pkl', 'wb') as f:
    pickle.dump({'r15': r15, 'r30': r30}, f)
