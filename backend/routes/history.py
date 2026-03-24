import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db.models import HealthLog


router = APIRouter(prefix="/history", tags=["history"])


@router.get("")
def get_history(db: Session = Depends(get_db)):
    logs = db.query(HealthLog).order_by(HealthLog.created_at.desc()).limit(20).all()
    return [
        {
            "id": log.id,
            "created_at": log.created_at,
            "input_text": log.input_text,
            "risk": log.risk_level,
            "reasons": json.loads(log.reasons_json),
            "actions": json.loads(log.actions_json),
        }
        for log in logs
    ]
