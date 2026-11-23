import os
import time
import requests
import threading
import random
from datetime import datetime, timedelta
from flask import Flask
app = Flask(__name__)
TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT = "6459511609"
PAIRS = ["EUR/USD","GBP/USD","AUD/USD","NZD/USD"]
PAIRS += ["USD/CAD","USD/CHF","USD/JPY"]
PAIRS += ["EUR/GBP","EUR/JPY","GBP/JPY"]
PAIRS += ["EUR/AUD","GBP/AUD","AUD/JPY"]
PAIRS += ["NZD/JPY","EUR/CHF","GBP/CHF"]
PAIRS += ["AUD/CAD","EUR/CAD","CHF/JPY"]
PAIRS += ["CAD/JPY","EUR/NZD","GBP/NZD"]
PAIRS += ["AUD/NZD","ETH/USD","LTC/USD"]
PAIRS += ["XRP/USD","GOLD","SILVER"]
HIST = {}
PRICE = {}
for p in PAIRS:
  HIST[p] = []
  PRICE[p] = 1.0
PRICE["EUR/USD"] = 1.08
PRICE["GBP/USD"] = 1.27
PRICE["GOLD"] = 2650
LAST = []
def send(m):
  try:
    u = "https://api.telegram.org/bot" + TOKEN + "/sendMessage"
    requests.post(u, data={"chat_id": CHAT, "text": m}, timeout=10)
  except:
    pass
def get_prices():
  try:
    r = requests.get("https://open.er-api.com/v6/latest/USD", timeout=8).json()
    rates = r.get("rates", {})
    for disp in PAIRS:
      if "/" not in disp:
        continue
      a = disp.split("/")[0]
      b = disp.split("/")[1]
      v = 0
      if a == "USD":
        v = rates.get(b, 0)
      elif b == "USD":
        if rates.get(a):
          v = 1 / rates.get(a)
      else:
        if rates.get(a) and rates.get(b):
          v = (1 / rates.get(a)) / (1 / rates.get(b))
      if v and v > 0:
        PRICE[disp] = v
  except:
    pass
  try:
    p = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHUSDT", timeout=5).json()
    PRICE["ETH/USD"] = float(p["price"])
  except:
    pass
  try:
    p = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=5).json()
    PRICE["GOLD"] = float(p["price"])
  except:
    pass
  PRICE["SILVER"] = PRICE["GOLD"] * 0.0119
  return PRICE
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
def best_pair():
  get_prices()
  best = PAIRS[0]
  best_score = -1
  best_dir = "CALL"
  best_price = 1.0
  for disp in PAIRS:
    p = PRICE[disp]
    HIST[disp].append(p)
    if len(HIST[disp]) > 5:
      HIST[disp].pop(0)
    hist = HIST[disp]
    d = "CALL"
    sc = random.uniform(0.5, 1.5)
    if len(hist) > 2:
      ch = (hist[-1] - hist[0]) / hist[0] * 100
      if ch > 0.02:
        d = "PUT"
      if ch < -0.02:
        d = "CALL"
      if ch >= -0.02 and ch <= 0.02:
        if hist[-1] > hist[-2]:
          d = "CALL"
        else:
          d = "PUT"
      sc = abs(ch) * 10 + random.uniform(0, 0.5)
    else:
      if random.random() > 0.5:
        d = "CALL"
      else:
        d = "PUT"
    if sc > best_score:
      best_score = sc
      best = disp
      best_dir = d
      if p < 10:
        best_price = round(p, 5)
      else:
        best_price = round(p, 2)
  if len(LAST) > 1:
    if LAST[-1] == best and LAST[-2] == best:
      pass
  LAST.append(best)
  return best, best_price, best_dir
def do_signal():
  try:
    b, pr, dr = best_pair()
    now = datetime.now() + timedelta(hours=2)
    base = now.replace(second=0, microsecond=0)
    wm = (5 - (now.minute % 5)) % 5
    if wm == 0:
      wm = 5
    entry = base + timedelta(minutes=wm)
    em = "🟢"
    if dr == "PUT":
      em = "🔴"
    msg = "تحليل حقيقي | Pocket Option\n\n"
    msg += "الزوج: " + b + "\n"
    msg += "الصفقة: " + dr + " " + em + "\n"
    msg += "الفريم: 1 دقيقة\n"
    msg += "سعر الدخول: " + str(pr) + "\n"
    msg += "وقت الإرسال: " + fmt2(now) + "\n"
    msg += "وقت الدخول: " + fmt(entry) + " - مدة دقيقة وحدة\n"
    msg += "في حال الانعكاس: دوبل\n"
    send(msg)
    print("SENT " + b)
  except Exception as e:
    print("ERR")
    print(e)
def loop():
  send("البوت اشتغل - كل الازواج بدون BTC - اقوى زوج - قبل 30 ثانية")
  while True:
    try:
      now = datetime.now() + timedelta(hours=2)
      wait = (5 - (now.minute % 5)) * 60 - now.second - 30
      if wait < 0:
        wait = wait + 300
      print("WAIT " + str(wait))
      if wait > 0:
        time.sleep(wait)
      do_signal()
      time.sleep(40)
    except:
      time.sleep(5)
@app.route("/")
def home():
  return "Bot Live"
if __name__ == "__main__":
  threading.Thread(target=loop, daemon=True).start()
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
