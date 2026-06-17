import os
import requests
import yfinance as yf

print("V6 BOT STARTED")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "8662141509"

WATCHLIST = ["AAPL", "TSLA", "NVDA", "AMD", "META", "AMZN", "MSFT"]

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def analyze(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="1h")

        if data is None or len(data) < 10:
            return None

        close = float(data["Close"].iloc[-1])
        prev = float(data["Close"].iloc[-5])

        price_change = ((close - prev) / prev) * 100

        volume_avg = float(data["Volume"].mean())
        volume_last = float(data["Volume"].iloc[-1])

        volume_change = ((volume_last - volume_avg) / volume_avg) * 100

        score = 0

        # 📈 trend
        if price_change > 4:
            score += 3
        elif price_change > 2:
            score += 2
        elif price_change < -4:
            score -= 3

        # 📊 volume
        if volume_change > 70:
            score += 3
        elif volume_change > 30:
            score += 1

        # ⚠️ risk filter
        if abs(price_change) > 12:
            score -= 3

        return symbol, price_change, volume_change, score

    except Exception as e:
        print("ERROR:", symbol, e)
        return None


results = []

for s in WATCHLIST:
    r = analyze(s)

    if r:
        sym, pc, vc, sc = r

        if sc >= 6:
            results.append(f"🔥 BUY SIGNAL\n{sym}\nScore: {sc}/10\nPrice: {pc:.2f}%\nVolume: {vc:.1f}%")

        elif sc >= 3:
            results.append(f"👀 WATCH\n{sym}\nScore: {sc}/10")

        else:
            results.append(f"⚠️ WEAK\n{sym}\nScore: {sc}/10")

if results:
    send("\n\n".join(results))
else:
    send("📊 V6 BOT: No strong signals")

print("V6 BOT FINISHED")
