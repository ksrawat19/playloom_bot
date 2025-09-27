from fastapi import APIRouter, Response
from telethon_client import client

router = APIRouter()

@router.get("/download/{file_id}")
async def download_video(file_id: str):
    file = await client.download_media(file_id, file=bytes)
    return Response(content=file, media_type="application/octet-stream", headers={
        "Content-Disposition": f"attachment; filename={file_id}.mp4"
    })
