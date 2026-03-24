from typing import List, Optional, Literal
from pydantic import BaseModel, Field


MatchFormat = Literal["T20", "ODI", "Test"]
BowlerType = Literal["pace", "spin"]
LineType = Literal["outside_off", "middle", "leg"]
LengthType = Literal["full", "good", "short"]
ShotType = Literal["drive", "cut", "defend", "pull", "sweep", "flick", "leave", "none"]
OutcomeType = Literal["dot", "run", "boundary", "wicket"]
DismissalType = Literal["caught", "bowled", "lbw", "stumped", "run_out", "hit_wicket"]


class MatchCreate(BaseModel):
    opponent: str = Field(min_length=1)
    match_date: str = Field(min_length=8)  # ISO-like date string, e.g. 2026-03-05
    format: MatchFormat


class DeliveryCreate(BaseModel):
    player_id: int = Field(ge=1)
    over: int = Field(ge=0)
    ball: int = Field(ge=1, le=10)
    bowler_type: BowlerType
    line: LineType
    length: LengthType
    shot: ShotType
    outcome: OutcomeType
    dismissal: Optional[DismissalType] = None

    # Pro-mode optional fields for richer tracking.
    pitch_x: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    pitch_y: Optional[float] = Field(default=None, ge=0.0, le=22.0)
    release_x: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    release_y: Optional[float] = Field(default=None, ge=0.0, le=3.0)
    speed_kph: Optional[float] = Field(default=None, ge=40.0, le=180.0)


class MatchWithDeliveries(BaseModel):
    match: MatchCreate
    deliveries: List[DeliveryCreate]


class BulkDeliveriesCreate(BaseModel):
    match_id: int = Field(ge=1)
    deliveries: List[DeliveryCreate]
