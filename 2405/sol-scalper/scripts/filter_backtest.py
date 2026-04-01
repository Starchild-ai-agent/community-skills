import requests, json, time, pandas as pd, numpy as np

def fetch_candles(coin, interval, limit=2881):
    url = "https://api.hyperliquid.xyz/info"
    end_ms = int(time.time() * 1000)
    # 15m candles: 2881 covers ~30 days
    start_ms = end_ms - (limit * 15 * 60 * 1000)
    body = {"type": "candleSnapshot", "req": {"coin": coin, "interval": interval, "startTime": start_ms, "endTime": end_ms}}
    r = requests.post(url, json=body, timeout=15)
    raw = r.json()
    cols = ['t','T','s','i','o','c','h','l','v','n']
    if isinstance(raw[0], dict):
        df = pd.DataFrame(raw)
    else:
        df = pd.DataFrame(raw, columns=cols)
    df = df.rename(columns={'o':'open','h':'high','l':'low','c':'close','v':'volume','t':'time'})
    for col in ['open','high','low','close','volume']:
        df[col] = df[col].astype(float)
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df.sort_values('time').reset_index(drop=True)
    return df

def fetch_1h_candles(coin, limit=720):
    url = "https://api.hyperliquid.xyz/info"
    end_ms = int(time.time() * 1000)
    start_ms = end_ms - (limit * 60 * 60 * 1000)
    body = {"type": "candleSnapshot", "req": {"coin": coin, "interval": "1h", "startTime": start_ms, "endTime": end_ms}}
    r = requests.post(url, json=body, timeout=15)
    raw = r.json()
    cols = ['t','T','s','i','o','c','h','l','v','n']
    if isinstance(raw[0], dict):
        df = pd.DataFrame(raw)
    else:
        df = pd.DataFrame(raw, columns=cols)
    df = df.rename(columns={'o':'open','h':'high','l':'low','c':'close','v':'volume','t':'time'})
    for col in ['open','high','low','close','volume']:
        df[col] = df[col].astype(float)
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df.sort_values('time').reset_index(drop=True)
    return df

def add_indicators(df):
    df['ema9']  = df['close'].ewm(span=9, adjust=False).mean()
    df['ema21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()
    delta = df['close'].diff()
    gain = delta.clip(lower=0).ewm(com=13, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(com=13, adjust=False).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss.replace(0, 1e-9)))
    df['vol_avg'] = df['volume'].rolling(5).mean()
    df['cross_up']   = (df['ema9'] > df['ema21']) & (df['ema9'].shift(1) <= df['ema21'].shift(1))
    df['cross_down'] = (df['ema9'] < df['ema21']) & (df['ema9'].shift(1) >= df['ema21'].shift(1))
    # VWAP — reset daily
    df['date'] = df['time'].dt.date
    df['tp'] = (df['high'] + df['low'] + df['close']) / 3
    df['tp_vol'] = df['tp'] * df['volume']
    df['cum_tp_vol'] = df.groupby('date')['tp_vol'].cumsum()
    df['cum_vol']    = df.groupby('date')['volume'].cumsum()
    df['vwap'] = df['cum_tp_vol'] / df['cum_vol']
    return df

def add_1h_bias(df_15m, df_1h):
    df_1h['ema50_1h'] = df_1h['close'].ewm(span=50, adjust=False).mean()
    df_1h['bias_1h'] = np.where(df_1h['close'] > df_1h['ema50_1h'], 1, -1)
    df_1h_clean = df_1h[['time','bias_1h']].copy()
    df_15m = df_15m.sort_values('time')
    df_1h_clean = df_1h_clean.sort_values('time')
    df_15m = pd.merge_asof(df_15m, df_1h_clean, on='time', direction='backward')
    df_15m['bias_1h'] = df_15m['bias_1h'].fillna(0)
    return df_15m

