# app.py
import streamlit as st
import time
import api
from strategy import run_agent

# --- PAGE CONFIG ---
st.set_page_config(page_title="Pro Terminal", layout="wide", page_icon="🦅")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .buy-row { background-color: #004400; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #00FF00; }
    .sell-row { background-color: #440000; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #FF4444; }
    .wait-row { background-color: #1E1E1E; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #555; }
    .big-font { font-size: 18px; font-weight: bold; font-family: monospace; }
    
    /* Faltu space hatane ke liye */
    .block-container { padding-top: 2rem; padding-bottom: 0rem; }
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR (Clean Controls) ---
st.sidebar.markdown("### ⚙️ Settings")
selected_tf = st.sidebar.selectbox("⏱️ Timeframe", ["15m", "1h", "4h"], index=1) # 1h default for pro mode
use_sim = st.sidebar.checkbox("🎮 Simulator Mode", value=True)
sim_balance = st.sidebar.number_input("Virtual Capital (₹)", value=50000, step=1000)
st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("🔄 Auto-Refresh (3 Mins)", value=True)
if st.sidebar.button("⚡ Manual Refresh"): 
    st.rerun()

# --- FETCH DATA ---
real_balance = api.get_wallet_balance()
current_balance = sim_balance if use_sim else real_balance

# Notice: Yahan ab hum selected_tf pass kar rahe hain
data = run_agent(current_balance, selected_tf)

# --- TOP BAR (Minimalist) ---
c1, c2 = st.columns([1, 1])
lbl = "🎮 Virtual Balance" if use_sim else "💼 Real Wallet Balance"
c1.markdown(f"#### 🦅 1% Trader Terminal | {lbl}: **₹ {current_balance:,.2f}**")
st.markdown("---")

# --- MAIN TABLE ---
if not data:
    st.error("❌ No Data Received. API Check karo.")
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
    for item in data:
        if "BUY" in item['signal']: row_class, icon, sig_color = "buy-row", "🚀", "#00FF00"
        elif "SELL" in item['signal']: row_class, icon, sig_color = "sell-row", "🔻", "#FF4444"
        else: row_class, icon, sig_color = "wait-row", "⏳", "#AAA"

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
                    <div style="width: 30%; font-size: 13px; color: #DDD;">{item['reason']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Trade Details sirf tab jab Buy ho
            if "BUY" in item['signal'] and item['qty'] > 0:
                t_fmt = f"₹{item['target']:.6f}" if item['target'] < 50 else f"₹{item['target']:,.2f}"
                s_fmt = f"₹{item['stop_loss']:.6f}" if item['stop_loss'] < 50 else f"₹{item['stop_loss']:,.2f}"
                
                tc1, tc2, tc3, tc4 = st.columns([1, 1, 1, 1])
                tc1.success(f"Target: {t_fmt}")
                tc2.error(f"SL: {s_fmt}")
                tc3.info(f"Qty: {item['qty']:.4f}")
                tc4.warning(f"Invest: ₹{item['invest_amt']:,.0f}")
                st.markdown("---")

# --- SILENT AUTO REFRESH ---
if auto_refresh:
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(1.8) # 3 Minutes (180s)
        progress_bar.progress(i + 1)
    st.rerun()
