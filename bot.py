import os
import asyncio
import logging
import numpy as np
import json
from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import CommandStart
from aiogram.utils import executor
from config import Config
from scraper import fetch_aviator_data, parse_multipliers
from analyzer import AviatorAnalyzer

# Initialize Flask app for Render health checks
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Aviator Prediction Bot is Running", 200

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User session data - should be moved to environment variables in production
USER_SESSION = {
    "balance": float(os.getenv("USER_BALANCE", "0.49")),
    "first_name": os.getenv("USER_FIRSTNAME", "edwin"),
    "last_name": os.getenv("USER_LASTNAME", "waithaka"),
    "id": os.getenv("SESSION_ID", "NnJNzkTM0gDN3EDfwYDNwcDNzQzN0UjM8FzN5MjNxUjKqQjNzkTM0gDN3EjK2MTMqUWbvJHaDpyc39GZul2VqAjbzgmZrl2ayZDclNma4ETZ1EHcuZzcwjQ")
}

# Initialize bot with error handling
try:
    bot = Bot(token=Config.TELEGRAM_TOKEN)
    dp = Dispatcher(bot)
    logger.info("Bot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize bot: {str(e)}")
    raise

@dp.message_handler(CommandStart())
async def handle_start(message: types.Message):
    """Handle /start command with session verification"""
    try:
        if message.from_user.id not in Config.ALLOWED_USER_IDS:
            await message.answer("🚫 Access Denied")
            logger.warning(f"Unauthorized access attempt by user {message.from_user.id}")
            return
        
        logger.info(f"Processing request for user {message.from_user.id}")
        
        # Verify session first
        if not USER_SESSION.get('id'):
            await message.answer("🔐 Session expired. Please update credentials.")
            return
            
        await message.answer("🔄 Fetching authenticated data...")
        
        # Get and process data with authenticated session
        html = await fetch_aviator_data(USER_SESSION)
        history = parse_multipliers(html)
        prediction = AviatorAnalyzer.analyze(history)
        
        # Calculate statistics
        recent_history = history[-100:]
        avg = np.mean(recent_history)
        maximum = max(recent_history)
        crash_rate = len([x for x in recent_history if x < 1.5]) / len(recent_history)
        
        # Format response with user info
        stats = (
            f"👤 User: {USER_SESSION['first_name']} {USER_SESSION['last_name']}\n"
            f"💰 Balance: {USER_SESSION['balance']:.2f}\n\n"
            f"📊 Last 100 rounds:\n"
            f"Avg: {avg:.2f}x | Max: {maximum:.2f}x\n"
            f"🛑 Crash rate: {crash_rate:.0%}\n\n"
            f"🔮 Next round prediction:\n{prediction}"
        )
        
        await message.answer(stats)
        logger.info(f"Prediction sent to user {message.from_user.id}")

    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        await message.answer(error_msg)
        logger.error(f"Error handling message: {error_msg}")

async def on_startup(dp):
    """Verify bot is working on startup"""
    me = await bot.get_me()
    logger.info(f"Bot @{me.username} started successfully")
    print(f"Bot @{me.username} is ready!")
    
    # Verify session data is valid
    if not USER_SESSION.get('id'):
        logger.warning("Initial session verification failed - check credentials")

def run_flask():
    """Run Flask app in separate thread"""
    app.run(host="0.0.0.0", port=10000)

if __name__ == "__main__":
    import threading
    
    # Start Flask server in a separate thread for Render health checks
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start the Telegram bot
    try:
        executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        raise
