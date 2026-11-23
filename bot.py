import os, time, requests, threading
from datetime import datetime, timedelta
from flask import Flask
app = Flask(__name__)
TELEGRAM_TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT_ID = "6459511609"
def send(msg):
    try: requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass
def price(s):
    try: return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}", timeout=10).json()["price"])
    except: return None
def klines(s):
    try:
        d = requests.get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval=1m&limit=5", timeout=10).json()
        return [float(x[4]) for x in d]
    except: return []
def loop():
    send("البوت اشتغل ✅ - النظام الجديد شغال")
    pairs = [("BTCUSDT","BTC/USD"),("ETHUSDT","ETH/USD"),("EURUSDT","EUR/USD")]
    while True:
        for sym, disp in pairs:
            p = price(sym); c = klines(sym)
            if not p or len(c) < 3: continue
            sig = "CALL 🟢" if c[-1] > c[-2] else "PUT 🔴"
            rsn = "السعر عم يطلع" if "CALL" in sig else "السعر عم ينزل"
            now = datetime.now() + timedelta(hours=2)
            msg = f"تحليل حقيقي | Pocket Option\n\nالزوج: {disp}\nالصفقة: {sig}\nسعر الدخول: {p}\nسبب التحليل: {rsn}\nالساعة: {now.strftime('%H:%M:%S')}\nوقت الدخول: {now.strftime('%H:%M')} - مدة 30 ثانية\n"
            send(msg)
            time.sleep(2)
        time.sleep(60)
@app.route("/")
def home(): return "Bot is Live ✅"
threading.Thread(target=loop, daemon=True).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