def run_backtest(df, use_1h_ema=False, use_vwap=False):
    trades = []
    in_trade = False

    for i in range(55, len(df)):
        row = df.iloc[i]
        if in_trade:
            if direction == 'long':
                if row['low'] <= sl:
                    trades.append({'result':'loss','pnl': -(entry - sl)/entry})
                    in_trade = False
                elif row['high'] >= tp2:
                    trades.append({'result':'win_full','pnl': (tp2 - entry)/entry})
                    in_trade = False
                elif row['high'] >= tp1 and not hit_tp1:
                    hit_tp1 = True
                    sl = entry  # move SL to breakeven
            else:
                if row['high'] >= sl:
                    trades.append({'result':'loss','pnl': -(sl - entry)/entry})
                    in_trade = False
                elif row['low'] <= tp2:
                    trades.append({'result':'win_full','pnl': (entry - tp2)/entry})
                    in_trade = False
                elif row['low'] <= tp1 and not hit_tp1:
                    hit_tp1 = True
                    sl = entry
            continue

        # --- Base signal conditions ---
        is_long  = (row['cross_up']   and row['close'] > row['ema50'] and 45 <= row['rsi'] <= 65 and row['volume'] >= row['vol_avg'] * 1.3)
        is_short = (row['cross_down'] and row['close'] < row['ema50'] and 35 <= row['rsi'] <= 55 and row['volume'] >= row['vol_avg'] * 1.3)

        # --- 1H EMA filter ---
        if use_1h_ema:
            bias = row.get('bias_1h', 0)
            if is_long  and bias != 1:  is_long  = False
            if is_short and bias != -1: is_short = False

        # --- VWAP filter ---
        if use_vwap:
            vwap = row['vwap']
            if is_long  and row['close'] <= vwap: is_long  = False
            if is_short and row['close'] >= vwap: is_short = False

        if not is_long and not is_short:
            continue

        direction = 'long' if is_long else 'short'
        entry = row['close']
        candle_range = row['high'] - row['low']
        sl_dist = max(candle_range * 0.5, entry * 0.003)
        sl  = entry - sl_dist if direction == 'long' else entry + sl_dist
        tp1 = entry + sl_dist * 1.5 if direction == 'long' else entry - sl_dist * 1.5
        tp2 = entry + sl_dist * 2.5 if direction == 'long' else entry - sl_dist * 2.5
        in_trade = True
        hit_tp1  = False

    if not trades:
        return {'trades':0,'win_rate':0,'pf':0,'net_pnl':0,'net_after_fees':0}

    wins   = [t for t in trades if t['result'] == 'win_full']
    losses = [t for t in trades if t['result'] == 'loss']
    gross_gain = sum(t['pnl'] for t in wins)
    gross_loss = abs(sum(t['pnl'] for t in losses))
    fee = 0.00045 * len(trades) * 2
    net = (gross_gain - gross_loss) * 100
    net_after = net - fee * 100

    return {
        'trades'        : len(trades),
        'wins'          : len(wins),
        'losses'        : len(losses),
        'win_rate'      : len(wins)/len(trades)*100,
        'profit_factor' : gross_gain/gross_loss if gross_loss > 0 else 999,
        'net_pnl'       : net,
        'net_after_fees': net_after,
    }

print("Fetching SOL candles...")
df15 = fetch_candles("SOL", "15m")
df1h = fetch_1h_candles("SOL")
df15 = add_indicators(df15)
df15 = add_1h_bias(df15, df1h)
print(f"Loaded {len(df15)} candles | 30 days\n")

configs = [
    ("Baseline (current)",         False, False),
    ("+ 1H EMA filter",            True,  False),
    ("+ VWAP filter",              False, True),
    ("+ 1H EMA + VWAP (combined)", True,  True),
]

results = []
for name, h1, vwap in configs:
    r = run_backtest(df15.copy(), use_1h_ema=h1, use_vwap=vwap)
    r['name'] = name
    results.append(r)
    print(f"{name}")
    print(f"  Trades      : {r['trades']} ({r.get('wins',0)}W / {r.get('losses',0)}L)")
    print(f"  Win Rate    : {r['win_rate']:.1f}%")
    print(f"  Prof Factor : {r['profit_factor']:.2f}")
    print(f"  Net P&L     : {r['net_pnl']:+.2f}%")
    print(f"  After Fees  : {r['net_after_fees']:+.2f}%")
    print()
