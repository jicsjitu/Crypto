# strategy.py
import time
import config
import api
from indicators import apply_all_indicators

def analyze_coin(df, pair_name, balance):
    df = apply_all_indicators(df)
    
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    price = curr['close']
    ema = curr['ema_50']
    rsi = curr['rsi']
    atr = curr['atr'] if curr['atr'] > 0 else price * 0.01
    adx = curr['adx']
    
    is_green_candle = price > curr['open'] 
    
    signal, reason, score = "WAIT ⏳", "No Setup", 0
    
    if price > ema:
        score += 10
        reason = "Uptrend"
    
    has_volume = (curr['volume'] > curr['vol_ma']) or (prev['volume'] > prev['vol_ma'])
    if has_volume: score += 10
        
    # LOGIC
    if price > ema and 45 < rsi < 75 and adx > 18 and is_green_candle and has_volume:
        score += 60
        signal, reason = "BUY TREND 🚀", f"Trend Starting (ADX {adx:.0f})"
    elif rsi < 35 and is_green_candle: 
        score += 50
        signal, reason = "BUY REVERSAL 🟢", "Oversold Dip Buy"
    elif rsi > 80:
        score -= 20
        signal, reason = "SELL 🔴", "Overbought"
    
    stop_loss = price - (1.5 * atr) 
    target = price + (3.5 * atr)    
    
    # Position Sizing Logic (Moved from UI)
    risk = price - stop_loss
    qty, amt = 0, 0
    if "BUY" in signal and risk > 0 and balance > 0:
        risk_amt = balance * config.RISK_PER_TRADE
        qty = risk_amt / risk
        amt = qty * price
        if amt > balance: 
            amt = balance
            qty = amt / price
            
    return {
        "pair": pair_name.replace("B-", "").replace("_", "/"),
        "price": price, "signal": signal, "score": score,
        "reason": reason, "target": target, "stop_loss": stop_loss,
        "rsi": rsi, "qty": qty, "invest_amt": amt
    }

def run_agent(current_balance):
    results = []
    for coindcx_pair in config.PAIRS.keys():
        df = api.fetch_candles(coindcx_pair)
        if df is not None:
            analysis = analyze_coin(df, coindcx_pair, current_balance)
            if analysis: results.append(analysis)
        time.sleep(0.05) 
        
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
