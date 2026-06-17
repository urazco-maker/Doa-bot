import os
import requests
import yfinance as yf

TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = "8662141509"

WATCHLIST = ["AAPL", "TSLA", "NVDA", "AMD", "META", "AMZN", "MSFT", "GOOGL"]

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def analyze(symbol):
    data = yf.download(symbol, period="5d", interval="1h")

    if len(data) < 20:
        return None

    close = data["Close"]
    volume = data["Volume"]

    price_change = (close.iloc[-1] - close.iloc[-10]) / close.iloc[-10] * 100
    vol_change = (volume.iloc[-1] - volume.mean()) / volume.mean() * 100

    score = 0

    # 🧠 momentum
    if price_change > 4:
        score += 3
    elif price_change > 2:
        score += 2
    elif price_change < -4:
        score -= 3

    # 📊 volume spike
    if vol_change > 80:
        score += 3
    elif vol_change > 40:
        score += 2

    # ⚠️ risk filter
    if abs(price_change) > 12:
        score -= 3

    if volume.mean() < 1e6:
        score -= 2

    return symbol, price_change, vol_change, score


results = []

for s in WATCHLIST:
    r = analyze(s)

    if r:
        sym, pc, vc, sc = r

        if sc >= 7:
            results.append(f"🔥 BUY SIGNAL\n{sym}\nScore: {sc}/10\nPrice: {pc:.2f}%\nVolume: {vc:.1f}%")

        elif sc >= 4:
            results.append(f"👀 WATCH\n{sym}\nScore: {sc}/10")

        else:
            results.append(f"⚠️ WEAK\n{sym}\nScore: {sc}/10")

if results:
    send("\n\n".join(results))
else:
    send("📊 PRO Bot: net sinyal yok")
