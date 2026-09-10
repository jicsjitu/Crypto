# app.py
import streamlit as st
import time
import api
from strategy import run_agent

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pro Terminal", layout="wide", page_icon="🦅")

# --- PRO STYLING (Binance / Premium Dark Theme) ---
st.markdown("""
<style>
    /* Main Background & Cleanups */
    .stApp { background-color: #0b0e11; color: #eaecef; }
    .block-container { padding-top: 2rem; padding-bottom: 0rem; max-width: 95%; }
    header { visibility: hidden; }
    
    /* Hide Streamlit default components spacing */
    div[data-testid="stVerticalBlock"] { gap: 0rem; }

    /* Custom Row Cards */
    .trade-card { 
        padding: 16px 20px; 
        border-radius: 8px; 
        margin-bottom: 12px; 
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    /* Card Variants */
    .card-buy { background: linear-gradient(90deg, #064e3b 0%, #022c22 100%); border-left: 6px solid #10b981; }
    .card-sell { background: linear-gradient(90deg, #7f1d1d 0%, #450a0a 100%); border-left: 6px solid #ef4444; }
    .card-wait { background: #1e2329; border-left: 6px solid #474d57; }
    
    /* Typography */
    .col-title { font-size: 12px; color: #848e9c; text-transform: uppercase; font-weight: 600; margin-bottom: 4px; }
    .col-val { font-size: 16px; font-weight: bold; }
    .pair-name { font-size: 18px; font-weight: 900; color: #fcd535; }
    
    /* Specific Colors */
    .text-green { color: #10b981; }
    .text-red { color: #ef4444; }
    .text-gray { color: #b7bdc6; }
    
    /* Sub-row for Trade Plan */
    .trade-plan-row { 
        margin-top: 12px; 
        padding-top: 12px; 
        border-top: 1px solid rgba(255,255,255,0.1); 
        display: flex; 
        justify-content: space-between;
        font-size: 14px;
        background-color: rgba(0,0,0,0.15);
        border-radius: 6px;
        padding: 10px 15px;
    }
    .plan-box { display: flex; gap: 8px; align-items: center; }
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

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# --- FETCH DATA ---
real_balance = api.get_wallet_balance()
display_balance = real_balance if real_balance > 0 else 50000.0 
data = get_market_data(selected_tf, display_balance)

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
        
        # FIX: Single line HTML construction to prevent Markdown Code Block bug
        html_content = f"<div class='trade-card {card_class}'><div style='display: flex; justify-content: space-between; align-items: center;'><div style='width: 15%;'><div class='col-title'>Pair</div><div class='pair-name'>{item['pair']}</div></div><div style='width: 20%;'><div class='col-title'>Live Price</div><div class='col-val'>{p_fmt}</div></div><div style='width: 15%;'><div class='col-title'>Signal</div><div class='col-val {sig_color}'>{icon} {item['signal']}</div></div><div style='width: 10%;'><div class='col-title'>RSI</div><div class='col-val'>{item['rsi']:.1f}</div></div><div style='width: 10%;'><div class='col-title'>Score</div><div class='col-val'>{item['score']}</div></div><div style='width: 30%;'><div class='col-title'>Analysis Reason</div><div class='col-val' style='font-size: 14px; font-weight: normal;'>{item['reason']}</div></div></div>"

        # Append Trade Plan if BUY
        if "BUY" in item['signal'] and item.get('qty', 0) > 0:
            t_fmt = f"₹{item['target']:.6f}" if item['target'] < 50 else f"₹{item['target']:,.2f}"
            s_fmt = f"₹{item['stop_loss']:.6f}" if item['stop_loss'] < 50 else f"₹{item['stop_loss']:,.2f}"
            
            html_content += f"<div class='trade-plan-row'><div class='plan-box'><span class='col-title'>Target:</span> <span class='text-green' style='font-weight:bold;'>{t_fmt}</span></div><div class='plan-box'><span class='col-title'>Stop-Loss:</span> <span class='text-red' style='font-weight:bold;'>{s_fmt}</span></div><div class='plan-box'><span class='col-title'>Qty:</span> <span class='col-val'>{item['qty']:.4f}</span></div><div class='plan-box'><span class='col-title'>Capital Req:</span> <span class='col-val text-gray'>₹{item.get('invest_amt', 0):,.0f}</span></div></div>"
            
        html_content += "</div>"
        
        st.markdown(html_content, unsafe_allow_html=True)

# --- SILENT REFRESH ---
if auto_refresh:
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(1.8) # 3 Mins Total
        progress_bar.progress(i + 1)
    
    get_market_data.clear()
    st.rerun()
