import json
from typing import Any

from services.llm_client import call_llm


def _parse_json(text: str) -> dict[str, Any]:
    raw = text.strip()

    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        raw = raw[start : end + 1]

    return json.loads(raw)


def _fallback_advice(analytics_data: dict, role: str) -> dict[str, Any]:
    clusters = analytics_data.get("dismissal_clusters", [])
    high_risk_phase = analytics_data.get("high_risk_phase", "middle")
    phase_risk = analytics_data.get("phase_risk", {})
    false_shot_rate = analytics_data.get("false_shot_rate", 0)

    if role == "bowling":
        primary = "Execution drops when pressure rises, especially in repeat line-length pockets"
        explanation = (
            "The data points to a repeatable execution issue rather than random bad luck. "
            "Under pressure, your control pattern narrows and batters predict your release pattern, "
            "which leads to boundaries in specific zones. This is mainly technical-tactical: "
            "technical because repeated misses are in the same channels, tactical because recovery balls "
            "after boundaries are not consistently high-control options. Your next block should target "
            "repeatability first, variation second."
        )
        improvements = [
            "Rebuild base control with a 36-ball channel drill: 6 sets of 6 balls, score only if ball lands in target box.",
            "Run a pressure-over simulation (6 overs): every boundary conceded adds a penalty and forces a reset ball next.",
            "Practice two preset wicket sequences per batter type (right-hander and left-hander) and commit to them.",
            "Train release consistency with video checkpoints every 12 balls: head position, front-arm pull, wrist alignment.",
            f"In the {high_risk_phase} phase, reduce random slower-ball usage and use one stock pace-off option only.",
            "Work with a keeper/coach callout routine: line target before run-up, miss feedback after each ball.",
        ]
        drill_routines = [
            "Drill A - Hard-Length Ladder: 24 balls, hit hard-length corridor 18/24 minimum.",
            "Drill B - Yorker Gate: 18 yorkers through cone gate, target 12/18 minimum.",
            "Drill C - Comeback Ball: after each simulated boundary, bowl one high-control ball to top of off.",
            "Drill D - Two-Ball Plan: set-up ball + finishing ball repeated for 5 batters.",
        ]
        mental_cues = [
            "Pre-ball cue: pick one exact landing spot, then one backup spot.",
            "After boundary cue: exhale, reset field picture, execute stock ball first.",
            "Over-end cue: review only process metrics (execution), not runs conceded.",
        ]
        match_plan = [
            "Over 1-2: start with your highest-control length and avoid low-percentage variations.",
            "If two scoring balls happen in a row, immediately return to stock line outside off with protective field.",
            "Use one pre-planned over script in powerplay, one in middle, one in death.",
            "Attack stumps when batter premeditates movement; avoid chasing wide lines reactively.",
            "At death, protect your miss side with field before trying wicket ball.",
            "Track one micro-goal each over: at least 4/6 balls in plan corridor.",
        ]
        progress_markers = [
            "Line-hit rate above 70% in training sets.",
            "Boundary balls reduced by at least 20% over next 3 matches.",
            "At least 4 balls per over in planned zone in match analysis.",
        ]
    else:
        primary = "Dismissals are repeating in similar line-length situations under early pressure"
        explanation = (
            "This pattern is not random. Your dismissals and false shots are clustering in similar zones, "
            "which indicates a stable weakness in decision quality at the ball-selection stage. The technical "
            "issue appears in bat path and contact point on fuller or good-length balls, while the tactical issue "
            "is shot selection too early in the innings. The correction is to build a strict early-innings scoring map, "
            "train delayed decision-making, and use repeatable reset routines after dot-ball pressure."
        )
        improvements = [
            "Build a first-18-balls batting plan: only 3 safe scoring options, no expansion shots until settled.",
            "Run 30-ball outside-off discipline drill: leave/defend percentage target above 70% for risky channels.",
            "Practice contact-point drill with sidearm on full and good length balls, focusing on head over ball.",
            "Add a dot-ball response routine: after two dots, force a low-risk rotation option instead of boundary attempt.",
            f"During the {high_risk_phase} phase, lock one scoring zone and one no-shot zone before each over.",
            "Review every dismissal with trigger question: shot choice error or execution error, then assign specific fix.",
        ]
        drill_routines = [
            "Drill A - Decision Grid: coach calls line/length late, batter must choose leave/defend/score option instantly.",
            "Drill B - Straight-Bat Corridor: 24 balls, score only through V, penalty for hard hands outside line.",
            "Drill C - Pressure 12: start on 0(6), then rotate strike for next 12 balls with no high-risk shots.",
            "Drill D - Dismissal Replication: recreate last dismissal ball 15 times and practice corrected response.",
        ]
        mental_cues = [
            "Pre-ball cue: line first, then length, then shot - in that order.",
            "After false shot cue: reset stance, one deep breath, next ball default to high-control option.",
            "Over-end cue: assess process (choices) not outcome (runs) to avoid panic acceleration.",
        ]
        match_plan = [
            "First 10 balls: no premeditated big shot outside off stump.",
            "If bowler hits same zone twice, counter with safest scoring option, not force shot.",
            "Against full pace early, prioritize straight bat and late contact.",
            "Against spin in middle overs, set single-first target every 2 balls.",
            "If pressure rises, take one reset over with low-risk strike rotation only.",
            "Before death overs, pre-commit 2 boundary balls per over and defend rest with low-risk options.",
        ]
        progress_markers = [
            f"False-shot rate below {max(0.15, round(float(false_shot_rate) * 0.8, 3)):.3f} over next 3 matches.",
            "At least 70% controlled shots in first 18 balls faced.",
            "No repeat dismissal in same line-length cluster across next 3 innings.",
        ]

    evidence = []
    if clusters:
        c0 = clusters[0]
        evidence.append(
            f"Top cluster: {c0.get('count', 0)} events at {c0.get('line', 'unknown')} / {c0.get('length', 'unknown')} ({c0.get('dismissal', 'pattern')})."
        )
    if high_risk_phase in phase_risk:
        p = phase_risk[high_risk_phase]
        evidence.append(
            f"Highest risk phase: {high_risk_phase} (risk index {p.get('risk_index', 0)}; balls {p.get('balls', 0)})."
        )
    evidence.append("Pattern repeats across matches, so treat this as a trainable tendency, not one-off variance.")

    return {
        "primary_weakness": primary,
        "cause": "tactical",
        "explanation": explanation,
        "evidence_points": evidence[:6],
        "improvements": improvements,
        "next_match_plan": match_plan,
        "drill_routines": drill_routines,
        "mental_cues": mental_cues,
        "progress_markers": progress_markers,
    }


