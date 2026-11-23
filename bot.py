import os
import time
import requests
import threading
from datetime import datetime, timedelta
from flask import Flask

app = Flask(__name__)

# حط التوكن تبعك هون اذا ما حاطو بـ Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "PUT_YOUR_TOKEN_HERE")
CHAT_ID = os.environ.get("CHAT_ID", "PUT_YOUR_CHAT_ID_HERE")

PAIRS = [
    ("BTCUSDT", "BTC/USD"),
    ("ETHUSDT", "ETH/USD"),
    ("EURUSDT", "EUR/USD"),
]

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=10)
        return float(r.json()["price"])
    except:
        return None

def get_klines(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=10"
        r = requests.get(url, timeout=10)
        data = r.json()
        closes = [float(x[4]) for x in data]
        return closes
    except:
        return []

def analyze():
    for symbol, display in PAIRS:
        price = get_price(symbol)
        closes = get_klines(symbol)
        if price is None or len(closes) < 5:
            continue

        # تحليل بسيط: اذا اخر شمعة طالعة -> CALL، اذا نازلة -> PUT
        if closes[-1] > closes[-2]:
            signal = "CALL 🟢"
