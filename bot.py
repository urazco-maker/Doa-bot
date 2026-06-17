import os
import requests

print("BOT STARTED")

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = "8662141509"

if not TOKEN:
    print("TOKEN MISSING")
    exit()

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

msg = "🚀 Bot çalışıyor test mesajı"

res = requests.post(url, data={
    "chat_id": CHAT_ID,
    "text": msg
})

print("STATUS:", res.status_code)
print("BOT FINISHED")
