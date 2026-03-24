from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class HealthMetric(BaseModel):
    systolic: int | None = None
    diastolic: int | None = None


class AlcoholData(BaseModel):
    drink_type: str | None = None
    quantity: float | None = None
    size_label: str | None = None
    volume_ml_each: float | None = None
    total_volume_ml: float | None = None
    alcohol_units: float = 0
    explanation: str | None = None


class FoodData(BaseModel):
    items: list[str] = Field(default_factory=list)
    salt_level: str | None = None
    food_type: str | None = None


class ParsedHealthData(BaseModel):
    bp: HealthMetric = Field(default_factory=HealthMetric)
    sugar_level: int | None = None
    morning_sugar_level: int | None = None
    alcohol: AlcoholData = Field(default_factory=AlcoholData)
    food: FoodData = Field(default_factory=FoodData)
    water_ml: int | None = None
    symptoms: list[str] = Field(default_factory=list)
    notes: str | None = None


class DailyMemory(BaseModel):
    entries_today: int = 0
    alcohol_units_today: float = 0
    high_risk_entries_today: int = 0
    medium_risk_entries_today: int = 0
    water_ml_today: int | None = None
    morning_sugar_level: int | None = None
    last_sugar_level: int | None = None
    last_bp: HealthMetric = Field(default_factory=HealthMetric)
    latest_symptoms: list[str] = Field(default_factory=list)
    salty_entries_today: int = 0
    summary: str = "No earlier entries yet today."


class AnalyzeResponse(BaseModel):
    status: str = "complete"
    risk: str
    reasons: list[str]
    actions: list[str]
    summary: str
    assistant_message: str
    follow_up_questions: list[str] = Field(default_factory=list)
    knowledge: list[str] = Field(default_factory=list)
    parsed_data: ParsedHealthData
    daily_memory: DailyMemory = Field(default_factory=DailyMemory)
