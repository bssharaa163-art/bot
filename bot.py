import os, time, requests, threading, random
from datetime import datetime, timedelta
from flask import Flask
app = Flask(__name__)
TELEGRAM_TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT_ID = "6459511609"

last_prices = {"EUR/USD": 1.0845, "GBP/USD": 1.2730, "AUD/USD": 0.6520, "BTC/USD": 97000, "ETH/USD": 3400}
last_dir = {"CALL 🟢": False}

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except:
        pass

def price(s, disp):
    try:
        p = float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}", timeout=5).json()["price"])
        if p and p > 0:
            last_prices[disp] = p
            return p
    except:
        pass
    last_prices[disp] = last_prices[disp] * (1 + random.uniform(-0.0005, 0.0005))
    return round(last_prices[disp], 5 if last_prices[disp] < 10 else 2)

def klines(s):
    try:
        d = requests.get(f"https://api.binance.com/api/v3/klines?symbol={s}&interval=1m&limit=10", timeout=5).json()
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
    candidates = []
    for sym, disp in pairs:
        p = price(sym, disp)
        c = klines(sym)
        if len(c) >= 5:
            change = (c[-1] - c[0]) / c[0] * 100
            if change > 0.03:
                direction = "PUT 🔴"
                strength = change
            elif change < -0.03:
                direction = "CALL 🟢"
                strength = abs(change)
            else:
                direction = "CALL 🟢" if c[-1] > c[-2] else "PUT 🔴"
                strength = abs(change) + 0.01
        else:
            direction = "PUT 🔴" if last_dir["CALL 🟢"] else "CALL 🟢"
            last_dir["CALL 🟢"] = not last_dir["CALL 🟢"]
            strength = random.uniform(0.02, 0.08)
        candidates.append((strength, disp, p, direction))
    candidates.sort(reverse=True)
    top = candidates[:3]
    chosen = random.choice(top)
    return chosen[1], chosen[2], chosen[3]

def send_signal(pairs):
    best, best_price, best_dir = get_best(pairs)
    send_time = datetime.now() + timedelta(hours=2)
    # الدخول = أول وقت على الـ 5 دقايق - 5
