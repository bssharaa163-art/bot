import os, time, requests, threading, random, traceback
from datetime import datetime, timedelta
from flask import Flask

app = Flask(__name__)
TELEGRAM_TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT_ID = "6459511609"

# كل الازواج - بدون BTC
PAIRS = [
    "EUR/USD", "GBP/USD", "AUD/USD", "NZD/USD",
    "USD/CAD", "USD/CHF", "USD/JPY",
    "EUR/GBP", "EUR/JPY", "GBP/JPY", "EUR/AUD",
    "GBP/AUD", "AUD/JPY", "NZD/JPY", "EUR/CHF",
    "GBP/CHF", "AUD/CAD", "EUR/CAD", "CHF/JPY",
    "CAD/JPY", "EUR/NZD", "GBP/NZD", "AUD/NZD",
    "ETH/USD", "LTC/USD", "XRP/USD",
    "GOLD", "SILVER"
]

vol_factor = {
    "EUR/USD": 0.02, "GBP/USD": 0.025, "AUD/USD": 0.025, "NZD/USD": 0.025,
    "USD/CAD": 0.02, "USD/CHF": 0.02, "USD/JPY": 0.03,
    "EUR/GBP": 0.015, "EUR/JPY": 0.03, "GBP/JPY": 0.04, "EUR/AUD": 0.03,
    "GBP/AUD": 0.035, "AUD/JPY": 0.03, "NZD/JPY": 0.03, "EUR/CHF": 0.02,
    "GBP/CHF": 0.03, "AUD/CAD": 0.025, "EUR/CAD": 0.03, "CHF/JPY": 0.03,
    "CAD/JPY": 0.03, "EUR/NZD": 0.03, "GBP/NZD": 0.04, "AUD/NZD": 0.025,
    "ETH/USD": 0.25, "LTC/USD": 0.30, "XRP/USD": 0.35,
    "GOLD": 0.15, "SILVER": 0.25
}

price_history = {p: [] for p in PAIRS}
last_prices = {p: 1.0 for p in PAIRS}
last_prices.update({"EUR/USD": 1.0845, "GBP/USD": 1.2730, "AUD/USD": 0.6520, "NZD/USD": 0.6050, "USD/CAD": 1.3650, "USD/CHF": 0.8850, "USD/JPY": 155.20, "ETH/USD": 3400, "LTC/USD": 105, "XRP/USD": 2.35, "GOLD": 2650, "SILVER": 31.5})
last_winners = []

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("send error", e)

def get_all_prices():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=8).json()
        rates = r.get("rates", {})
        def conv(base, quote):
            if base == "USD": return rates.get(quote, 0)
            if quote == "USD": return 1 / rates.get(base, 1) if rates.get(base) else 0
            usd_base = 1 / rates.get(base, 1) if rates.get(base) else 0
            usd_quote = 1 / rates.get(quote, 1) if rates.get(quote) else 0
            if usd_quote == 0: return 0
            return usd_base / usd_quote
        mapping = {
            "EUR/USD": ("EUR", "USD"), "GBP/USD": ("GBP", "USD"), "AUD/USD": ("AUD", "USD"), "NZD/USD": ("NZD", "USD"),
            "USD/CAD": ("USD", "CAD"), "USD/CHF": ("USD", "CHF"), "USD/JPY": ("USD", "JPY"),
            "EUR/GBP": ("EUR", "GBP"), "EUR/JPY": ("EUR", "JPY"), "GBP/JPY": ("GBP", "JPY"),
            "EUR/AUD": ("EUR", "AUD"), "GBP/AUD": ("GBP", "AUD"), "AUD/JPY": ("AUD", "JPY"),
            "NZD/JPY": ("NZD", "JPY"), "EUR/CHF": ("EUR", "CHF"), "GBP/CHF": ("GBP", "CHF"),
            "AUD/CAD": ("AUD", "CAD"), "EUR/CAD": ("EUR", "CAD"), "CHF/JPY": ("CHF", "JPY"),
            "CAD/JPY": ("CAD", "JPY"), "EUR/NZD": ("EUR", "NZD"), "GBP/NZD": ("GBP", "NZD"), "AUD/NZD": ("AUD", "NZD"),
        }
        for disp, (b, q) in mapping.items():
            p = conv(b, q)
            if p and p > 0:
                last_prices[disp] = p
    except Exception as e:
        print("forex error", e)

    # كريبتو بدون BTC
    bin_map = {"ETH/USD": "ETHUSDT", "LTC/USD": "LTCUSDT", "XRP/USD": "XRPUSDT", "GOLD": "PAXGUSDT"}
    for disp, sym in bin_map.items():
        try:
            p = float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={sym}", timeout=5).json()["price"])
            if p > 0:
                last_prices[disp] = p
        except:
            pass
    try:
        last_prices["SILVER"] = last_prices["GOLD"] * 0.0119 * (1 + random.uniform(-0.001, 0.001))
    except:
        pass
    return last_prices

def fmt(dt):
    h = dt.hour % 12
    if h == 0: h = 12
    ap = "م" if dt.hour >= 12 else "ص"
    return f"{h}:{dt.minute:02d} {ap}"

def fmt_sec(dt):
    h = dt.hour % 12
    if h == 0: h = 12
    ap = "م" if dt.hour >= 12 else "ص"
    return f"{h}:{dt.minute:02d}:{dt.second:02d} {ap}"

def get_strongest():
    get_all_prices()
    scored = []
    for disp in PAIRS:
        if disp == "BTC/USD":
            continue
        p = last_prices[disp]
        price_history[disp].append(p)
        if len(price_history[disp]) > 10:
            price_history[disp].pop(0)
        hist = price_history[disp]
        if len(hist) >= 3:
            ch = (hist[-1] - hist[0]) / hist[0] * 100 if hist[0] != 0 else 0
            if ch > 0.02: d = "PUT 🔴"
            elif ch < -0.02: d = "CALL 🟢"
            else: d = "CALL 🟢" if hist[-1] > hist[-2] else "PUT 🔴"
            vf = vol_factor.get(disp, 0.02)
            score = abs(ch) / vf
            last_move = abs(hist[-1] - hist[-2]) / hist[-2] * 100 / vf if len(hist) >= 2 and hist[-2] != 0 else 0
            score = score + last_move + random.uniform(0, 0.3)
        else:
            d = random.choice(["CALL 🟢", "PUT 🔴"])
            score = random.uniform(0.5, 2.0)
        scored.append((score, disp, round(p, 5 if p < 10 e
