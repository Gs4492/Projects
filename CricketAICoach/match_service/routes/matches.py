from fastapi import APIRouter, Query, HTTPException
from schemas.match import MatchWithDeliveries, MatchCreate, BulkDeliveriesCreate
from services.match_service import create_match, add_deliveries, get_last_matches_deliveries

router = APIRouter(tags=["Matches"])


@router.post("/matches")
def create_match_only(payload: MatchCreate):
    match_id = create_match(payload)
    return {"message": "Match stored", "match_id": match_id}


@router.post("/matches/deliveries/bulk")
def upload_deliveries_bulk(payload: BulkDeliveriesCreate):
    try:
        result = add_deliveries(payload.match_id, payload.deliveries)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return {
        "message": "Deliveries processed",
        "match_id": payload.match_id,
        "deliveries_count": len(payload.deliveries),
        "inserted": result["inserted"],
        "ignored_duplicates": result["ignored"],
    }


@router.post("/matches/with-deliveries")
def create_match_with_data(payload: MatchWithDeliveries):
    match_id = create_match(payload.match)
    result = add_deliveries(match_id, payload.deliveries)
    return {
        "message": "Match and deliveries stored",
        "match_id": match_id,
        "deliveries_count": len(payload.deliveries),
        "inserted": result["inserted"],
        "ignored_duplicates": result["ignored"],
    }


@router.get("/players/{player_id}/deliveries")
def get_player_deliveries(player_id: int, last_matches: int = Query(default=5, ge=1, le=50)):
    rows = get_last_matches_deliveries(player_id, last_matches)
    return [dict(row) for row in rows]
