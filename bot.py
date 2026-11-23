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

def send_telegram(text, chat_id=None):
    if chat_id is None:
        chat_id = TELEGRAM_CHAT_ID
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=10)
    except:
        pass

last_update_id = 0
def listen_loop():
    global last_update_id
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
            r = requests.get(url, params={"offset": last_update_id + 1, "timeout": 20}, timeout=30)
            data = r.json()
            if data.get("ok"):
                for upd in data.get("result", []):
                    last_update_id = upd["update_id"]
                    msg = upd.get("message", {})
                    text = msg.get("text", "").lower().strip()
                    chat_id = str(msg.get("chat", {}).get("id", ""))
                    if text in ["/start", "ستارت", "start", "hi", "هاي", "مرحبا"]:
                        send_telegram("اهلا فيك ✅\n\nالبوت السريع شغال\nتحليل حقيقي - سوق عالمي\n\nرح ابعتلك 4-6 صفقات بالساعة\nقبل 30 ثانية من الدخول", chat_id)
        except:
            pass
        time.sleep(2)

def get_data(symbol):
    try:
        url = "https://api.binance.com/api/v3/klines"
        r = requests.get(url, params={"symbol": symbol, "interval": "1m", "limit": 50}, timeout=10)
        data = r.json()
        closes = [float(x[4]) for x in data]
        price = closes[-1]
        # RSI
        gains=[]; losses=[]
        for i in range(1, 15):
            diff = closes[-15+i] - closes[-16+i]
            gains.append(diff if diff>=0 else 0)
            losses.append(-diff if diff<0 else 0)
        avg_gain = sum(gains)/14
        avg_loss = sum(losses)/14
        if avg_loss==0:
            rsi=100
        else:
            rsi = 100 - (100/(1+avg_gain/avg_loss))
        # EMA سريع
        ema9 = sum(closes[-9:])/9
        ema21 = sum(closes[-21:])/21
        return price, rsi, ema9, ema21
    except:
        return None, None, None, None

PAIRS = {
    "EURUSD": "EUR/USD", "GBPUSD": "GBP/USD", "USDJPY": "USD/JPY",
    "AUDUSD": "AUD/USD", "USDCAD": "USD/CAD", "EURGBP": "EUR/GBP",
    "EURJPY": "EUR/JPY", "GBPJPY": "GBP/JPY", "AUDJPY": "AUD/JPY",
    "NZDUSD": "NZD/USD", "USDCHF": "USD/CHF", "EURAUD": "EUR/AUD",
    "GBPAUD": "GBP/AUD", "AUDCAD": "AUD/CAD", "EURCAD": "EUR/CAD",
    "GBPCAD": "GBP/CAD", "NZDJPY": "NZD/JPY", "CADJPY": "CAD/JPY",
}

sent = {}

def bot_loop():
    send_telegram("بوت Pocket Option اشتغل\nالوضع السريع ON 🔥\nتحليل حقيقي - سوق عالمي\nرح ابعتلك قبل 30 ثانية\n4-6 صفقات بالساعة")
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

            count = 0
            for binance_symbol, display in PAIRS.items():
                if count >= 2:  # max 2 صفقات بالدقيقة مشان ما يخربطك
                    break
                price, rsi, ema9, ema21 = get_data(binance_symbol)
                if price is None:
                    continue
                signal = None
                reason = ""
                # شراء سريع: RSI طالع + السعر فوق EMA
                if rsi >= 45 and rsi <= 70 and ema9 > ema21:
                    signal = "شراء"
                    reason = f"زخم صاعد - RSI {round(rsi,1)} + فوق EMA"
                elif rsi <= 55 and rsi >= 30 and ema9 < ema21:
                    signal = "بيع"
                    reason = f"زخم هابط - RSI {round(rsi,1)} + تحت EMA"
                # اشارات قوية كمان
                elif rsi <= 35:
                    signal = "شراء"
                    reason = f"تشبع بيعي قوي - RSI {round(rsi,1)}"
                elif rsi >= 65:
                    signal = "بيع"
                    reason = f"تشبع شرائي قوي - RSI {round(rsi,1)}"

                if signal:
                    key = display + entry_time + signal
                    if sent.get(display) != key:
                        msg = f"━━━━━━━━━━━━━━━\nتحليل حقيقي | Pocket Option\n━━━━━━━━━━━━━━━\n\nالزوج: {display}\nالصفقة: {signal}\nسعر الدخول: {price}\nسبب التحليل: {reason}\n\nالساعة هلأ: {now_full}\nوقت الدخول: {entry_time} - بعد 30 ثانية\n\nمدة الفريم: 1 دقيقة\nمدة الصفقة: 1 دقيقة\n━━━━━━━━━━━━━━━\nفي حال الانعكاس: دوبل\n━━━━━━━━━━━━━━━"
                        send_telegram(msg)
                        sent[display] = key
            
