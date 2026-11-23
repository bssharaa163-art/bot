import os
import time
import requests
import threading
import random
import traceback
from datetime import datetime, timedelta
from flask import Flask

app = Flask(__name__)
TELEGRAM_TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT_ID = "6459511609"

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

vol_factor = {}
vol_factor["EUR/USD"] = 0.02
vol_factor["GBP/USD"] = 0.025
vol_factor["AUD/USD"] = 0.025
vol_factor["NZD/USD"] = 0.025
vol_factor["USD/CAD"] = 0.02
vol_factor["USD/CHF"] = 0.02
vol_factor["USD/JPY"] = 0.03
vol_factor["EUR/GBP"] = 0.015
vol_factor["EUR/JPY"] = 0.03
vol_factor["GBP/JPY"] = 0.04
vol_factor["EUR/AUD"] = 0.03
vol_factor["GBP/AUD"] = 0.035
vol_factor["AUD/JPY"] = 0.03
vol_factor["NZD/JPY"] = 0.03
vol_factor["EUR/CHF"] = 0.02
vol_factor["GBP/CHF"] = 0.03
vol_factor["AUD/CAD"] = 0.025
vol_factor["EUR/CAD"] = 0.03
vol_factor["CHF/JPY"] = 0.03
vol_factor["CAD/JPY"] = 0.03
vol_factor["EUR/NZD"] = 0.03
vol_factor["GBP/NZD"] = 0.04
vol_factor["AUD/NZD"] = 0.025
vol_factor["ETH/USD"] = 0.25
vol_factor["LTC/USD"] = 0.30
vol_factor["XRP/USD"] = 0.35
vol_factor["GOLD"] = 0.15
vol_factor["SILVER"] = 0.25

price_history = {}
last_prices = {}
for p in PAIRS:
    price_history[p] = []
    last_prices[p] = 1.0

last_prices["EUR/USD"] = 1.0845
last_prices["GBP/USD"] = 1.2730
last_prices["AUD/USD"] = 0.6520
last_prices["NZD/USD"] = 0.6050
last_prices["USD/CAD"] = 1.3650
last_prices["USD/CHF"] = 0.8850
last_prices["USD/JPY"] = 155.20
last_prices["ETH/USD"] = 3400
last_prices["LTC/USD"] = 105
last_prices["XRP/USD"] = 2.35
last_prices["GOLD"] = 2650
last_prices["SILVER"] = 31.5

last_winners = []

def send(msg):
    try:
        requests.post("https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except Exception as e:
        print("send error")
        print(e)

def fmt_price(p):
    if p < 10:
        return round(p, 5)
    else:
        return round(p, 2)

def get_all_prices():
    try:
        r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=8).json()
        rates = r.get("rates", {})
        for disp in PAIRS:
            if "/" not in disp:
                continue
            parts = disp.split("/")
            base = parts[0]
            quote = parts[1]
            price = 0
            if base == "USD":
                price = rates.get(quote, 0)
            elif quote == "USD":
                if rates.get(base):
                    price = 1 / rates.get(base)
            else:
                if rates.get(base) and rates.get(quote):
                    usd_base = 1 / rates.get(base)
                    usd_quote = 1 / rates.get(quote)
                    if usd_quote != 0:
                        price = usd_base / usd_quote
            if price and price > 0:
                last_prices[disp] = price
    except Exception as e:
        print("forex error")
        print(e)
    try:
        p = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT", timeout=5).json()["price"])
        if p > 0:
            last_prices["ETH/USD"] = p
    except:
        pass
    try:
        p = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=LTCUSDT", timeout=5).json()["price"])
        if p > 0:
            last_prices["LTC/USD"] = p
    except:
        pass
    try:
        p = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=XRPUSDT", timeout=5).json()["price"])
        if p > 0:
            last_prices["XRP/USD"] = p
    except:
        pass
    try:
        p = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=5).json()["price"])
        if p > 0:
            last_prices["GOLD"] = p
    except:
        pass
    try:
        last_prices["SILVER"] = last_prices["GOLD"] * 0.0119
    except:
        pass
    return last_prices

def fmt(dt):
    h = dt.hour % 12
    if h == 0:
        h = 12
    if dt.hour >= 12:
        ap = "م"
    else:
        ap = "ص"
    return str(h) + ":" + str(dt.minute).zfill(2) + " " + ap

def fmt_sec(dt):
    h = dt.hour % 12
    if h == 0:
        h = 12
    if dt.hour >= 12:
        ap = "م"
    else:
        ap = "ص"
    return str(h) + ":" + str(dt.minute).zfill(2) + ":" + str(dt.second).zfill(2) + " " + ap

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
        d = "CALL 🟢"
        score = 1.0
        if len(hist) >=