def _normalize_list(values: Any, min_len: int = 0, max_len: int = 8) -> list[str]:
    if not isinstance(values, list):
        return []
    items = [str(x).strip() for x in values if str(x).strip()]
    if len(items) > max_len:
        items = items[:max_len]
    return items if len(items) >= min_len else []


def _validate_response(data: dict[str, Any]) -> dict[str, Any]:
    required = {
        "primary_weakness",
        "cause",
        "explanation",
        "evidence_points",
        "improvements",
        "next_match_plan",
        "drill_routines",
        "mental_cues",
        "progress_markers",
    }
    if not required.issubset(data.keys()):
        raise ValueError("LLM output missing required keys")

    cause = str(data["cause"]).strip().lower()
    if cause not in {"technical", "tactical", "mental"}:
        data["cause"] = "tactical"

    evidence_points = _normalize_list(data["evidence_points"], min_len=3, max_len=6)
    improvements = _normalize_list(data["improvements"], min_len=5, max_len=8)
    next_match_plan = _normalize_list(data["next_match_plan"], min_len=5, max_len=8)
    drill_routines = _normalize_list(data["drill_routines"], min_len=4, max_len=8)
    mental_cues = _normalize_list(data["mental_cues"], min_len=3, max_len=6)
    progress_markers = _normalize_list(data["progress_markers"], min_len=3, max_len=6)

    if not all([evidence_points, improvements, next_match_plan, drill_routines, mental_cues, progress_markers]):
        raise ValueError("List fields are incomplete")

    data["primary_weakness"] = str(data["primary_weakness"]).strip()
    data["explanation"] = str(data["explanation"]).strip()
    data["cause"] = str(data["cause"]).strip().lower()

    if len(data["explanation"]) < 260:
        raise ValueError("Explanation too short")

    data["evidence_points"] = evidence_points
    data["improvements"] = improvements
    data["next_match_plan"] = next_match_plan
    data["drill_routines"] = drill_routines
    data["mental_cues"] = mental_cues
    data["progress_markers"] = progress_markers
    return data


def generate_coaching_advice(analytics_data: dict, role: str = "batting"):
    role = "bowling" if role == "bowling" else "batting"
    role_label = "bowling" if role == "bowling" else "batting"

    prompt = f"""
You are an elite cricket {role_label} coach AI for high-performance players.
You must reason only from the provided analytics JSON and never invent events.
For small samples, speak in tendencies and probabilities, not absolutes.
Your response must be specific enough that a real coach can run a session from it.

Input analytics:
{json.dumps(analytics_data, indent=2)}

Return JSON only with this exact schema:
{{
  "primary_weakness": "one clear sentence",
  "cause": "technical|tactical|mental",
  "explanation": "8-12 detailed sentences linking data pattern -> root cause -> consequences -> correction logic",
  "evidence_points": ["string", "string", "string", "string", "string", "string"],
  "improvements": ["string", "string", "string", "string", "string", "string"],
  "next_match_plan": ["string", "string", "string", "string", "string", "string"],
  "drill_routines": ["string", "string", "string", "string"],
  "mental_cues": ["string", "string", "string"],
  "progress_markers": ["string", "string", "string"]
}}

Rules:
- Evidence must reference analytics patterns (risk phase, clusters, rates, counts).
- Improvements must be concrete training actions with specific constraints or targets.
- Drill routines must be executable practice blocks (balls/reps/time/targets).
- Mental cues must be short in-the-moment routines (pre-ball / post-error / between overs).
- Next match plan must be explicit in-game rules by phase and trigger.
- Progress markers must be measurable over next 2-4 matches.
- No markdown, no extra keys, no generic motivational language.
"""

    try:
        llm_output = call_llm(prompt)
        parsed = _parse_json(llm_output)
        return _validate_response(parsed)
    except Exception:
        return _fallback_advice(analytics_data, role)
