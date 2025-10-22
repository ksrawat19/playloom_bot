# PlayLoom/utils/handler.py

import asyncio
from typing import Callable

# --- REMOVED: from pyrogram.errors import FloodWait, MessageNotModified (This was the problem) ---

from PlayLoom.utils.logger import logger


async def handle_flood_wait(func: Callable, *args, **kwargs):
    # --- FIX: Import Pyrogram errors here, inside the function ---
    from pyrogram.errors import FloodWait, MessageNotModified
    # -----------------------------------------------------------
    
    retries = kwargs.pop('retries', 3)
    delay = kwargs.pop('delay', 3)

    for i in range(retries):
        try:
            return await func(*args, **kwargs)
        except FloodWait as e:
            wait_time = e.value
            logger.debug(f"FloodWait encountered in '{func.__name__}'. Waiting for {wait_time}s. Retry {i + 1}/{retries}.")
            await asyncio.sleep(wait_time)
        except MessageNotModified:
            logger.debug(f"MessageNotModified in '{func.__name__}' - not retrying as content hasn't changed.")
            # Note: This 'raise' statement handles the case where the message content is the same, 
            # and prevents further retries on this specific Pyrogram error.
            raise 
        except Exception:
            logger.error(f"An exception occurred in '{func.__name__}' on retry {i + 1}/{retries}", exc_info=True)
            if i < retries - 1:
                await asyncio.sleep(delay)
            else:
                raise
    return None