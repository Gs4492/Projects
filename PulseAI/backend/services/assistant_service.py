from backend.schemas.request_response import AnalyzeResponse, GuidanceSections
from backend.services.llm_service import try_llm_guidance


async def build_assistant_message(
    *,
    input_text: str,
    response: AnalyzeResponse,
) -> str:
    parsed = response.parsed_data

    # 🔥 Build structured signals for LLM (critical for better reasoning)
    signal_bits = []

    if parsed.alcohol.alcohol_units:
        signal_bits.append(f"Alcohol units: {parsed.alcohol.alcohol_units}")

    if parsed.food.food_type:
        signal_bits.append(f"Food type: {parsed.food.food_type}")

    if parsed.food.items:
        signal_bits.append(f"Food items: {', '.join(parsed.food.items[:3])}")

    if parsed.water_ml:
        signal_bits.append(f"Water: {parsed.water_ml} ml")

    if parsed.symptoms:
        signal_bits.append(f"Symptoms: {', '.join(parsed.symptoms)}")

    # Combine original input + structured signals
    enhanced_text = input_text
    if signal_bits:
        enhanced_text = (
            f"{input_text}\n\n"
            f"Structured signals: {' | '.join(signal_bits)}"
        )

    llm_message = await try_llm_guidance(
        text=enhanced_text,
        risk=response.risk,
        reasons=response.reasons,
        actions=[],  # 🔥 REMOVE influence of generic actions
        knowledge=response.knowledge,
        daily_summary=response.daily_memory.summary,
    )

    if llm_message:
        return llm_message

    return _fallback_message(response)


