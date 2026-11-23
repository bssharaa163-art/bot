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
    requests.post(u, data={
      "chat_id": CHAT,
      "text": m
    }, timeout=10)
  except:
    pass

def klines(sym):
  u = "https://api.binance.com"
  u = u + "/api/v3/klines"
  u = u + "?symbol=" + sym
  u = u + "&interval=1m&limit=30"
  try:
    d = requests.get(u, timeout=5).json()
    out = []
    for x in d:
      out.append(float(x[4]))
    return out
  except:
    return []

def rsi(c):
  if len(c) < 15:
    return 50
  g = 0
  l = 0
  for i in range(1, 15):
    d = c[i] - c[i-1]
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
  m = str(d.minute).zfill(2)
  return str(h) + ":" + m + " " + ap

def fmt2(d):
  h = d.hour % 12
  if h == 0:
    h = 12
  ap = "م"
  if d.hour < 12:
    ap = "ص"
  m = str(d.minute).zfill(2)
  s = str(d.second).zfill(2)
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

def calc_price(disp, last):
  p = last
  if disp == "USD/CAD":
    p = 1 / last
  if disp == "USD/CHF":
    p = 1 / last
  if disp == "USD/JPY":
    p = last * 150
  if disp == "EUR/JPY":
    p = last * 165
  if disp == "GBP/JPY":
    p = last * 190
  if disp == "AUD/JPY":
    p = last * 100
  if disp == "NZD/JPY":
    p = last * 95
  if disp == "CHF/JPY":
    p = last * 175
  if disp == "CAD/JPY":
    p = last * 110
  if disp == "EUR/GBP":
    p = last * 0.85
  if disp == "EUR/AUD":
    p = last * 1.65
  if disp == "GBP/AUD":
    p = last * 1.95
  if disp == "EUR/CHF":
    p = last * 0.95
  if disp == "GBP/CHF":
    p = last * 1.12
  if disp == "AUD/CAD":
    p = last * 0.90
  if disp == "EUR/CAD":
    p = last * 1.47
  if disp == "EUR/NZD":
    p = last * 1.78
  if disp == "GBP/NZD":
    p = last * 2.10
  if disp == "AUD/NZD":
    p = last * 1.07
  if p < 10:
    return round(p, 5)
  return round(p, 2)

def analyse(disp):
  cl = klines(get_sym(disp))
  if len(cl) < 5:
    return 0.5, disp, 1.0, "CALL"
  r = rsi(cl)
  last = cl[-1]
  prev = cl[-2]
  ema = sum(cl[-10:]) / 10
  mom = abs(last - prev) / prev * 100
  d = "CALL"
  sc = mom * 10
  if r > 68:
    d = "PUT"
    sc = r - 68
  if r < 32:
    d = "CALL"
    sc = 32 - r
  if r >= 32 and r <= 68:
    if last > ema:
      d = "PUT"
    else:
      d = "CALL"
  sc = sc + random.uniform(0, 1.5)
  p = calc_price(disp, last)
  return sc, disp, p, d

def best_pair():
  alls = []
  for x in PAIRS:
    alls.append(analyse(x))
  alls.sort(reverse=True)
  pick = alls[0]
  if len(LAST) > 0:
    if LAST[-1] == pick[1]:
      if len(alls) > 1:
        pick = alls[1]
  LAST.append(pick[1])
  if len(LAST) > 5:
    LAST.pop(0)
  print("TOP " + alls[0][1])
  return pick[1], pick[2], pick[3]

def do_signal():
  b, pr, dr = best_pair()
  now = datetime.now()
  now = now + timedelta(hours=2)
  base = now.replace(
    second=0,
    microsecond=0
  )
  mm = now.minute % 5
  wm = 5 - mm
  if wm == 0:
    wm = 5
  entry = base + timedelta(minutes=wm)
  em = "
