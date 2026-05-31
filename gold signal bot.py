import requests
import time
import datetime
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

TOKEN = "8987191949:AAEO9M67XH7lRD5U0rBGpoNxN2kh2zLZaqs"
CHAT_ID = "642192218"
subscribers = [CHAT_ID]

def get_gold_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=XAUUSDT"
        r = requests.get(url, timeout=5)
        return round(float(r.json()["price"]), 2)
    except:
        try:
            url = "https://api.binance.com/api/v3/ticker/price?symbol=XAUUSD"
            r = requests.get(url, timeout=5)
            return round(float(r.json()["price"]), 2)
        except:
            return None

def get_candles():
    try:
        url = "https://api.binance.com/api/v3/klines?symbol=XAUUSDT&interval=5m&limit=50"
        r = requests.get(url, timeout=10)
        data = r.json()
        candles = []
        for c in data:
            candles.append({
                "open": float(c[1]),
                "high": float(c[2]),
                "low": float(c[3]),
                "close": float(c[4])
            })
        return candles
    except:
        return []

def analyze():
    candles = get_candles()
    price = get_gold_price()
    if not candles or not price:
        return None

    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    close = candles[-1]["close"]
    prev_close = candles[-2]["close"]

    recent_high = max(highs[-10:-1])
    recent_low = min(lows[-10:-1])

    # CHoCH
    if close > recent_high and prev_close < recent_high:
        structure, stype = "BULLISH", "CHoCH"
    elif close < recent_low and prev_close > recent_low:
        structure, stype = "BEARISH", "CHoCH"
    elif close > max(highs[-5:-1]):
        structure, stype = "BULLISH", "BOS"
    elif close < min(lows[-5:-1]):
        structure, stype = "BEARISH", "BOS"
    else:
        return None

    sorted_highs = sorted(highs[-20:], reverse=True)
    sorted_lows = sorted(lows[-20:])
    eq_high = abs(sorted_highs[0] - sorted_highs[1]) < 1.0
    eq_low = abs(sorted_lows[0] - sorted_lows[1]) < 1.0

    if structure == "BULLISH" and eq_low:
        return {"type": "BUY", "entry": price, "sl": round(price-6,2), "tp1": round(price+10,2), "tp2": round(price+20,2), "structure": stype, "liquidity": f"EQL @ {sorted_lows[0]}"}
    elif structure == "BEARISH" and eq_high:
        return {"type": "SELL", "entry": price, "sl": round(price+6,2), "tp1": round(price-10,2), "tp2": round(price-20,2), "structure": stype, "liquidity": f"EQH @ {sorted_highs[0]}"}

    return None

def send_message(chat_id, text):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})
    except:
        pass

def send_signal(signal):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    emoji = "🟢" if signal["type"] == "BUY" else "🔴"
    direction = "شراء" if signal["type"] == "BUY" else "بيع"
    msg = f"""{emoji} <b>XAUUSD {direction}</b>

📌 <b>Entry:</b> {signal['entry']}
🛑 <b>SL:</b> {signal['sl']}
🎯 <b>TP1:</b> {signal['tp1']}
🎯 <b>TP2:</b> {signal['tp2']}

📊 <b>الهيكل:</b> {signal['structure']}
💧 <b>Liquidity:</b> {signal['liquidity']}
🕐 <b>الوقت:</b> {now}

⚠️ هذه إشارة فقط - القرار النهائي لك"""
    for sub in subscribers:
        send_message(sub, msg)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"A4kgold Bot Running!")
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(length))
        send_signal(body)
        self.send_response(200)
        self.end_headers()
    def log_message(self, *args):
        pass

def bot_loop():
    offset = None
    last_check = 0
    while True:
        now = time.time()
        if now - last_check > 180:
            last_check = now
            signal = analyze()
            if signal:
                send_signal(signal)
        try:
            params = {"timeout": 30}
            if offset:
                params["offset"] = offset
            updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", params=params).json()
            for u in updates.get("result", []):
                offset = u["update_id"] + 1
                text = u.get("message", {}).get("text", "")
                cid = str(u.get("message", {}).get("chat", {}).get("id", ""))
                if text == "/start":
                    send_message(cid, "🥇 A4kgold Bot يعمل!\n/price - السعر\n/analyze - تحليل\n/buy - شراء\n/sell - بيع")
                elif text == "/price":
                    p = get_gold_price()
                    send_message(cid, f"🥇 <b>XAUUSD = {p}</b>" if p else "❌ تعذر جلب السعر")
                elif text == "/analyze":
                    send_message(cid, "🔍 جاري التحليل...")
                    s = analyze()
                    if s:
                        send_signal(s)
                    else:
                        send_message(cid, "⏳ لا توجد إشارة واضحة الآن")
                elif text == "/buy":
                    p = get_gold_price()
                    if p:
                        send_signal({"type":"BUY","entry":p,"sl":round(p-6,2),"tp1":round(p+10,2),"tp2":round(p+20,2),"structure":"Manual","liquidity":"Manual"})
                elif text == "/sell":
                    p = get_gold_price()
                    if p:
                        send_signal({"type":"SELL","entry":p,"sl":round(p+6,2),"tp1":round(p-10,2),"tp2":round(p-20,2),"structure":"Manual","liquidity":"Manual"})
        except:
            pass
        time.sleep(1)

if __name__ == "__main__":
    send_message(CHAT_ID, "🥇 <b>A4kgold Bot</b> يعمل!\n\n/price - السعر\n/analyze - تحليل\n/buy - شراء\n/sell - بيع")
    t = threading.Thread(target=bot_loop)
    t.daemon = True
    t.start()
    HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
