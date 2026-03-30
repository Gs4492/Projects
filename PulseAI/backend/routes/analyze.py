from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.engine.safety_engine import evaluate_health
from backend.schemas.request_response import AnalyzeRequest, AnalyzeResponse
from backend.services.assistant_service import build_assistant_message, build_guidance_sections
from backend.services.daily_memory_service import get_daily_memory, merge_with_daily_memory
from backend.services.health_parser import parse_health_input
from backend.services.intake_service import build_follow_up_questions, build_incomplete_response
from backend.services.knowledge_service import retrieve_health_context
from backend.services.log_service import create_log


router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_health(request: AnalyzeRequest, db: Session = Depends(get_db)):
    parsed = await parse_health_input(request.text)
    daily_memory = get_daily_memory(db)
    enriched = merge_with_daily_memory(parsed, daily_memory)
    follow_up_questions = build_follow_up_questions(enriched, daily_memory)

    if follow_up_questions:
        response = build_incomplete_response(enriched, follow_up_questions, daily_memory)
        response.guidance = build_guidance_sections(response)
        return response

    response = evaluate_health(enriched, daily_memory)
    response.knowledge = retrieve_health_context(enriched, response.risk)
    response.guidance = build_guidance_sections(response)
    response.assistant_message = await build_assistant_message(input_text=request.text, response=response)
    create_log(db, request.text, response)
    return response
