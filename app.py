import os
import hashlib
import requests
import logging
from flask import Flask, request
from keep_alive import keep_alive  # Make sure keep_alive.py is present

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_CHAT_ID = os.getenv("ALLOWED_CHAT_ID")
PLAYER_URL = os.getenv("PLAYER_URL", "https://playloom.vercel.app")
SECRET_KEY = os.getenv("SECRET_KEY", "mysecret123")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Setup logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Validate config
if not BOT_TOKEN or not ALLOWED_CHAT_ID:
    logger.error("Missing BOT_TOKEN or ALLOWED_CHAT_ID in environment variables.")
    exit(1)

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    logger.info("Health check received.")
    return "✅ PlayLoom Bot is running."

@app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
def webhook():
    data = request.get_json()
    logger.debug(f"📩 Incoming update: {data}")

    message = data.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")

    if not chat_id or not message_id:
        logger.warning("Missing chat_id or message_id.")
        return "ignored", 200

    # Handle /start
    if message.get("text") == "/start":
        logger.info(f"Received /start from {chat_id}")
        send_message(chat_id, "🎬 Welcome to PlayLoom!\nForward a video from my private channel to get a Play button.")
        return "ok", 200

    # Handle forwarded video
    if "forward_from_chat" in message and "video" in message:
        forward_chat_id = str(message["forward_from_chat"]["id"])
        logger.info(f"Forwarded from chat {forward_chat_id}")

        if forward_chat_id != ALLOWED_CHAT_ID:
            logger.warning(f"Invalid source: {forward_chat_id}")
            send_message(chat_id, "⚠️ Please forward a video from my private channel.")
            return "ok", 200

        file_id = message["video"]["file_id"]
        try:
            file_info = requests.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}").json()
            if not file_info.get("ok"):
                logger.error(f"Failed to fetch file info: {file_info}")
                send_message(chat_id, "❌ Error fetching video. Try again.")
                return "ok", 200

            file_path = file_info["result"]["file_path"]
            telegram_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            token = hashlib.md5(f"{telegram_url}{SECRET_KEY}".encode()).hexdigest()
            player_link = f"{PLAYER_URL}?url={telegram_url}&token={token}"

            keyboard = {
                "inline_keyboard": [[{"text": "▶️ Play", "url": player_link}]]
            }
            send_message(chat_id, "🎥 Your video is ready:", reply_markup=keyboard)
        except Exception as e:
            logger.error(f"Error generating player link: {e}")
            send_message(chat_id, "❌ Error generating link. Try again.")
        return "ok", 200

    # Fallback response
    logger.info(f"Unhandled message from {chat_id}")
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
        logger.debug(f"Message sent: {response.json()}")
    except Exception as e:
        logger.error(f"Error sending message: {e}")

# Startup
if __name__ == '__main__':
    # Set webhook automatically
    webhook_url = f"https://playloom-bot-v2.onrender.com/webhook/{BOT_TOKEN}"
    response = requests.post(f"{TELEGRAM_API_URL}/setWebhook", json={"url": webhook_url})
    logger.info(f"Webhook set: {response.json()}")

    # Start Flask keep-alive server
    keep_alive(app)
    logger.info("Bot is running and waiting for Telegram updates.")
    while True:
        pass
