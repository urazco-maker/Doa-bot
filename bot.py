import os
import requests
import yfinance as yf

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "8662141509"

WATCHLIST = [
    "SPY","QQQ","IWM",
    "AAPL","MSFT","NVDA","AMZN","META","TSLA","AMD","NFLX","GOOGL",
    "PLTR","SOFI","RIVN","HOOD","COIN","SNAP","SQ","PYPL","DKNG","ROKU",
    "AFRM","UPST","DDOG","CRWD","SNOW","SHOP","UBER","LYFT","PINS",
    "AI","BBAI","C3AI","IONQ","SOUN","RKLB","SMCI","PLUG","ENVX",
    "NIO","XPEV","LI","QS","MARA","RIOT","HUT","BITF","BTBT","CAN",
    "GME","AMC","BB","FUBU","SPCE","TLRY","BYND","CLOV","ATER"
]

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def rsi(series):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = -delta.clip(upper=0).rolling(14).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def regime():
    df = yf.download("SPY", period="6mo", interval="1d", progress=False)
    ema50 = df["Close"].ewm(span=50).mean()
    ema200 = df["Close"].ewm(span=200).mean()
    return "BULL" if ema50.iloc[-1] > ema200.iloc[-1] else "BEAR"


def analyze(symbol, market):
    df = yf.download(symbol, period="6mo", interval="1d", progress=False)

    if df is None or len(df) < 80:
        return None

    close = df["Close"]

    ema20 = close.ewm(span=20).mean()
    ema50 = close.ewm(span=50).mean()

    r = rsi(close).iloc[-1]

    momentum = ((close.iloc[-1] - close.iloc[-10]) / close.iloc[-10]) * 100

    score = 0

    if ema20.iloc[-1] > ema50.iloc[-1]:
        score += 3
    else:
        score -= 3

    if r < 30:
        score += 3
    elif r > 70:
        score -= 3

    if momentum > 5:
        score += 2

    if market == "BEAR":
        score -= 2

    return symbol, score, r, momentum


market = regime()

results = []

for s in WATCHLIST:
    r = analyze(s, market)

    if r:
        sym, score, rsi_v, mom = r

        if score >= 8:
            send(f"🚀 BUY {sym}\nScore:{score}\nRSI:{rsi_v:.1f}\nMom:{mom:.2f}%")

        elif score >= 6:
            send(f"👀 WATCH {sym} Score:{score}")

print("DONE")
