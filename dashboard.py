# app.py
import streamlit as st
import time
import api
from strategy import run_agent

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pro Terminal", layout="wide", page_icon="🦅")

# --- PRO STYLING (True Binance Dark Theme) ---
st.markdown("""
<style>
    /* Main Background */
    .stApp { background-color: #0b0e11; color: #eaecef; }
    .block-container { padding-top: 2rem; padding-bottom: 0rem; max-width: 95%; }
    header { visibility: hidden; }
    
    /* Custom Row Cards */
    .trade-card { 
        background-color: #181a20; 
        padding: 20px; 
        border-radius: 8px; 
        border: 1px solid #2b3139; 
        box-shadow: 0 4px 8px rgba(0,0,0,0.4);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Accent Borders */
    .card-buy { border-left: 6px solid #0ecb81; }
    .card-sell { border-left: 6px solid #f6465d; }
    .card-wait { border-left: 6px solid #474d57; }
    
    /* Typography */
    .col-title { font-size: 11px; color: #848e9c; text-transform: uppercase; font-weight: 600; margin-bottom: 6px; letter-spacing: 0.5px; }
    .col-val { font-size: 16px; font-weight: bold; color: #eaecef; }
    .pair-name { font-size: 18px; font-weight: 900; color: #fcd535; }
    
    /* Specific Text Colors */
    .text-green { color: #0ecb81 !important; }
    .text-red { color: #f6465d !important; }
    .text-gray { color: #848e9c !important; }
    .text-whale { color: #0ea5e9 !important; font-weight: bold; text-shadow: 0 0 5px rgba(14,165,233,0.3); } /* Whale Blue Highlight */
    
    /* Sub-row for Trade Plan */
    .trade-plan-row { 
        margin-top: 16px; 
        padding-top: 16px; 
        border-top: 1px dashed #2b3139; 
        display: flex; 
        justify-content: space-between;
        align-items: center;
    }
    .plan-box { display: flex; gap: 8px; align-items: baseline; }
</style>
""", unsafe_allow_html=True)

# --- CACHE LOGIC (Instant Filtering) ---
@st.cache_data(ttl=180, show_spinner=False)
def get_market_data(tf, balance):
    return run_agent(balance, tf)

# --- TOP CONTROL BAR (Ultra Clean) ---
col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 2, 1.5, 1.5])

with col1:
    selected_tf = st.selectbox("⏱️ Timeframe", ["15m", "1h", "4h"], index=1)
with col2:
    filter_opt = st.selectbox("🔍 Filter Signal", ["All", "BUY", "SELL"])
with col3:
    st.write("") # Spacer
with col4:
    st.write("")
    auto_refresh = st.checkbox("🔄 Auto-Refresh (3 Min)", value=True)
with col5:
    st.write("")
    if st.button("⚡ Scan Market", use_container_width=True):
        get_market_data.clear()
        st.rerun()

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

# --- FETCH DATA ---
real_balance = api.get_wallet_balance()
display_balance = real_balance if real_balance > 0 else 50000.0 

# Data unpack: Ab strategy.py results aur btc_is_bullish dono return karta hai
result_data = get_market_data(selected_tf, display_balance)

# Safety check agar purana data cache mein ho
if isinstance(result_data, tuple):
    data, btc_bullish = result_data
else:
    data, btc_bullish = result_data, True

# --- 👑 TOP BANNER: BTC GLOBAL TREND ---
btc_status = "BULLISH 🟢 (Safe to Trade)" if btc_bullish else "BEARISH 🔴 (Risk is High - Trading Quantities Halved)"
btc_color = "#0ecb81" if btc_bullish else "#f6465d"
st.markdown(f"""
<div style='background-color: #181a20; padding: 12px 20px; border-radius: 8px; border-left: 4px solid {btc_color}; margin-bottom: 20px; border-top: 1px solid #2b3139; border-right: 1px solid #2b3139; border-bottom: 1px solid #2b3139;'>
    <b style='color:#848e9c; font-size:12px; letter-spacing:1px; font-family: sans-serif;'>👑 GLOBAL BTC (4H) TREND:</b>&nbsp;&nbsp;
    <span style='color: {btc_color}; font-weight:bold; font-size:16px; font-family: sans-serif;'>{btc_status}</span>
</div>
""", unsafe_allow_html=True)

