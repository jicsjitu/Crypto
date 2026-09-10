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
    ema_50 = curr['ema_50']
    ema_200 = curr['ema_200']
    rsi = curr['rsi']
    atr = curr['atr'] if curr['atr'] > 0 else price * 0.01
    adx = curr['adx']
    macd = curr['macd']
    macd_sig = curr['macd_signal']
    bb_lower = curr['bb_lower']
    bb_upper = curr['bb_upper']
    
    is_green_candle = price > curr['open'] 
    has_volume = (curr['volume'] > curr['vol_ma']) or (prev['volume'] > prev['vol_ma'])
    
    signal, reason, score = "WAIT ⏳", "No Setup", 0
    
    # 🛑 1. MACRO TREND FILTER (EMA 200)
    if price < ema_200:
        reason = "Below EMA200 (Bearish)"
        # Hum short nahi kar rahe, toh isko sidha wait mein dalenge.
    else:
        score += 20  # Overall trend is UP
        
        if price > ema_50:
            score += 10
            
        if has_volume: 
            score += 10

        # 🚀 STRATEGY 1: PRO TREND RIDER (High Probability)
        # Price > EMA50/200, MACD Bullish Crossover, ADX > 20, Good RSI
        if price > ema_50 and macd > macd_sig and 50 < rsi < 70 and adx > 20 and is_green_candle and has_volume:
            score += 50
            signal, reason = "BUY TREND 🚀", f"MACD Bullish + Trend Up"
            
        # 🟢 STRATEGY 2: BOLLINGER BAND SNIPER (Dip Buy)
        # Price dropped to BB Lower Band but macro trend is UP (Price > EMA200)
        elif (curr['low'] <= bb_lower or prev['low'] <= bb_lower) and is_green_candle and rsi < 40:
            score += 45
            signal, reason = "BUY REVERSAL 🟢", "BB Lower Band Bounce"

    # 🔴 STRATEGY 3: TAKE PROFIT / SELL WARNING
    # If RSI > 80 or price touches upper Bollinger Band
    if rsi > 80 or curr['high'] >= bb_upper:
        score -= 30
        if "BUY" in signal:
            signal = "WAIT ⏳" # Cancel buy if overbought
        else:
            signal, reason = "SELL 🔴", "Overbought / BB Upper"
    
    # RISK MANAGEMENT (ATR Based)
    stop_loss = price - (1.5 * atr) 
    target = price + (3.0 * atr)  # 1:2 Risk Reward ratio
    
    # Position Sizing
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
