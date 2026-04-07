from __future__ import annotations

import asyncio

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.models import GoalRequest
from app.orchestrator import broadcaster, process_run
from app.store import store

app = FastAPI(title="AgentForge API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/runs")
async def create_run(payload: GoalRequest) -> dict:
    run = store.create_run(payload.goal)
    asyncio.create_task(process_run(run.id))
    return run.model_dump(mode="json")


@app.get("/runs/{run_id}")
async def get_run(run_id: str) -> dict:
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run.model_dump(mode="json")


@app.websocket("/ws/runs/{run_id}")
async def run_updates(websocket: WebSocket, run_id: str) -> None:
    await websocket.accept()
    broadcaster.register(run_id, websocket)
    run = store.get_run(run_id)
    if run:
        await websocket.send_json(
            {
                "type": "snapshot",
                "payload": run.model_dump(mode="json"),
            }
        )
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        broadcaster.unregister(run_id, websocket)
