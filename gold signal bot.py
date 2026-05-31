import requests
import time
import datetime

# ==============================
# إعدادات البوت
# ==============================
TOKEN = "8987191949:AAEO9M67XH7lRD5U0rBGpoNxN2kh2zLZaqs"
CHAT_ID = "642192218"
TWELVEDATA_API_KEY = "78205beca0c641c183df17074fa99f02"

# ==============================
# قائمة المشتركين
# ==============================
subscribers = [CHAT_ID]

# ==============================
# جلب سعر الذهب الحالي
# ==============================
def get_gold_price():
    try:
        url = f"https://api.twelvedata.com/price?symbol=XAU/USD&apikey={TWELVEDATA_API_KEY}"
        response = requests.get(url, timeout=5)
        data = response.json()
        price = float(data["price"])
        return round(price, 2)
    except Exception as e:
        print(f"خطأ في جلب السعر: {e}")
        return None

# ==============================
# إرسال رسالة
# ==============================
def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"خطأ في الإرسال: {e}")

# ==============================
# إرسال الإشارة لجميع المشتركين
# ==============================
def send_signal_to_all(signal_type, entry, sl, tp1, tp2):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if signal_type == "BUY":
        emoji = "🟢"
        direction = "شراء"
    else:
        emoji = "🔴"
        direction = "بيع"

    message = f"""
{emoji} <b>XAUUSD {direction}</b>

📌 <b>Entry:</b> {entry}
🛑 <b>SL:</b> {sl}
🎯 <b>TP1:</b> {tp1}
🎯 <b>TP2:</b> {tp2}

📊 <b>الاستراتيجية:</b> ICT Liquidity M5
🕐 <b>الوقت:</b> {now}

⚠️ هذه إشارة فقط - القرار النهائي لك
"""

    for subscriber in subscribers:
        send_message(subscriber, message)
        time.sleep(0.3)

    print(f"✅ تم إرسال إشارة {signal_type} لـ {len(subscribers)} مشترك")

# ==============================
# الاستماع للأوامر
# ==============================
def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    params = {"timeout": 30}
    if offset:
        params["offset"] = offset
    try:
        response = requests.get(url, params=params)
        return response.json()
    except:
        return {"result": []}

def handle_commands():
    offset = None
    print("🤖 البوت يعمل ويستمع للأوامر...")

    # رسالة ترحيب
    send_message(CHAT_ID, "🥇 <b>A4kgold Bot</b> يعمل الآن!\n\nالأوامر:\n/buy - إشارة شراء\n/sell - إشارة بيع\n/price - السعر الحالي\n/subscribers - عدد المشتركين")

    while True:
        updates = get_updates(offset)

        for update in updates.get("result", []):
            offset = update["update_id"] + 1
            message = update.get("message", {})
            text = message.get("text", "")
            chat_id = str(message.get("chat", {}).get("id", ""))

            if text == "/start":
                send_message(chat_id, "🥇 مرحباً في A4kgold!\n\n/buy - إشارة شراء\n/sell - إشارة بيع\n/price - السعر الحالي")

            elif text == "/price":
                price = get_gold_price()
                if price:
                    send_message(chat_id, f"🥇 <b>سعر الذهب الحالي:</b>\nXAUUSD = <b>{price}</b>")
                else:
                    send_message(chat_id, "❌ تعذر جلب السعر، حاول مجدداً")

            elif text == "/buy":
                price = get_gold_price()
                if price:
                    sl = round(price - 5, 2)
                    tp1 = round(price + 8, 2)
                    tp2 = round(price + 15, 2)
                    send_signal_to_all("BUY", price, sl, tp1, tp2)
                else:
                    send_message(chat_id, "❌ تعذر جلب السعر، حاول مجدداً")

            elif text == "/sell":
                price = get_gold_price()
                if price:
                    sl = round(price + 5, 2)
                    tp1 = round(price - 8, 2)
                    tp2 = round(price - 15, 2)
                    send_signal_to_all("SELL", price, sl, tp1, tp2)
                else:
                    send_message(chat_id, "❌ تعذر جلب السعر، حاول مجدداً")

            elif text == "/subscribers":
                send_message(chat_id, f"👥 عدد المشتركين: {len(subscribers)}")

        time.sleep(1)

if __name__ == "__main__":
    handle_commands()
