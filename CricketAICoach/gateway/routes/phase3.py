from fastapi import APIRouter, HTTPException, Query
import httpx

from db.history_store import save_history
from services.service_clients import get_player, get_ai_coaching, get_ai_bowling_coaching

router = APIRouter(tags=["Phase3"])


@router.get("/phase3/player/{player_id}/coaching")
async def phase3_coaching(player_id: int, last_matches: int = Query(default=5, ge=1, le=50)):
    try:
        player = await get_player(player_id)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = exc.response.text
        raise HTTPException(status_code=status, detail=f"player_service error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"player_service unavailable: {exc}") from exc

    try:
        coaching = await get_ai_coaching(player_id, last_matches)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = exc.response.text
        raise HTTPException(status_code=status, detail=f"ai_service error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"ai_service unavailable: {exc}") from exc

    response = {
        "role": "batting",
        "player": player,
        "last_matches": last_matches,
        "coaching": coaching,
    }
    save_history(player_id=player_id, phase="phase3_batting", last_matches=last_matches, payload=response)
    return response


@router.get("/phase3/player/{player_id}/bowling/coaching")
async def phase3_bowling_coaching(player_id: int, last_matches: int = Query(default=5, ge=1, le=50)):
    try:
        player = await get_player(player_id)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = exc.response.text
        raise HTTPException(status_code=status, detail=f"player_service error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"player_service unavailable: {exc}") from exc

    try:
        coaching = await get_ai_bowling_coaching(player_id, last_matches)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = exc.response.text
        raise HTTPException(status_code=status, detail=f"ai_service error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"ai_service unavailable: {exc}") from exc

    response = {
        "role": "bowling",
        "player": player,
        "last_matches": last_matches,
        "coaching": coaching,
    }
    save_history(player_id=player_id, phase="phase3_bowling", last_matches=last_matches, payload=response)
    return response
