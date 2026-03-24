from backend.schemas.request_response import AnalyzeResponse, DailyMemory, ParsedHealthData


class EvaluationResult(AnalyzeResponse):
    pass


def evaluate_health(parsed: ParsedHealthData, daily_memory: DailyMemory | None = None) -> EvaluationResult:
    daily_memory = daily_memory or DailyMemory()
    reasons: list[str] = []
    actions: list[str] = []
    risk_score = 0

    systolic = parsed.bp.systolic
    diastolic = parsed.bp.diastolic
    sugar = parsed.sugar_level
    morning_sugar = parsed.morning_sugar_level
    alcohol_units = parsed.alcohol.alcohol_units or 0
    salt_level = parsed.food.salt_level
    water_ml = parsed.water_ml or 0
    food_type = parsed.food.food_type
    drink_type = parsed.alcohol.drink_type
    symptoms = parsed.symptoms
    total_alcohol_today = round((daily_memory.alcohol_units_today or 0) + alcohol_units, 1)

    if systolic and diastolic:
        if systolic >= 180 or diastolic >= 110:
            risk_score += 6
            reasons.append(f"Blood pressure is dangerously high at {systolic}/{diastolic}.")
            actions.append("Stop alcohol immediately and get urgent medical help if symptoms are present.")
            actions.append("Sit down quietly and recheck blood pressure within 15 minutes.")
        elif systolic >= 160 or diastolic >= 100:
            risk_score += 4
            reasons.append(f"Blood pressure is very high at {systolic}/{diastolic}.")
            actions.append("Do not drink more alcohol today.")
            actions.append("Recheck blood pressure within 30 to 60 minutes.")
        elif systolic >= 140 or diastolic >= 90:
            risk_score += 2
            reasons.append(f"Blood pressure is elevated at {systolic}/{diastolic}.")
            actions.append(_bp_elevated_action(alcohol_units))
        else:
            reasons.append(f"Blood pressure is currently in a lower-risk range at {systolic}/{diastolic}.")

    if morning_sugar is not None:
        if morning_sugar >= 180:
            risk_score += 2
            reasons.append(f"Morning sugar was already high at {morning_sugar}.")
        elif morning_sugar < 70:
            risk_score += 2
            reasons.append(f"Morning sugar started low at {morning_sugar}.")

    if sugar is not None:
        if sugar < 70:
            risk_score += 5
            reasons.append(f"Blood sugar is low at {sugar}.")
            actions.append("Take a fast sugar source now and recheck sugar in 15 minutes.")
            actions.append("Take a small snack after that so the sugar does not drop again.")
        elif sugar >= 250:
            risk_score += 4
            reasons.append(f"Blood sugar is very high at {sugar}.")
            actions.append("Avoid sweets and heavy carbs, drink water, and monitor sugar closely.")
        elif sugar >= 180:
            risk_score += 3
            reasons.append(f"Blood sugar is high at {sugar}.")
            actions.append("Keep the next meal light and avoid sweets or extra carbs.")
        elif sugar <= 140:
            reasons.append(f"Blood sugar is currently more controlled at {sugar}.")

    if alcohol_units >= 6:
        risk_score += 5
        reasons.append(f"Alcohol intake is very high at about {alcohol_units:.1f} units.")
        actions.append("No more alcohol today and ask someone to stay aware of how you feel.")
    elif alcohol_units >= 4:
        risk_score += 4
        reasons.append(f"Alcohol intake is high at about {alcohol_units:.1f} units.")
        actions.append("Stop drinking for the rest of today.")
    elif alcohol_units >= 2:
        risk_score += 2
        reasons.append(f"Alcohol intake is moderate at about {alcohol_units:.1f} units.")
        actions.append("Do not take another drink for at least 2 hours.")
    elif alcohol_units > 0:
        reasons.append(f"Alcohol intake is low at about {alcohol_units:.1f} unit.")

    if total_alcohol_today >= 6 and alcohol_units > 0:
        risk_score += 2
        reasons.append(f"Total alcohol logged today is already about {total_alcohol_today:.1f} units.")
        actions.append("Do not add any more alcohol today, even if you feel okay right now.")
    elif total_alcohol_today >= 3 and alcohol_units > 0:
        risk_score += 1
        reasons.append(f"Today already includes about {total_alcohol_today:.1f} alcohol units.")

    if alcohol_units > 0 and drink_type:
        actions.append(_drink_specific_guidance(drink_type, alcohol_units))

    if salt_level == "high":
        risk_score += 2
        reasons.append("High-salt food can worsen blood pressure.")
        actions.append("Keep the next 1 or 2 meals low in salt.")
    elif salt_level == "medium":
        reasons.append("Salt intake may add some blood pressure strain.")

    if alcohol_units > 0 and salt_level in {"high", "medium"}:
        risk_score += 2
        reasons.append("Alcohol combined with salty food raises blood pressure risk.")
        actions.append("Avoid more snacks, namkeen, chips, pickle, or fried salty food today.")

    if alcohol_units > 0:
        target_water = min(max(int(alcohol_units * 300), 300), 1200)
        if water_ml < target_water:
            risk_score += 1
            reasons.append("Hydration is low for the amount of alcohol taken.")
            actions.append(f"Drink about {target_water} ml of water over the next 1 to 2 hours.")
        else:
            reasons.append("Water intake is helping reduce dehydration risk.")

    if daily_memory.high_risk_entries_today > 0:
        risk_score += 1
        reasons.append("There was already a high-risk warning earlier today.")
        actions.append("Take today's pattern seriously and keep the rest of the day simple and low-risk.")

    if daily_memory.salty_entries_today >= 2 and salt_level in {"high", "medium"}:
        risk_score += 1
        reasons.append("Salty food has already shown up multiple times today.")
        actions.append("Choose a clearly low-salt next meal instead of another snack.")

    if (
        morning_sugar is not None
        and daily_memory.morning_sugar_level is not None
        and morning_sugar >= 180
        and daily_memory.alcohol_units_today >= 2
    ):
        risk_score += 1
        reasons.append("High morning sugar plus repeated drinking today increases overall strain.")

    if food_type == "carb-heavy" and ((sugar is not None and sugar >= 180) or (morning_sugar is not None and morning_sugar >= 180)):
        risk_score += 2
        reasons.append("Heavy carbs plus high sugar increase glucose risk.")
        actions.append("Keep the next meal lighter with fewer carbs.")

    if food_type == "junk":
        reasons.append("Junk or fried food may make blood pressure and sugar control harder.")

    if symptoms and "normal" not in symptoms:
        symptom_text = ", ".join(symptoms[:3])
        risk_score += 2
        reasons.append(f"Symptoms were reported: {symptom_text}.")
        actions.append("If symptoms get worse or feel severe, seek urgent medical care.")

    _add_food_and_drink_guidance(
        actions=actions,
        systolic=systolic,
        diastolic=diastolic,
        sugar=sugar,
        morning_sugar=morning_sugar,
        alcohol_units=alcohol_units,
        salt_level=salt_level,
        food_type=food_type,
        total_alcohol_today=total_alcohol_today,
    )

    if daily_memory.entries_today > 0:
        reasons.append(daily_memory.summary)

    if not reasons:
        reasons.append("No major risk markers were detected from this entry.")
        actions.append("Keep monitoring and log new readings if symptoms change.")

    if not actions:
        actions.append("Stay with light food, keep hydrated, and check again later if needed.")

    actions = _dedupe(actions)
    reasons = _dedupe(reasons)

    if risk_score >= 9:
        risk = "HIGH"
    elif risk_score >= 4:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    summary = build_summary(risk=risk, parsed=parsed, actions=actions, daily_memory=daily_memory)
    return EvaluationResult(
        status="complete",
        risk=risk,
        reasons=reasons[:6],
        actions=actions[:8],
        summary=summary,
        assistant_message="",
        follow_up_questions=[],
        knowledge=[],
        parsed_data=parsed,
        daily_memory=daily_memory,
    )


