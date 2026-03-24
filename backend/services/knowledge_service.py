from backend.schemas.request_response import ParsedHealthData


KNOWLEDGE_BASE = [
    {
        "id": "bp-elevated",
        "keywords": ["bp", "blood_pressure"],
        "text": "A blood pressure reading at or above 140/90 is a warning sign and alcohol or high sodium can push it higher.",
    },
    {
        "id": "bp-very-high",
        "keywords": ["high_bp"],
        "text": "Blood pressure at or above 160/100 is a high-risk reading and should be treated more seriously than a mild elevation.",
    },
    {
        "id": "alcohol-bp",
        "keywords": ["alcohol"],
        "text": "Alcohol can raise blood pressure temporarily, especially when combined with dehydration or salty foods.",
    },
    {
        "id": "salt-bp",
        "keywords": ["salt"],
        "text": "High-salt food can increase fluid retention and make blood pressure control harder.",
    },
    {
        "id": "sugar-high",
        "keywords": ["high_sugar"],
        "text": "A sugar reading around or above 180 means closer monitoring is wise and extra sweets or heavy carbs should be limited.",
    },
    {
        "id": "sugar-low",
        "keywords": ["low_sugar"],
        "text": "A sugar reading under 70 can become urgent because it may cause shakiness, sweating, or confusion.",
    },
    {
        "id": "hydration",
        "keywords": ["water"],
        "text": "Water helps after alcohol intake because dehydration can worsen dizziness and blood pressure changes.",
    },
]


def retrieve_health_context(parsed: ParsedHealthData, risk: str) -> list[str]:
    tags: set[str] = set()

    if parsed.bp.systolic or parsed.bp.diastolic:
        tags.add("bp")
    if (parsed.bp.systolic and parsed.bp.systolic >= 160) or (parsed.bp.diastolic and parsed.bp.diastolic >= 100):
        tags.add("high_bp")
    if parsed.alcohol.alcohol_units and parsed.alcohol.alcohol_units > 0:
        tags.add("alcohol")
    if parsed.food.salt_level == "high":
        tags.add("salt")
    if parsed.sugar_level is not None and parsed.sugar_level >= 180:
        tags.add("high_sugar")
    if parsed.sugar_level is not None and parsed.sugar_level < 70:
        tags.add("low_sugar")
    if (parsed.water_ml or 0) < 500:
        tags.add("water")
    if risk == "HIGH":
        tags.add("high_bp")

    results = []
    for item in KNOWLEDGE_BASE:
        if any(keyword in tags for keyword in item["keywords"]):
            results.append(item["text"])

    return results[:4]
