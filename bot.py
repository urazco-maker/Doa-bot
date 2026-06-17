import os
import requests
import yfinance as yf

print("BOT STARTED")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "8662141509"

def send(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# Veri çek
data = yf.download("AAPL", period="5d", interval="1h")

# Güvenli float hesaplama
last = float(data["Close"].iloc[-1])
prev = float(data["Close"].iloc[-2])

change = ((last - prev) / prev) * 100

# Mesaj gönder
send(f"🚀 Test Bot Çalışıyor | AAPL: {change:.2f}%")

print("BOT FINISHED")
