import os

class Config:
    # Telegram
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7973528127:AAF-IdHNXlUUHLGgojzjQ2x_MEy2WhP4DIA")
    ALLOWED_USER_IDS = [7959705230]  # Add more IDs as needed
    
    # Aviator
    ODIBETS_URL = "https://odibets.com/aviator"
    REQUEST_HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html"
    }
    
    # Analysis
    HISTORY_SIZE = 30000
    MIN_DATA_THRESHOLD = 100
