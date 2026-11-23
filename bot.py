import os
import time
import threading
import requests
from flask import Flask
from datetime import datetime, timedelta

TELEGRAM_CHAT_ID = "6459511609"
TELEGRAM_TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"

app = Flask(__name__)

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
    "EURCAD": "EUR/CAD",
    "GBPCAD": "GBP/CAD",
    "NZDJPY": "NZD/JPY",
    "CADJPY": "CAD/JPY",
}

sent = {}
last_heartbeat = datetime.now()

def bot_loop():
    global last_heartbeat
    send_telegram("بوت Pocket Option اشتغل\nتحليل حقيقي - سوق عالمي\nرح ابعتلك قبل 30 ثانية\nالنظام الجديد: شغال و بيفحص كل دقيقة")
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

            found = False
            for binance_symbol, display in PAIRS.items():
                price, rsi = get_rsi(binance_symbol)
                if price is None:
                    continue
                signal = None
                if rsi <= 40:
                    signal = f"━━━━━━━━━━━━━━━\nتحليل حقيقي | Pocket Option\n━━━━━━━━━━━━━━━\n\nالزوج: {display}\nالصفقة: شراء\nسعر الدخول: {price}\nسبب التحليل: تشبع بيعي - RSI {round(rsi,1)}\n\nالساعة هلأ: {now_full}\nوقت الدخول: {entry_time} - بعد 30 ثانية\n\nمدة الفريم: 1 دقيقة\nمدة الصفقة: 1 دقيقة\n━━━━━━━━━━━━━━━\nفي حال الانعكاس: دوبل\n━━━━━━━━━━━━━━━"
                elif rsi >= 60:
                    signal = f"━━━━━━━━━━━━━━━\nتحليل حقيقي | Pocket Option\n━━━━━━━━━━━━━━━\n\nالزوج: {display}\nالصفقة: بيع\nسعر الدخول: {price}\nسبب التحليل: تشبع شرائي - RSI {round(rsi,1)}\n\nالساعة هلأ: {now_full}\nوقت الدخول: {entry_time} - بعد 30 ثانية\n\nمدة الفريم: 1 دقيقة\nمدة الصفقة: 1 دقيقة\n━━━━━━━━━━━━━━━\nفي حال الانعكاس: دوبل\n━━━━━━━━━━━━━━━"
                if signal:
                    found = True
                    key = display + entry_time + ("شراء" if "الصفقة: شراء" in signal else "بيع")
                    if sent.get(display) != key:
                        send_telegram(signal)
                        sent[display] = key
            
            # اذا مرق 15 دقيقة بلا صفقة، بعتلك انو بعدو شغال
            if datetime.now() - last_heartbeat > timedelta(minutes=15):
                if not found:
                    send_telegram(f"البوت بعدو شغال نظامي ✅\nالساعة هلأ: {now_full}\nعم بيفحص 18 زوج كل دقيقة\nما في صفقة قوية هلأ، ناطر اشارة قوية")
                last_heartbeat = datetime.now()

            time.sleep(5)
        except Exception as e:
            print(f"LOOP ERROR: {e}")
            time.sleep(10)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
