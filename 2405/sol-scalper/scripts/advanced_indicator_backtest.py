import requests, json, time, pandas as pd, numpy as np

def fetch_candles(coin, interval, lookback_hours=1300):
    end = int(time.time() * 1000)
    start = end - lookback_hours * 3600 * 1000
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
    return df.reset_index(drop=True)

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def atr(df, period=14):
    tr = pd.concat([
        df['h'] - df['l'],
        (df['h'] - df['c'].shift()).abs(),
        (df['l'] - df['c'].shift()).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def supertrend(df, period=10, multiplier=2.0):
    a = atr(df, period)
    hl2 = (df['h'] + df['l']) / 2
    upper = hl2 + multiplier * a
    lower = hl2 - multiplier * a
    st = pd.Series(index=df.index, dtype=float)
    direction = pd.Series(1, index=df.index)
    for i in range(1, len(df)):
        if df['c'].iloc[i] > upper.iloc[i-1]:
            direction.iloc[i] = 1
        elif df['c'].iloc[i] < lower.iloc[i-1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i-1]
        st.iloc[i] = lower.iloc[i] if direction.iloc[i] == 1 else upper.iloc[i]
    return direction

def ichimoku_cloud(df):
    # Tenkan (9), Kijun (26), Senkou A/B
    tenkan = (df['h'].rolling(9).max() + df['l'].rolling(9).min()) / 2
    kijun  = (df['h'].rolling(26).max() + df['l'].rolling(26).min()) / 2
    senkou_a = ((tenkan + kijun) / 2).shift(26)
    senkou_b = ((df['h'].rolling(52).max() + df['l'].rolling(52).min()) / 2).shift(26)
    return tenkan, kijun, senkou_a, senkou_b

def market_structure(df, lookback=10):
    """Break of Structure (BOS) — bullish if recent HH, bearish if recent LL"""
    swing_high = df['h'].rolling(lookback).max()
    swing_low  = df['l'].rolling(lookback).min()
    bos_bull = df['c'] > swing_high.shift(1)
    bos_bear = df['c'] < swing_low.shift(1)
    return bos_bull, bos_bear

def pivot_points(df):
    """Classic daily pivot points as S/R filter"""
    pivot = (df['h'] + df['l'] + df['c']) / 3
    r1 = 2 * pivot - df['l']
    s1 = 2 * pivot - df['h']
    return pivot, r1, s1

def run_backtest(df, extra_filter=None, label=""):
    e9  = ema(df['c'], 9)
    e21 = ema(df['c'], 21)
    e50 = ema(df['c'], 50)
    rsi_v = rsi(df['c'])
    vol_ma = df['v'].rolling(5).mean()
    e50_1h = ema(df['c'], 100)   # ~1H 50 EMA proxy on 15M
    vwap = (df['c'] * df['v']).cumsum() / df['v'].cumsum()

    # Extra indicators
    st_dir = supertrend(df, 10, 2.0)
    tenkan, kijun, senkou_a, senkou_b = ichimoku_cloud(df)
    bos_bull, bos_bear = market_structure(df, 10)
    pivot, r1, s1 = pivot_points(df)
    macd_line = ema(df['c'], 12) - ema(df['c'], 26)
    macd_sig  = ema(macd_line, 9)
    rsi_ma    = rsi_v.rolling(5).mean()  # RSI smoothed (avoid noise)

    trades, winners, losers = [], 0, 0
    in_trade = False

    for i in range(100, len(df) - 5):
        if in_trade:
            if in_trade == 'long':
                if df['l'].iloc[i] <= sl:
                    losers += 1; in_trade = False; continue
                if df['h'].iloc[i] >= tp2:
                    winners += 1; in_trade = False; continue
            else:
                if df['h'].iloc[i] >= sl:
                    losers += 1; in_trade = False; continue
                if df['l'].iloc[i] <= tp2:
                    winners += 1; in_trade = False; continue
            continue

        cross_up = e9.iloc[i] > e21.iloc[i] and e9.iloc[i-1] <= e21.iloc[i-1]
        cross_dn = e9.iloc[i] < e21.iloc[i] and e9.iloc[i-1] >= e21.iloc[i-1]
        vol_spike = df['v'].iloc[i] >= 1.3 * vol_ma.iloc[i]
        above_50  = df['c'].iloc[i] > e50.iloc[i]
        h1_ok_l   = df['c'].iloc[i] > e50_1h.iloc[i]
        h1_ok_s   = df['c'].iloc[i] < e50_1h.iloc[i]
        vwap_ok_l = df['c'].iloc[i] > vwap.iloc[i]
        vwap_ok_s = df['c'].iloc[i] < vwap.iloc[i]
        rsi_long  = 45 <= rsi_v.iloc[i] <= 65
        rsi_short = 35 <= rsi_v.iloc[i] <= 55

        base_long  = cross_up and above_50 and vol_spike and rsi_long  and h1_ok_l and vwap_ok_l
        base_short = cross_dn and not above_50 and vol_spike and rsi_short and h1_ok_s and vwap_ok_s

        # Apply extra filter
        extra_long = extra_short = True
        if extra_filter == 'supertrend':
            extra_long  = st_dir.iloc[i] == 1
            extra_short = st_dir.iloc[i] == -1
        elif extra_filter == 'ichimoku_tk':
            extra_long  = tenkan.iloc[i] > kijun.iloc[i]
            extra_short = tenkan.iloc[i] < kijun.iloc[i]
        elif extra_filter == 'ichimoku_cloud':
            extra_long  = (df['c'].iloc[i] > max(senkou_a.iloc[i], senkou_b.iloc[i])
                           if not pd.isna(senkou_a.iloc[i]) else False)
            extra_short = (df['c'].iloc[i] < min(senkou_a.iloc[i], senkou_b.iloc[i])
                           if not pd.isna(senkou_a.iloc[i]) else False)
        elif extra_filter == 'bos':
            extra_long  = bos_bull.iloc[i]
            extra_short = bos_bear.iloc[i]
        elif extra_filter == 'macd':
            extra_long  = macd_line.iloc[i] > macd_sig.iloc[i] and macd_line.iloc[i] > 0
            extra_short = macd_line.iloc[i] < macd_sig.iloc[i] and macd_line.iloc[i] < 0
        elif extra_filter == 'rsi_smooth':
            extra_long  = rsi_ma.iloc[i] > 50 and rsi_ma.iloc[i] < 65
            extra_short = rsi_ma.iloc[i] < 50 and rsi_ma.iloc[i] > 35
        elif extra_filter == 'pivot':
            extra_long  = df['c'].iloc[i] > pivot.iloc[i]
            extra_short = df['c'].iloc[i] < pivot.iloc[i]
        elif extra_filter == 'supertrend+ichimoku':
            extra_long  = st_dir.iloc[i] == 1 and tenkan.iloc[i] > kijun.iloc[i]
            extra_short = st_dir.iloc[i] == -1 and tenkan.iloc[i] < kijun.iloc[i]
        elif extra_filter == 'macd+bos':
            extra_long  = (macd_line.iloc[i] > macd_sig.iloc[i]) and bos_bull.iloc[i]
            extra_short = (macd_line.iloc[i] < macd_sig.iloc[i]) and bos_bear.iloc[i]

        atr_val = atr(df).iloc[i]
        if base_long and extra_long:
            entry = df['c'].iloc[i]
            sl = entry - atr_val * 0.8
            tp1 = entry + (entry - sl) * 1.5
            tp2 = entry + (entry - sl) * 2.5
            in_trade = 'long'
        elif base_short and extra_short:
            entry = df['c'].iloc[i]
            sl = entry + atr_val * 0.8
            tp1 = entry - (sl - entry) * 1.5
            tp2 = entry - (sl - entry) * 2.5
            in_trade = 'short'

    total = winners + losers
    if total == 0:
        return {"label": label, "trades": 0, "win_pct": 0, "pf": 0, "net": 0}
    wr = winners / total
    avg_win = 0.45; avg_loss = 0.40
    gross = winners * avg_win - losers * avg_loss
    fee = total * 0.045 * 2
    net = gross - fee
    pf = (winners * avg_win) / max(losers * avg_loss, 0.001)
    return {"label": label, "trades": total, "win_pct": round(wr*100,1),
            "pf": round(pf,2), "net": round(net,2)}

print("Fetching SOL 15M candles...")
df = fetch_candles("SOL", "15m", lookback_hours=1300)
print(f"Loaded {len(df)} candles\n")

configs = [
    (None,                   "Baseline (1H EMA + VWAP)"),
    ("supertrend",           "+ Supertrend (10,2)"),
    ("ichimoku_tk",          "+ Ichimoku TK cross"),
    ("ichimoku_cloud",       "+ Ichimoku Cloud filter"),
    ("macd",                 "+ MACD (12/26/9)"),
    ("bos",                  "+ Break of Structure"),
    ("rsi_smooth",           "+ RSI Smoothed (5-MA)"),
    ("pivot",                "+ Daily Pivot Points"),
    ("supertrend+ichimoku",  "+ Supertrend + Ichimoku TK"),
    ("macd+bos",             "+ MACD + BOS"),
]

results = []
print(f"{'Config':<32} {'Trades':>7} {'Win%':>6} {'PF':>5} {'Net%':>7}")
print("-" * 62)
for filt, label in configs:
    r = run_backtest(df.copy(), extra_filter=filt, label=label)
    results.append(r)
    print(f"{label:<32} {r['trades']:>7} {r['win_pct']:>6.1f} {r['pf']:>5.2f} {r['net']:>7.2f}")

print("\nDone.")
