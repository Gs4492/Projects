from fastapi import APIRouter, Query

from services.delivery_client import fetch_deliveries
from services.batting_analysis import analyze_batting
from schemas.analytics import BattingAnalytics

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/batting/{player_id}", response_model=BattingAnalytics)
def batting_analytics(player_id: int, last_matches: int = Query(default=5, ge=1, le=50)):
    deliveries = fetch_deliveries(player_id, last_matches)
    analytics = analyze_batting(deliveries)
    return analytics
