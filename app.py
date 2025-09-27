import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
PROXY_URL = os.getenv("PROXY_URL")

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup
    }
    requests.post(url, json=payload)

@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    if message.get("text") == "/start":
        send_message(chat_id, "🎬 Welcome to PlayLoom!\nSend or forward a video to get a Play button.")
        return "ok", 200

    if "video" in message:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/forwardMessage", json={
            "chat_id": CHANNEL_ID,
            "from_chat_id": chat_id,
            "message_id": message_id
        })
        send_message(chat_id, "📤 Uploading to PlayLoom Stream...\nYou'll get your Play button shortly.")
        return "ok", 200

    send_message(chat_id, "👋 Send or forward a video to get started.")
    return "ok", 200
