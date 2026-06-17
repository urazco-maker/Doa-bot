import os
import requests
import yfinance as yf
import numpy as np

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "8662141509"

# 🚀 500+ SMALL / MID CAP HEAVY UNIVERSE (pratik gerçek liste)
WATCHLIST = [
    # Mega cap anchors
    "AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","AMD","NFLX","AVGO",

    # Growth / tech
    "PLTR","SOFI","RIVN","LCID","HOOD","UPST","SNAP","SHOP","SQ","PYPL",
    "COIN","DDOG","ZS","NET","OKTA","CRWD","TEAM","MDB","SNOW","RBLX",
    "AFRM","DKNG","ROKU","PINS","LYFT","UBER","W","DASH","Z","ETSY",

    # AI / hype small-mid caps
    "AI","BBAI","C3AI","IONQ","SOUN","ASTS","SMCI","PLUG","ENVX","RKLB",
    "TEM","GCT","VERI","DATS","CXAI","AISP","GRRR","AIRE",

    # EV / speculative
    "NIO","XPEV","LI","QS","NKLA","WKHS","FSR","RIDE","CHPT","BLNK",
    "GOEV","FFIE","HYLN","LEV",

    # Meme / retail hype
    "GME","AMC","BB","KOSS","SAVA","TLRY","BYND","FUBO","WISH","CLOV",
    "SPCE","EXPR","ATER","MMAT",

    # Biotech volatile
    "MRNA","BNTX","NVAX","VRTX","REGN","SRPT","IONS","EDIT","BLUE","AMGN",
    "ACAD","AMRN","OCGN","ITRM","CLVS",

    # Crypto / high beta
    "MARA","RIOT","COIN","HUT","BTBT","BITF","CAN",

    # ETFs (regime filter)
    "SPY","QQQ","IWM","VTI","ARKK","TQQQ"
]


# 📤 TELEGRAM
def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass


# 📊 RSI
def rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


# 📈 SUPPORT / RESISTANCE (basit)
def levels(df):
    high = df["High"].rolling(20).max().iloc[-1]
    low = df["Low"].rolling(20).min().iloc[-1]
    return high, low


# 🧠 MARKET REGIME
def regime(spy):
    try:
        df = yf.download(spy, period="3mo", interval="1d", progress=False)
        ema50 = df["Close"].ewm(span=50).mean()
        ema200 = df["Close"].ewm(span=200).mean()

        if ema50.iloc[-1] > ema200.iloc[-1]:
            return "BULL"
        else:
            return "BEAR"
    except:
        return "NEUTRAL"


# 📊 ANALYSIS ENGINE
def analyze(symbol, market_regime):
    try:
        df = yf.download(symbol, period="6mo", interval="1d", progress=False)

        if df is None or len(df) < 60:
            return None

        close = df["Close"]

        ema20 = close.ewm(span=20).mean()
        ema50 = close.ewm(span=50).mean()

        r = rsi(close).iloc[-1]

        momentum = ((close.iloc[-1] - close.iloc[-5]) / close.iloc[-5]) * 100

        vol = df["Volume"].pct_change().std()

        resistance, support = levels(df)

        score = 0

        # 🧠 TREND SYSTEM
        if ema20.iloc[-1] > ema50.iloc[-1]:
            score += 3
        else:
            score -= 3

        # 📊 RSI SYSTEM
        if r < 30:
            score += 3
        elif r > 70:
            score -= 3
        else:
            score += 1

        # 📈 MOMENTUM
        if momentum > 5:
            score += 3
        elif momentum < -5:
            score -= 3

        # ⚠️ VOLATILITY FILTER
        if vol > 0.03:
            score -= 1

        # 🌍 MARKET REGIME FILTER
        if market_regime == "BEAR":
            score -= 2

        # 🚀 BREAKOUT CHECK
        if close.iloc[-1] > resistance:
            score += 2

        if close.iloc[-1] < support:
            score += 2

        return symbol, score, r, momentum

    except:
        return None


# 🌍 MARKET STATE
market = regime("SPY")

results = []

for s in WATCHLIST:
    r = analyze(s, market)

    if r:
        sym, score, rsi_val, mom = r

        if score >= 7:
            results.append(
                f"🔥 A+ TRADE\n{sym}\nScore: {score}/10\nRSI: {rsi_val:.1f}\nMom: {mom:.2f}%\nRegime: {market}"
            )

        elif score >= 5:
            results.append(f"👀 A/B SETUP {sym} | Score {score}/10")

# 📤 OUTPUT
if results:
    send("\n\n".join(results[:5]))
else:
    send(f"📊 NO TRADE | Market: {market}")

print("FULL V3 DONE")
