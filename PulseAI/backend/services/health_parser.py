import re
from dataclasses import dataclass

from backend.schemas.request_response import ParsedHealthData
from backend.services.llm_service import try_llm_parse


SPIRIT_TYPES = ["whiskey", "whisky", "vodka", "rum", "gin", "brandy", "spirit"]
BEER_TYPES = ["beer", "lager", "ale", "stout"]
WINE_TYPES = ["wine"]
SALTY_FOODS = ["chips", "namkeen", "fries", "salted peanuts", "pickle", "snacks", "papad", "bhujia"]
JUNK_FOODS = ["chips", "pizza", "burger", "fries", "namkeen", "samosa", "pakora"]
CARB_FOODS = ["rice", "bread", "roti", "naan", "sweets", "dessert", "cake", "ice cream"]
SYMPTOMS = [
    "chest pain",
    "chest discomfort",
    "shortness of breath",
    "breathless",
    "faint",
    "confused",
    "dizzy",
    "weak",
    "headache",
    "sweating",
    "nausea",
    "shaky",
    "blurred",
]
NORMAL_FEELING_PHRASES = ["feeling normal", "i am feeling normal", "i feel normal"]
NORMAL_FEELING_STANDALONE = ["normal", "fine", "okay", "ok"]
NUMBER_WORDS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "half": 0.5,
}


@dataclass
class DrinkConversion:
    size_label: str | None
    volume_ml_each: float | None
    total_volume_ml: float | None
    alcohol_units: float
    explanation: str | None


async def parse_health_input(text: str) -> ParsedHealthData:
    llm_result = await try_llm_parse(text)
    if llm_result:
        try:
            merged = _merge_with_normalization(llm_result)
            return ParsedHealthData.model_validate(merged)
        except Exception:
            pass

    heuristic = _heuristic_parse(text)
    return ParsedHealthData.model_validate(heuristic)


def _merge_with_normalization(raw: dict) -> dict:
    alcohol = raw.get("alcohol") or {}
    drink_type = (alcohol.get("drink_type") or "").lower() or None
    quantity = _to_float(alcohol.get("quantity"))
    size_label = alcohol.get("size_label")
    volume_ml_each = _to_float(alcohol.get("volume_ml_each"))
    total_volume_ml = _to_float(alcohol.get("total_volume_ml"))

    if not drink_type and size_label and "peg" in str(size_label).lower():
        drink_type = "spirit"

    conversion = normalize_alcohol(
        drink_type=drink_type,
        quantity=quantity,
        size_label=size_label,
        volume_ml_each=volume_ml_each,
        total_volume_ml=total_volume_ml,
    )

    alcohol["drink_type"] = drink_type
    alcohol["quantity"] = quantity
    alcohol["size_label"] = conversion.size_label
    alcohol["volume_ml_each"] = conversion.volume_ml_each
    alcohol["total_volume_ml"] = conversion.total_volume_ml
    alcohol["alcohol_units"] = conversion.alcohol_units
    alcohol["explanation"] = conversion.explanation
    raw["alcohol"] = alcohol
    return raw


def _heuristic_parse(text: str) -> dict:
    lowered = text.lower()
    systolic, diastolic = _parse_bp(lowered)
    morning_sugar = _parse_morning_sugar(lowered)
    sugar = _parse_current_sugar(lowered, morning_sugar)
    water_ml = _parse_water(lowered)

    drink_type = _parse_drink_type(lowered)
    quantity = _parse_drink_quantity(lowered, drink_type)
    size_label = _parse_size_label(lowered)
    volume_ml_each = _parse_volume_ml(lowered)
    total_volume_ml = None
    if volume_ml_each is not None and quantity is not None:
        total_volume_ml = volume_ml_each * quantity

    conversion = normalize_alcohol(
        drink_type=drink_type,
        quantity=quantity,
        size_label=size_label,
        volume_ml_each=volume_ml_each,
        total_volume_ml=total_volume_ml,
    )

    food_items = [food for food in SALTY_FOODS + JUNK_FOODS + CARB_FOODS if food in lowered]
    food_type = _derive_food_type(lowered)
    salt_level = _derive_salt_level(lowered, food_items)
    symptoms = _parse_symptoms(lowered)

    return {
        "bp": {"systolic": systolic, "diastolic": diastolic},
        "sugar_level": sugar,
        "morning_sugar_level": morning_sugar,
        "alcohol": {
            "drink_type": drink_type,
            "quantity": quantity,
            "size_label": conversion.size_label,
            "volume_ml_each": conversion.volume_ml_each,
            "total_volume_ml": conversion.total_volume_ml,
            "alcohol_units": conversion.alcohol_units,
            "explanation": conversion.explanation,
        },
        "food": {
            "items": list(dict.fromkeys(food_items)),
            "salt_level": salt_level,
            "food_type": food_type,
        },
        "water_ml": water_ml,
        "symptoms": list(dict.fromkeys(symptoms)),
        "notes": text.strip(),
    }


