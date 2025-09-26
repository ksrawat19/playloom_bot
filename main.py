# curl -X POST "https://api.telegram.org/bot8467061785:AAGPIz5pcNQRNfZnVH5iRTt2T2fENPmOyPs/setWebhook" -d "url=https://playloom-bot-v2.onrender.com/webhook/8467061785:AAGPIz5pcNQRNfZnVH5iRTt2T2fENPmOyPs"

import os
import hashlib
import requests
from flask import Flask, request
from keep_alive import keep_alive
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TOKEN = os.getenv('BOT_TOKEN')
ALLOWED_CHAT_ID = os.getenv('ALLOWED_CHAT_ID')
PLAYER_URL = os.getenv('PLAYER_URL', 'https://playloom.vercel.app')
SECRET_KEY = os.getenv('SECRET_KEY', 'mysecret123')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

if not TOKEN or not ALLOWED_CHAT_ID:
    logger.error("Missing BOT_TOKEN or ALLOWED_CHAT_ID in environment variables.")
    exit(1)

@app.route('/')
def home():
    logger.info("Received request to /, responding with 'Bot is running'")
    return "Bot is running!"

@app.route(f'/webhook/{TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    logger.debug(f"Received update: {data}")

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        message = data["message"]

        if message.get("text") == "/start":
            logger.debug(f"Received /start from chat {chat_id}")
            send_message(chat_id, "🎬 Welcome to PlayLoomBot!\nForward a video from my private channel to get a Play button.")
            return "ok", 200

        if "forward_from_chat" in message and "video" in message:
            forward_chat_id = str(message["forward_from_chat"]["id"])
            logger.debug(f"Forwarded message from chat {forward_chat_id}")
            if forward_chat_id != ALLOWED_CHAT_ID:
                logger.debug(f"Invalid chat ID: {forward_chat_id}, expected {ALLOWED_CHAT_ID}")
                send_message(chat_id, "⚠️ Please forward a video from my private channel.")
                return "ok", 200

            file_id = message["video"]["file_id"]
            try:
                file_response = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}").json()
                if not file_response.get("ok"):
                    logger.error(f"Failed to get file: {file_response}")
                    send_message(chat_id, "❌ Error fetching video. Try again.")
                    return "ok", 200

                telegram_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_response['result']['file_path']}"
                token = hashlib.md5(f'{telegram_url}{SECRET_KEY}'.encode()).hexdigest()
                player_link = f'{PLAYER_URL}?url={telegram_url}&token={token}'

                keyboard = {
                    "inline_keyboard": [[{"text": "▶️ Play", "url": player_link}]]
                }
                send_message(chat_id, "🎥 Your video is ready:", reply_markup=keyboard)
            except Exception as e:
                logger.error(f"Error processing video: {e}")
                send_message(chat_id, "❌ Error generating link. Try again.")
            return "ok", 200

        logger.debug(f"Received message from chat {chat_id}: {message.get('text', 'no text')}")
        send_message(chat_id, "👋 Hello! Use /start or forward a video from my private channel.")

    return "ok", 200

def send_message(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        response = requests.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)
        logger.debug(f"Sent message response: {response.json()}")
    except Exception as e:
        logger.error(f"Error sending message: {e}")

if __name__ == '__main__':
    webhook_url = f"https://playloom-bot-v2.onrender.com/webhook/{TOKEN}"
    response = requests.post(f"{TELEGRAM_API_URL}/setWebhook", json={"url": webhook_url})
    logger.info(f"Set webhook response: {response.json()}")

    keep_alive(app)
    logger.info("Keep-alive server started. Waiting for Telegram updates...")
    while True:
        pass
