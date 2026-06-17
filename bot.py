import os
import requests
import pandas as pd
from datetime import datetime

# -----------------------------
# CONFIG (GitHub Secrets)
# -----------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

WATCHLIST = ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "META", "AMD", "GOOGL"]
MIN_SCORE = 45


# -----------------------------
# TELEGRAM
# -----------------------------
def send_telegram(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram credentials missing")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg
    })


# -----------------------------
# PRICE DATA
# -----------------------------
def get_data(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
    r = requests.get(url).json()

    try:
        result = r["chart"]["result"][0]
        closes = result["indicators"]["quote"][0]["close"]
        volumes = result["indicators"]["quote"][0]["volume"]
        return closes, volumes
    except:
        return None, None


# -----------------------------
# INDICATORS
# -----------------------------
def rsi(prices):
    s = pd.Series(prices).dropna()
    if len(s) < 3:
        return 50

    delta = s.diff()
    gain = delta.clip(lower=0).rolling(3).mean()
    loss = (-delta.clip(upper=0)).rolling(3).mean()

    rs = gain / loss
    rsi_val = 100 - (100 / (1 + rs))
    return rsi_val.iloc[-1]


def score(symbol):
    prices, volumes = get_data(symbol)
    if prices is None:
        return None

    try:
        score = 0
        r = rsi(prices)

        # RSI
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
        if volumes[-1] > sum(volumes) / len(volumes):
            score += 10

        return {
            "symbol": symbol,
            "score": round(score, 2),
            "rsi": round(r, 2)
        }

    except:
        return None


# -----------------------------
# RUN
# -----------------------------
def run():
    results = []

    for s in WATCHLIST:
        data = score(s)
        if data:
            results.append(data)

    results = sorted(results, key=lambda x: x["score"], reverse=True)

    top = [x for x in results if x["score"] >= MIN_SCORE][:5]

    if not top:
        top = results[:3]
        header = "⚠️ FORCED SET (low quality market)\n\n"
    else:
        header = "🚀 AGGRESSIVE SIGNALS\n\n"

    msg = header
    msg += f"Time: {datetime.now()}\n\n"

    for t in top:
        msg += f"{t['symbol']} | SCORE {t['score']} | RSI {t['rsi']}\n"

    print(msg)
    send_telegram(msg)


if __name__ == "__main__":
    run()
