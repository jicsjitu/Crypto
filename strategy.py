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
    macd = curr['macd']
    macd_sig = curr['macd_signal']
    bb_lower = curr['bb_lower']
    bb_upper = curr['bb_upper']
    
    is_green_candle = price > curr['open'] 
    has_volume = (curr['volume'] > curr['vol_ma']) or (prev['volume'] > prev['vol_ma'])
    
    # Base SL & Target (Crypto Safe Mode: 2x ATR for SL to avoid wick hunting)
    stop_loss = price - (2.0 * atr) 
    target = price + (4.0 * atr)  # 1:2 Risk-Reward
    
    trend_status = "BULLISH 🟢" if price > ema_200 else "BEARISH 🔴"
    signal, reason, score = "WAIT ⏳", f"Trend: {trend_status}", 0
    
    if has_volume: score += 10
        
    # 🚀 STRATEGY 1: MOMENTUM RIDER (Trend Catching)
    # Price EMA 50 ke upar hai, MACD badh raha hai, overbought nahi hai.
    if price > ema_50 and macd > macd_sig and 40 < rsi < 65 and has_volume:
        score += 50
        signal, reason = "BUY TREND 🚀", "Momentum & Vol Uptrend"
        if price > ema_200: 
            score += 20  # Super Safe agar Macro trend bhi UP hai
            
    # 🟢 STRATEGY 2: THE PANIC DIP (Crypto Special)
    # Coin crash hua hai, log darr rahe hain, RSI < 32 aur Bollinger lower touch kiya.
    elif rsi < 32 and (curr['low'] <= bb_lower or prev['low'] <= bb_lower):
        score += 65
        signal, reason = "BUY DIP 🟢", "Panic Sell Bounce"
        # Dip buy mein Stop Loss thoda tight rakhenge
        stop_loss = price - (1.5 * atr)
        target = price + (3.0 * atr)

    # 🔴 STRATEGY 3: PROFIT BOOKING / OVERBOUGHT
    # Market mein fomo hai, dur raho ya sell karo.
    elif rsi > 78 or curr['high'] >= (bb_upper + (atr * 0.5)):
        score -= 40
        if "BUY" in signal:
            signal = "WAIT ⏳" # Entry mat lo
        else:
            signal, reason = "SELL 🔴", "Overbought / FOMO Peak"
    
    # Position Sizing based on risk
    risk = price - stop_loss
    qty, amt = 0, 0
    if "BUY" in signal and risk > 0 and balance > 0:
        risk_amt = balance * config.RISK_PER_TRADE
        qty = risk_amt / risk
        amt = qty * price
        # Cap to max balance
        if amt > balance: 
            amt = balance
            qty = amt / price
            
    return {
        "pair": pair_name.replace("B-", "").replace("_", "/"),
        "price": price, "signal": signal, "score": score,
        "reason": reason, "target": target, "stop_loss": stop_loss,
        "rsi": rsi, "qty": qty, "invest_amt": amt
    }

# Yahan `tf` (timeframe) add kiya gaya hai
def run_agent(current_balance, tf):
    results = []
    for coindcx_pair in config.PAIRS.keys():
        df = api.fetch_candles(coindcx_pair, tf) # Pass tf to api
        if df is not None:
            analysis = analyze_coin(df, coindcx_pair, current_balance)
            if analysis: results.append(analysis)
        time.sleep(0.05) 
        
    results.sort(key=lambda x: x['score'], reverse=True)
    return results
