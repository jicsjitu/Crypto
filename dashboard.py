import streamlit as st
import time
import api
from strategy import run_agent

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pro Terminal", layout="wide", page_icon="🦅")

# --- UI COLORS & STYLING ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    
    /* Clean Pro Colors for Rows */
    .buy-row { background-color: #052e16; padding: 15px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #22c55e; }
    .sell-row { background-color: #450a0a; padding: 15px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #ef4444; }
    .wait-row { background-color: #1c1917; padding: 15px; border-radius: 8px; margin-bottom: 8px; border-left: 5px solid #57534e; }
    
    .big-font { font-size: 18px; font-weight: bold; font-family: monospace; }
    
    /* Faltu margin aur header hata diya */
    .block-container { padding-top: 1.5rem; padding-bottom: 0rem; }
    header {visibility: hidden;}
    
    /* Radio buttons spacing */
    div.row-widget.stRadio > div{ flex-direction:row; }
</style>
""", unsafe_allow_html=True)

# --- CACHE LOGIC (For Instant Filtering) ---
# Yeh line ensure karegi ki filter change karne par wapas API call na ho!
@st.cache_data(ttl=180, show_spinner=False)
def get_market_data(tf, balance):
    return run_agent(balance, tf)

# --- TOP BAR (No Sidebar, Everything on Top) ---
c1, c2, c3, c4 = st.columns([1.5, 2.5, 1.5, 1.5])

with c1:
    selected_tf = st.selectbox("⏱️ Timeframe", ["15m", "1h", "4h"], index=1)

with c2:
    # Instant Filter!
    filter_opt = st.radio("🔍 Filter Data", ["All", "BUY", "SELL"], horizontal=True)

with c3:
    st.write("") # Button align karne ke liye space
    auto_refresh = st.checkbox("🔄 Auto-Refresh (3 Min)", value=True)

with c4:
    st.write("") # Button align karne ke liye space
    if st.button("⚡ Manual Refresh"):
        get_market_data.clear() # Cache clear hoga aur fresh scan chalega
        st.rerun()

st.markdown("---")

# --- FETCH DATA ---
real_balance = api.get_wallet_balance()
data = get_market_data(selected_tf, real_balance)

# --- APPLY FILTER (Instantly) ---
filtered_data = []
if data:
    for item in data:
        if filter_opt == "BUY" and "BUY" not in item['signal']: continue
        if filter_opt == "SELL" and "SELL" not in item['signal']: continue
        filtered_data.append(item)

# --- MAIN TABLE ---
if not filtered_data:
    st.warning(f"⚠️ Is timeframe par abhi koi '{filter_opt}' setup nahi mila. Thodi der baad check karein.")
else:
    # Table Headers
    hc1, hc2, hc3, hc4, hc5, hc6 = st.columns([1, 1.5, 1, 1, 1, 2.5])
    hc1.write("🪙 PAIR")
    hc2.write("💰 PRICE")
    hc3.write("📈 SIGNAL")
    hc4.write("📊 RSI")
    hc5.write("🏆 SCORE")
    hc6.write("🤖 ANALYSIS")
    st.markdown("---")

    # Data Rows
    for item in filtered_data:
        # Strict Colors apply kiye hain
        if "BUY" in item['signal']: 
            row_class, icon, sig_color = "buy-row", "🚀", "#4ade80" # Bright Green
        elif "SELL" in item['signal']: 
            row_class, icon, sig_color = "sell-row", "🔻", "#f87171" # Bright Red
        else: 
            row_class, icon, sig_color = "wait-row", "⏳", "#a8a29e" # Grey

        p_fmt = f"₹{item['price']:.6f}" if item['price'] < 50 else f"₹{item['price']:,.2f}"
        
        with st.container():
            st.markdown(f"""
            <div class="{row_class}">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="width: 15%; font-weight: bold;">{item['pair']}</div>
                    <div style="width: 20%;" class="big-font">{p_fmt}</div>
                    <div style="width: 15%; font-weight: bold; color: {sig_color};">{icon} {item['signal'].split(' ')[0]}</div>
                    <div style="width: 10%;">{item['rsi']:.1f}</div>
                    <div style="width: 10%; font-weight: bold;">{item['score']}</div>
                    <div style="width: 30%; font-size: 13px; color: #e5e5e5;">{item['reason']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Trade Plan sirf BUY wale setup pe dikhega
            if "BUY" in item['signal'] and item.get('qty', 0) > 0:
                t_fmt = f"₹{item['target']:.6f}" if item['target'] < 50 else f"₹{item['target']:,.2f}"
                s_fmt = f"₹{item['stop_loss']:.6f}" if item['stop_loss'] < 50 else f"₹{item['stop_loss']:,.2f}"
                
                tc1, tc2, tc3, tc4 = st.columns([1, 1, 1, 1])
                tc1.success(f"Target: {t_fmt}")
                tc2.error(f"SL: {s_fmt}")
                tc3.info(f"Qty: {item['qty']:.4f}")
                tc4.warning(f"Invest: ₹{item.get('invest_amt', 0):,.0f}")
                st.markdown("---")

# --- SILENT AUTO REFRESH ---
if auto_refresh:
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(1.8) # 3 Minutes
        progress_bar.progress(i + 1)
    
    # Refresh se pehle cache clear karo taaki naya data aaye
    get_market_data.clear()
    st.rerun()
