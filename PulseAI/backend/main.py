from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.db.database import Base, engine
from backend.routes.analyze import router as analyze_router
from backend.routes.history import router as history_router


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(history_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.app_name}
