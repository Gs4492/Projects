from fastapi import APIRouter, Query

from schemas.ai_response import AIResponse
from services.analytics_client import fetch_batting_analytics, fetch_bowling_analytics
from services.coaching_logic import generate_coaching_advice

router = APIRouter(prefix="/ai", tags=["AI"])


@router.get("/batting/{player_id}", response_model=AIResponse)
def interpret_batting(player_id: int, last_matches: int = Query(default=5, ge=1, le=50)):
    analytics = fetch_batting_analytics(player_id, last_matches)
    advice = generate_coaching_advice(analytics, role="batting")
    return advice


@router.get("/bowling/{player_id}", response_model=AIResponse)
def interpret_bowling(player_id: int, last_matches: int = Query(default=5, ge=1, le=50)):
    analytics = fetch_bowling_analytics(player_id, last_matches)
    advice = generate_coaching_advice(analytics, role="bowling")
    return advice
