import requests
import pandas as pd
from datetime import datetime

# -----------------------------
# TELEGRAM CONFIG
# -----------------------------
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "8662141509"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

# -----------------------------
# WATCHLIST
# -----------------------------
WATCHLIST = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "AMD", "GOOGL"]
MIN_SCORE = 45

# -----------------------------
# PRICE DATA
# -----------------------------
def get_price_data(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
    r = requests.get(url).json()

    try:
        closes = r["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        volumes = r["chart"]["result"][0]["indicators"]["quote"][0]["volume"]
        return closes, volumes
    except:
        return None, None

# -----------------------------
# INDICATORS
# -----------------------------
def rsi(prices):
    s = pd.Series(prices).dropna()
    delta = s.diff()

    gain = (delta.where(delta > 0, 0)).rolling(3).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(3).mean()

    rs = gain / loss
    return 100 - (100 / (1 + rs)).iloc[-1]


def score_symbol(symbol):
    prices, volumes = get_price_data(symbol)
    if prices is None:
        return None

    score = 0

    r = rsi(prices)

    # RSI score
    if r < 30:
        score += 25
    elif r < 45:
        score += 15
    elif r < 60:
        score += 5

    # momentum
    if prices[-1] > prices[-3]:
        score += 15

    # volume
    if volumes[-1] > sum(volumes)/len(volumes):
        score += 10

    return {
        "symbol": symbol,
        "score": round(score, 2),
        "rsi": round(r, 2)
    }

# -----------------------------
# RUN
# -----------------------------
def run():
    results = []

    for s in WATCHLIST:
        data = score_symbol(s)
        if data:
            results.append(data)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    top = [x for x in results if x["score"] >= MIN_SCORE][:5]

    time = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not top:
        top = results[:3]
        msg = "⚠️ LOW QUALITY SET (forced signals)\n\n"
    else:
        msg = "🚀 AGGRESSIVE SIGNALS\n\n"

    msg += f"Time: {time}\n\n"

    for t in top:
        msg += f"{t['symbol']} | SCORE: {t['score']} | RSI: {t['rsi']}\n"

    print(msg)
    send_telegram(msg)

if __name__ == "__main__":
    run()