def normalize_alcohol(*, drink_type: str | None, quantity: float | None, size_label: str | None, volume_ml_each: float | None, total_volume_ml: float | None) -> DrinkConversion:
    normalized_size = (size_label or "").lower() or None
    if quantity is None:
        quantity = 1 if drink_type else 0

    if drink_type in SPIRIT_TYPES:
        readable_size = normalized_size
        if normalized_size in {"large", "large peg", "big", "double"}:
            volume_ml_each = 60
            readable_size = "large peg"
        elif normalized_size in {"small", "small peg", "single"} or not volume_ml_each:
            volume_ml_each = 30
            readable_size = "small peg"
        total_volume_ml = volume_ml_each * quantity if volume_ml_each else None
        units = quantity * (2 if readable_size == "large peg" else 1)
        explanation = "1 small peg = 30 ml, 1 large peg = 60 ml."
        return DrinkConversion(readable_size, volume_ml_each, total_volume_ml, units, explanation)

    if drink_type in BEER_TYPES or normalized_size in {"small bottle", "large bottle", "half bottle"}:
        if volume_ml_each is None:
            if normalized_size == "large bottle":
                volume_ml_each = 650
            elif normalized_size == "half bottle":
                volume_ml_each = 325
            else:
                volume_ml_each = 330
                normalized_size = normalized_size or "small bottle"
        if volume_ml_each <= 350:
            units_per_item = 1
            normalized_size = normalized_size or "small bottle"
        else:
            units_per_item = 2
            normalized_size = normalized_size or "large bottle"
        total_volume_ml = volume_ml_each * quantity if quantity else total_volume_ml
        explanation = "Small beer = 330 ml, half bottle = about 325 ml, large beer = 650 ml."
        return DrinkConversion(normalized_size, volume_ml_each, total_volume_ml, quantity * units_per_item if quantity else units_per_item, explanation)

    if drink_type in WINE_TYPES:
        volume_ml_each = volume_ml_each or 150
        total_volume_ml = volume_ml_each * quantity if quantity else volume_ml_each
        explanation = "1 wine glass = about 150 ml."
        return DrinkConversion("glass", volume_ml_each, total_volume_ml, quantity, explanation)

    return DrinkConversion(normalized_size, volume_ml_each, total_volume_ml, 0, None)


def _parse_bp(text: str) -> tuple[int | None, int | None]:
    match = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def _parse_water(text: str) -> int | None:
    match = re.search(r"(\d{2,4})\s*ml\s*(?:of\s+)?water\b", text)
    if match:
        return int(match.group(1))

    water_number = re.search(r"water[^\d]*(\d{2,4})\s*ml\b", text)
    if water_number:
        return int(water_number.group(1))

    glass_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:glass|glasses)\s*(?:of\s+)?water\b", text)
    if glass_match:
        return int(float(glass_match.group(1)) * 250)

    reverse_glass_match = re.search(r"water[^\d]*(\d+(?:\.\d+)?)\s*(?:glass|glasses)\b", text)
    if reverse_glass_match:
        return int(float(reverse_glass_match.group(1)) * 250)

    if "liter of water" in text or "litre of water" in text or "water" in text:
        liter_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:liter|litre|l)\s*(?:of\s+)?water\b", text)
        if liter_match:
            return int(float(liter_match.group(1)) * 1000)
        reverse_liter_match = re.search(r"water[^\d]*(\d+(?:\.\d+)?)\s*(?:liter|litre|l)\b", text)
        if reverse_liter_match:
            return int(float(reverse_liter_match.group(1)) * 1000)

    return None


