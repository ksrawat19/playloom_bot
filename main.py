# curl -X POST "https://api.telegram.org/bot8467061785:AAGPIz5pcNQRNfZnVH5iRTt2T2fENPmOyPs/setWebhook" -d "url=https://playloom-bot-19.onrender.com/webhook/8467061785:AAGPIz5pcNQRNfZnVH5iRTt2T2fENPmOyPs"

from flask import Flask, request
import requests
import os
from keep_alive import keep_alive

app = Flask(__name__)

TOKEN = '8467061785:AAGPIz5pcNQRNfZnVH5iRTt2T2fENPmOyPs'
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

@app.route('/')
def home():
    return "Bot is running!"

@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"Received update: {data}")

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        reply = f"You said: {text}"
        payload = {
            "chat_id": chat_id,
            "text": reply
        }

        try:
            requests.post(TELEGRAM_API_URL, json=payload)
        except Exception as e:
            print(f"Error sending message: {e}")

    return "ok", 200

if __name__ == '__main__':
    keep_alive(app)
    print("Keep-alive server started. Waiting for Telegram updates...")
    while True:
        pass

