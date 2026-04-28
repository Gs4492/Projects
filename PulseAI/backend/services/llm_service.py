import json
import httpx

from backend.config import settings


PARSE_SYSTEM_PROMPT = (
    "You are a strict health data parser.\n\n"

    "INPUT FORMAT:\n"
    "The user provides structured text like:\n"
    "Food: ... | Drinks: ... | BP: ... | Sugar: ... | Water: ... | Feeling: ...\n\n"

    "RULES:\n"
    "- ALWAYS extract values if present\n"
    "- NEVER return null if a value exists in the text\n"
    "- If a number appears (like 144), you MUST capture it\n"
    "- BP like 138/75 must always be extracted\n"
    "- Sugar like 144 must always be extracted even if no keyword nearby\n"
    "- Water like '2 glasses' should be converted to ml (1 glass = 250 ml)\n"
    "- If user says 'feeling normal', return symptoms as ['normal']\n"
    "- Only use null when the value is truly missing\n\n"

    "OUTPUT:\n"
    "Return ONLY valid JSON. No explanation."
)


async def try_llm_parse(text: str) -> dict | None:
    if not settings.nvidia_api_key:
        print("LLM SKIPPED: No API key")
        return None

    prompt = (
        "Return JSON with this shape: "
        '{"bp":{"systolic":null,"diastolic":null},"sugar_level":null,"morning_sugar_level":null,'
        '"alcohol":{"drink_type":null,"quantity":null,"size_label":null,"volume_ml_each":null,"total_volume_ml":null},'
        '"food":{"items":[],"salt_level":null,"food_type":null},"water_ml":null,"symptoms":[],"notes":null}. '
        "If user says peg but not size, keep size_label as null. "
        "If user says they feel normal, put ['normal'] in symptoms. "
        f"Message: {text}"
    )

    return await _chat_json(
        system_prompt=PARSE_SYSTEM_PROMPT,
        user_prompt=prompt,
        max_tokens=500,
    )


async def try_llm_guidance(
    *,
    text: str,
    risk: str,
    reasons: list[str],
    actions: list[str],
    knowledge: list[str],
    daily_summary: str | None = None,
) -> str | None:

    if not settings.nvidia_api_key:
        print("LLM SKIPPED: No API key")
        return None

    user_prompt = (
        "You are a practical health assistant.\n\n"

        "Your job is to give SPECIFIC, situation-aware guidance.\n"
        "Do NOT be generic.\n\n"

        "Rules:\n"
        "- Use the exact numbers provided (BP, sugar, water, alcohol)\n"
        "- Explain what those numbers mean in simple terms\n"
        "- Combine factors (e.g., BP + coffee, sugar + carbs, alcohol + salt)\n"
        "- Give clear next steps (what to eat, what to drink, what to avoid)\n"
        "- Mention timing if relevant (rest now, recheck later)\n"
        "- Keep tone simple, direct, and helpful\n"
        "- Max 110 words\n\n"

        "Examples of GOOD guidance:\n"
        "- 'Sugar 144 after rice is borderline. Avoid sweets for the rest of the day.'\n"
        "- 'BP 138/75 with coffee is mildly elevated. Switch to water and avoid more caffeine today.'\n"
        "- 'Alcohol with salty snacks can push BP higher tonight. Stop here and hydrate.'\n\n"

        f"Original input: {text}\n\n"

        "Observed situation:\n"
        f"- Risk level: {risk}\n"
        f"- Key observations: {json.dumps(reasons)}\n"
        f"- Current recommendations (may be generic): {json.dumps(actions)}\n"
        f"- Context info: {json.dumps(knowledge)}\n"
        f"- Today so far: {daily_summary or 'No earlier entries today.'}\n\n"

        "Your task:\n"
        "Do NOT repeat the recommendations blindly.\n"
        "Instead, interpret the situation and give specific advice based on numbers and behavior.\n"
    )

    result = await _chat_text(
        system_prompt="You are a careful health assistant. Stay grounded in the provided facts and keep the message simple.",
        user_prompt=user_prompt,
        max_tokens=220,
    )

    return result.strip() if result else None


async def _chat_json(*, system_prompt: str, user_prompt: str, max_tokens: int) -> dict | None:
    content = await _chat_text(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_tokens=max_tokens,
    )

    if not content:
        return None

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(content[start : end + 1])
            except json.JSONDecodeError:
                return None
        return None


async def _chat_text(*, system_prompt: str, user_prompt: str, max_tokens: int) -> str | None:
    headers = {
        "Authorization": f"Bearer {settings.nvidia_api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": settings.nvidia_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }

    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(
                f"{settings.nvidia_base_url}/chat/completions",
                headers=headers,
                json=payload,
            )

            response.raise_for_status()
            data = response.json()

            return data["choices"][0]["message"]["content"]

    except Exception as e:
        print("LLM ERROR:", str(e))  # keep this only
        return None