def _parse_morning_sugar(text: str) -> int | None:
    patterns = [
        r"morning sugar[^\d]*(\d{2,3})",
        r"sugar in the morning[^\d]*(\d{2,3})",
        r"fasting sugar[^\d]*(\d{2,3})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return None


def _parse_current_sugar(text: str, morning_sugar: int | None) -> int | None:
    lowered = text.lower()
    if "morning sugar" in lowered or "fasting sugar" in lowered or "sugar in the morning" in lowered:
        generic = _extract_number_after_keywords(lowered, ["sugar", "glucose"])
        if generic == morning_sugar:
            return None
    return _extract_number_after_keywords(lowered, ["sugar", "glucose"])


def _parse_drink_type(text: str) -> str | None:
    for drink in SPIRIT_TYPES + BEER_TYPES + WINE_TYPES:
        if drink in text:
            return drink
    if "peg" in text or "pegs" in text:
        return "spirit"
    return None


def _parse_drink_quantity(text: str, drink_type: str | None) -> float | None:
    if drink_type in SPIRIT_TYPES:
        quantity = _extract_quantity(text, ["peg", "pegs"])
        if quantity is not None:
            return quantity
        if any(token in text for token in ["a peg", "one peg"]):
            return 1

    if drink_type in BEER_TYPES:
        quantity = _extract_quantity(text, ["beer", "beers", "bottle", "bottles"])
        if quantity is not None:
            return quantity
        if any(token in text for token in ["a beer", "one beer"]):
            return 1

    if drink_type in WINE_TYPES:
        quantity = _extract_quantity(text, ["glass", "glasses"])
        if quantity is not None:
            return quantity
        if any(token in text for token in ["a glass", "one glass"]):
            return 1

    return None


def _parse_size_label(text: str) -> str | None:
    if "large peg" in text or "big peg" in text or "double peg" in text:
        return "large peg"
    if "small peg" in text or "single peg" in text:
        return "small peg"
    if "half bottle" in text:
        return "half bottle"
    if "650" in text or "large beer" in text or "big bottle" in text:
        return "large bottle"
    if "330" in text or "small beer" in text or "small bottle" in text:
        return "small bottle"
    return None


def _parse_volume_ml(text: str) -> float | None:
    match = re.search(r"(\d{2,4})\s*ml", text)
    if match:
        return float(match.group(1))
    return None


def _parse_symptoms(text: str) -> list[str]:
    symptoms = [symptom for symptom in SYMPTOMS if symptom in text]
    if symptoms:
        return symptoms

    if any(phrase in text for phrase in NORMAL_FEELING_PHRASES):
        return ["normal"]

    segments = [segment.strip() for segment in text.split(",")]
    if any(segment in NORMAL_FEELING_STANDALONE for segment in segments):
        return ["normal"]

    return []


def _extract_number_after_keywords(text: str, keywords: list[str]) -> int | None:
    for keyword in keywords:
        match = re.search(rf"{keyword}[^\d]*(\d{{2,3}})", text)
        if match:
            return int(match.group(1))
    return None


def _extract_quantity(text: str, keywords: list[str]) -> float | None:
    descriptors = r"(?:small|large|big|single|double|half)?"
    for keyword in keywords:
        number_match = re.search(rf"(\d+(?:\.\d+)?)\s*(?:{descriptors}\s*)?{keyword}\b", text)
        if number_match:
            return float(number_match.group(1))
        for word, value in NUMBER_WORDS.items():
            word_match = re.search(rf"\b{word}\b\s*(?:{descriptors}\s*)?{keyword}\b", text)
            if word_match:
                return float(value)
    return None


def _derive_food_type(text: str) -> str | None:
    if any(food in text for food in JUNK_FOODS):
        return "junk"
    if any(food in text for food in CARB_FOODS):
        return "carb-heavy"
    if any(food in text for food in ["salad", "dal", "vegetable", "balanced"]):
        return "balanced"
    return None


def _derive_salt_level(text: str, food_items: list[str]) -> str | None:
    if "very salty" in text or "too much salt" in text:
        return "high"
    if any(food in text for food in SALTY_FOODS):
        return "high"
    if "salty" in text or "salt" in text:
        return "medium"
    if any(food in food_items for food in SALTY_FOODS):
        return "medium"
    return None


def _to_float(value) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
