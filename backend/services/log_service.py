import json

from sqlalchemy.orm import Session

from backend.db.models import HealthLog
from backend.schemas.request_response import AnalyzeResponse


def create_log(db: Session, input_text: str, response: AnalyzeResponse) -> HealthLog:
    parsed = response.parsed_data
    log = HealthLog(
        input_text=input_text,
        bp_systolic=parsed.bp.systolic,
        bp_diastolic=parsed.bp.diastolic,
        sugar_level=parsed.sugar_level,
        alcohol_units=parsed.alcohol.alcohol_units,
        drink_type=parsed.alcohol.drink_type,
        drink_quantity=parsed.alcohol.quantity,
        drink_size_label=parsed.alcohol.size_label,
        drink_volume_ml=parsed.alcohol.total_volume_ml,
        salt_level=parsed.food.salt_level,
        food_type=parsed.food.food_type,
        water_ml=parsed.water_ml,
        parsed_json=parsed.model_dump_json(),
        risk_level=response.risk,
        reasons_json=json.dumps(response.reasons),
        actions_json=json.dumps(response.actions),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
