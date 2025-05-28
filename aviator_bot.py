import os
import json
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import CommandStart
from flask import Flask, request

# === CONFIGURATION ===
API_TOKEN = os.getenv("TELEGRAM_TOKEN", "7973528127:AAH50AiPubhkJKkT9mnidO4XSBRczxBUdeQ")
ALLOWED_USER_ID = 7959705230
COOKIE = {
    "session": "ZDINzgTM4QzNxwXOxUjNzgTMxEDN1IDf4MjN2MzMzEjKqkTO0MDOxgDN3EjK2MTMqUWbvJHaDpyc39GZul2VqcDZilzZ1kDO1YXYq9WdyY3byYmMu1WNwDk5"
}
ODIBETS_URL = "https://odibets.com/aviator"

# === FLASK SETUP ===
app = Flask(__name__)

@app.route('/')
def index():
    return "Aviator Prediction Bot is Running!"

# === TELEGRAM BOT SETUP ===
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return await message.answer("Access Denied.")
    await message.answer("Welcome to Aviator Prediction Bot. Analyzing...")
    prediction = await get_prediction()
    await message.answer(f"Next Round Prediction: {prediction}×")

# === AVIATOR PREDICTION LOGIC ===
async def get_prediction():
    try:
        async with aiohttp.ClientSession(cookies=COOKIE) as session:
            async with session.get(ODIBETS_URL) as resp:
                html = await resp.text()
                # Simple simulated logic. Real logic should analyze multiplier patterns.
                history = parse_multipliers_from_html(html)
                predicted = analyze_history(history)
                return predicted
    except Exception as e:
        print("Failed to fetch or analyze results:", e)
        return "Error"

def parse_multipliers_from_html(html):
    import re
    return [float(m) for m in re.findall(r"(\d+\.\d+)x", html)][-30000:]  # Last 30k

def analyze_history(history):
    if not history:
        return "N/A"
    import random
    average = sum(history) / len(history)
    jitter = random.uniform(-0.3, 0.3)
    return f"{max(1.01, average + jitter):.2f}"

# === RUN EVERYTHING ===
if __name__ == '__main__':
    import threading
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000)).start()
    asyncio.run(dp.start_polling(bot))
