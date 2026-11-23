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
        d = requests.get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval=1m&limit=10", timeout=10).json()
        return [float(x[4]) for x in d]
    except: return []
def loop():
    send("البوت اشتغل ✅ - كل 5 دقايق صفقة وحدة للزوج الأقوى")
    pairs = [("BTCUSDT","BTC/USD"),("ETHUSDT","ETH/USD"),("EURUSDT","EUR/USD")]
    while True:
        best = None
        best_strength = 0
        best_price = 0
        best_dir = ""
        for sym, disp in pairs:
            p = price(sym); c = klines(sym)
            if not p or len(c) < 5: continue
            change = (c[-1] - c[0]) / c[0] * 100
            strength = abs(change)
            if strength > best_strength:
                best_strength = strength
                best = disp
                best_price = p
                best_dir = "CALL 🟢" if change > 0 else "PUT 🔴"
        if best:
            now = datetime.now() + timedelta(hours=2)
            msg = f"تحليل حقيقي | Pocket Option\n\nالزوج الأقوى: {best}\nالصفقة: {best_dir}\nقوة الحركة: {round(best_strength, 3)}%\nسعر الدخول: {best_price}\nالساعة: {now.strftime('%H:%M:%S')}\nوقت الدخول: {now.strftime('%H:%M')} - مدة 5 دقايق\n"
            send(msg)
        time.sleep(300)
@app.route("/")
def home(): return "Bot is Live ✅"
threading.Thread(target=loop, daemon=True).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
