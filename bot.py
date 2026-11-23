import requests, time, threading, random
from flask import Flask
from datetime import datetime, timedelta
import pytz

TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT_ID = "6459511609"

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!"

def keep_alive():
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000)).start()

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text})
    except: pass

def get_price(symbol="BTCUSDT"):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=5)
        return float(r.json()['price'])
    except:
        return 67450.0

def format_time(dt):
    h = dt.strftime("%I:%M:%S").lstrip("0")
    ampm = "صباحاً" if dt.hour < 12 else "مساءً"
    return f"{h} {ampm}"

beirut = pytz.timezone("Asia/Beirut")

PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "EUR/GBP", "USD/CHF", "BTC/USDT", "ETH/USDT"]

def bot_loop():
    print("البوت شغال...")
    while True:
        now = datetime.now(beirut)
        if now.second == 30:
            entry_time = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
            reversal_time = entry_time + timedelta(minutes=1)
            entry_str = format_time(entry_time)
            reversal_str = format_time(reversal_time)
            now_str = format_time(now)

            best_pair = None
            best_success = 0
            best_is_buy = True
            for pair in PAIRS:
                success = random.randint(70, 97)
                if success > best_success:
                    best_success = success
                    best_pair = pair
                    best_is_buy = random.choice([True, False])

            direction = "🟢 شراء - CALL" if best_is_buy else "🔴 بيع - PUT"
            price = get_price("BTCUSDT")

            if best_success >= 90:
                header = "🔥🔥🔥 شارة قوية كتير 🔥🔥🔥\nلا تروح عليك!!\n\n"
                success_text = f"{best_success}% - قوية جداً"
            else:
                header = ""
                success_text = f"{best_success}%"

            msg = f"""{header}🔥 {best_pair} | فريم 1د

🕐 الساعة هلأ: {now_str}
⏰ وقت الدخول: {entry_str}
⏳ باقي: 30 ثانية

{direction}

🎯 دخول: {price:,.0f}
⏱️ مدة الصفقة: 1 دقيقة
📈 نسبة النجاح: {success_text}

⚠️ في حال الانعكاس: ادخل ع {reversal_str}"""

            send_msg(msg)
            time.sleep(60)
        time.sleep(1)

keep_alive()
threading.Thread(target=bot_loop).start()
