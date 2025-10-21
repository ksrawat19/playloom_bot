# PlayLoom/__init__.py

import os
os.environ["PYROGRAM_DISABLE_SYNC"] = "1"

from pyrogram import Client

import time

StartTime = time.time()
__version__ = "1.9.5"
