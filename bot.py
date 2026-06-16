from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = 8890631109:AAE0qz3y40hoCG5k6XKNjbTt8-BFotNGfjc

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 Doa Nasdaq Bot Aktif!"
    )

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.run_polling()
