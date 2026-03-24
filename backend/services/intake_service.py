from backend.schemas.request_response import AnalyzeResponse, DailyMemory, ParsedHealthData


SEVERE_SYMPTOMS = {"chest pain", "chest discomfort", "shortness of breath", "breathless", "faint", "confused"}


def build_follow_up_questions(parsed: ParsedHealthData, memory: DailyMemory | None = None) -> list[str]:
    memory = memory or DailyMemory()
    questions: list[str] = []
    morning_sugar = parsed.morning_sugar_level if parsed.morning_sugar_level is not None else memory.morning_sugar_level
    water_ml = parsed.water_ml if parsed.water_ml is not None else memory.water_ml_today
    has_symptoms = bool(parsed.symptoms)
    elevated_bp = (parsed.bp.systolic is not None and parsed.bp.systolic >= 140) or (parsed.bp.diastolic is not None and parsed.bp.diastolic >= 90)
    sugar_concern = (parsed.sugar_level is not None and (parsed.sugar_level < 70 or parsed.sugar_level >= 180)) or (morning_sugar is not None and morning_sugar >= 180)

    if morning_sugar is None and parsed.sugar_level is None:
        questions.append("What was the sugar level in the morning today?")

    if parsed.bp.systolic is None or parsed.bp.diastolic is None:
        questions.append("What is the blood pressure right now?")

    if (parsed.alcohol.alcohol_units > 0 or elevated_bp) and water_ml is None:
        questions.append("How much water have you had today in ml or glasses?")

    if parsed.alcohol.alcohol_units > 0 and not parsed.food.items:
        questions.append("Did you eat anything with the drink, especially salty snacks or fried food?")

    if (parsed.alcohol.alcohol_units > 0 or elevated_bp or sugar_concern) and not has_symptoms:
        questions.append("How are you feeling right now? You can say normal, fine, okay, or mention symptoms like dizzy, weak, chest discomfort, or sweating.")

    if parsed.food.food_type == "carb-heavy" and parsed.sugar_level is None and morning_sugar is None:
        questions.append("Do you know your current sugar or morning sugar after eating these carbs?")

    return questions[:4]


def build_incomplete_response(parsed: ParsedHealthData, questions: list[str], memory: DailyMemory | None = None) -> AnalyzeResponse:
    memory = memory or DailyMemory()
    summary_bits: list[str] = []
    if parsed.alcohol.alcohol_units:
        summary_bits.append(f"Alcohol about {parsed.alcohol.alcohol_units:.1f} units")
    if parsed.food.items:
        summary_bits.append(f"Food: {', '.join(parsed.food.items[:3])}")
    if parsed.bp.systolic and parsed.bp.diastolic:
        summary_bits.append(f"BP {parsed.bp.systolic}/{parsed.bp.diastolic}")
    if parsed.sugar_level is not None:
        summary_bits.append(f"Sugar {parsed.sugar_level}")

    severe = any(symptom in SEVERE_SYMPTOMS for symptom in parsed.symptoms)
    short_summary = ", ".join(summary_bits) if summary_bits else "I need a little more information before giving proper guidance."
    reasons = ["The app needs a little more context before giving tailored food and drink guidance."]
    actions = ["Answer the follow-up questions below so the advice can be more specific."]
    assistant_message = "I can give better guidance if you answer a few quick questions first."

    if severe:
        reasons = ["A serious symptom was reported, so this should not be treated like a low-risk situation."]
        actions = ["Do not wait for the app alone. Get urgent medical help if the symptom is active or worsening."]
        assistant_message = "A serious symptom was mentioned. Please treat this more urgently and seek medical help if it is still happening."

    return AnalyzeResponse(
        status="needs_more_info",
        risk="PENDING",
        reasons=reasons,
        actions=actions,
        summary=short_summary,
        assistant_message=assistant_message,
        follow_up_questions=questions,
        knowledge=[],
        parsed_data=parsed,
        daily_memory=memory,
    )
