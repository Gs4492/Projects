from pydantic import BaseModel, Field


class SessionAnalyzeRequest(BaseModel):
    dominant_hand: str = Field(default="right")
    practice_type: str = Field(default="nets")
    surface_type: str = Field(default="turf")
    bowling_type: str = Field(default="mixed")
    focus_area: str = Field(default="shot selection")
