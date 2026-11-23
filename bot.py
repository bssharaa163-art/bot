import os
import time
import threading
import requests
from flask import Flask
from datetime import datetime, timedelta

TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6459511609")
TELEGRAM_TOKEN ="9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"

app = Flask(name)

@app.route("/")
def home():
    return "Bot Live!"

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": text}, timeout=10)
    except Exception as e:
        print(f"ERROR: {e}")

def get_rsi(symbol):
    try:
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": symbol, "interval": "1m", "limit": 50}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
        closes = [float(x[4]) for x in data]
        price = closes[-1]
        gains = []
        losses = []
        for i in range(1, 15):
            diff = closes[-15 + i] - closes[-16 + i]
            if diff >= 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(-diff)
        avg_gain = sum(gains) / 14
        avg_loss = sum(losses) / 14
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        return price, rsi
    except:
        return None, None

PAIRS = {
    "EURUSD": "EUR/USD",
    "GBPUSD": "GBP/USD",
    "USDJPY": "USD/JPY",
    "AUDUSD": "AUD/USD",
    "USDCAD": "USD/CAD",
    "EURGBP": "EUR/GBP",
    "EURJPY": "EUR/JPY",
    "GBPJPY": "GBP/JPY",
    "AUDJPY": "AUD/JPY",
    "NZDUSD": "NZD/USD",
    "USDCHF": "USD/CHF",
    "EURAUD": "EUR/AUD",
    "GBPAUD": "GBP/AUD",
    "AUDCAD": "AUD/CAD",
}

sent = {}

def bot_loop():
    send_telegram("بوت Pocket Option اشتغل\nتحليل حقيقي - سوق عالمي\nرح ابعتلك قبل 30 ثانية")
    while True:
        try:
            now_sec = datetime.now().second
            if now_sec < 30:
                time.sleep(30 - now_sec)
            elif now_sec > 30:
                time.sleep(60 - now_sec + 30)

            now_full = datetime.now().strftime("%H:%M:%S")
            next_minute = datetime.now().replace(second=0, microsecond=0) + timedelta(minutes=1)
            entry_time = next_minute.strftime("%H:%M")

            for binance_symbol, display in PAIRS.items():
                price, rsi = get_rsi(binance_symbol)
                if price is None:
                    continue
                signal = None
                if rsi <= 35:
                    signal = f"━━━━━━━━━━━━━━━\nتحليل حقيقي | Pocket Option\n━━━━━━━━━━━━━━━\n\nالزوج: {display}\nالصفقة: شراء\nسعر الدخول: {price}\nسبب التحليل: تشبع بيعي - RSI {round(rsi,1)}\n\nالساعة هلأ: {now_full}\nوقت الدخول: {entry_time} - بعد 30 ثانية\n\nمدة الفريم: 1 دقيقة\nمدة الصفقة: 1 دقيقة\n━━━━━━━━━━━━━━━\nفي حال الانعكاس: دوبل\n━━━━━━━━━━━━━━━"
                elif rsi >= 65:
                    signal = f"━━━━━━━━━━━━━━━\nتحليل حقيقي | Pocket Option\n━━━━━━━━━━━━━━━\n\nالزوج: {display}\nالصفقة: بيع\nسعر الدخول: {price}\nسبب التحليل: تشبع شرائي - RSI {round(rsi,1)}\n\nالساعة هلأ: {now_full}\nوقت الدخول: {entry_time} - بعد 30 ثانية\n\nمدة الفريم: 1 دقيقة\nمدة الصفقة: 1 دقيقة\n━━━━━━━━━━━━━━━\nفي حال الانعكاس: دوبل\n━━━━━━━━━━━━━━━"
                if signal:
                    key = display + entry_time + ("شراء" if "شراء" in signal else "بيع")
                    if sent.get(display) != key:
                        send_telegram(signal)
                        sent[display] = key
            time.sleep(5)
        except Exception as e:
            print(f"LOOP ERROR: {e}")
            time.sleep(10)

threading.Thread(target=bot_loop, daemon=True).start()

if name == "main":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
