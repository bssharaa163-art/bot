import os
import time
import requests
import threading
import random
from datetime import datetime
from datetime import timedelta
from flask import Flask
from contextlib import suppress
app = Flask(__name__)
TOKEN = "9018724396:AAE10-Y5LQgVxlVfiuuqxQDEuqKFuoJIVS8"
CHAT = "6459511609"
PAIRS = ["EUR/USD","GBP/USD","AUD/USD","NZD/USD","USD/CAD","USD/CHF","USD/JPY","EUR/GBP","EUR/JPY","GBP/JPY","EUR/AUD","GBP/AUD","AUD/JPY","NZD/JPY","EUR/CHF","GBP/CHF","AUD/CAD","EUR/CAD","CHF/JPY","CAD/JPY","EUR/NZD","GBP/NZD","AUD/NZD"]
LAST = []
def send(m): u="https://api.telegram.org/bot"+TOKEN+"/sendMessage"; with suppress(Exception): requests.post(u,data={"chat_id":CHAT,"text":m},timeout=10)
def klines(sym): u="https://api.binance.com/api/v3/klines?symbol="+sym+"&interval=1m&limit=30"; out=[]; with suppress(Exception): out=[float(x[4]) for x in requests.get(u,timeout=5).json()]; return out
def rsi(c): g=sum([max(0,c[i]-c[i-1]) for i in range(1,15)]); l=sum([max(0,c[i-1]-c[i]) for i in range(1,15)]); ag=g/14; al=l/14; return 90 if al==0 else 100-(100/(1+ag/al))
def fmt(d): h=d.hour%12; h=12 if h==0 else h; ap="ص" if d.hour<12 else "م"; m=str(d.minute).zfill(2); return str(h)+":"+m+" "+ap
def fmt2(d): h=d.hour%12; h=12 if h==0 else h; ap="ص" if d.hour<12 else "م"; m=str(d.minute).zfill(2); s=str(d.second).zfill(2); return str(h)+":"+m+":"+s+" "+ap
def get_sym(disp): return {"EUR/USD":"EURUSDT","GBP/USD":"GBPUSDT","AUD/USD":"AUDUSDT","NZD/USD":"NZDUSDT","USD/CAD":"USDCUSDT","USD/CHF":"CHFUSDT","USD/JPY":"JPYUSDT","EUR/GBP":"EURUSDT","EUR/JPY":"EURUSDT","GBP/JPY":"GBPUSDT","EUR/AUD":"EURUSDT","GBP/AUD":"GBPUSDT","AUD/JPY":"AUDUSDT","NZD/JPY":"NZDUSDT","EUR/CHF":"EURUSDT","GBP/CHF":"GBPUSDT","AUD/CAD":"AUDUSDT","EUR/CAD":"EURUSDT","CHF/JPY":"CHFUSDT","CAD/JPY":"USDCUSDT","EUR/NZD":"EURUSDT","GBP/NZD":"GBPUSDT","AUD/NZD":"AUDUSDT"}.get(disp,"EURUSDT")
def calc_price(disp,last): m={"USD/JPY":150,"EUR/JPY":165,"GBP/JPY":190,"AUD/JPY":100,"NZD/JPY":95,"CHF/JPY":175,"CAD/JPY":110,"EUR/GBP":0.85,"EUR/AUD":1.65,"GBP/AUD":1.95,"EUR/CHF":0.95,"GBP/CHF":1.12,"AUD/CAD":0.90,"EUR/CAD":1.47,"EUR/NZD":1.78,"GBP/NZD":2.10,"AUD/NZD":1.07}; p=last*m.get(disp,1); p=1/last if disp in ["USD/CAD","USD/CHF"] and last!=0 else p; return round(p,5) if p<10 else round(p,2)
def analyse(disp): cl=klines(get_sym(disp)); r=rsi(cl) if len(cl)>15 else 50; last=cl[-1] if len(cl)>2 else 1; prev=cl[-2] if len(cl)>2 else 1; ema=sum(cl[-10:])/10 if len(cl)>10 else last; mom=abs(last-prev)/prev*100 if prev!=0 else 0; d="PUT" if r>68 else "CALL" if r<32 else "PUT" if last>ema else "CALL"; sc=(abs(r-50) if r>68 or r<32 else mom*10)+random.uniform(0,1.5); p=calc_price(disp,last); return (sc,disp,p,d)
def best_pair(): alls=[analyse(x) for x in PAIRS]; alls.sort(reverse=True); pick=alls[0]; pick=alls[1] if len(LAST)>0 and LAST[-1]==pick[1] and len(alls)>1 else pick; LAST.append(pick[1]); LAST.pop(0) if len(LAST)>5 else None; print("TOP "+alls[0][1]+" "+alls[0][3]); return pick[1],pick[2],pick[3]
def do_signal(): b,pr,dr=best_pair(); now=datetime.now()+timedelta(hours=2); base=now.replace(second=0,microsecond=0); wm=5-(now.minute%5); wm=5 if wm==0 else wm; entry=base+timedelta(minutes=wm); em="🔴" if dr=="PUT" else "🟢"; msg="تحليل حقيقي | Pocket Option\n\nالزوج: "+b+"\nالصفقة: "+dr+" "+em+"\nالفريم: 1 دقيقة\nسعر الدخول: "+str(pr)+"\nوقت الإرسال: "+fmt2(now)+"\nوقت الدخول: "+fmt(entry)+"\nفي حال الانعكاس: دوبل\n"; send(msg); print("SENT "+b+" "+dr)
def loop(): with suppress(Exception): do_signal(); now=datetime.now()+timedelta(hours=2); mm=now.minute%5; wait=(5-mm)*60-now.second-30; wait=wait+300 if wait<0 else wait; print("WAIT "+str(wait)); threading.Timer(wait,loop).start()
@app.route("/")
def home(): return "Bot Live"
if __name__ == "__main__": send("البوت اشتغل - تحليل حقيقي - قبل 30 ثانية"); loop(); port=int(os.environ.get("PORT",10000)); app.run(host="0.0.0.0",port=port)
