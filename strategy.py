# strategy.py (Puri file replace kardo)
import time
import config
import api
from indicators import apply_all_indicators

def analyze_coin(df, pair_name, balance, btc_is_bullish):
    df = apply_all_indicators(df)
    
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    price = curr['close']
    ema_50 = curr['ema_50']
    ema_200 = curr['ema_200']
    rsi = curr['rsi']
    atr = curr['atr'] if curr['atr'] > 0 else price * 0.01
    macd, macd_sig = curr['macd'], curr['macd_signal']
    bb_lower, bb_upper = curr['bb_lower'], curr['bb_upper']
    whale_alert = curr['whale_spike'] # 🐋
    
    is_green_candle = price > curr['open'] 
    has_volume = (curr['volume'] > curr['vol_ma']) or (prev['volume'] > prev['vol_ma'])
    
    stop_loss = price - (2.0 * atr) 
    target = price + (4.0 * atr) 
    trailing_sl = price - (1.2 * atr) # 📈 Dynamic TSL
    
    trend_status = "BULLISH 🟢" if price > ema_200 else "BEARISH 🔴"
    signal, reason, score = "WAIT ⏳", f"Trend: {trend_status}", 0
    
    if has_volume: score += 10
        
    # 🚀 STRATEGY 1: MOMENTUM RIDER
    if price > ema_50 and macd > macd_sig and 40 < rsi < 70 and has_volume:
        score += 50
        signal, reason = "BUY TREND 🚀", "Momentum & Vol Uptrend"
        if price > ema_200: score += 15 
            
    # 🟢 STRATEGY 2: THE PANIC DIP
    elif rsi < 32 and (curr['low'] <= bb_lower or prev['low'] <= bb_lower):
        score += 65
        signal, reason = "BUY DIP 🟢", "Panic Sell Bounce"
        stop_loss = price - (1.5 * atr)

    # 🔴 STRATEGY 3: TAKE PROFIT
    elif rsi > 78 or curr['high'] >= (bb_upper + (atr * 0.5)):
        score -= 40
        if "BUY" in signal: signal = "WAIT ⏳"
        else: signal, reason = "SELL 🔴", "Overbought / Peak"

    # 👑 THE KING FILTER (BTC Trend Check)
    if "BUY" in signal and not btc_is_bullish:
        # Trade cancel nahi hogi, bas warning milegi taaki tum quantity kam rakho
        reason += " ⚠️ (BTC BEARISH)"
        score -= 20 

    # 🐋 WHALE TRACKER
    if "BUY" in signal and whale_alert:
        reason = "🐋 WHALE ENTRY + " + reason
        score += 30 # High Conviction Trade!

    risk = price - stop_loss
    qty, amt = 0, 0
    if "BUY" in signal and risk > 0 and balance > 0:
        risk_amt = balance * config.RISK_PER_TRADE
        if not btc_is_bullish: risk_amt = risk_amt / 2 # BTC down hai toh risk aada (half) kar diya!
        
        qty = risk_amt / risk
        amt = qty * price
        if amt > balance: 
            amt, qty = balance, amt / price
            
    return {
        "pair": pair_name.replace("B-", "").replace("_", "/"),
        "price": price, "signal": signal, "score": score,
        "reason": reason, "target": target, "stop_loss": stop_loss,
        "tsl": trailing_sl, # Naya feature added
        "rsi": rsi, "qty": qty, "invest_amt": amt
    }

def run_agent(current_balance, tf):
    results = []
    
    # 👑 THE KING FILTER (Pehle BTC ka Trend check karenge 4H par)
    btc_df = api.fetch_candles('B-BTC_INR', '4h')
    btc_is_bullish = True
    if btc_df is not None:
        btc_df = apply_all_indicators(btc_df)
        if btc_df.iloc[-1]['close'] < btc_df.iloc[-1]['ema_200']:
            btc_is_bullish = False # BTC Crash mode me hai!

    for coindcx_pair in config.PAIRS.keys():
        df = api.fetch_candles(coindcx_pair, tf)
        if df is not None:
            analysis = analyze_coin(df, coindcx_pair, current_balance, btc_is_bullish)
            if analysis: results.append(analysis)
        time.sleep(0.05) 
        
    results.sort(key=lambda x: x['score'], reverse=True)
    return results, btc_is_bullish