def build_guidance_sections(response: AnalyzeResponse) -> GuidanceSections:
    if response.status == "needs_more_info":
        return GuidanceSections(
            what_is_happening="A little more information is needed before the guidance can be made more exact.",
            do_now=response.follow_up_questions[:4],
        )

    parsed = response.parsed_data
    bp = parsed.bp
    alcohol_units = parsed.alcohol.alcohol_units or 0
    drink_type = parsed.alcohol.drink_type.title() if parsed.alcohol.drink_type else "alcohol"
    sugar = parsed.sugar_level
    morning_sugar = parsed.morning_sugar_level
    salt_level = parsed.food.salt_level
    food_type = parsed.food.food_type
    water_ml = parsed.water_ml or 0
    symptoms = parsed.symptoms

    what_bits: list[str] = []
    if bp.systolic and bp.diastolic:
        if bp.systolic >= 180 or bp.diastolic >= 110:
            what_bits.append(f"BP {bp.systolic}/{bp.diastolic} — hypertensive crisis. Seek urgent help.")
        elif bp.systolic >= 160 or bp.diastolic >= 100:
            what_bits.append(f"BP {bp.systolic}/{bp.diastolic} — very high (Stage 2 hypertension).")
        elif bp.systolic >= 140 or bp.diastolic >= 90:
            what_bits.append(f"BP {bp.systolic}/{bp.diastolic} — Stage 1 hypertension. Needs attention.")
        elif bp.systolic >= 130 or bp.diastolic >= 80:
            what_bits.append(f"BP {bp.systolic}/{bp.diastolic} — elevated. Worth watching.")
        elif bp.systolic >= 120:
            what_bits.append(f"BP {bp.systolic}/{bp.diastolic} — slightly above normal.")
        else:
            what_bits.append(f"BP {bp.systolic}/{bp.diastolic} — normal range.")

    if sugar is not None:
        if sugar < 70:
            what_bits.append(f"Sugar {sugar} — dangerously low. Act immediately.")
        elif sugar >= 250:
            what_bits.append(f"Sugar {sugar} — very high. Risk of complications.")
        elif sugar >= 180:
            what_bits.append(f"Sugar {sugar} — high. Avoid carbs and sweets.")
        elif sugar >= 126:
            what_bits.append(f"Sugar {sugar} — above normal. May indicate diabetes if consistent.")
        elif sugar >= 100:
            what_bits.append(f"Sugar {sugar} — prediabetic range. Monitor closely.")
        else:
            what_bits.append(f"Sugar {sugar} — normal range.")
    elif morning_sugar is not None:
        if morning_sugar >= 180:
            what_bits.append(f"Morning sugar {morning_sugar} — already high at the start of the day.")
        elif morning_sugar >= 126:
            what_bits.append(f"Morning sugar {morning_sugar} — above normal fasting range.")
        elif morning_sugar >= 100:
            what_bits.append(f"Morning sugar {morning_sugar} — prediabetic fasting range.")
        elif morning_sugar < 70:
            what_bits.append(f"Morning sugar {morning_sugar} — started low. Eat something soon.")
        else:
            what_bits.append(f"Morning sugar {morning_sugar} — normal fasting range.")

    if alcohol_units > 0:
        what_bits.append(f"{drink_type} intake is about {alcohol_units:.1f} alcohol unit{'s' if alcohol_units != 1 else ''}.")

    if alcohol_units > 0 and salt_level in {"high", "medium"}:
        what_bits.append("Alcohol plus salty food can push blood pressure and dehydration risk higher.")
    elif salt_level == "high":
        what_bits.append("Salty food may make blood pressure control harder.")

    if symptoms and "normal" not in symptoms:
        what_bits.append(f"Symptoms reported today: {', '.join(symptoms[:3])}.")

    do_now: list[str] = []
    eat_next: list[str] = []
    drink_now: list[str] = []
    avoid: list[str] = []
    check_again: list[str] = []
    when_to_get_help: list[str] = []

    for action in response.actions:
        lowered = action.lower()
        if any(token in lowered for token in ["urgent medical", "seek", "medical care", "get help"]):
            when_to_get_help.append(action)
        elif lowered.startswith("next meal:") or "small snack" in lowered or "simple home meal" in lowered:
            eat_next.append(action)
        elif lowered.startswith("for drinks now:") or "drink about" in lowered or "water is best" in lowered or "lemon water" in lowered or "coconut water" in lowered:
            drink_now.append(action)
        elif any(token in lowered for token in ["recheck", "check again", "15 minutes", "30 to 60", "later today"]):
            check_again.append(action)
        elif lowered.startswith("avoid") or lowered.startswith("do not") or lowered.startswith("no more") or lowered.startswith("keep "):
            avoid.append(action)
        else:
            do_now.append(action)

    if alcohol_units > 0:
        if alcohol_units >= 2:
            do_now.insert(0, f"Stop at this amount of {drink_type.lower()} for now and do not add another drink yet.")
        else:
            do_now.insert(0, f"Keep {drink_type.lower()} limited and do not stack it with more salty snacks.")

    if bp.systolic and bp.diastolic and (bp.systolic >= 140 or bp.diastolic >= 90):
        do_now.insert(0, "Sit quietly, avoid more strain, and keep the rest of the day simple.")
        if not check_again:
            check_again.append("Recheck blood pressure after resting quietly for 30 to 60 minutes.")

    if sugar is not None and sugar >= 180:
        do_now.insert(0, "Keep the next few hours simple and do not add sweets or another heavy carb-heavy meal.")
        if not check_again:
            check_again.append("Recheck sugar later if you normally monitor it or if symptoms change.")
    elif sugar is not None and sugar < 70:
        do_now.insert(0, "Take fast sugar now and do not delay a recheck.")

    if alcohol_units > 0:
        target_water = min(max(int(alcohol_units * 300), 300), 1200)
        drink_now.insert(0, f"Drink about {target_water} ml of water over the next 1 to 2 hours.")
        drink_now.append("Use water first, not another alcoholic, energy, or sugary drink.")
    elif water_ml and water_ml < 500 and response.risk != "LOW":
        drink_now.insert(0, "Increase water gradually over the next hour unless a doctor has told you to restrict fluids.")

    if salt_level == "high" or (bp.systolic and bp.diastolic and (bp.systolic >= 140 or bp.diastolic >= 90)):
        eat_next.insert(0, "Next meal: choose dal, vegetables, curd, fruit, or plain home food with less salt.")
        avoid.insert(0, "Avoid chips, namkeen, pickle, papad, fried snacks, and restaurant salty food for the rest of the day.")

    sugar_concern = (sugar is not None and sugar >= 180) or (morning_sugar is not None and morning_sugar >= 180)
    if sugar_concern:
        eat_next.insert(0, "Next meal: prefer vegetables, dal, eggs, grilled protein, or salad instead of sweets or a heavy rice meal.")
        avoid.append("Avoid sweets, dessert, sugary drinks, and a large carb-heavy meal for now.")
    elif food_type == "junk":
        eat_next.insert(0, "Next meal: switch to simple home food instead of another fried or packaged snack.")
    elif food_type == "carb-heavy":
        eat_next.insert(0, "Next meal: keep it lighter with vegetables, dal, eggs, or salad.")

    if alcohol_units > 0:
        if alcohol_units <= 1:
            avoid.insert(0, f"Do not combine more {drink_type.lower()} with salty food later today.")
        else:
            avoid.insert(0, f"Do not take more {drink_type.lower()} for the rest of today.")

    if symptoms and "normal" not in symptoms:
        when_to_get_help.insert(0, "Get help now if symptoms suddenly worsen, feel severe, or include chest pain, confusion, fainting, or trouble breathing.")
    elif response.risk == "HIGH":
        when_to_get_help.insert(0, "Get urgent medical help if readings keep rising or you start feeling faint, confused, breathless, or have chest discomfort.")

    if response.daily_memory.entries_today > 0 and response.risk != "LOW":
        do_now.append("This is not the first entry today, so treat the whole-day pattern seriously.")

    if not do_now and response.actions:
        do_now = response.actions[:2]

    what_is_happening = " ".join(_dedupe(what_bits)[:4]) if what_bits else "This entry needs attention."

    return GuidanceSections(
        what_is_happening=what_is_happening,
        do_now=_dedupe(do_now)[:4],
        eat_next=_dedupe(eat_next)[:3],
        drink_now=_dedupe(drink_now)[:3],
        avoid=_dedupe(avoid)[:4],
        check_again=_dedupe(check_again)[:3],
        when_to_get_help=_dedupe(when_to_get_help)[:2],
    )


def _fallback_message(response: AnalyzeResponse) -> str:
    if response.status == "needs_more_info":
        return "I need a few quick details first so I can give specific food, drink, and recheck advice."

    guidance = response.guidance
    bits = [f"{response.risk.title()} risk right now."]
    if guidance.what_is_happening:
        bits.append(guidance.what_is_happening)
    if guidance.do_now:
        bits.append(f"Do now: {guidance.do_now[0]}")
    if guidance.eat_next:
        bits.append(f"Eat next: {guidance.eat_next[0]}")
    if guidance.drink_now:
        bits.append(f"Drink now: {guidance.drink_now[0]}")
    if guidance.avoid:
        bits.append(f"Avoid: {guidance.avoid[0]}")
    if guidance.check_again:
        bits.append(f"Check again: {guidance.check_again[0]}")
    if response.daily_memory.entries_today:
        bits.append(response.daily_memory.summary)
    bits.append("Guidance only, not a diagnosis.")
    return " ".join(bits)


def _dedupe(items: list[str]) -> list[str]:
    picked: list[str] = []
    for item in items:
        if item and item not in picked:
            picked.append(item)
    return picked
