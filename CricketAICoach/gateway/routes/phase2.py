from fastapi import APIRouter, HTTPException, Query
import httpx

from db.history_store import save_history
from services.service_clients import get_player, get_batting_analytics, get_bowling_analytics

router = APIRouter(tags=["Phase2"])


@router.get("/phase2/player/{player_id}/batting")
async def phase2_batting_analytics(player_id: int, last_matches: int = Query(default=5, ge=1, le=50)):
    try:
        player = await get_player(player_id)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = exc.response.text
        raise HTTPException(status_code=status, detail=f"player_service error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"player_service unavailable: {exc}") from exc

    try:
        analytics = await get_batting_analytics(player_id, last_matches)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = exc.response.text
        raise HTTPException(status_code=status, detail=f"analytics_service error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"analytics_service unavailable: {exc}") from exc

    response = {
        "role": "batting",
        "player": player,
        "last_matches": last_matches,
        "analytics": analytics,
    }
    save_history(player_id=player_id, phase="phase2_batting", last_matches=last_matches, payload=response)
    return response


@router.get("/phase2/player/{player_id}/bowling")
async def phase2_bowling_analytics(player_id: int, last_matches: int = Query(default=5, ge=1, le=50)):
    try:
        player = await get_player(player_id)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = exc.response.text
        raise HTTPException(status_code=status, detail=f"player_service error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"player_service unavailable: {exc}") from exc

    try:
        analytics = await get_bowling_analytics(player_id, last_matches)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = exc.response.text
        raise HTTPException(status_code=status, detail=f"analytics_service error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"analytics_service unavailable: {exc}") from exc

    response = {
        "role": "bowling",
        "player": player,
        "last_matches": last_matches,
        "analytics": analytics,
    }
    save_history(player_id=player_id, phase="phase2_bowling", last_matches=last_matches, payload=response)
    return response
