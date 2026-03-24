from backend.schemas.request_response import AnalyzeResponse
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


def _fallback_message(response: AnalyzeResponse) -> str:
    if response.status == "needs_more_info":
        return "I need a few quick details first so I can give specific food, drink, and recheck advice."

    reason_text = " ".join(response.reasons[:2]) if response.reasons else "This entry needs attention."
    now_action = response.actions[0] if response.actions else "Keep monitoring your readings."
    food_action = _pick_action(response.actions, ["meal", "eat", "food", "avoid"])
    drink_action = _pick_action(response.actions, ["water", "drink", "alcohol"])
    recheck_action = _pick_action(response.actions, ["recheck", "check", "15 minutes", "30 to 60"])
    daily_context = response.daily_memory.summary if response.daily_memory.entries_today else ""

    bits = [
        f"{response.risk.title()} risk right now.",
        reason_text,
        f"Do this now: {now_action}",
    ]
    if food_action:
        bits.append(f"Food: {food_action}")
    if drink_action and drink_action != now_action:
        bits.append(f"Drink: {drink_action}")
    if recheck_action:
        bits.append(f"Check again: {recheck_action}")
    if daily_context:
        bits.append(daily_context)
    bits.append("Guidance only, not a diagnosis.")
    return " ".join(bits)


def _pick_action(actions: list[str], keywords: list[str]) -> str | None:
    lowered_keywords = [keyword.lower() for keyword in keywords]
    for action in actions:
        lowered = action.lower()
        if any(keyword in lowered for keyword in lowered_keywords):
            return action
    return None
