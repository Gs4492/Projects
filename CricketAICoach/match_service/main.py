from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.matches import router as match_router
from db.models import create_tables

app = FastAPI(title="Match Service")

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
    return {"service": "match_service", "status": "ok"}


app.include_router(match_router)
