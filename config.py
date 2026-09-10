# config.py

CANDLE_URL = "https://public.coindcx.com/market_data/candles"
USER_URL = "https://api.coindcx.com/exchange/v1/users/balances"

TIMEFRAME = '1h'
RISK_PER_TRADE = 0.02  # 2% Risk

TELEGRAM_BOT_TOKEN = "DUMMY_TOKEN" 
TELEGRAM_CHAT_ID = "DUMMY_CHAT_ID"

PAIRS = {
    # 👑 Core Majors & High Liquidity
    'B-BTC_INR': 'btcinr', 
    'B-ETH_INR': 'ethinr', 
    'B-SOL_INR': 'solinr', 
    'B-XRP_INR': 'xrpinr', 
    'B-BNB_INR': 'bnbinr', 
    'B-ADA_INR': 'adainr',
    'B-AVAX_INR': 'avaxinr', 
    'B-LINK_INR': 'linkinr', 
    'B-NEAR_INR': 'nearinr',
    'B-TRX_INR': 'trxinr',
    'B-DOT_INR': 'dotinr',
    
    # 🚀 Fast Layer-1s & Layer-2s (High Momentum)
    'B-SUI_INR': 'suiinr', 
    'B-ARB_INR': 'arbinr', 
    'B-OP_INR': 'opinr',
    'B-SEI_INR': 'seiinr', 
    'B-ICP_INR': 'icpinr', 
    'B-APT_INR': 'aptinr', 
    'B-TIA_INR': 'tiainr', 
    'B-POL_INR': 'polinr',
    'B-ATOM_INR': 'atominr',
    'B-ZRO_INR': 'zroinr',
    
    # 🤖 AI, DeFi & Infrastructure Powerhouses
    'B-FET_INR': 'fetinr', 
    'B-RENDER_INR': 'renderinr', 
    'B-INJ_INR': 'injinr',
    'B-UNI_INR': 'uniinr', 
    'B-GRT_INR': 'grtinr', 
    'B-OM_INR': 'ominr',
    
    # 🔥 Viral Memes & High Volatility (The Money Makers)
    'B-PEPE_INR': 'pepeinr', 
    'B-DOGE_INR': 'dogeinr', 
    'B-SHIB_INR': 'shibinr',
    'B-WIF_INR': 'wifinr', 
    'B-BONK_INR': 'bonkinr', 
    'B-FLOKI_INR': 'flokiinr', 
    'B-JUP_INR': 'jupinr', 
    'B-MEME_INR': 'memeinr',
    'B-GALA_INR': 'galainr'
}
