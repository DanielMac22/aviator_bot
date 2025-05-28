from flask import Flask
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Aviator Bot is running", 200
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import CommandStart
from config import Config
from scraper import fetch_aviator_data, parse_multipliers
from analyzer import AviatorAnalyzer
import asyncio

bot = Bot(token=Config.TELEGRAM_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(CommandStart())
async def handle_start(message: types.Message):
    """Handle /start command"""
    if message.from_user.id not in Config.ALLOWED_USER_IDS:
        await message.answer("🚫 Access Denied")
        return
    
    await message.answer("🔄 Fetching and analyzing data...")
    
    try:
        # Get and process data
        html = await fetch_aviator_data()
        history = parse_multipliers(html)
        prediction = AviatorAnalyzer.analyze(history)
        
        # Send results
        stats = (
            f"📊 Last 100 rounds:\n"
            f"Avg: {np.mean(history[-100:]):.2f}x | "
            f"Max: {max(history[-100:]):.2f}x\n"
            f"🛑 Crash rate: {len([x for x in history[-100:] if x < 1.5])/100:.0%}\n\n"
            f"🔮 Next round prediction:\n{prediction}"
        )
        await message.answer(stats)
        
    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
