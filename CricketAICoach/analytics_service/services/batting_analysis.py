from collections import Counter, defaultdict
from math import sqrt


SAFE_SHOTS = {"leave", "defend", "none"}


def _is_dismissal(delivery: dict) -> bool:
    return bool(delivery.get("dismissal"))


def _is_false_shot(delivery: dict) -> bool:
    shot = (delivery.get("shot") or "").strip().lower()
    outcome = (delivery.get("outcome") or "").strip().lower()
    # Simple cricket heuristic: attacking shot ending in dot or wicket indicates low control.
    return shot not in SAFE_SHOTS and outcome in {"dot", "wicket"}


def _phase_for_over(over: int) -> str:
    # T20-oriented phase buckets for MVP analytics.
    if over <= 6:
        return "powerplay"
    if over <= 15:
        return "middle"
    return "death"


def _speed_metrics(deliveries: list[dict]):
    speeds = [float(d["speed_kph"]) for d in deliveries if d.get("speed_kph") is not None]
    if not speeds:
        return None, None

    avg = sum(speeds) / len(speeds)
    variance = sum((s - avg) ** 2 for s in speeds) / len(speeds)
    std = sqrt(variance)

    # Higher value means more stable speeds spell-to-spell.
    stability = 1 - (std / avg) if avg > 0 else 0
    stability = max(0.0, min(1.0, stability))
    return round(avg, 1), round(stability * 100, 1)


def _event_intensity(delivery: dict) -> int:
    outcome = (delivery.get("outcome") or "").lower()
    dismissal = delivery.get("dismissal")
    intensity = 1
    if outcome in {"boundary", "wicket"}:
        intensity = 2
    if dismissal:
        intensity = 3
    return intensity


def _pitch_points(deliveries: list[dict]):
    points = []
    for d in deliveries:
        if d.get("pitch_x") is None or d.get("pitch_y") is None:
            continue

        points.append(
            {
                "pitch_x": float(d["pitch_x"]),
                "pitch_y": float(d["pitch_y"]),
                "outcome": (d.get("outcome") or "unknown").lower(),
                "dismissal": d.get("dismissal"),
                "intensity": _event_intensity(d),
            }
        )
    return points


def _release_points(deliveries: list[dict]):
    points = []
    for d in deliveries:
        if d.get("release_x") is None:
            continue

        points.append(
            {
                "release_x": float(d["release_x"]),
                "release_y": float(d.get("release_y") or 2.0),
                "outcome": (d.get("outcome") or "unknown").lower(),
                "dismissal": d.get("dismissal"),
                "intensity": _event_intensity(d),
            }
        )
    return points


def _speed_by_over(deliveries: list[dict]):
    buckets = defaultdict(list)
    for d in deliveries:
        if d.get("speed_kph") is None:
            continue
        over = int(d.get("over") or 0)
        buckets[over].append(float(d["speed_kph"]))

    result = []
    for over in sorted(buckets.keys()):
        vals = buckets[over]
        result.append(
            {
                "over": over,
                "avg_speed_kph": round(sum(vals) / len(vals), 1),
                "balls": len(vals),
            }
        )
    return result


def analyze_batting(deliveries: list[dict]):
    total_balls = len(deliveries)
    dismissals = [d for d in deliveries if _is_dismissal(d)]
    false_shots = [d for d in deliveries if _is_false_shot(d)]

    dismissals_by_bowler = Counter(d.get("bowler_type", "unknown") for d in dismissals)

    cluster_counter = Counter(
        (
            d.get("line", "unknown"),
            d.get("length", "unknown"),
            d.get("dismissal", "unknown"),
        )
        for d in dismissals
    )
    dismissal_clusters = [
        {
            "line": line,
            "length": length,
            "dismissal": dismissal,
            "count": count,
        }
        for (line, length, dismissal), count in cluster_counter.items()
    ]
    dismissal_clusters.sort(key=lambda x: x["count"], reverse=True)

    phase_totals = {
        "powerplay": {"balls": 0, "dismissals": 0, "false_shots": 0, "dots": 0, "risk_index": 0.0},
        "middle": {"balls": 0, "dismissals": 0, "false_shots": 0, "dots": 0, "risk_index": 0.0},
        "death": {"balls": 0, "dismissals": 0, "false_shots": 0, "dots": 0, "risk_index": 0.0},
    }

    for d in deliveries:
        over = int(d.get("over", 0))
        phase = _phase_for_over(over)
        row = phase_totals[phase]
        row["balls"] += 1
        if _is_dismissal(d):
            row["dismissals"] += 1
        if _is_false_shot(d):
            row["false_shots"] += 1
        if (d.get("outcome") or "").lower() == "dot":
            row["dots"] += 1

    high_risk_phase = "middle"
    highest_risk = -1.0

    for phase, row in phase_totals.items():
        balls = row["balls"]
        if balls == 0:
            row["risk_index"] = 0.0
            continue

        dismissal_rate = row["dismissals"] / balls
        false_shot_rate_phase = row["false_shots"] / balls
        dot_rate = row["dots"] / balls

        # Weighted index to identify the phase where decision-making/control is weakest.
        risk_index = (0.5 * dismissal_rate) + (0.3 * false_shot_rate_phase) + (0.2 * dot_rate)
        row["risk_index"] = round(risk_index, 3)

        if risk_index > highest_risk:
            highest_risk = risk_index
            high_risk_phase = phase

    false_shot_rate = round((len(false_shots) / total_balls), 3) if total_balls else 0.0

    line_counts = Counter((d.get("line") or "unknown") for d in deliveries)
    length_counts = Counter((d.get("length") or "unknown") for d in deliveries)
    line_consistency = round((max(line_counts.values()) / total_balls), 3) if total_balls else 0.0
    length_consistency = round((max(length_counts.values()) / total_balls), 3) if total_balls else 0.0

    avg_speed_kph, speed_stability = _speed_metrics(deliveries)
    pitch_points = _pitch_points(deliveries)
    release_points = _release_points(deliveries)
    speed_by_over = _speed_by_over(deliveries)

    control_score = round((1 - false_shot_rate) * 100, 1)
    pressure_score = round((1 - max(0.0, highest_risk)) * 100, 1) if total_balls else 0.0

    return {
        "total_balls": total_balls,
        "dismissals": len(dismissals),
        "dismissals_by_bowler": dict(dismissals_by_bowler),
        "dismissal_clusters": dismissal_clusters,
        "false_shots": len(false_shots),
        "false_shot_rate": false_shot_rate,
        "phase_risk": phase_totals,
        "high_risk_phase": high_risk_phase,
        "pro_metrics": {
            "control_score": control_score,
            "pressure_score": pressure_score,
            "avg_speed_kph": avg_speed_kph,
            "speed_stability": speed_stability,
            "consistency": {
                "line_consistency": line_consistency,
                "length_consistency": length_consistency,
            },
        },
        "pitch_points": pitch_points,
        "release_points": release_points,
        "speed_by_over": speed_by_over,
    }
