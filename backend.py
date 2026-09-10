import requests
import pandas as pd
import numpy as np
import hmac
import hashlib
import json
import time
import streamlit as st

# ==========================================
# 🔐 SECRETS MANAGEMENT
# ==========================================
try:
    API_KEY = st.secrets["API_KEY"]
    API_SECRET = st.secrets["API_SECRET"]
except Exception:
    try:
        from keys import API_KEY, API_SECRET
    except ImportError:
        API_KEY = "DUMMY_KEY"
        API_SECRET = "DUMMY_SECRET"

# ==========================================
# ⚙️ CONFIGURATION
# ==========================================
# WazirX hata diya. Ab Candles bhi CoinDCX se aayengi data match karne ke liye!
CANDLE_URL = "https://public.coindcx.com/market_data/candles" 
TICKER_URL = "https://api.coindcx.com/exchange/ticker"
USER_URL = "https://api.coindcx.com/exchange/v1/users/balances"

PAIRS = {
    'B-BTC_INR': 'btcinr', 'B-ETH_INR': 'ethinr', 'B-BNB_INR': 'bnbinr',
    'B-SOL_INR': 'solinr', 'B-XRP_INR': 'xrpinr', 'B-DOGE_INR': 'dogeinr',
    'B-SHIB_INR': 'shibinr', 'B-PEPE_INR': 'pepeinr', 'B-BONK_INR': 'bonkinr',
    'B-FLOKI_INR': 'flokiinr', 'B-WIF_INR': 'wifinr', 'B-MEME_INR': 'memeinr',
    'B-FET_INR': 'fetinr', 'B-RNDR_INR': 'rndrinr', 'B-NEAR_INR': 'nearinr',
    'B-GALA_INR': 'galainr', 'B-MATIC_INR': 'maticinr', 'B-ADA_INR': 'adainr',
    'B-TRX_INR': 'trxinr', 'B-AVAX_INR': 'avaxinr', 'B-DOT_INR': 'dotinr',
    'B-ATOM_INR': 'atominr', 'B-FANTOM_INR': 'ftminr', 'B-LINK_INR': 'linkinr',
    'B-APT_INR': 'aptinr', 'B-PAXG_INR': 'paxginr', 'B-XAUT_INR': 'xautinr',
    'B-ULTIMA_INR': 'ultimainr', 'B-ZEC_INR': 'zecinr', 'B-BIFI_INR': 'bifinr',
    'B-BDX_INR': 'bdxinr', 'B-HTX_INR': 'htxinr', 'B-SIREN_INR': 'sireninr',
    'B-SUI_INR': 'suiinr', 'B-OM_INR': 'ominr', 'B-VVV_INR': 'vvvinr',
    'B-ZRO_INR': 'zroinr',
}

TIMEFRAME = '15m'

# --- 1. LIVE PRICE FETCH ---
def get_live_prices():
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(TICKER_URL, headers=headers, timeout=10)
        data = response.json()
        
        price_map = {}
        for item in data:
            if 'last_price' not in item: continue
            raw_market = item['market']
            price = float(item['last_price'])
            
            clean_market = raw_market.replace("_", "").replace("-", "")
            if clean_market.startswith("B") and len(clean_market) > 4:
                clean_market = clean_market[1:] 
            
            price_map[clean_market] = price
            
        return price_map
    except Exception as e:
        return {}

# --- 2. BALANCE ---
def generate_signature(json_body, secret_key):
    secret_bytes = bytes(secret_key, encoding='utf-8')
    body_bytes = bytes(json.dumps(json_body), encoding='utf-8')
    return hmac.new(secret_bytes, body_bytes, hashlib.sha256).hexdigest()

def get_wallet_balance():
    try:
        if "DUMMY" in API_KEY: return 0.0
        json_body = {"timestamp": int(time.time() * 1000)}
        signature = generate_signature(json_body, API_SECRET)
        headers = {
            'X-AUTH-APIKEY': API_KEY,
            'X-AUTH-SIGNATURE': signature,
            'Content-Type': 'application/json'
        }
        response = requests.post(USER_URL, data=json.dumps(json_body), headers=headers)
        data = response.json()
        for item in data:
            if item['currency'] == 'INR':
                return float(item['balance'])
        return 0.0
    except:
        return 0.0

