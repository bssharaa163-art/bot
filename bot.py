import os
import time
import requests
import threading
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
PRICE = {}
for p in PAIRS:
  PRICE[p] = 1.0
PRICE["EUR/USD"] = 1.08
PRICE["GBP/USD"] = 1.27
PRICE["USD/JPY"] = 155.2
def send(m):
  u = "https://api.telegram.org/bot"
  u = u + TOKEN + "/sendMessage"
  try:
    requests.post(u, data={"chat_id": CHAT, "text": m}, timeout=10)
  except:
    pass
def get_prices():
  url = "https://open.er-api.com/v6/latest/USD"
  r = requests.get(url, timeout=8).json()
  rates = r.get("rates", {})
  for disp in PAIRS:
    a = disp.split("/")[0]
    b = disp.split("/")[1]
    v = 0
    if a == "USD":
      v = rates.get(b, 0)
    if b == "USD":
      if rates.get(a):
        v = 1 / rates.get(a)
    if a != "USD":
      if b != "USD":
        if rates.get(a):
          if rates.get(b):
            x = 1 / rates.get(a)
            y = 1 / rates.get(b)
            v = x / y
    if v > 0:
      PRICE[disp] = v
  return PRICE
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
def klines(sym):
  u = "https://api.binance.com/api/v3/klines"
  u = u + "?symbol=" + sym
  u = u + "&interval=1m&limit=20"
  try:
    d = requests.get(u, timeout=5).json()
    c = []
    for x in d:
      c.append(float(x[4]))
    return c
  except:
    return []
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
  best = "EUR/USD"
  bs = -1
  bd = "CALL"
  bp = 1.08
  for disp in PAIRS:
    p = PRICE[disp]
    sym = ""
    if disp == "EUR/USD":
      sym = "EURUSDT"
    if disp == "GBP/USD":
      sym = "GBPUSDT"
    if disp == "AUD/USD":
      sym = "AUDUSDT"
    if disp == "NZD/USD":
      sym = "NZDUSDT"
    r = 50
    tr = 0
    if sym != "":
      cl = klines(sym)
      if len(cl) > 5:
        r = rsi(cl)
        tr = (cl[-1] - cl[0]) / cl[0] * 100
    d = "CALL"
    sc = 0.5
    if r > 70:
      d = "PUT"
      sc = r - 70
    if r < 30:
      d = "CALL"
      sc = 30 - r
    if r >= 30:
      if r <= 70:
        if tr > 0:
          d = "PUT"
        else:
          d = "CALL"
        sc = abs(tr) * 10 + 0.5
    if sc > bs:
      bs = sc
      best = disp
      bd = d
      if p < 10:
        bp = round(p, 5)
      else:
        bp = round(p, 2)
  return best, bp, bd
def do_signal():
  b, pr, dr = best_pair()
  now = datetime.now()
  now = now + timedelta(hours=2)
  base = now.replace(second=0, microsecond=0)
  mm = now.minute % 5
  wm = 5 - mm
  if wm == 0:
    wm = 5
  entry = base + timedelta(minutes=wm)
  em = "🟢"
  if dr == "PUT":
    em = "🔴"
  msg = "تحليل حقيقي | Pocket Option\n\n"
  msg = msg + "الزوج: " + b + "\n"
  msg = msg + "الصفقة: " + dr + " " + em + "\n"
  msg = msg + "الفريم: 1 دقيقة\n"
  msg = msg + "سعر الدخول: " + str(pr) + "\n"
  msg = msg + "وقت الإرسال: " + fmt2(now) + "\n"
  msg = msg + "وقت الدخول: " + fmt(entry) + "\n"
  msg = msg + "في حال الانعكاس: دوبل\n"
  send(msg)
  print("SENT " + b)
def loop():
  send("البوت اشتغل - ازواج عادية فقط - قبل 30 ثانية")
  while True:
    now = datetime.now()
    now = now + timedelta(hours=2)
    mm = now.minute % 5
    left = 5 - mm
    wait = left * 60
    wait = wait - now.second
    wait = wait - 30
    if wait < 0:
      wait = wait + 300
    print("WAIT " + str(wait))
    if wait > 0:
      time.sleep(wait)
    try:
      do_signal()
    except:
      pass
    time.sleep(40)
@app.route("/")
def home():
  return "Bot Live"
if __name__ == "__main__":
  t = threading.Thread(target=loop, daemon=True)
  t.start()
  port = int(os.environ.get("PORT", 10000))
  app.run(host="0.0.0.0", port=port)
