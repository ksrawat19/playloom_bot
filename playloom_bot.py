import os
import json
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import hashlib
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ALLOWED_CHAT_ID = os.getenv('ALLOWED_CHAT_ID')
PLAYER_URL = os.getenv('PLAYER_URL', 'https://your-player.vercel.app/video')
PROXY_URL = os.getenv('PROXY_URL', 'https://your-proxy.onrender.com/proxy')
SECRET_KEY = os.getenv('SECRET_KEY', 'mysecret123')
CACHE_FILE = 'file_cache.json'

def load_cache():
    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Forward a video from my private channel to stream!')

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message.forward_from_chat or str(message.forward_from_chat.id) != ALLOWED_CHAT_ID:
        await message.reply_text('Please forward from my private channel.')
        return
    if not message.video:
        await message.reply_text('Forward a video.')
        return
    file_id = message.video.file_id
    cache = load_cache()
    if file_id in cache and cache[file_id]['expires'] > time.time():
        telegram_url = cache[file_id]['url']
    else:
        try:
            file = await context.bot.get_file(file_id)
            telegram_url = file.file_path
            cache[file_id] = {'url': telegram_url, 'expires': time.time() + 24*3600}
            save_cache(cache)
        except Exception as e:
            logger.error(f"Error fetching file: {e}")
            await message.reply_text('Error generating link. Try again.')
            return
    token = hashlib.md5(f'{file_id}{SECRET_KEY}'.encode()).hexdigest()
    proxy_url = f'{PROXY_URL}?url={telegram_url}&token={token}'
    player_link = f'{PLAYER_URL}?url={proxy_url}&token={token}'
    keyboard = [[InlineKeyboardButton("Play", url=player_link)]]
    await message.reply_text('Ready to watch?', reply_markup=InlineKeyboardMarkup(keyboard))

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.VIDEO & filters.FORWARDED, handle_video))
    app.run_polling()

if __name__ == '__main__':
    main()