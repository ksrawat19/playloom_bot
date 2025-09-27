from fastapi import APIRouter, Response
from telethon_client import client

router = APIRouter()

@router.get("/stream/{file_id}")
async def stream_video(file_id: str):
    file = await client.download_media(file_id, file=bytes)
    return Response(content=file, media_type="video/mp4", headers={
        "Accept-Ranges": "bytes"
    })
