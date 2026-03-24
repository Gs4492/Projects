from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.history_store import init_history_db
from routes.history import router as history_router
from routes.phase1 import router as phase1_router
from routes.phase2 import router as phase2_router
from routes.phase3 import router as phase3_router
from routes.video import router as video_router

app = FastAPI(title="Gateway Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_history_db()


@app.get("/health")
def health():
    return {"service": "gateway", "status": "ok"}


app.include_router(phase1_router)
app.include_router(phase2_router)
app.include_router(phase3_router)
app.include_router(video_router)
app.include_router(history_router)
