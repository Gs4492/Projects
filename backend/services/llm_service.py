import json

import httpx

from backend.config import settings


PARSE_SYSTEM_PROMPT = (
    "You extract structured health tracking data from casual user messages. "
    "Return only valid JSON. Use null when unknown. "
    "Capture blood pressure, current sugar, morning sugar, alcohol type, quantity, peg or bottle size, ml if mentioned, water, food items, salt level, food type, symptoms, and notes."
)


async def try_llm_parse(text: str) -> dict | None:
    if not settings.nvidia_api_key:
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
    return await _chat_json(system_prompt=PARSE_SYSTEM_PROMPT, user_prompt=prompt, max_tokens=500)


async def try_llm_guidance(*, text: str, risk: str, reasons: list[str], actions: list[str], knowledge: list[str], daily_summary: str | None = None) -> str | None:
    if not settings.nvidia_api_key:
        return None

    user_prompt = (
        "Create a short health guidance message for a non-technical older adult. "
        "Do not diagnose. Do not add facts outside the provided context. "
        "Keep it under 110 words. Mention the main risk, the best drink right now, the best next meal direction, and when to recheck if the actions mention it. "
        f"Original input: {text}\n"
        f"Risk: {risk}\n"
        f"Reasons: {json.dumps(reasons)}\n"
        f"Actions: {json.dumps(actions)}\n"
        f"Context: {json.dumps(knowledge)}\n"
        f"Today so far: {daily_summary or 'No earlier entries today.'}"
    )
    result = await _chat_text(
        system_prompt="You are a careful health assistant. Stay grounded in the provided facts and keep the message simple.",
        user_prompt=user_prompt,
        max_tokens=220,
    )
    return result.strip() if result else None


async def _chat_json(*, system_prompt: str, user_prompt: str, max_tokens: int) -> dict | None:
    content = await _chat_text(system_prompt=system_prompt, user_prompt=user_prompt, max_tokens=max_tokens)
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
    except Exception:
        return None
