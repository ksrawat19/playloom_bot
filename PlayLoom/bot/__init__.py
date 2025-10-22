# PlayLoom/bot/__init__.py

from PlayLoom.vars import Var

StreamBot_Config = {
    "name": "Web Streamer",
    "api_id": Var.API_ID,
    "api_hash": Var.API_HASH,
    "bot_token": Var.BOT_TOKEN,
    "sleep_threshold": Var.SLEEP_THRESHOLD,
    "workers": Var.WORKERS
}

StreamBot = None

multi_clients = {}
work_loads = {}