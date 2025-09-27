from telethon import TelegramClient

api_id = 27937013
api_hash = '264ad097f0d8f8eff60b9e8eec0751df'
session_name = 'playloom_session'

client = TelegramClient(session_name, api_id, api_hash)
client.start()
