import streamlit as st
import time
from backend import run_agent

# --- PAGE CONFIG ---
st.set_page_config(page_title="CoinDCX Pro Terminal", layout="wide", page_icon="🦅")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    .buy-row { background-color: #004400; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #00FF00; }
    .sell-row { background-color: #440000; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #FF4444; }
    .wait-row { background-color: #1E1E1E; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #555; }
    .big-font { font-size: 18px; font-weight: bold; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
st.sidebar.title("🎮 Controls")
use_sim = st.sidebar.checkbox("Use Simulator Mode", value=True)
sim_balance = st.sidebar.number_input("Virtual Capital (₹)", value=50000)

st.sidebar.markdown("---")
# Auto Refresh Toggle
auto_refresh = st.sidebar.checkbox("✅ Auto-Refresh (60s)", value=True)

st.title("🦅 1% Trader: Live Terminal")
if st.button("🔄 MANUAL REFRESH"):
    st.rerun()

# --- MAIN SCANNER ---
status = st.empty()
status.info("📡 Scanning Market Data...")

# Run Backend Agent
data, real_balance = run_agent()
status.empty()

# --- BALANCE DISPLAY ---
current_balance = sim_balance if use_sim else real_balance
lbl = "🎮 Virtual Balance" if use_sim else "💼 Real Wallet Balance"
st.markdown(f"### {lbl}: **₹ {current_balance:,.2f}**")
st.markdown("---")

# --- DATA TABLE ---
if not data:
    st.error("❌ No Data Received. Check API connection.")
else:
    # Headers
    c1, c2, c3, c4, c5, c6 = st.columns([1, 1.5, 1, 1, 1, 2.5])
    c1.write("🪙 PAIR")
    c2.write("💰 PRICE")
    c3.write("📈 SIGNAL")
    c4.write("📊 RSI")
    c5.write("🏆 SCORE")
    c6.write("🤖 ANALYSIS")
    st.markdown("---")

    # Rows
    for item in data:
        # Color Logic
        if "BUY" in item['signal']:
            row_class = "buy-row"
            icon = "🚀"
            sig_color = "#00FF00"
        elif "SELL" in item['signal']:
            row_class = "sell-row"
            icon = "🔻"
            sig_color = "#FF4444"
        else:
            row_class = "wait-row"
            icon = "⏳"
            sig_color = "#AAA"

        # Formatting
        if item['price'] < 50:
            p_fmt = f"₹{item['price']:.6f}"
            t_fmt = f"₹{item['target']:.6f}"
            s_fmt = f"₹{item['stop_loss']:.6f}"
        else:
            p_fmt = f"₹{item['price']:,.2f}"
            t_fmt = f"₹{item['target']:,.2f}"
            s_fmt = f"₹{item['stop_loss']:,.2f}"

        # HTML Row
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

            # Trade Plan (Only for BUY)
            if "BUY" in item['signal']:
                c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
                c1.success(f"Target: {t_fmt}")
                c2.error(f"SL: {s_fmt}")
                
                risk = item['price'] - item['stop_loss']
                if risk > 0:
                    risk_amt = current_balance * 0.02 # 2% Risk per trade
                    qty = risk_amt / risk
                    amt = qty * item['price']
                    
                    # Cap Investment to Balance
                    if amt > current_balance: 
                        amt = current_balance
                        qty = amt / item['price']
                        
                    c3.info(f"Qty: {qty:.4f}")
                    c4.warning(f"Invest: ₹{amt:,.0f}")
                st.markdown("---")

# --- AUTO REFRESH LOGIC ---
if auto_refresh:
    st.write("") # Gap
    st.write("⏳ Next Refresh in:")
    
    # Progress Bar Animation
    progress_bar = st.progress(0)
    for i in range(100):
        # 60 seconds total wait (0.6s * 100)
        time.sleep(0.6) 
        progress_bar.progress(i + 1)
    
    # Refresh Page
    st.rerun()