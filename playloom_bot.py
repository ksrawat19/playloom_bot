import os
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

BOT_TOKEN='8467061785:AAGPIz5pcNQRNfZnVH5iRTt2T2fENPmOyPs'
PORT = int(os.getenv('PORT', 10000))

async def reply_rawat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I am Rawat's bot.")

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Rawat bot is running')

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

async def run_bot():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, reply_rawat))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()

def main():
    loop = asyncio.get_event_loop()
    server = HTTPServer(('0.0.0.0', PORT), DummyHandler)
    loop.run_in_executor(None, server.serve_forever)
    loop.run_until_complete(run_bot())

if __name__ == '__main__':
    main()