# --- 3. FETCH CANDLES (Ab WazirX ki jagah CoinDCX use hoga) ---
def fetch_candles(coindcx_pair):
    try:
        # Pura data CoinDCX se aayega
        params = {"pair": coindcx_pair, "interval": TIMEFRAME, "limit": 100}
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(CANDLE_URL, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if not data or not isinstance(data, list): return None
        
        df = pd.DataFrame(data)
        if len(df) < 30: return None
        
        # Data ko seedha karna zaroori hai (Oldest to Newest)
        df.sort_values(by='time', ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        cols = ['open', 'high', 'low', 'close', 'volume']
        df[cols] = df[cols].astype(float)
        
        return df
    except:
        return None

# --- CORRECTED ADX INDICATOR ---
def calculate_adx(df, period=14):
    plus_dm = df['high'].diff()
    minus_dm = df['low'].shift(1) - df['low'] # Sahi Formula for -DM
    
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
    adx = dx.ewm(alpha=1/period, adjust=False).mean()
    return adx

# --- ANALYSIS ---
def analyze_coin(df, pair_name, live_price):
    if df is None or len(df) < 50: return None
    
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

    # ADX & Vol
    df['adx'] = calculate_adx(df)
    df['vol_ma'] = df['volume'].rolling(20).mean()
    
    curr = df.iloc[-1]
    prev = df.iloc[-2] # Pichli candle check karne ke liye
    
    price = live_price if live_price > 0 else curr['close']
    ema = curr['ema_50']
    rsi = curr['rsi']
    atr = curr['atr'] if curr['atr'] > 0 else price * 0.01
    adx = curr['adx']
    
    # Sahi green candle logic live price ke mutabik
    is_green_candle = price > curr['open'] 
    
    # ==========================================
    # 🧠 FIXED LOGIC FOR INR PAIRS
    # ==========================================
    signal = "WAIT ⏳"
    reason = "No Setup"
    score = 0
    
    if price > ema:
        score += 10
        reason = "Uptrend"
    
    # Volume Logic Relaxed (Current ya Pichli candle dono me se kisi ek me volume ho)
    has_volume = (curr['volume'] > curr['vol_ma']) or (prev['volume'] > prev['vol_ma'])
    if has_volume: score += 10
        
    # STRATEGIES
    # Trend Buy
    if price > ema and 45 < rsi < 75 and adx > 18 and is_green_candle and has_volume:
        score += 60
        signal = "BUY TREND 🚀"
        reason = f"Trend Starting (ADX {adx:.0f})"
        
    # Reversal Dip Buy (RSI Thoda adjust kiya taaki zyada signals milein)
    elif rsi < 35 and is_green_candle: 
        score += 50
        signal = "BUY REVERSAL 🟢"
        reason = "Oversold Dip Buy"
        
    # Sell Overbought
    elif rsi > 80:
        score -= 20
        signal = "SELL 🔴"
        reason = "Overbought"
    
    # SL aur Target calculation
    stop_loss = price - (1.5 * atr) 
    target = price + (3.5 * atr)    
        
    return {
        "pair": pair_name.replace("B-", "").replace("_", "/"),
        "price": price,
        "signal": signal,
        "score": score,
        "reason": reason,
        "target": target,
        "stop_loss": stop_loss,
        "atr": atr,
        "rsi": rsi,
        "adx": adx
    }

def run_agent():
    balance = get_wallet_balance()
    live_prices = get_live_prices()
    results = []
    
    for coindcx_pair in PAIRS.keys():
        my_clean_key = coindcx_pair.replace("B-", "").replace("_", "")
        current_live_price = live_prices.get(my_clean_key, 0.0)
        
        df = fetch_candles(coindcx_pair)
        
        if df is not None:
            analysis = analyze_coin(df, coindcx_pair, current_live_price)
            if analysis:
                results.append(analysis)
        
        time.sleep(0.05) 
        
    # Sirf unhi coins ko upar dikhayega jinke signals aaye hain
    results.sort(key=lambda x: x['score'], reverse=True)
    return results, balance
