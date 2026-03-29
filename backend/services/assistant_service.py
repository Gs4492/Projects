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

    what_is_happening = " ".join(response.reasons[:2]) if response.reasons else "This entry needs attention."

    do_now = _pick_many(response.actions, ["do not", "stop", "drink about", "take a fast sugar", "sit quietly", "avoid more alcohol", "pause", "keep salt low"])
    eat_next = _pick_many(response.actions, ["next meal", "simple home meal", "small snack", "balanced meal"])
    drink_now = _pick_many(response.actions, ["water", "drinks now", "lemon water", "coconut water"])
    avoid = _pick_many(response.actions, ["avoid", "do not take any more", "do not add any more", "no more alcohol"])
    check_again = _pick_many(response.actions, ["recheck", "check again", "30 to 60", "15 minutes", "later today"])
    when_to_get_help = _pick_many(response.actions, ["urgent medical", "medical care", "seek"])

    if not do_now and response.actions:
        do_now = response.actions[:2]

    return GuidanceSections(
        what_is_happening=what_is_happening,
        do_now=do_now[:3],
        eat_next=eat_next[:3],
        drink_now=drink_now[:3],
        avoid=avoid[:3],
        check_again=check_again[:2],
        when_to_get_help=when_to_get_help[:2],
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
    if guidance.check_again:
        bits.append(f"Check again: {guidance.check_again[0]}")
    if response.daily_memory.entries_today:
        bits.append(response.daily_memory.summary)
    bits.append("Guidance only, not a diagnosis.")
    return " ".join(bits)


def _pick_many(actions: list[str], keywords: list[str]) -> list[str]:
    picked: list[str] = []
    lowered_keywords = [keyword.lower() for keyword in keywords]
    for action in actions:
        lowered = action.lower()
        if any(keyword in lowered for keyword in lowered_keywords) and action not in picked:
            picked.append(action)
    return picked
