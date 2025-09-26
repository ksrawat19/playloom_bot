import os
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

BOT_TOKEN='8467061785:AAGPIz5pcNQRNfZnVH5iRTt2T2fENPmOyPs'

async def reply_rawat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I am Rawat's bot.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, reply_rawat))
    app.run_polling()

if __name__ == '__main__':
    main()
