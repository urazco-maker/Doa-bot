import os
import requests
import yfinance as yf

print("BOT STARTED")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "CHAT_ID"

WATCHLIST = ["AAPL", "TSLA", "NVDA", "AMD", "META"]

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

data = yf.download("AAPL", period="5d", interval="1h")

change = (data["Close"].iloc[-1] - data["Close"].iloc[-2]) / data["Close"].iloc[-2] * 100

send(f"🚀 Test Bot Çalışıyor | AAPL: {change:.2f}%")

print("BOT FINISHED")
