import requests, time, threading, datetime
from flask import Flask

TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT_ID = "6459511609"

app = Flask(__name__)
@app.route('/')
def home():
    return "Bot is alive!"

def keep_alive():
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

def send(text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except: pass

NAMES = {
    "EUR/USD": "يورو / دولار",
    "GBP/USD": "باوند / دولار",
    "USD/JPY": "دولار / ين",
    "AUD/USD": "استرالي / دولار",
    "USD/CAD": "دولار / كندي",
    "EUR/GBP": "يورو / باوند",
    "USD/CHF": "دولار / فرنك",
    "NZD/USD": "نيوزيلندي / دولار"
}

def get_price(pair):
    try:
        symbol = pair.replace("/", "") + "=X"
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1h", headers={"User-Agent":"Mozilla/5.0"}, timeout=10).json()
        closes = r['chart']['result'][0]['indicators']['quote'][0]['close']
        closes = [c for c in closes if c is not None]
        return closes[-1], closes
    except:
        return None, None

def get_rsi(closes, period=14):
    if len(closes) < period+1: return 50
    gains, losses = [], []
    for i in range(1, period+1):
        diff = closes[-i] - closes[-i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains)/period
    avg_loss = sum(losses)/period
    if avg_loss == 0: return 100.0
    rs = avg_gain/avg_loss
    return round(100 - (100/(1+rs)), 1)

def beirut_time():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=2)

def format_clock(dt):
    # بيحول 18:45 -> 06:45 مساءً
    hour = dt.hour
    if hour == 0:
        return dt.strftime("12:%M صباحاً")
    elif hour < 12:
        return dt.strftime("%I:%M صباحاً")
    elif hour == 12:
        return dt.strftime("12:%M ظهراً")
    else:
        return dt.strftime("%I:%M مساءً")

def format_signal(pair, price, rsi, direction):
    now = beirut_time()
    entry = format_clock(now)
    end = format_clock(now + datetime.timedelta(minutes=5))
    arabic_name = NAMES.get(pair, pair)
    if direction == "شراء":
        emoji = "📈"
        action = "شراء - صعود"
    else:
        emoji = "📉"
        action = "بيع - هبوط"
    return f"""{emoji} اشارة جديدة {emoji}

الزوج: {pair}
اسم الزوج: {arabic_name}
الاتجاه: {action}
وقت الشمعة: 5 دقائق
وقت الدخول: {entry}
وقت انتهاء الصفقة: {end}
السعر الحالي: {price:.5f}
قوة الاشارة RSI: {rsi}

Pocket Option - اشارات بالعربي"""

last_update_id = 0
def check_commands():
    global last_update_id
    while True:
        try:
            r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=10", timeout=15).json()
            for upd in r.get("result", []):
                last_update_id = upd["update_id"]
                msg = upd.get("message", {})
                text = msg.get("text", "").lower()
                if not text: continue
                if "/start" in text or "/help" in text:
                    send("اهلا فيك! انا شغال ✅\nاكتب /price لتشوف الاسعار هلأ\nالاشارات بتوصلك تلقائيا من الاثنين للجمعة")
                elif "/price" in text:
                    out = "📊 الاسعار هلأ:\n\n"
                    for p in ["EUR/USD","GBP/USD","USD/CHF","EUR/GBP"]:
                        price, closes = get_price(p)
                        if price:
                            out += f"الزوج: {p} - {NAMES.get(p,p)}\nالسعر: {price:.5f} - RSI: {get_rsi(closes)}\n\n"
                    out += f"وقت الفحص: {format_clock(beirut_time())}"
                    send(out)
        except: pass
        time.sleep(3)

keep_alive()
threading.Thread(target=check_commands, daemon=True).start()
send("البوت اشتغل - شغال 24/24 - بيرد على /start و /price ✅")

weekend_sent = False
pairs = ["EUR/USD","GBP/USD","USD/JPY","AUD/USD","USD/CAD","EUR/GBP","USD/CHF","NZD/USD"]

while True:
    now_utc = datetime.datetime.utcnow()
    if now_utc.weekday() >= 5:
        if not weekend_sent:
            send("السوق مسكر - ويكند - ناطرين ليوم الاثنين")
            weekend_sent = True
        time.sleep(3600)
        continue
    weekend_sent = False
    for p in pairs:
        price, closes = get_price(p)
        if not price: continue
        rsi = get_rsi(closes)
        if rsi > 70:
            send(format_signal(p, price, rsi, "بيع"))
        elif rsi < 30:
            send(format_signal(p, price, rsi, "شراء"))
    time.sleep(300)
