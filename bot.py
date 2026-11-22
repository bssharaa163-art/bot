import os
import requests
import time
import datetime
import yfinance as yf
from zoneinfo import ZoneInfo
from flask import Flask
from threading import Thread

TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT_ID = "6459511609"
PAIRS = ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X"]
FRAME = "5 دقائق"

app = Flask('')

@app.route('/')
def home():
    return "Bot shaghal!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

def send(msg):
    url = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def beirut_now():
    return datetime.datetime.now(ZoneInfo("Asia/Beirut"))

keep_alive()
send("البوت اشتغل - شغال 24/24 - Render")

while True:
    now = beirut_now()
    if now.weekday() >= 5:
        send("السوق مسكر - ويكند - ناطرين ليوم الاثنين")
        time.sleep(3600)
        continue
    for pair in PAIRS:
        try:
            df = yf.download(pair, period="1d", interval="5m", progress=False)
            if len(df) < 20:
                continue
            close = df['Close'].values.flatten()
            gains = []
            losses = []
            for i in range(1, len(close)):
                diff = close[i] - close[i-1]
                if diff > 0:
                    gains.append(diff)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(-diff)
            avg_gain = sum(gains[-14:]) / 14
            avg_loss = sum(losses[-14:]) / 14
            rsi = 100 - (100 / (1 + (avg_gain / (avg_loss + 0.0001))))
            name = pair.replace("=X", "").replace("USD", "/USD")
            entry = beirut_now()
            end = entry + datetime.timedelta(minutes=5)
            entry_str = entry.strftime("%H:%M")
            end_str = end.strftime("%H:%M")
            if rsi > 70:
                send("إشارة بيع 📉 هبوط\n\nالزوج: " + name + "\nالاتجاه: هبوط\nوقت الدخول: " + entry_str + " بيروت\nوقت انتهاء الصفقة: " + end_str + "\nالفريم: " + FRAME + "\nالمبلغ: انت بتختار\nRSI: " + str(round(rsi,1)))
            if rsi < 30:
                send("إشارة شراء 📈 صعود\n\nالزوج: " + name + "\nالاتجاه: صعود\nوقت الدخول: " + entry_str + " بيروت\nوقت انتهاء الصفقة: " + end_str + "\nالفريم: " + FRAME + "\nالمبلغ: انت بتختار\nRSI: " + str(round(rsi,1)))
        except:
            pass
    time.sleep(300)
