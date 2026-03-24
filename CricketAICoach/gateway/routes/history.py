from fastapi import APIRouter, Query

from db.history_store import list_history

router = APIRouter(tags=["History"])


@router.get("/history/player/{player_id}")
def get_player_history(player_id: int, phase: str | None = Query(default=None), limit: int = Query(default=20, ge=1, le=200)):
    return {
        "player_id": player_id,
        "phase": phase,
        "limit": limit,
        "items": list_history(player_id=player_id, phase=phase, limit=limit),
    }
