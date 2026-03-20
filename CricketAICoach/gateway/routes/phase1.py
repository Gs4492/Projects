from fastapi import APIRouter, HTTPException, Query
import httpx

from services.service_clients import get_player, get_player_deliveries

router = APIRouter(tags=["Phase1"])


@router.get("/phase1/player/{player_id}/deliveries")
async def phase1_player_deliveries(player_id: int, last_matches: int = Query(default=5, ge=1, le=50)):
    try:
        player = await get_player(player_id)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = exc.response.text
        raise HTTPException(status_code=status, detail=f"player_service error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"player_service unavailable: {exc}") from exc

    try:
        deliveries = await get_player_deliveries(player_id, last_matches)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        detail = exc.response.text
        raise HTTPException(status_code=status, detail=f"match_service error: {detail}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"match_service unavailable: {exc}") from exc

    return {
        "player": player,
        "last_matches": last_matches,
        "deliveries_count": len(deliveries),
        "deliveries": deliveries,
    }
