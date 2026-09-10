# api.py
import requests
import pandas as pd
import hmac
import hashlib
import json
import time
import streamlit as st
import config

# Keys Handling
try:
    API_KEY = st.secrets["API_KEY"]
    API_SECRET = st.secrets["API_SECRET"]
except Exception:
    API_KEY = "DUMMY_KEY"
    API_SECRET = "DUMMY_SECRET"

def generate_signature(json_body, secret_key):
    secret_bytes = bytes(secret_key, encoding='utf-8')
    body_bytes = bytes(json.dumps(json_body), encoding='utf-8')
    return hmac.new(secret_bytes, body_bytes, hashlib.sha256).hexdigest()

def get_wallet_balance():
    if "DUMMY" in API_KEY: return 0.0
    try:
        json_body = {"timestamp": int(time.time() * 1000)}
        signature = generate_signature(json_body, API_SECRET)
        headers = {
            'X-AUTH-APIKEY': API_KEY,
            'X-AUTH-SIGNATURE': signature,
            'Content-Type': 'application/json'
        }
        response = requests.post(config.USER_URL, data=json.dumps(json_body), headers=headers)
        data = response.json()
        for item in data:
            if item['currency'] == 'INR':
                return float(item['balance'])
        return 0.0
    except:
        return 0.0

def fetch_candles(coindcx_pair, tf='15m'):  # <-- tf add kiya
    try:
        params = {"pair": coindcx_pair, "interval": tf, "limit": 100} # config.TIMEFRAME hataya
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(config.CANDLE_URL, params=params, headers=headers, timeout=10)
        data = response.json()
        
        if not data or not isinstance(data, list): return None
        
        df = pd.DataFrame(data)
        if len(df) < 50: return None
        
        df.sort_values(by='time', ascending=True, inplace=True)
        df.reset_index(drop=True, inplace=True)
        
        cols = ['open', 'high', 'low', 'close', 'volume']
        df[cols] = df[cols].astype(float)
        
        return df
    except:
        return None
def get_fear_and_greed():
    try:
        response = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
        data = response.json()
        if data and "data" in data and len(data["data"]) > 0:
            val = int(data["data"][0]["value"])
            classification = data["data"][0]["value_classification"]
            return {"value": val, "class": classification}
    except:
        return None