def build_summary(*, risk: str, parsed: ParsedHealthData, actions: list[str], daily_memory: DailyMemory) -> str:
    parts: list[str] = []
    if parsed.bp.systolic and parsed.bp.diastolic:
        parts.append(f"BP {parsed.bp.systolic}/{parsed.bp.diastolic}")
    if parsed.sugar_level is not None:
        parts.append(f"Sugar {parsed.sugar_level}")
    if parsed.morning_sugar_level is not None:
        parts.append(f"Morning sugar {parsed.morning_sugar_level}")
    if parsed.alcohol.alcohol_units:
        parts.append(f"Alcohol {parsed.alcohol.alcohol_units:.1f} units")
    if parsed.food.salt_level:
        parts.append(f"Salt {parsed.food.salt_level}")
    if daily_memory.entries_today:
        parts.append(f"{daily_memory.entries_today} earlier entries today")

    leading = ", ".join(parts) if parts else "Based on the current entry"
    return f"{risk.title()} risk. {leading}. Main next step: {actions[0]}"


def _bp_elevated_action(alcohol_units: float) -> str:
    if alcohol_units > 0:
        return "Avoid more alcohol and salty foods for the rest of the day."
    return "Keep salt low, sit quietly, and recheck blood pressure later today."


def _drink_specific_guidance(drink_type: str, alcohol_units: float) -> str:
    readable = drink_type.title()
    if alcohol_units >= 4:
        return f"Do not take any more {readable} today."
    if alcohol_units >= 2:
        return f"Pause {readable} for now and see how you feel before any more."
    return f"Keep {readable} limited and avoid mixing it with salty food."


def _add_food_and_drink_guidance(*, actions: list[str], systolic, diastolic, sugar, morning_sugar, alcohol_units, salt_level, food_type, total_alcohol_today):
    if (systolic and systolic >= 140) or (diastolic and diastolic >= 90) or salt_level == "high":
        actions.append("Next meal: choose dal, vegetables, curd, fruit, or plain home food with less salt.")
        actions.append("Avoid chips, namkeen, pickle, papad, fried snacks, and restaurant salty food today.")

    sugar_concern = (sugar is not None and sugar >= 180) or (morning_sugar is not None and morning_sugar >= 180)
    if sugar_concern:
        actions.append("Next meal: prefer vegetables, dal, eggs, grilled protein, or salad instead of sweets or a heavy rice meal.")
        actions.append("Avoid sweets, dessert, sugary drinks, and a large carb-heavy meal for now.")

    if alcohol_units > 0:
        actions.append("For drinks now: water is best. Avoid more alcohol, energy drinks, or sugary soft drinks.")
        if total_alcohol_today >= 4:
            actions.append("For the rest of today, keep drinks simple: water, lemon water without sugar, or plain coconut water only if sugar is under control.")

    if alcohol_units == 0 and not sugar_concern and not ((systolic and systolic >= 140) or (diastolic and diastolic >= 90)):
        actions.append("Food and drink can stay simple: regular balanced meal, normal water intake, and continue monitoring.")

    if food_type == "junk":
        actions.append("Try a simple home meal next instead of another fried or packaged snack.")


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
