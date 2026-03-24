from pydantic import BaseModel
from typing import Dict, List, Optional


class DismissalCluster(BaseModel):
    line: str
    length: str
    dismissal: str
    count: int


class PhaseRisk(BaseModel):
    balls: int
    dismissals: int
    false_shots: int
    dots: int
    risk_index: float


class ConsistencyMetrics(BaseModel):
    line_consistency: float
    length_consistency: float


class ProMetrics(BaseModel):
    control_score: float
    pressure_score: float
    avg_speed_kph: Optional[float] = None
    speed_stability: Optional[float] = None
    consistency: ConsistencyMetrics


class PitchPoint(BaseModel):
    pitch_x: float
    pitch_y: float
    outcome: str
    dismissal: Optional[str] = None
    intensity: int


class ReleasePoint(BaseModel):
    release_x: float
    release_y: float
    outcome: str
    dismissal: Optional[str] = None
    intensity: int


class OverSpeed(BaseModel):
    over: int
    avg_speed_kph: float
    balls: int


class BattingAnalytics(BaseModel):
    total_balls: int
    dismissals: int
    dismissals_by_bowler: Dict[str, int]
    dismissal_clusters: List[DismissalCluster]
    false_shots: int
    false_shot_rate: float
    phase_risk: Dict[str, PhaseRisk]
    high_risk_phase: str
    pro_metrics: ProMetrics
    pitch_points: List[PitchPoint]
    release_points: List[ReleasePoint]
    speed_by_over: List[OverSpeed]
