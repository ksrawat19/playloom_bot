import os
import hashlib
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ALLOWED_CHAT_ID = os.getenv('ALLOWED_CHAT_ID')
PLAYER_URL = os.getenv('PLAYER_URL', 'https://playloom.vercel.app')
SECRET_KEY = os.getenv('SECRET_KEY', 'mysecret123')
PORT = int(os.getenv('PORT', 10000))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Forward a video from my private channel to get a Play button!')

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message.forward_from_chat or str(message.forward_from_chat.id) != ALLOWED_CHAT_ID:
        await message.reply_text('Please forward a video from my private channel.')
        return
    if not message.video:
        await message.reply_text('Please forward a video.')
        return
    file_id = message.video.file_id
    try:
        file = await context.bot.get_file(file_id)
        telegram_url = file.file_path
        token = hashlib.md5(f'{telegram_url}{SECRET_KEY}'.encode()).hexdigest()
        player_link = f'{PLAYER_URL}?url={telegram_url}&token={token}'
        keyboard = [[InlineKeyboardButton("Play", url=player_link)]]
        await message.reply_text('Ready to watch?', reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error fetching file: {e}")
        await message.reply_text('Error generating link. Try again.')

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is running')

async def run_bot():
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler('start', start))
        app.add_handler(MessageHandler(filters.VIDEO & filters.FORWARDED, handle_video))
        await app.initialize()
        await app.start()
        await app.updater.start_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Bot failed to start: {e}")
        raise

def main():
    loop = asyncio.get_event_loop()
    server = HTTPServer(('0.0.0.0', PORT), DummyHandler)
    loop.run_in_executor(None, server.serve_forever)
    loop.run_until_complete(run_bot())

if __name__ == '__main__':
    main()