from typing import Literal
from pydantic import BaseModel, Field


BattingHand = Literal["R", "L", "right", "left"]
PlayerLevel = Literal["academy", "club", "school", "college", "semi_pro", "pro"]


class PlayerCreate(BaseModel):
    name: str = Field(min_length=1)
    batting_hand: BattingHand
    level: PlayerLevel


class PlayerResponse(BaseModel):
    id: int
    name: str
    batting_hand: str
    level: str
