import os
import requests
import logging
from flask import Flask, request
from keep_alive import keep_alive  # Ensure keep_alive.py is present

# Load environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_CHAT_ID = os.getenv("ALLOWED_CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Logging setup
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Validate config
if not BOT_TOKEN or not ALLOWED_CHAT_ID:
    logger.error("Missing BOT_TOKEN or ALLOWED_CHAT_ID.")
    exit(1)

# Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ PlayLoom Bot is alive."

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
        send_message(chat_id, "🎬 Welcome to PlayLoom!\nSend or forward a video to get a Play button.")
        return "ok", 200

    # Handle video message
    if "video" in message:
        try:
            # Forward to private channel
            forward_payload = {
                "chat_id": ALLOWED_CHAT_ID,
                "from_chat_id": chat_id,
                "message_id": message_id
            }
            response = requests.post(f"{TELEGRAM_API_URL}/forwardMessage", json=forward_payload)
            logger.debug(f"Forward response: {response.json()}")

            send_message(chat_id, "📤 Uploading to PlayLoom Stream...\nYou'll get your Play button shortly.")
        except Exception as e:
            logger.error(f"Error forwarding video: {e}")
            send_message(chat_id, "❌ Error uploading your video. Try again.")
        return "ok", 200

    # Fallback
    send_message(chat_id, "👋 Send or forward a video to get started.")
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
    webhook_url = f"https://playloom-bot-v2.onrender.com/webhook/{BOT_TOKEN}"
    response = requests.post(f"{TELEGRAM_API_URL}/setWebhook", json={"url": webhook_url})
    logger.info(f"Webhook set: {response.json()}")

    keep_alive(app)
    logger.info("Bot is running and waiting for Telegram updates.")
    while True:
        pass
