from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.batting import router as batting_router
from routes.bowling import router as bowling_router

app = FastAPI(title="Analytics Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"service": "analytics_service", "status": "ok"}


app.include_router(batting_router)
app.include_router(bowling_router)
