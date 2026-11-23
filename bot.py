import os, time, threading, requests
from flask import Flask
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

app = Flask(__name__)
@app.route("/")
def home():
    return "Bot is alive!", 200

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"Send error: {e}", flush=True)

def get_price(symbol):
    # Yahoo Finance - مجاني
    mapping = {"EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "USDJPY=X", "XAU/USD": "GC=F"}
    try:
        r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{mapping[symbol]}?range=1d&interval=1m", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        closes = r.json()["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        closes = [c for c in closes if c is not None]
        return closes
    except Exception as e:
        print(f"Price error {symbol}: {e}", flush=True)
        return None

def calc_rsi(closes, period=14):
    if len(closes) < period+1: return 50
    gains, losses = [], []
    for i in range(1, period+1):
        diff = closes[-i] - closes[-i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    avg_gain = sum(gains)/period
    avg_loss = sum(losses)/period
    if avg_loss == 0: return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def bot_loop():
    print(">>> BOT LOOP STARTED <<<", flush=True)
    time.sleep(5)
    send("✅ <b>البوت V3 اشتغل</b>\nعم افحص السوق كل دقيقة...")
    sent = {}
    while True:
        try:
            print(f"--- CHECK {datetime.now().strftime('%H:%M:%S')} ---", flush=True)
            for pair in ["EUR/USD", "GBP/USD", "USD/JPY", "XAU/USD"]:
                closes = get_price(pair)
                if not closes: continue
                price = closes[-1]
                rsi = calc_rsi(closes)
                print(f"{pair}: {price:.5f} RSI {rsi:.1f}", flush=True)
                # شروط أخف مشان يبعت - للتجربة
                signal = None
                if rsi < 35: signal = "🟢 CALL ⬆️"
                elif rsi > 65: signal = "🔴 PUT ⬇️"
                if signal and sent.get(pair) != signal:
                    send(f"{signal} <b>{pair}</b>\nالسعر: {price:.5f}\nRSI: {rsi:.1f}\n⏰ دقيقة واحدة")
                    sent[pair] = signal
                    print(f"SENT {pair} {signal}", flush=True)
            time.sleep(60)
        except Exception as e:
            print(f"LOOP ERROR: {e}", flush=True)
            time.sleep(10)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
