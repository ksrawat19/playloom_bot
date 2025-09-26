import os
import hashlib
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ALLOWED_CHAT_ID = os.getenv('ALLOWED_CHAT_ID')
PLAYER_URL = os.getenv('PLAYER_URL', 'https://playloom.vercel.app')
SECRET_KEY = os.getenv('SECRET_KEY', 'mysecret123')

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
        token = hashlib.md5(f'{file_id}{SECRET_KEY}'.encode()).hexdigest()
        player_link = f'{PLAYER_URL}?url={telegram_url}&token={token}'
        keyboard = [[InlineKeyboardButton("Play", url=player_link)]]
        await message.reply_text('Ready to watch?', reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        logger.error(f"Error fetching file: {e}")
        await message.reply_text('Error generating link. Try again.')

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.VIDEO & filters.FORWARDED, handle_video))
    app.run_polling()

if __name__ == '__main__':
    main()