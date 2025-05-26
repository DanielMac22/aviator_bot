import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from flask import Flask, request
import threading
import requests
import re
import time

API_TOKEN = '7973528127:AAH50AiPubhkJKkT9mnidO4XSBRczxBUdeQ'
USER_ID = 7959705230
ODIBETS_COOKIE = {
    'Cookie': '__cf_bm=ZDINzgTM4QzNxwXOxUjNzgTMxEDN1IDf4MjN2MzMzEjKqkTO0MDOxgDN3EjK2MTMqUWbvJHaDpyc39GZul2VqcDZilzZ1kDO1YXYq9WdyY3byYmMu1WNwDk5'
}

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Flask app setup for Render
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

# Background scraping thread to keep fetching results
def fetch_results():
    while True:
        try:
            response = requests.get('https://odibets.com/aviator', headers=ODIBETS_COOKIE)
            if response.status_code == 200:
                html = response.text
                results = re.findall(r'<div class="round-history-value">(\d+\.\d+x)</div>', html)
                if results:
                    prediction = analyze_pattern(results[:30000])
                    bot.send_message(USER_ID, f"Next round: {prediction}")
            time.sleep(5)
        except Exception as e:
            logging.error(f"Failed to fetch or send: {e}")
            time.sleep(10)

def analyze_pattern(data):
    # Placeholder for actual pattern detection logic
    try:
        nums = [float(x.replace('x','')) for x in data]
        avg = sum(nums) / len(nums)
        return f"{avg:.2f}×"
    except:
        return "1.00×"

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if message.from_user.id == USER_ID:
        await message.reply("Welcome James! Aviator prediction bot is active.")
    else:
        await message.reply("You are not authorized to use this bot.")

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

if __name__ == '__main__':
    threading.Thread(target=fetch_results).start()
    threading.Thread(target=run_flask).start()
    executor.start_polling(dp, skip_updates=True)
