import os
import requests
import yfinance as yf

print("BOT STARTED")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "CHAT_ID"

WATCHLIST = ["AAPL", "TSLA", "NVDA", "AMD", "META", "AMZN", "MSFT"]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })
    print("Telegram response:", response.status_code)

def analyze(symbol):
    try:
        data = yf.download(symbol, period="5d", interval="1h")

        if data is None or len(data) < 10:
            return None

        price_change = (data["Close"].iloc[-1] - data["Close"].iloc[-5]) / data["Close"].iloc[-5] * 100
        volume_avg = data["Volume"].mean()
        volume_last = data["Volume"].iloc[-1]

        vol_change = ((volume_last - volume_avg) / volume_avg) * 100

        score = 0

        # Momentum
        if price_change > 3:
            score += 3
        elif price_change > 1:
            score += 1
        elif price_change < -3:
            score -= 3

        # Volume spike
        if vol_change > 50:
            score += 2

        # Risk filter
        if abs(price_change) > 10:
            score -= 3

        return symbol, price_change, vol_change, score

    except Exception as e:
        print("Error:", symbol, e)
        return None


results = []

for stock in WATCHLIST:
    r = analyze(stock)

    if r:
        sym, pc, vc, sc = r

        if sc >= 5:
            results.append(f"🔥 BUY SIGNAL\n{sym}\nScore: {sc}/10\nPrice: {pc:.2f}%\nVolume: {vc:.1f}%")

        elif sc >= 2:
            results.append(f"👀 WATCH\n{sym}\nScore: {sc}/10")

        else:
            results.append(f"⚠️ WEAK\n{sym}\nScore: {sc}/10")

if results:
    send_message("\n\n".join(results))
else:
    send_message("📊 PRO BOT: No strong signals")

print("BOT FINISHED")
