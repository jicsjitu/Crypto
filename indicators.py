# indicators.py
import pandas as pd
import numpy as np

def calculate_adx(df, period=14):
    plus_dm = df['high'].diff()
    minus_dm = df['low'].shift(1) - df['low']
    
    pos_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0)
    neg_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0)
    
    tr1 = df['high'] - df['low']
    tr2 = abs(df['high'] - df['close'].shift(1))
    tr3 = abs(df['low'] - df['close'].shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = tr.ewm(alpha=1/period, adjust=False).mean()
    
    plus_di = 100 * (pd.Series(pos_dm).ewm(alpha=1/period, adjust=False).mean() / atr)
    minus_di = 100 * (pd.Series(neg_dm).ewm(alpha=1/period, adjust=False).mean() / atr)
    
    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    return dx.ewm(alpha=1/period, adjust=False).mean()

def apply_all_indicators(df):
    # EMA 50
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    
    # RSI
    delta = df['close'].diff()
    up = delta.clip(lower=0)
    down = -1 * delta.clip(upper=0)
    ema_up = up.ewm(com=13, adjust=False).mean()
    ema_down = down.ewm(com=13, adjust=False).mean()
    rs = ema_up / ema_down
    df['rsi'] = 100 - (100 / (1 + rs))
    df['rsi'] = df['rsi'].fillna(50)
    
    # ATR
    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['close'].shift())
    df['tr3'] = abs(df['low'] - df['close'].shift())
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
    df['atr'] = df['tr'].rolling(14).mean()

    # ADX & Vol MA
    df['adx'] = calculate_adx(df)
    df['vol_ma'] = df['volume'].rolling(20).mean()
    
    return df
