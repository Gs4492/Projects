from collections import Counter, defaultdict
from math import sqrt


def _phase_for_over(over: int) -> str:
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


def analyze_bowling(deliveries: list[dict]):
    total_balls = len(deliveries)
    wickets = [d for d in deliveries if d.get("dismissal")]
    boundaries = [d for d in deliveries if (d.get("outcome") or "").lower() == "boundary"]

    # Bowling "problem clusters": zones leaking boundaries or failing to create wickets.
    pressure_counter = Counter((d.get("line", "unknown"), d.get("length", "unknown"), "run_leak") for d in boundaries)
    if not pressure_counter:
        pressure_counter = Counter((d.get("line", "unknown"), d.get("length", "unknown"), "no_wicket_pressure") for d in deliveries if (d.get("outcome") or "").lower() == "run")

    clusters = [
        {
            "line": line,
            "length": length,
            "dismissal": issue,
            "count": count,
        }
        for (line, length, issue), count in pressure_counter.items()
    ]
    clusters.sort(key=lambda x: x["count"], reverse=True)

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

        if d.get("dismissal"):
            row["dismissals"] += 1

        outcome = (d.get("outcome") or "").lower()
        if outcome == "boundary":
            row["false_shots"] += 1  # reused field = boundaries conceded
        if outcome == "dot":
            row["dots"] += 1

    high_risk_phase = "middle"
    highest_risk = -1.0

    for phase, row in phase_totals.items():
        balls = row["balls"]
        if balls == 0:
            row["risk_index"] = 0.0
            continue

        wicket_rate = row["dismissals"] / balls
        boundary_rate = row["false_shots"] / balls
        dot_rate = row["dots"] / balls

        # High risk when boundary rate is high and wicket threat is low.
        risk_index = (0.55 * boundary_rate) + (0.25 * (1 - wicket_rate)) + (0.2 * (1 - dot_rate))
        row["risk_index"] = round(risk_index, 3)

        if risk_index > highest_risk:
            highest_risk = risk_index
            high_risk_phase = phase

    boundary_rate_all = round((len(boundaries) / total_balls), 3) if total_balls else 0.0

    line_counts = Counter((d.get("line") or "unknown") for d in deliveries)
    length_counts = Counter((d.get("length") or "unknown") for d in deliveries)
    line_consistency = round((max(line_counts.values()) / total_balls), 3) if total_balls else 0.0
    length_consistency = round((max(length_counts.values()) / total_balls), 3) if total_balls else 0.0

    avg_speed_kph, speed_stability = _speed_metrics(deliveries)
    pitch_points = _pitch_points(deliveries)
    release_points = _release_points(deliveries)
    speed_by_over = _speed_by_over(deliveries)

    control_score = round((1 - boundary_rate_all) * 100, 1)
    pressure_score = round((1 - max(0.0, highest_risk)) * 100, 1) if total_balls else 0.0

    return {
        "total_balls": total_balls,
        "dismissals": len(wickets),
        "dismissals_by_bowler": {"self": len(wickets)},
        "dismissal_clusters": clusters,
        "false_shots": len(boundaries),
        "false_shot_rate": boundary_rate_all,
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
