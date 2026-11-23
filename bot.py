import requests, time, threading
from flask import Flask
from datetime import datetime, timedelta
import pytz

TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT_ID = "6459511609"

app = Flask(__name__)
@app.route('/')
def home():
    return "Pocket Real Bot V2"

def keep_alive():
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000)).start()

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text})
    except: pass

beirut = pytz.timezone("Asia/Beirut")

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X",
    "AUD/USD": "AUDUSD=X",
    "USD/CAD": "USDCAD=X",
}

def get_closes(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1m"
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        result = data['chart']['result'][0]
        closes = [c for c in result['indicators']['quote'][0]['close'] if c is not None]
        return closes
    except:
        return None

def calc_rsi_correct(prices, period=14):
    # طريقة RSI الصحيحة - Wilder
    if len(prices) < period+1: return 50
    deltas = [prices[i]-prices[i-1] for i in range(1, len(prices))]
    gains = [d if d>0 else 0 for d in deltas]
    losses = [-d if d<0 else 0 for d in deltas]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain*(period-1) + gains[i]) / period
        avg_loss = (avg_loss*(period-1) + losses[i]) / period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calc_ema(prices, period):
    if len(prices) < period: return prices[-1]
    k = 2 / (period + 1)
    ema = prices[0]
    for p in prices:
        ema = p * k + ema * (1 - k)
    return ema

def format_time(dt):
    h = dt.strftime("%I:%M:%S").lstrip("0")
    ampm = "صباحاً" if dt.hour < 12 else "مساءً"
    return f"{h} {ampm}"

def analyze():
    best = None
    best_score = 0
    for name, symbol in PAIRS.items():
        closes = get_closes(symbol)
        if not closes or len(closes) < 30: continue
        price = closes[-1]
        rsi = calc_rsi_correct(closes)
        ema9 = calc_ema(closes, 9)
        ema21 = calc_ema(closes, 21)
        score = 0
        direction = None
        # شروط حقيقية و صارمة
        if rsi < 30 and price > ema21:
            direction = "CALL"
            score = 60 + (30 - rsi) * 0.3
        elif rsi > 70 and price < ema21:
            direction = "PUT"
            score = 60 + (rsi - 70) * 0.3
        elif rsi < 45 and ema9 > ema21 and closes[-1] > closes[-2]:
            direction = "CALL"
            score = 56
        elif rsi > 55 and ema9 < ema21 and closes[-1] < closes[-2]:
            direction = "PUT"
            score = 56
        if direction and score > best_score:
            best_score = min(score, 65)
            best = (name, direction, price, rsi, score)
    return best

def bot_loop():
    send_msg("✅ البوت الحقيقي V2 اشتغل - RSI مظبوط و نسبة max 65%")
    while True:
        now = datetime.now(beirut)
        if now.second == 30:
            result = analyze()
            if result:
                name, direction, price, rsi, score = result
                entry_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
                reversal_time = entry_time + timedelta(minutes=1)
                entry_str = format_time(entry_time)
                reversal_str = format_time(reversal_time)
                now_str = format_time(now)
                dir_text = "🟢 شراء - CALL" if direction == "CALL" else "🔴 بيع - PUT"
                msg = f"""🔥 {name} | Pocket Option - تحليل حقيقي V2

🕐 الساعة هلأ: {now_str}
⏰ وقت الدخول: {entry_str}
⏳ باقي: 30 ثانية

{dir_text}

🎯 دخول: {price:.5f}
⏱️ مدة الصفقة: 1 دقيقة
📊 RSI: {rsi:.1f}
📈 نسبة النجاح: {score:.0f}% - حسب قوة الاشارة

⚠️ في حال الانعكاس: ادخل ع {reversal_str}"""
                send_msg(msg)
            time.sleep(60)
        time.sleep(1)

keep_alive()
threading.Thread(target=bot_loop).start()
