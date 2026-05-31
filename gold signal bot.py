import requests
import time
import datetime

# ==============================
# إعدادات البوت
# ==============================
TOKEN = "8987191949:AAEO9M67XH7lRD5U0rBGpoNxN2kh2zLZaqs"
CHAT_ID = "642192218"

# ==============================
# قائمة المشتركين
# ==============================
subscribers = [CHAT_ID]  # أضف Chat ID المشتركين هنا

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
def send_signal_to_all(signal_type, entry, sl, tp1, tp2, reason=""):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if signal_type == "BUY":
        emoji = "🟢"
    else:
        emoji = "🔴"

    message = f"""
{emoji} <b>XAUUSD {signal_type}</b>

📌 <b>Entry:</b> {entry}
🛑 <b>SL:</b> {sl}
🎯 <b>TP1:</b> {tp1}
🎯 <b>TP2:</b> {tp2}

📊 <b>السبب:</b> {reason if reason else "Liquidity ICT Setup"}
🕐 <b>الوقت:</b> {now}

⚠️ هذه إشارة فقط - القرار النهائي لك
"""

    for subscriber in subscribers:
        send_message(subscriber, message)
        time.sleep(0.3)

    print(f"✅ تم إرسال إشارة {signal_type} لـ {len(subscribers)} مشترك")

# ==============================
# رسالة ترحيب
# ==============================
def send_welcome():
    message = """
🥇 <b>A4kgold Signal Bot</b>

✅ البوت يعمل الآن!
📊 سيرسل إشارات XAUUSD
⚡ على فريم M1/M5 - ICT Liquidity

أرسل /signal لإرسال إشارة يدوية
"""
    send_message(CHAT_ID, message)

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

    while True:
        updates = get_updates(offset)

        for update in updates.get("result", []):
            offset = update["update_id"] + 1
            message = update.get("message", {})
            text = message.get("text", "")
            chat_id = str(message.get("chat", {}).get("id", ""))

            # أمر /start
            if text == "/start":
                send_message(chat_id, "🥇 مرحباً في A4kgold!\nأرسل /signal لإرسال إشارة")

            # أمر /signal - مثال إشارة يدوية
            elif text == "/signal":
                send_signal_to_all(
                    signal_type="BUY",
                    entry="2350.00",
                    sl="2345.00",
                    tp1="2355.00",
                    tp2="2362.00",
                    reason="Liquidity Sweep - ICT Setup M5"
                )

            # أمر /sell - مثال إشارة بيع
            elif text == "/sell":
                send_signal_to_all(
                    signal_type="SELL",
                    entry="2350.00",
                    sl="2355.00",
                    tp1="2345.00",
                    tp2="2338.00",
                    reason="Liquidity Sweep - ICT Setup M5"
                )

            # أمر /subscribers
            elif text == "/subscribers":
                send_message(chat_id, f"👥 عدد المشتركين: {len(subscribers)}")

# ==============================
# تشغيل البوت
# ==============================
if __name__ == "__main__":
    send_welcome()
    handle_commands()
