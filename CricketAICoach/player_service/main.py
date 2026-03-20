from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.players import router as player_router
from db.models import create_tables

app = FastAPI(title="Player Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()


@app.get("/health")
def health():
    return {"service": "player_service", "status": "ok"}


app.include_router(player_router)
