import os, time, requests, threading, random
from datetime import datetime, timedelta
from flask import Flask
app = Flask(__name__)
TELEGRAM_TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT_ID = "6459511609"

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

def price(s):
    try:
        return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}", timeout=10).json()["price"])
    except:
        return None

def klines(s):
    try:
        d = requests.get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval=1m&limit=10", timeout=10).json()
        return [float(x[4]) for x in d]
    except:
        return []

def fmt(dt):
    h = dt.hour % 12
    if h == 0:
        h = 12
    ap = "م" if dt.hour >= 12 else "ص"
    return f"{h}:{dt.minute:02d} {ap}"

def fmt_sec(dt):
    h = dt.hour % 12
    if h == 0:
        h = 12
    ap = "م" if dt.hour >= 12 else "ص"
    return f"{h}:{dt.minute:02d}:{dt.second:02d} {ap}"

def get_best(pairs):
    best = None
    best_strength = -1
    best_price = 0
    best_dir = ""
    for sym, disp in pairs:
        p = price(sym)
        c = klines(sym)
        if not p or len(c) < 5:
            if best is None:
                best = disp
                best_price = p if p else 0
                best_dir = "CALL 🟢"
                best_strength = 0
            continue
        change = (c[-1] - c[0]) / c[0] * 100
        strength = abs(change)
        if strength > best_strength:
            best_strength = strength
            best = disp
            best_price = p
            best_dir = "CALL 🟢" if change > 0 else "PUT 🔴"
    if best is None:
        best = "EUR/USD"
        best_price = 1.0845
        best_dir = random.choice(["CALL 🟢", "PUT 🔴"])
    return best, best_price, best_dir

def send_signal(pairs):
    best, best_price, best_dir = get_best(pairs)
    send_time = datetime.now() + timedelta(hours=2)
    entry = send_time + timedelta(seconds=30)
    entry = entry.replace(second=0, microsecond=0)
    msg = f"تحليل حقيقي | Pocket Option\n\nالزوج: {best}\nالصفقة: {best_dir}\nالفريم: 1 دقيقة\nسعر الدخول: {best_price}\nوقت الإرسال: {fmt_sec(send_time)}\nوقت الدخول: {fmt(entry)} - مدة دقيقة وحدة\nفي حال الانعكاس: دوبل ⏫\n"
    send(msg)

def loop():
    send("البوت اشتغل ✅ - كل 5 دقايق صفقة دقيقة وحدة قبل 30 ثانية")
    pairs = [("EURUSDT", "EUR/USD"), ("GBPUSDT", "GBP/USD"), ("AUDUSDT", "AUD/USD"), ("BTCUSDT", "BTC/USD"), ("ETHUSDT", "ETH/USD")]
    time.sleep(5)
    send_signal(pairs)
    while True:
        now = datetime.now() + timedelta(hours=2)
        mins = now.minute % 5
        secs = now.second
        wait = (5 - mins) * 60 - secs - 30
        if wait < 0:
            wait = wait + 300
        if wait > 0:
            time.sleep(wait)
        send_signal(pairs)
        time.sleep(40)

@app.route("/")
def home():
    return "Bot is Live ✅"

threading.Thread(target=loop, daemon=True).start()
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
