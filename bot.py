import requests, time, threading
from flask import Flask
from datetime import datetime, timedelta
import pytz

TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT_ID = "6459511609"

app = Flask(__name__)
@app.route('/')
def home():
    return "Pocket Real Bot is alive!"

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
    "EUR/GBP": "EURGBP=X",
    "EUR/JPY": "EURJPY=X",
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

def calc_rsi(prices, period=14):
    if len(prices) < period+1: return 50
    gains = []
    losses = []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff >= 0: gains.append(diff)
        else: losses.append(abs(diff))
    if len(gains)==0: return 0
    if len(losses)==0: return 100
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
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
        rsi = calc_rsi(closes)
        ema9 = calc_ema(closes, 9)
        ema21 = calc_ema(closes, 21)
        score = 0
        direction = None
        if rsi < 32 and price > ema21:
            direction = "CALL"
            score = 65 + (32 - rsi)
        elif rsi < 40 and ema9 > ema21 and closes[-1] > closes[-2] and closes[-2] > closes[-3]:
            direction = "CALL"
            score = 58 + (40 - rsi) * 0.5
        elif rsi > 68 and price < ema21:
            direction = "PUT"
            score = 65 + (rsi - 68)
        elif rsi > 60 and ema9 < ema21 and closes[-1] < closes[-2] and closes[-2] < closes[-3]:
            direction = "PUT"
            score = 58 + (rsi - 60) * 0.5
        if direction and score > best_score:
            best_score = min(score, 72)
            best = (name, direction, price, rsi, score)
    return best

def bot_loop():
    print("بوت بوكت الحقيقي شغال...")
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
                msg = f"""🔥 {name} | Pocket Option - تحليل حقيقي

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
            else:
                print(f"ما في فرصة واضحة - {now}")
            time.sleep(60)
        time.sleep(1)

keep_alive()
threading.Thread(target=bot_loop).start()
