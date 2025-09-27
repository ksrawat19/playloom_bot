from fastapi import FastAPI
from stream import router as stream_router
from download import router as download_router

app = FastAPI()

app.include_router(stream_router)
app.include_router(download_router)

@app.get("/")
def home():
    return {"status": "PlayLoom Stream is alive"}
