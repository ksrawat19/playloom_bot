# PlayLoom/utils/file_properties.py

from datetime import datetime as dt
from typing import Any, Optional

# --- REMOVED TOP-LEVEL IMPORTS:
# from pyrogram.client import Client
# from pyrogram.file_id import FileId
# from pyrogram.types import Message

from PlayLoom.server.exceptions import FileNotFound
from PlayLoom.utils.handler import handle_flood_wait
from PlayLoom.utils.logger import logger


def get_media(message) -> Optional[Any]:
    # --- FIX: Import Pyrogram classes here (Message is only used for annotation, but since other utils use it, we'll maintain the call signature) ---
    for attr in ("audio", "document", "photo", "sticker", "animation", "video", "voice", "video_note"):
        media = getattr(message, attr, None)
        if media:
            if hasattr(media, 'thumbs') and media.thumbs:
                pass
            return media
    return None


def get_uniqid(message) -> Optional[str]:
    # --- FIX: Import Pyrogram classes here ---
    # from pyrogram.types import Message
    
    media = get_media(message)
    return getattr(media, 'file_unique_id', None)


def get_hash(media_msg) -> str:
    # --- FIX: Import Pyrogram classes here ---
    # from pyrogram.types import Message
    
    uniq_id = get_uniqid(media_msg)
    return uniq_id[:6] if uniq_id else ''


def get_fsize(message) -> int:
    # --- FIX: Import Pyrogram classes here ---
    # from pyrogram.types import Message
    
    media = get_media(message)
    return getattr(media, 'file_size', 0) if media else 0


def parse_fid(message):
    # --- FIX: Import Pyrogram classes here ---
    from pyrogram.file_id import FileId
    from pyrogram.types import Message

    media = get_media(message)
    if media and hasattr(media, 'file_id'):
        try:
            return FileId.decode(media.file_id)
        except Exception:
            return None
    return None


def get_fname(msg) -> str:
    # --- FIX: Import Pyrogram classes here ---
    # from pyrogram.types import Message

    media = get_media(msg)
    fname = None
    
    if media:
        fname = getattr(media, 'file_name', None)
    
    if not fname:
        ext = "bin"
        if media and hasattr(media, '_file_type'):
            file_type = media._file_type
            if file_type == "photo":
                ext = "jpg"
            elif file_type == "audio":
                ext = "mp3"
            elif file_type == "voice":
                ext = "ogg"
            elif file_type in ["video", "animation", "video_note"]:
                ext = "mp4"
            elif file_type == "sticker":
                ext = "webp"
            else:
                ext = "bin"
        timestamp = dt.now().strftime("%Y%m%d%H%M%S")
        fname = f"PlayLoom File To Link_{timestamp}.{ext}"
    
    return fname


async def get_fids(client, chat_id: int, message_id: int):
    # --- FIX: Import Pyrogram classes here ---
    from pyrogram.client import Client
    from pyrogram.file_id import FileId
    from pyrogram.types import Message

    try:
        msg: Message = await handle_flood_wait(client.get_messages, chat_id, message_id)
        
        if not msg or getattr(msg, 'empty', False):
            raise FileNotFound("Message not found")
        
        media = get_media(msg)
        if media:
            if not hasattr(media, 'file_id') or not hasattr(media, 'file_unique_id'):
                raise FileNotFound("Media metadata incomplete")
            return FileId.decode(media.file_id)
        
        raise FileNotFound("No media in message")
        
    except Exception as e:
        logger.error(f"Error in get_fids: {e}", exc_info=True)
        raise FileNotFound(str(e))