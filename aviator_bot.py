import logging, requests, random
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import re

BOT_TOKEN = "7973528127:AAF-IdHNXlUUHLGgojzjQ2x_MEy2WhP4DIA"
USER_ID = 7959705230
RESULTS_URL = "https://odibets.com/aviator"  # Site to scrape

# Storage for rounds
rounds = []

logging.basicConfig(level=logging.INFO)

def scrape_results():
    try:
        response = requests.get(RESULTS_URL, timeout=10)
        matches = re.findall(r'(\d+\.\d+)x', response.text)
        if matches:
            floats = [float(m) for m in matches[:30000]]
            return floats
    except Exception as e:
        logging.error("Scrape error: " + str(e))
    return []

def predict_next(rounds):
    if not rounds or len(rounds) < 50:
        return round(random.uniform(1.00, 2.00), 2)
    
    # Simple statistical cluster frequency detection
    cluster = {
        "low": len([x for x in rounds if x <= 1.50]),
        "mid": len([x for x in rounds if 1.51 <= x <= 3.0]),
        "high": len([x for x in rounds if x > 3.0])
    }
    total = sum(cluster.values())
    weights = {
        "low": cluster["low"] / total,
        "mid": cluster["mid"] / total,
        "high": cluster["high"] / total,
    }

    # Weighted random prediction
    if weights["high"] > 0.3:
        return round(random.uniform(3.5, 6.0), 2)
    elif weights["mid"] > 0.5:
        return round(random.uniform(2.0, 3.5), 2)
    else:
        return round(random.uniform(1.1, 2.0), 2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != USER_ID:
        await update.message.reply_text("Access Denied.")
        return

    await update.message.reply_text("Welcome James! Scraping results and analyzing...")

    global rounds
    rounds = scrape_results()

    if not rounds:
        await update.message.reply_text("Failed to retrieve results.")
        return

    prediction = predict_next(rounds)
    await update.message.reply_text(f"Next Round Prediction: {prediction}×")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
