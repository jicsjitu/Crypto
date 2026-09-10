# config.py

CANDLE_URL = "https://public.coindcx.com/market_data/candles"
USER_URL = "https://api.coindcx.com/exchange/v1/users/balances"

TIMEFRAME = '15m'
RISK_PER_TRADE = 0.02  # 2% Risk

PAIRS = {
    'B-BTC_INR': 'btcinr', 'B-ETH_INR': 'ethinr', 'B-BNB_INR': 'bnbinr',
    'B-SOL_INR': 'solinr', 'B-XRP_INR': 'xrpinr', 'B-DOGE_INR': 'dogeinr',
    'B-SHIB_INR': 'shibinr', 'B-PEPE_INR': 'pepeinr', 'B-BONK_INR': 'bonkinr',
    'B-FLOKI_INR': 'flokiinr', 'B-WIF_INR': 'wifinr', 'B-MEME_INR': 'memeinr',
    'B-FET_INR': 'fetinr', 'B-RNDR_INR': 'rndrinr', 'B-NEAR_INR': 'nearinr',
    'B-GALA_INR': 'galainr', 'B-MATIC_INR': 'maticinr', 'B-ADA_INR': 'adainr',
    'B-TRX_INR': 'trxinr', 'B-AVAX_INR': 'avaxinr', 'B-DOT_INR': 'dotinr',
    'B-ATOM_INR': 'atominr', 'B-FANTOM_INR': 'ftminr', 'B-LINK_INR': 'linkinr',
    'B-APT_INR': 'aptinr', 'B-PAXG_INR': 'paxginr', 'B-XAUT_INR': 'xautinr',
    'B-ULTIMA_INR': 'ultimainr', 'B-ZEC_INR': 'zecinr', 'B-BIFI_INR': 'bifinr',
    'B-BDX_INR': 'bdxinr', 'B-HTX_INR': 'htxinr', 'B-SIREN_INR': 'sireninr',
    'B-SUI_INR': 'suiinr', 'B-OM_INR': 'ominr', 'B-VVV_INR': 'vvvinr',
    'B-ZRO_INR': 'zroinr',
}
