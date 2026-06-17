import os
import requests
import yfinance as yf

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "8662141509"

WATCHLIST = [
    "AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","AMD","NFLX","AVGO",
    "PLTR","SOFI","RIVN","LCID","HOOD","UPST","SNAP","SHOP","SQ","PYPL","COIN",
    "DDOG","ZS","NET","OKTA","CRWD","TEAM","MDB","SNOW","RBLX",
    "AI","BBAI","C3AI","IONQ","SOUN","ASTS","SMCI","PLUG","ENVX",
    "NIO","XPEV","LI","QS","MARA","RIOT","COIN","HOOD","DKNG","ROKU"
]

# (opsiyonel) ücretsiz news endpoint placeholder
NEWS_API = None  # istersen sonra Finnhub/Benzinga ekleriz


def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


# 🧠 NEWS SENTIMENT (basit placeholder AI)
def news_score(symbol):
    try:
        # gerçek API yoksa nötr döner
        if NEWS_API is None:
            return 0

        # future: sentiment API
        return 0

    except:
        return 0


# 📊 TECHNICAL SCORE ENGINE
def technical_score(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="30m", progress=False)

        if data is None or len(data) < 25:
            return None

        close = float(data["Close"].iloc[-1])
        prev = float(data["Close"].iloc[-6])

        momentum = ((close - prev) / prev) * 100

        vol_avg = float(data["Volume"].mean())
        vol_now = float(data["Volume"].iloc[-1])
        vol_ratio = vol_now / vol_avg if vol_avg > 0 else 0

        high = float(data["High"].max())
        low = float(data["Low"].min())
        volatility = ((high - low) / low) * 100

        score = 0

        # 🚀 momentum
        if momentum > 1.5: score += 2
        if momentum > 3: score += 3
        if momentum > 6: score += 2

        # 📊 volume breakout
        if vol_ratio > 2.5: score += 5
        elif vol_ratio > 1.8: score += 3
        elif vol_ratio > 1.3: score += 1

        # ⚡ volatility breakout
        if volatility > 12: score += 3
        elif volatility > 8: score += 2

        # 🚫 risk filter
        if abs(momentum) > 15: score -= 3

        return symbol, momentum, vol_ratio, volatility, score

    except:
        return None


results = []

for s in WATCHLIST:
    r = technical_score(s)

    if r:
        sym, m, v, vol, tech = r

        news = news_score(sym)

        # 🧠 FINAL COMPOSITE SCORE (AI ENGINE)
        final_score = tech + news

        results.append({
            "symbol": sym,
            "score": final_score,
            "momentum": m,
            "volume": v,
            "volatility": vol
        })


# 🏆 TOP 10 SELECTION ENGINE
top = sorted(results, key=lambda x: x["score"], reverse=True)[:10]

if not top:
    send("📊 No opportunities found")
else:
    msg = "🔥 TOP 10 TRADE PICKS (AI ENGINE)\n\n"

    for i, t in enumerate(top, 1):
        msg += (
            f"{i}) {t['symbol']}\n"
            f"Score: {t['score']:.2f}/10\n"
            f"Momentum: {t['momentum']:.2f}%\n"
            f"Volume: {t['volume']:.2f}x\n"
            f"Vol: {t['volatility']:.2f}%\n\n"
        )

    send(msg)

print("PRO+ ENGINE DONE")
