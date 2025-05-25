from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
from bs4 import BeautifulSoup
import asyncio
import re
from collections import deque
import threading
from flask import Flask

TOKEN = "7973528127:AAF-IdHNXlUUHLGgojzjQ2x_MEy2WhP4DIA"
CHAT_ID = None
history = deque(maxlen=30000)

# Flask dummy server to keep Render alive
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)

# Start Flask in background
threading.Thread(target=run_flask).start()

# Aviator scraping and prediction
def predict_next_round():
    if not history:
        return "Not enough data yet."
    avg = sum(history[-100:]) / len(history[-100:])
    return "LOW (<2.0x)" if avg > 2.0 else "HIGH (>2.0x)"

def scrape_odibets():
    try:
        res = requests.get("https://odibets.com/aviator", headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        results = soup.find_all("div", class_="aviator-history-item")
        values = []
        for div in results:
            match = re.search(r"(\d+\.\d+)x", div.text)
            if match:
                val = float(match.group(1))
                values.append(val)
        return values[::-1]
    except:
        return []

# Telegram bot logic
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    await context.bot.send_message(chat_id=CHAT_ID, text="Aviator Prediction Bot activated!")
    asyncio.create_task(send_prediction_loop(context))  # run loop without blocking

async def send_prediction_loop(context):
    while True:
        results = scrape_odibets()
        if results:
            for r in results:
                if r not in history:
                    history.append(r)
                    prediction = predict_next_round()
                    await context.bot.send_message(chat_id=CHAT_ID, text=f"New Round: {r}x\nPrediction: {prediction}")
        await asyncio.sleep(10)

# Start the bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
