from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.interpret import router as ai_router

app = FastAPI(title="AI Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"service": "ai_service", "status": "ok"}


app.include_router(ai_router)
