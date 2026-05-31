import requests
import time
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import threading

TOKEN = "8987191949:AAEO9M67XH7lRD5U0rBGpoNxN2kh2zLZaqs"
CHAT_ID = "642192218"
subscribers = [CHAT_ID]

def send_message(chat_id, message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"خطأ: {e}")

def send_signal(data):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    signal_type = data.get("type", "BUY")
    emoji = "🟢" if signal_type == "BUY" else "🔴"
    direction = "شراء" if signal_type == "BUY" else "بيع"

    message = f"""
{emoji} <b>XAUUSD {direction}</b>

📌 <b>Entry:</b> {data.get('entry', '')}
🛑 <b>SL:</b> {data.get('sl', '')}
🎯 <b>TP1:</b> {data.get('tp1', '')}
🎯 <b>TP2:</b> {data.get('tp2', '')}

📊 <b>الهيكل:</b> {data.get('structure', 'ICT')}
💧 <b>Liquidity:</b> {data.get
