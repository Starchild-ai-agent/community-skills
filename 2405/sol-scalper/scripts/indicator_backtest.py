import requests, json, time, pandas as pd, numpy as np

def fetch_candles(coin, interval, hours=720):
    end = int(time.time() * 1000)
    start = end - hours * 3600 * 1000
    url = "https://api.hyperliquid.xyz/info"
    payload = {"type": "candleSnapshot", "req": {"coin": coin, "interval": interval, "startTime": start, "endTime": end}}
    r = requests.post(url, json=payload, timeout=15)
    data = r.json()
    if not data:
        return None
    df = pd.DataFrame(data)
    df.columns = ['t','T','s','i','o','c','h','l','v','n'] if len(df.columns) == 10 else df.columns
    for col in ['o','c','h','l','v']:
        df[col] = pd.to_numeric(df[col])
    df['t'] = pd.to_datetime(df['t'], unit='ms')
    df = df.sort_values('t').reset_index(drop=True)
    return df

def compute_indicators(df):
    # Core EMAs
    df['ema9']  = df['c'].ewm(span=9, adjust=False).mean()
    df['ema21'] = df['c'].ewm(span=21, adjust=False).mean()
    df['ema50'] = df['c'].ewm(span=50, adjust=False).mean()

    # 1H EMA (4 x 15M candles)
    df['ema50_1h'] = df['c'].ewm(span=50*4, adjust=False).mean()

    # RSI
    delta = df['c'].diff()
    gain = delta.clip(lower=0).ewm(span=14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(span=14, adjust=False).mean()
    df['rsi'] = 100 - (100 / (1 + gain / loss.replace(0, 1e-9)))

    # VWAP (daily reset)
    df['date'] = df['t'].dt.date
    df['tp'] = (df['h'] + df['l'] + df['c']) / 3
    df['tp_vol'] = df['tp'] * df['v']
    df['cum_tp_vol'] = df.groupby('date')['tp_vol'].cumsum()
    df['cum_vol'] = df.groupby('date')['v'].cumsum()
    df['vwap'] = df['cum_tp_vol'] / df['cum_vol']

    # Volume spike
    df['vol_avg'] = df['v'].rolling(5).mean()
    df['vol_spike'] = df['v'] > df['vol_avg'] * 1.3

    # ADX
    high, low, close = df['h'], df['l'], df['c']
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    df['atr'] = tr.ewm(span=14, adjust=False).mean()
    plus_dm = (high.diff()).clip(lower=0).where(high.diff() > (-low.diff()), 0)
    minus_dm = (-low.diff()).clip(lower=0).where((-low.diff()) > high.diff(), 0)
    plus_di = 100 * plus_dm.ewm(span=14, adjust=False).mean() / df['atr'].replace(0, 1e-9)
    minus_di = 100 * minus_dm.ewm(span=14, adjust=False).mean() / df['atr'].replace(0, 1e-9)
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1e-9))
    df['adx'] = dx.ewm(span=14, adjust=False).mean()

    # Stochastic RSI
    rsi_min = df['rsi'].rolling(14).min()
    rsi_max = df['rsi'].rolling(14).max()
    stoch_rsi_raw = (df['rsi'] - rsi_min) / (rsi_max - rsi_min).replace(0, 1e-9)
    df['stoch_k'] = stoch_rsi_raw.rolling(3).mean() * 100
    df['stoch_d'] = df['stoch_k'].rolling(3).mean()

    # Bollinger Bands
    df['bb_mid']   = df['c'].rolling(20).mean()
    df['bb_std']   = df['c'].rolling(20).std()
    df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
    df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
    df['bb_pct']   = (df['c'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower']).replace(0, 1e-9)

    # EMA cross
    df['cross_up']   = (df['ema9'] > df['ema21']) & (df['ema9'].shift() <= df['ema21'].shift())
    df['cross_down'] = (df['ema9'] < df['ema21']) & (df['ema9'].shift() >= df['ema21'].shift())

    return df

def run_backtest(df, name, extra_long_filter=None, extra_short_filter=None, atr_stop=False):
    trades, equity = [], 1000.0
    i = 60
    while i < len(df) - 20:
        row = df.iloc[i]
        base_long  = row['cross_up']   and row['c'] > row['ema50'] and 42 <= row['rsi'] <= 68 and row['vol_spike'] and row['c'] > row['ema50_1h'] and row['c'] > row['vwap']
        base_short = row['cross_down'] and row['c'] < row['ema50'] and 32 <= row['rsi'] <= 58 and row['vol_spike'] and row['c'] < row['ema50_1h'] and row['c'] < row['vwap']

        if extra_long_filter:  base_long  = base_long  and extra_long_filter(df, i)
        if extra_short_filter: base_short = base_short and extra_short_filter(df, i)

        direction = None
        if base_long:  direction = 'long'
        if base_short: direction = 'short'

        if direction:
            entry = row['c']
            sl_dist = row['atr'] * 1.2 if atr_stop else entry * 0.004
            sl   = entry - sl_dist if direction == 'long' else entry + sl_dist
            tp1  = entry + sl_dist * 1.5 if direction == 'long' else entry - sl_dist * 1.5
            tp2  = entry + sl_dist * 2.5 if direction == 'long' else entry - sl_dist * 2.5
            risk = equity * 0.01
            outcome, exit_p = 'open', entry
            for j in range(i+1, min(i+40, len(df))):
                c2 = df.iloc[j]['c']
                if direction == 'long':
                    if c2 <= sl:   outcome, exit_p = 'loss', sl;  break
                    if c2 >= tp2:  outcome, exit_p = 'tp2',  tp2; break
                    if c2 >= tp1:  outcome, exit_p = 'tp1',  tp1; break
                else:
                    if c2 >= sl:   outcome, exit_p = 'loss', sl;  break
                    if c2 <= tp2:  outcome, exit_p = 'tp2',  tp2; break
                    if c2 <= tp1:  outcome, exit_p = 'tp1',  tp1; break
            if outcome == 'open': i += 1; continue
            pct  = (exit_p - entry) / entry if direction == 'long' else (entry - exit_p) / entry
            if outcome == 'tp1': pct *= 0.5
            pnl  = risk * (pct / 0.004) - equity * 0.00045
            equity += pnl
            trades.append({'outcome': outcome, 'pnl': pnl})
            i += 5
        i += 1

    if not trades: return name, 0, 0.0, 1.0, 0.0
    t  = pd.DataFrame(trades)
    wins = len(t[t.outcome.isin(['tp1','tp2'])])
    losses = len(t[t.outcome == 'loss'])
    gross_w = t[t.pnl > 0]['pnl'].sum()
    gross_l = abs(t[t.pnl < 0]['pnl'].sum())
    pf = gross_w / gross_l if gross_l > 0 else 99.0
    net = (equity - 1000) / 1000 * 100
    return name, len(t), wins/len(t)*100, pf, net

print("Fetching SOL 15M candles...")
df = fetch_candles("SOL", "15m", hours=720)
print(f"Loaded {len(df)} candles\n")
df = compute_indicators(df)

# Baseline (1H EMA + VWAP)
r0 = run_backtest(df, "Baseline (1H EMA + VWAP)")

# + ADX > 20 filter (trend strength)
r1 = run_backtest(df, "+ ADX > 20",
    extra_long_filter  = lambda d,i: d.iloc[i]['adx'] > 20,
    extra_short_filter = lambda d,i: d.iloc[i]['adx'] > 20)

# + ADX > 25 filter (stronger trend)
r2 = run_backtest(df, "+ ADX > 25",
    extra_long_filter  = lambda d,i: d.iloc[i]['adx'] > 25,
    extra_short_filter = lambda d,i: d.iloc[i]['adx'] > 25)

# + StochRSI (long: K>D and both < 80; short: K<D and both > 20)
r3 = run_backtest(df, "+ Stoch RSI",
    extra_long_filter  = lambda d,i: d.iloc[i]['stoch_k'] > d.iloc[i]['stoch_d'] and d.iloc[i]['stoch_k'] < 80,
    extra_short_filter = lambda d,i: d.iloc[i]['stoch_k'] < d.iloc[i]['stoch_d'] and d.iloc[i]['stoch_k'] > 20)

# + BB position (long: bb_pct 30–70 i.e. mid-band, not extended)
r4 = run_backtest(df, "+ Bollinger Band (mid-zone)",
    extra_long_filter  = lambda d,i: 0.30 <= d.iloc[i]['bb_pct'] <= 0.70,
    extra_short_filter = lambda d,i: 0.30 <= d.iloc[i]['bb_pct'] <= 0.70)

# + ATR-based dynamic stops
r5 = run_backtest(df, "+ ATR Dynamic Stops", atr_stop=True)

# Best combo: ADX > 20 + StochRSI
r6 = run_backtest(df, "ADX>20 + StochRSI",
    extra_long_filter  = lambda d,i: d.iloc[i]['adx'] > 20 and d.iloc[i]['stoch_k'] > d.iloc[i]['stoch_d'] and d.iloc[i]['stoch_k'] < 80,
    extra_short_filter = lambda d,i: d.iloc[i]['adx'] > 20 and d.iloc[i]['stoch_k'] < d.iloc[i]['stoch_d'] and d.iloc[i]['stoch_k'] > 20)

# Champion: ADX>20 + StochRSI + ATR stops
r7 = run_backtest(df, "ADX>20 + StochRSI + ATR (CHAMP)",
    extra_long_filter  = lambda d,i: d.iloc[i]['adx'] > 20 and d.iloc[i]['stoch_k'] > d.iloc[i]['stoch_d'] and d.iloc[i]['stoch_k'] < 80,
    extra_short_filter = lambda d,i: d.iloc[i]['adx'] > 20 and d.iloc[i]['stoch_k'] < d.iloc[i]['stoch_d'] and d.iloc[i]['stoch_k'] > 20,
    atr_stop=True)

results = [r0, r1, r2, r3, r4, r5, r6, r7]
print(f"\n{'Config':<35} {'Trades':>7} {'Win%':>7} {'PF':>6} {'Net%':>7}")
print("-" * 68)
for name, trades, wr, pf, net in results:
    marker = " 🏆" if "CHAMP" in name else ""
    print(f"{name:<35} {trades:>7} {wr:>6.1f}% {pf:>6.2f} {net:>+6.2f}%{marker}")
