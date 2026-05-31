import requests
import time
import datetime

# ==============================
# إعدادات البوت
# ==============================
TOKEN = "8987191949:AAEO9M67XH7lRD5U0rBGpoNxN2kh2zLZaqs"
CHAT_ID = "642192218"
TWELVEDATA_API_KEY = "78205beca0c641c183df17074fa99f02"

subscribers = [CHAT_ID]

# ==============================
# جلب بيانات الشموع
# ==============================
def get_candles(interval="5min", outputsize=50):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval={interval}&outputsize={outputsize}&apikey={TWELVEDATA_API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        candles = data.get("values", [])
        result = []
        for c in candles:
            result.append({
                "time": c["datetime"],
                "open": float(c["open"]),
                "high": float(c["high"]),
                "low": float(c["low"]),
                "close": float(c["close"])
            })
        return result
    except Exception as e:
        print(f"خطأ في جلب الشموع: {e}")
        return []

# ==============================
# جلب السعر الحالي
# ==============================
def get_gold_price():
    try:
        url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={TWELVEDATA_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        return round(float(data["price"]), 2)
    except:
        return None

# ==============================
# كشف Market Structure
# ==============================
def detect_market_structure(candles):
    if len(candles) < 10:
        return None, None

    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]

    recent_high = max(highs[-10:-1])
    recent_low = min(lows[-10:-1])
    current_close = candles[-1]["close"]
    prev_close = candles[-2]["close"]

    # CHoCH
    if current_close > recent_high and prev_close < recent_high:
        return "BULLISH", "CHoCH"
    elif current_close < recent_low and prev_close > recent_low:
        return "BEARISH", "CHoCH"
    # BOS
    elif current_close > max(highs[-5:-1]):
        return "BULLISH", "BOS"
    elif current_close < min(lows[-5:-1]):
        return "BEARISH", "BOS"

    return None, None

# ==============================
# كشف Liquidity
# ==============================
def detect_liquidity(candles):
    if len(candles) < 20:
        return None, None

    highs = [c["high"] for c in candles[-20:]]
    lows = [c["low"] for c in candles[-20:]]

    # Equal Highs
    sorted_highs = sorted(highs, reverse=True)
    if abs(sorted_highs[0] - sorted_highs[1]) < 0.5:
        return "SELL", sorted_highs[0]

    # Equal Lows
    sorted_lows = sorted(lows)
    if abs(sorted_lows[0] - sorted_lows[1]) < 0.5:
        return "BUY", sorted_lows[0]

    # Previous High/Low
    prev_high = max(highs[:-3])
    prev_low = min(lows[:-3])
    current_price = candles[-1]["close"]

    if current_price > prev_high:
        return "SELL", prev_high
    elif current_price < prev_low:
        return "BUY", prev_low

    return None, None

# ==============================
# التحليل الكامل ICT
# ==============================
def analyze_ict():
    candles_m5 = get_candles("5min", 50)
    if not candles_m5:
        return None

    structure, change_type = detect_market_structure(candles_m5)
    liq_side, liq_level = detect_liquidity(candles_m5)
    current_price = get_gold_price()

    if not current_price:
        return None

    if structure == "BULLISH" and liq_side == "BUY":
        return {
            "type": "BUY",
            "entry": current_price,
            "sl": round(current_price - 6, 2),
            "tp1": round(current_price + 10, 2),
            "tp2": round(current_price + 20, 2),
            "structure": change_type,
            "liquidity": f"Buy-side @ {liq_level}"
        }
    elif structure == "BEARISH" and liq_side == "SELL":
        return {
            "type": "SELL",
            "entry": current_price,
            "sl": round(current_price + 6, 2),
            "tp1": round(current_price - 10, 2),
            "tp2": round(current_price - 20, 2),
            "structure": change_type,
            "liquidity": f"Sell-side @ {liq_level}"
        }

    return None

# ==============================
# إرسال رسالة
# ==============================
def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"خطأ: {e}")

# ==============================
# إرسال الإشارة
# ==============================
def send_signal(signal):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    emoji = "🟢" if signal["type"] == "BUY" else "🔴"
    direction = "شراء" if signal["type"] == "BUY" else "بيع"

    message = f"""
{emoji} <b>XAUUSD {direction}</b>

📌 <b>Entry:</b> {signal['entry']}
🛑 <b>SL:</b> {signal['sl']}
🎯 <b>TP1:</b> {signal['tp1']}
🎯 <b>TP2:</b> {signal['tp2']}

📊 <b>الهيكل:</b> {signal['structure']}
💧 <b>Liquidity:</b> {signal['liquidity']}
🕐 <b>الوقت:</b> {now}

⚠️ هذه إشارة فقط - القرار النهائي لك
"""
    for sub in subscribers:
        send_message(sub, message)
        time.sleep(0.3)
    print(f"✅ إشارة {signal['type']} أُرسلت")

# ==============================
# الأوامر
# ==============================
def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        return requests.get(url, params=params).json()
    except:
        return {"result": []}

def handle_commands():
    offset = None
    last_auto_check = 0

    send_message(CHAT_ID, """🥇 <b>A4kgold ICT Bot</b> يعمل الآن!

🤖 يحلل السوق كل دقيقة ويرسل عند أي إشارة ICT

الأوامر:
/analyze - تحليل فوري
/price - السعر الحالي
/buy - إشارة شراء يدوية
/sell - إشارة بيع يدوية""")

    print("🤖 البوت يعمل 24/7...")

    while True:
        now = time.time()

        # تحليل تلقائي كل دقيقة
        if now - last_auto_check > 60:
            last_auto_check = now
            print("🔍 تحليل...")
            signal = analyze_ict()
            if signal:
                send_signal(signal)

        # أوامر يدوية
        updates = get_updates(offset)
        for update in updates.get("result", []):
            offset = update["update_id"] + 1
            message = update.get("message", {})
            text = message.get("text", "")
            chat_id = str(message.get("chat", {}).get("id", ""))

            if text == "/start":
                send_message(chat_id, "🥇 مرحباً!\n/analyze - تحليل\n/price - السعر\n/buy - شراء\n/sell - بيع")

            elif text == "/price":
                price = get_gold_price()
                if price:
                    send_message(chat_id, f"🥇 <b>XAUUSD = {price}</b>")
                else:
                    send_message(chat_id, "❌ تعذر جلب السعر")

            elif text == "/analyze":
                send_message(chat_id, "🔍 جاري التحليل...")
                signal = analyze_ict()
                if signal:
                    send_signal(signal)
                else:
                    send_message(chat_id, "⏳ لا توجد إشارة واضحة الآن")

            elif text == "/buy":
                price = get_gold_price()
                if price:
                    signal = {"type": "BUY", "entry": price, "sl": round(price-6,2), "tp1": round(price+10,2), "tp2": round(price+20,2), "structure": "Manual", "liquidity": "Manual"}
                    send_signal(signal)

            elif text == "/sell":
                price = get_gold_price()
                if price:
                    signal = {"type": "SELL", "entry": price, "sl": round(price+6,2), "tp1": round(price-10,2), "tp2": round(price-20,2), "structure": "Manual", "liquidity": "Manual"}
                    send_signal(signal)

            elif text == "/subscribers":
                send_message(chat_id, f"👥 المشتركين: {len(subscribers)}")

        time.sleep(1)

if __name__ == "__main__":
    handle_commands()
