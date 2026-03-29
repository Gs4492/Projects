from backend.schemas.request_response import AnalyzeResponse, GuidanceSections
from backend.services.llm_service import try_llm_guidance


async def build_assistant_message(
    *,
    input_text: str,
    response: AnalyzeResponse,
) -> str:
    llm_message = await try_llm_guidance(
        text=input_text,
        risk=response.risk,
        reasons=response.reasons,
        actions=response.actions,
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
    what_is_happening = " ".join(response.reasons[:3]) if response.reasons else "This entry needs attention."

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

    if parsed.alcohol.alcohol_units > 0 and not any("alcohol" in item.lower() or parsed.alcohol.drink_type and parsed.alcohol.drink_type.lower() in item.lower() for item in avoid + do_now + drink_now):
        readable = parsed.alcohol.drink_type.title() if parsed.alcohol.drink_type else "alcohol"
        if parsed.alcohol.alcohol_units <= 1:
            avoid.insert(0, f"Keep {readable} limited today and avoid mixing it with salty food.")
        else:
            avoid.insert(0, f"Do not add more {readable} right now.")

    if parsed.food.food_type and not eat_next:
        if parsed.food.food_type == "junk":
            eat_next.append("Next meal: choose simple home food instead of another fried or packaged snack.")
        elif parsed.food.food_type == "carb-heavy":
            eat_next.append("Next meal: keep it lighter with vegetables, dal, eggs, or salad.")

    if parsed.bp.systolic and parsed.bp.diastolic and parsed.bp.systolic >= 140 and not check_again:
        check_again.append("Recheck blood pressure later today after resting quietly.")

    if parsed.alcohol.alcohol_units > 0 and not drink_now:
        drink_now.append("Drink water now rather than another alcoholic or sugary drink.")

    if not do_now and response.actions:
        do_now = response.actions[:2]

    return GuidanceSections(
        what_is_happening=what_is_happening,
        do_now=_dedupe(do_now)[:3],
        eat_next=_dedupe(eat_next)[:3],
        drink_now=_dedupe(drink_now)[:3],
        avoid=_dedupe(avoid)[:4],
        check_again=_dedupe(check_again)[:2],
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