# --- FILTER DATA ---
filtered_data = []
if data:
    for item in data:
        if filter_opt == "BUY" and "BUY" not in item['signal']: continue
        if filter_opt == "SELL" and "SELL" not in item['signal']: continue
        filtered_data.append(item)

# --- RENDER MAIN TABLE ---
if not filtered_data:
    st.info(f"⚠️ No '{filter_opt}' setups found on {selected_tf} timeframe right now.")
else:
    for item in filtered_data:
        if "BUY" in item['signal']: 
            card_class, icon, sig_color = "card-buy", "🚀", "text-green"
        elif "SELL" in item['signal']: 
            card_class, icon, sig_color = "card-sell", "🔻", "text-red"
        else: 
            card_class, icon, sig_color = "card-wait", "⏳", "text-gray"

        p_fmt = f"₹{item['price']:.6f}" if item['price'] < 50 else f"₹{item['price']:,.2f}"
        
        # 🐋 Whale Reason Glow effect logic
        reason_html = item['reason']
        if "🐋" in reason_html:
            reason_html = reason_html.replace("🐋 WHALE ENTRY +", "<span class='text-whale'>🐋 WHALE ENTRY</span> +")
            reason_html = reason_html.replace("🐋 WHALE ENTRY", "<span class='text-whale'>🐋 WHALE ENTRY</span>")
        
        # Single line HTML for Main Row
        html_content = f"<div class='trade-card {card_class}'><div style='display: flex; justify-content: space-between; align-items: center;'><div style='width: 15%;'><div class='col-title'>PAIR</div><div class='pair-name'>{item['pair']}</div></div><div style='width: 20%;'><div class='col-title'>LIVE PRICE</div><div class='col-val'>{p_fmt}</div></div><div style='width: 15%;'><div class='col-title'>SIGNAL</div><div class='col-val {sig_color}'>{icon} {item['signal']}</div></div><div style='width: 10%;'><div class='col-title'>RSI</div><div class='col-val'>{item['rsi']:.1f}</div></div><div style='width: 10%;'><div class='col-title'>SCORE</div><div class='col-val'>{item['score']}</div></div><div style='width: 30%;'><div class='col-title'>ANALYSIS REASON</div><div class='col-val' style='font-size: 14px; font-weight: normal; color: #b7bdc6;'>{reason_html}</div></div></div>"

        # Append Trade Plan sub-row if BUY (With TRAIL-SL added)
        if "BUY" in item['signal'] and item.get('qty', 0) > 0:
            t_fmt = f"₹{item['target']:.6f}" if item['target'] < 50 else f"₹{item['target']:,.2f}"
            s_fmt = f"₹{item['stop_loss']:.6f}" if item['stop_loss'] < 50 else f"₹{item['stop_loss']:,.2f}"
            tsl_fmt = f"₹{item.get('tsl', 0):.6f}" if item.get('tsl', 0) < 50 else f"₹{item.get('tsl', 0):,.2f}" # Trailing SL Fetch
            invest_fmt = f"₹{item.get('invest_amt', 0):,.0f}"
            
            html_content += f"<div class='trade-plan-row'><div class='plan-box'><span class='col-title'>TARGET:</span> <span class='col-val text-green'>{t_fmt}</span></div><div class='plan-box'><span class='col-title'>STOP-LOSS:</span> <span class='col-val text-red'>{s_fmt}</span></div><div class='plan-box'><span class='col-title text-whale'>TRAIL-SL:</span> <span class='col-val'>{tsl_fmt}</span></div><div class='plan-box'><span class='col-title'>QTY:</span> <span class='col-val'>{item['qty']:.4f}</span></div><div class='plan-box'><span class='col-title'>CAPITAL REQ:</span> <span class='col-val'>{invest_fmt}</span></div></div>"
            
        html_content += "</div>"
        
        # Spacer
        html_content += "<div style='height: 15px;'></div>"
        
        st.markdown(html_content, unsafe_allow_html=True)

# --- SILENT REFRESH ---
if auto_refresh:
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(1.8) # 3 Mins Total
        progress_bar.progress(i + 1)
    
    get_market_data.clear()
    st.rerun()
