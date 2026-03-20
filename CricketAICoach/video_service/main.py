from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.video import router as video_router

app = FastAPI(title="Video Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"service": "video_service", "status": "ok"}


app.include_router(video_router)
