# app.py
import streamlit as st
import time
import api
from strategy import run_agent

st.set_page_config(page_title="CoinDCX Pro Terminal", layout="wide", page_icon="🦅")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .buy-row { background-color: #004400; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #00FF00; }
    .sell-row { background-color: #440000; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #FF4444; }
    .wait-row { background-color: #1E1E1E; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #555; }
    .big-font { font-size: 18px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🎮 Controls")
use_sim = st.sidebar.checkbox("Use Simulator Mode", value=True)
sim_balance = st.sidebar.number_input("Virtual Capital (₹)", value=50000)
st.sidebar.markdown("---")
auto_refresh = st.sidebar.checkbox("✅ Auto-Refresh (60s)", value=True)

st.title("🦅 1% Trader: Live Terminal")
if st.button("🔄 MANUAL REFRESH"): st.rerun()

# --- FETCH DATA ---
status = st.empty()
status.info("📡 Scanning Market Data...")

real_balance = api.get_wallet_balance()
current_balance = sim_balance if use_sim else real_balance
data = run_agent(current_balance)

status.empty()

# --- HEADER ---
lbl = "🎮 Virtual Balance" if use_sim else "💼 Real Wallet Balance"
st.markdown(f"### {lbl}: **₹ {current_balance:,.2f}**")
st.markdown("---")

# --- MAIN TABLE ---
if not data:
    st.error("❌ No Data Received. Check API connection.")
else:
    c1, c2, c3, c4, c5, c6 = st.columns([1, 1.5, 1, 1, 1, 2.5])
    c1.write("🪙 PAIR")
    c2.write("💰 PRICE")
    c3.write("📈 SIGNAL")
    c4.write("📊 RSI")
    c5.write("🏆 SCORE")
    c6.write("🤖 ANALYSIS")
    st.markdown("---")

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

            if "BUY" in item['signal'] and item['qty'] > 0:
                t_fmt = f"₹{item['target']:.6f}" if item['target'] < 50 else f"₹{item['target']:,.2f}"
                s_fmt = f"₹{item['stop_loss']:.6f}" if item['stop_loss'] < 50 else f"₹{item['stop_loss']:,.2f}"
                
                c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
                c1.success(f"Target: {t_fmt}")
                c2.error(f"SL: {s_fmt}")
                c3.info(f"Qty: {item['qty']:.4f}")
                c4.warning(f"Invest: ₹{item['invest_amt']:,.0f}")
                st.markdown("---")

# --- AUTO REFRESH ---
if auto_refresh:
    st.write("⏳ Next Refresh in:")
    progress_bar = st.progress(0)
    for i in range(100):
        time.sleep(1.8) 
        progress_bar.progress(i + 1)
    st.rerun()
