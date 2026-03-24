from fastapi import APIRouter, Query

from services.delivery_client import fetch_deliveries
from services.bowling_analysis import analyze_bowling
from schemas.analytics import BattingAnalytics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/bowling/{player_id}", response_model=BattingAnalytics)
def bowling_analytics(player_id: int, last_matches: int = Query(default=5, ge=1, le=50)):
    deliveries = fetch_deliveries(player_id, last_matches)
    analytics = analyze_bowling(deliveries)
    return analytics
