import os
import time
import requests
import threading
import random
from datetime import datetime
from datetime import timedelta
from flask import Flask
app = Flask(__name__)
TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT = "6459511609"
PAIRS = []
PAIRS.append("EUR/USD")
PAIRS.append("GBP/USD")
PAIRS.append("AUD/USD")
PAIRS.append("NZD/USD")
PAIRS.append("USD/CAD")
PAIRS.append("USD/CHF")
PAIRS.append("USD/JPY")
PAIRS.append("EUR/GBP")
PAIRS.append("EUR/JPY")
PAIRS.append("GBP/JPY")
PAIRS.append("EUR/AUD")
PAIRS.append("GBP/AUD")
PAIRS.append("AUD/JPY")
PAIRS.append("NZD/JPY")
PAIRS.append("EUR/CHF")
PAIRS.append("GBP/CHF")
PAIRS.append("AUD/CAD")
PAIRS.append("EUR/CAD")
PAIRS.append("CHF/JPY")
PAIRS.append("CAD/JPY")
PAIRS.append("EUR/NZD")
PAIRS.append("GBP/NZD")
PAIRS.append("AUD/NZD")
LAST = []
def send(m):
  u = "https://api.telegram.org/bot"
  u = u + TOKEN + "/sendMessage"
  try:
    requests.post(u, data={"chat_id": CHAT, "text": m}, timeout=10)
  except:
    pass
def klines(sym):
  u = "https://api.binance.com/api/v3/klines"
  u = u + "?symbol=" + sym
  u = u + "&interval=1m&limit=30"
  try:
    d = requests.get(u, timeout=5).json()
    c = []
    for x in d:
      c.append(float(x[4]))
    return c
  except:
    return []
def rsi(closes):
  if len(closes) < 15:
    return 50
  g = 0
  l = 0
  for i in range(1, 15):
    d = closes[i] - closes[i-1]
    if d > 0:
      g = g + d
    else:
      l = l - d
  ag = g / 14
  al = l / 14
  if al == 0:
    return 90
  rs = ag / al
  return 100 - (100 / (1 + rs))
def fmt(d):
  h = d.hour % 12
  if h == 0:
    h = 12
  ap = "م"
  if d.hour < 12:
    ap = "ص"
  m = str(d.minute)
  if d.minute < 10:
    m = "0" + m
  return str(h) + ":" + m + " " + ap
def fmt2(d):
  h = d.hour % 12
  if h == 0:
    h = 12
  ap = "م"
  if d.hour < 12:
    ap = "ص"
  m = str(d.minute)
  if d.minute < 10:
    m = "0" + m
  s = str(d.second)
  if d.second < 10:
    s = "0" + s
  return str(h) + ":" + m + ":" + s + " " + ap
def get_sym(disp):
  if disp == "EUR/USD":
    return "EURUSDT"
  if disp == "GBP/USD":
    return "GBPUSDT"
  if disp == "AUD/USD":
    return "AUDUSDT"
  if disp == "NZD/USD":
    return "NZDUSDT"
  if disp == "USD/CAD":
    return "USDCUSDT"
  if disp == "USD/CHF":
    return "CHFUSDT"
  if disp == "USD/JPY":
    return "JPYUSDT"
  if disp == "EUR/GBP":
    return "EURUSDT"
  if disp == "EUR/JPY":
    return "EURUSDT"
  if disp == "GBP/JPY":
    return "GBPUSDT"
  if disp == "EUR/AUD":
    return "EURUSDT"
  if disp == "GBP/AUD":
    return "GBPUSDT"
  if disp == "AUD/JPY":
    return "AUDUSDT"
  if disp == "NZD/JPY":
    return "NZDUSDT"
  if disp == "EUR/CHF":
    return "EURUSDT"
  if disp == "GBP/CHF":
    return "GBPUSDT"
  if disp == "AUD/CAD":
    return "AUDUSDT"
  if disp == "EUR/CAD":
    return "EURUSDT"
  if disp == "CHF/JPY":
    return "CHFUSDT"
  if disp == "CAD/JPY":
    return "USDCUSDT"
  if disp == "EUR/NZD":
    return "EURUSDT"
  if disp == "GBP/NZD":
    return "GBPUSDT"
  return "AUDUSDT"
def analyse(disp):
  sym = get_sym(disp)
  cl = klines(sym)
  if len(cl) < 5:
    return 1.0, 0.5, "CALL"
  r = rsi(cl)
  last = cl[-1]
  prev = cl[-2]
  ema = sum(cl[-10:]) / 10
  mom = (last - prev) / prev * 100
  d = "CALL"
  sc = 0
  if r > 68:
    d = "PUT"
    sc = r - 68
  if r < 32:
    d = "CALL"
    sc = 32 - r
  if r >= 32:
    if r <= 68:
      if last > ema:
        d = "PUT"
      else:
        d = "CALL"
      sc = abs(mom) * 10
  sc = sc + random.uniform(0, 1.5)
  price = last
  if disp == "USD/CAD":
    if last != 0:
      price = 1 / last
  if disp == "USD/CHF":
    if last != 0:
      price = 1 / last
  if disp == "USD/JPY":
    price = price * 150
  if disp == "EUR/JPY":
    price = price * 165
  if disp == "GBP/JPY":
    price = price * 190
  if disp == "AUD/JPY":
    price = price * 100
  if disp == "NZD/JPY":
    price = price * 95
  if disp == "CHF/JPY":
    price = price * 175
  if disp == "CAD/JPY":
    price = price * 110
  if disp == "EUR/GBP":
    price = price * 0.85
  if disp == "EUR/AUD":
    price = price * 1.65
  if disp == "GBP/AUD":
    price = price * 1.95
  if disp == "EUR/CHF":
    price = price * 0.95
  if disp == "GBP/CHF":
    price = price * 1.12
  if disp == "AUD/CAD":
    price = price * 0.90
  if disp == "EUR/CAD":
    price = price * 1.47
  if disp == "EUR/NZD":
    price = price * 1.78
  if disp == "GBP/NZD":
    price = price * 2.10
  if disp == "AUD/NZD":
    price = price * 1.07
  if price < 10:
    price = round(price, 5)
  else:
    price = round(price, 2)
  return price, sc, d
def best_pair():
  alls = []
  for disp in PAIRS:
    pr, sc, d = analyse(disp)
    alls.append((sc, disp, pr, d))
  alls.sort(reverse=True)
  print("TOP3")
  for x in alls[:3]:
    print(x[1], round(x[0], 2), x[3])
  pick = alls[0]
  if len(LAST) >= 1:
    if LAST[-1] == pick[1]:
      if len(alls) > 1:
        pick = alls[1]
  if len(LAST) >= 2:
    if LAST[-1] == pick[1]:
      if LAST[-2] == pick[1]:
       
