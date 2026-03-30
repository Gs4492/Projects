import json
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from backend.db.models import HealthLog
from backend.schemas.request_response import DailyMemory, HealthMetric, ParsedHealthData


def get_daily_memory(db: Session) -> DailyMemory:
    start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    logs = (
        db.query(HealthLog)
        .filter(HealthLog.created_at >= start_of_day, HealthLog.created_at < end_of_day)
        .order_by(HealthLog.created_at.asc(), HealthLog.id.asc())
        .all()
    )

    if not logs:
        return DailyMemory()

    alcohol_units_today = 0.0
    high_risk_entries_today = 0
    medium_risk_entries_today = 0
    salty_entries_today = 0
    water_ml_today: int | None = None
    morning_sugar_level: int | None = None
    last_sugar_level: int | None = None
    last_bp = HealthMetric()
    latest_symptoms: list[str] = []

    for log in logs:
        parsed = _load_parsed(log)
        alcohol_units_today += float(log.alcohol_units or parsed.alcohol.alcohol_units or 0)

        if log.risk_level == "HIGH":
            high_risk_entries_today += 1
        elif log.risk_level == "MEDIUM":
            medium_risk_entries_today += 1

        if parsed.food.salt_level == "high":
            salty_entries_today += 1

        if parsed.water_ml is not None:
            water_ml_today = max(water_ml_today or 0, parsed.water_ml)

        if parsed.morning_sugar_level is not None:
            morning_sugar_level = parsed.morning_sugar_level

        if parsed.sugar_level is not None:
            last_sugar_level = parsed.sugar_level

        if parsed.bp.systolic is not None and parsed.bp.diastolic is not None:
            last_bp = parsed.bp

        if parsed.symptoms and "normal" not in parsed.symptoms:
            latest_symptoms = parsed.symptoms

    alcohol_units_today = round(alcohol_units_today, 1)
    return DailyMemory(
        entries_today=len(logs),
        alcohol_units_today=alcohol_units_today,
        high_risk_entries_today=high_risk_entries_today,
        medium_risk_entries_today=medium_risk_entries_today,
        water_ml_today=water_ml_today,
        morning_sugar_level=morning_sugar_level,
        last_sugar_level=last_sugar_level,
        last_bp=last_bp,
        latest_symptoms=latest_symptoms,
        salty_entries_today=salty_entries_today,
        summary=_build_summary(
            entries_today=len(logs),
            alcohol_units_today=alcohol_units_today,
            high_risk_entries_today=high_risk_entries_today,
            water_ml_today=water_ml_today,
            morning_sugar_level=morning_sugar_level,
            last_bp=last_bp,
        ),
    )


def merge_with_daily_memory(parsed: ParsedHealthData, memory: DailyMemory) -> ParsedHealthData:
    payload = parsed.model_dump()

    if payload.get("morning_sugar_level") is None and memory.morning_sugar_level is not None:
        payload["morning_sugar_level"] = memory.morning_sugar_level

    if payload.get("water_ml") is None and memory.water_ml_today is not None:
        payload["water_ml"] = memory.water_ml_today

    return ParsedHealthData.model_validate(payload)


def _load_parsed(log: HealthLog) -> ParsedHealthData:
    try:
        return ParsedHealthData.model_validate_json(log.parsed_json)
    except Exception:
        try:
            return ParsedHealthData.model_validate(json.loads(log.parsed_json))
        except Exception:
            return ParsedHealthData()


def _build_summary(
    *,
    entries_today: int,
    alcohol_units_today: float,
    high_risk_entries_today: int,
    water_ml_today: int | None,
    morning_sugar_level: int | None,
    last_bp: HealthMetric,
) -> str:
    bits: list[str] = [f"{entries_today} entr{'y' if entries_today == 1 else 'ies'} logged today"]
    if alcohol_units_today > 0:
        bits.append(f"{alcohol_units_today:.1f} alcohol units so far")
    if water_ml_today is not None:
        bits.append(f"about {water_ml_today} ml water logged")
    if morning_sugar_level is not None:
        bits.append(f"morning sugar {morning_sugar_level}")
    if last_bp.systolic is not None and last_bp.diastolic is not None:
        bits.append(f"last BP {last_bp.systolic}/{last_bp.diastolic}")
    if high_risk_entries_today > 0:
        bits.append(f"{high_risk_entries_today} high-risk warning already today")
    return "Today so far: " + ", ".join(bits) + "."
