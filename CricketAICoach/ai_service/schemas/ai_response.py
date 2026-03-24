from pydantic import BaseModel
from typing import List, Literal


class AIResponse(BaseModel):
    primary_weakness: str
    cause: Literal["technical", "tactical", "mental"]
    explanation: str
    evidence_points: List[str]
    improvements: List[str]
    next_match_plan: List[str]
    drill_routines: List[str]
    mental_cues: List[str]
    progress_markers: List[str]
