from __future__ import annotations

from pathlib import Path
from typing import Any

from services.video_cv import analyze_video_file


def _fmt_pct(value: float) -> str:
    return f"{round(value * 100, 1)}%"


def _front_side(hand: str) -> str:
    return "left side" if str(hand).lower() == "right" else "right side"


def _back_side(hand: str) -> str:
    return "right side" if str(hand).lower() == "right" else "left side"


def _front_leg(hand: str) -> str:
    return "left leg" if str(hand).lower() == "right" else "right leg"


def _back_leg(hand: str) -> str:
    return "right leg" if str(hand).lower() == "right" else "left leg"


def _batting_detail_bucket(stability: float, center_ratio: float) -> str:
    if stability < 58 and center_ratio < 0.35:
        return "major_drift"
    if stability < 70 or center_ratio < 0.42:
        return "moderate_drift"
    return "late_leak"


def _bowling_detail_bucket(stability: float, center_ratio: float) -> str:
    if stability < 55:
        return "unstable_release"
    if center_ratio < 0.35:
        return "alignment_leak"
    return "rhythm_leak"


def _build_batting_analysis(session: dict[str, Any], payload: Any, cv_result: dict[str, Any]) -> dict[str, Any]:
    metadata = cv_result.get("video_metadata", {})
    movement = cv_result.get("movement_profile", {})
    windows = cv_result.get("motion_windows", [])
    sample = cv_result.get("sampling_summary", {})
    limitations = list(cv_result.get("limitations", []))
    dominant_hand = getattr(payload, "dominant_hand", "right")
    front_side = _front_side(dominant_hand)
    back_side = _back_side(dominant_hand)
    front_leg = _front_leg(dominant_hand)
    back_leg = _back_leg(dominant_hand)

    if cv_result.get("cv_status") != "ready":
        return {
            "mode": "batting_video_analysis",
            "session_id": session["session_id"],
            "player_id": session["player_id"],
            "cv_status": cv_result.get("cv_status", "unavailable"),
            "summary": "I could not properly read this practice video yet, so I do not want to guess and give you poor advice.",
            "video_observations": limitations,
            "shot_selection_issues": [
                "Once the video opens cleanly, I can give you a stronger read on head position, front-leg stability, and whether the hands are reaching away from the body.",
            ],
            "technical_workons": [
                "Install OpenCV and rerun the same video so the frame analysis can work properly.",
            ],
            "recommended_drills": [],
            "mental_cues": ["No problem, this is just a setup issue. Once the video runs, we can coach from real footage."],
            "progress_markers": [],
            "video_metadata": metadata,
            "sampling_summary": sample,
            "movement_profile": movement,
            "motion_windows": windows,
            "limitations": limitations,
        }

    stability = float(movement.get("stability_score", 0.0))
    center_ratio = float(movement.get("center_corridor_ratio", 0.0))
    dominant_side = movement.get("dominant_motion_side", "center")
    detail_bucket = _batting_detail_bucket(stability, center_ratio)

    if detail_bucket == "major_drift":
        weakness = f"your {front_leg} and {front_side} are committing too early, so the bat swing is starting before the base is fully set"
        cause = f"your head and chest are not staying stacked over the {front_leg}, which makes the hands work away from the body"
    elif detail_bucket == "moderate_drift":
        weakness = f"your base is there, but your {front_side} gets a little eager and the swing loses shape through contact"
        cause = f"your balance is leaking just before commitment, so the bat path starts to travel with the body instead of under the eyes"
    else:
        weakness = f"you look composed early, but late in the shot your {front_side} keeps moving and control slips"
        cause = f"this is a smaller timing leak than a big technical fault, but it still affects how cleanly the bat comes through the ball"

    summary = (
        f"There is a good base here, so this is very workable. The main issue is not your setup, it is what happens just before and during contact. "
        f"Your {front_side} is committing a fraction early, and because the head does not stay quiet for long enough, the body continues moving through the shot. "
        f"That movement pulls the hands away from the body and the bat path stops looking as straight and controlled as it should. "
        f"For a {str(dominant_hand).lower()}-hand batter, that usually means the {front_leg} is not holding the base strongly enough while the {back_side} chases balance. "
        f"The encouraging part is that this looks like a control-and-timing correction, not a full rebuild."
    )

    observations = [
        f"Your head position is close to good at the start, but it does not stay still long enough once the shot begins.",
        f"The {front_leg} should be giving you a stronger post to hit from, but at the moment it looks like it is allowing the body to keep drifting.",
        f"Once that drift starts, the hands begin reaching away from the body, which is why contact control drops.",
        f"The {back_leg} is then asked to recover balance late instead of helping you stay stable early.",
    ]
    if dominant_side != "center":
        observations.append(
            f"Most of the visible movement load is showing on the {dominant_side} side of the frame, which supports the idea that one side of the body is taking over instead of the whole base working together."
        )
    if windows:
        observations.append(
            "The clearest errors come in the parts of the clip where your body keeps travelling through contact instead of staying strong and still at the ball."
        )

    shot_issues = [
        f"You are starting the scoring movement before the {front_leg} has fully stabilized the base.",
        "That is why the shot begins to happen to you instead of you staying in charge of the shot.",
        f"When the body moves early, the hands from the {back_side} have to chase the ball rather than present the bat cleanly under the eyes.",
        "This is exactly the kind of issue that can make you feel rushed even when the ball itself is not especially dangerous.",
    ]

    workons = [
        f"Keep the head and chest quieter for longer so the {front_leg} becomes a stronger post at the point of contact.",
        f"Delay the {front_side} commitment slightly, especially on balls outside off or anything you want to drive on the rise.",
        "Let the hands stay tighter to the body at the start of the downswing so the bat comes down straighter.",
        f"Make the {back_leg} hold shape instead of using it to rescue balance late in the shot.",
        "In the first 12 to 18 balls of each net block, earn the drive by defending and leaving well first.",
        "If you clean up this timing point, your natural scoring game should open up without needing to force it.",
    ]

    drills = [
        f"Front-leg post drill: play 12 balls with the only focus on landing and holding the {front_leg} strong through contact for a two-second freeze.",
        "Leave-defend-drive ladder: first 6 balls leave, next 6 defend, next 6 drive only if the ball is truly in your scoring zone.",
        "Straight-bat gate drill: place two cones just outside the bat path and play through them without the hands reaching away early.",
        f"Head-over-knee drill: on every front-foot shot, check that the head finishes over the {front_leg} rather than falling away to the side.",
    ]

    mental_cues = [
        "Still head first, scoring option second.",
        f"Land the {front_leg}, then let the bat come through.",
        "You do not need to rush the shot. If you stay balanced, the runs will still be there.",
    ]

    progress = [
        f"In the next three sessions, look for more shots where the head stays over the {front_leg} through contact.",
        "You should start seeing fewer reaching drives and more clean straight-bat contacts.",
        "If the ball starts sounding cleaner off the middle without you feeling rushed, that is a strong sign the fix is working.",
    ]

    return {
        "mode": "batting_video_analysis",
        "session_id": session["session_id"],
        "player_id": session["player_id"],
        "cv_status": cv_result.get("cv_status"),
        "cv_engine": cv_result.get("cv_engine"),
        "summary": summary,
        "primary_weakness": weakness,
        "cause": cause,
        "video_observations": observations,
        "shot_selection_issues": shot_issues,
        "technical_workons": workons,
        "recommended_drills": drills,
        "mental_cues": mental_cues,
        "progress_markers": progress,
        "video_metadata": metadata,
        "sampling_summary": sample,
        "movement_profile": movement,
        "motion_windows": windows,
        "limitations": limitations,
    }


def _build_bowling_analysis(session: dict[str, Any], payload: Any, cv_result: dict[str, Any]) -> dict[str, Any]:
    metadata = cv_result.get("video_metadata", {})
    movement = cv_result.get("movement_profile", {})
    windows = cv_result.get("motion_windows", [])
    sample = cv_result.get("sampling_summary", {})
    limitations = list(cv_result.get("limitations", []))
    dominant_hand = getattr(payload, "dominant_hand", "right")
    front_side = _front_side(dominant_hand)
    back_side = _back_side(dominant_hand)
    front_leg = _front_leg(dominant_hand)
    back_leg = _back_leg(dominant_hand)

    if cv_result.get("cv_status") != "ready":
        return {
            "mode": "bowling_video_analysis",
            "session_id": session["session_id"],
            "player_id": session["player_id"],
            "cv_status": cv_result.get("cv_status", "unavailable"),
            "summary": "I could not properly read this bowling video yet, so I do not want to guess and give you poor advice.",
            "video_observations": limitations,
            "execution_issues": [
                "Once the video opens cleanly, I can give you a stronger read on front-leg bracing, head position, and release repeatability.",
            ],
            "technical_workons": [
                "Install OpenCV and rerun the same video so the frame analysis can work properly.",
            ],
            "recommended_drills": [],
            "mental_cues": ["No problem, this is just a setup issue. Once the video runs, we can coach from real footage."],
            "progress_markers": [],
            "video_metadata": metadata,
            "sampling_summary": sample,
            "movement_profile": movement,
            "motion_windows": windows,
            "limitations": limitations,
        }

    stability = float(movement.get("stability_score", 0.0))
    center_ratio = float(movement.get("center_corridor_ratio", 0.0))
    dominant_side = movement.get("dominant_motion_side", "center")
    detail_bucket = _bowling_detail_bucket(stability, center_ratio)

    if detail_bucket == "unstable_release":
        weakness = f"your action is changing too much through the final gather, and the {front_leg} is not bracing firmly enough at release"
        cause = f"your head and chest are drifting away from the target line, so the release point keeps moving"
    elif detail_bucket == "alignment_leak":
        weakness = f"your body is leaking away from the target line before the ball leaves the hand"
        cause = f"the {front_side} is opening too early and the release path is working around the target instead of through it"
    else:
        weakness = f"your stock action is there, but rhythm changes are making the release less repeatable"
        cause = f"the shape through the crease is not staying consistent once intent goes up"

    summary = (
        f"There is enough here to work with, so this is very coachable. The main issue is not effort, it is repeatability through release. "
        f"Your action shape changes a little too much just before the ball comes out, and that usually means the {front_leg} is not bracing strongly enough while the upper body drifts. "
        f"Once that happens, the release point moves and the stock ball becomes harder to trust. For a {str(dominant_hand).lower()}-arm action, the key is keeping the head, chest, and {front_side} travelling through the target together."
    )

    observations = [
        f"Your run-up and gather are giving you a base, but the {front_leg} is not turning that base into a firm release position often enough.",
        "The head is not staying stacked over the line of release for long enough, so the ball is more likely to come out from slightly different positions.",
        f"The {back_leg} then has to do extra work to recover shape late instead of helping the action stay aligned early.",
        "That is why the stock ball can feel harder to repeat than it should.",
    ]
    if dominant_side != "center":
        observations.append(
            f"Most of the visible movement load is showing on the {dominant_side} side of the frame, which supports the idea that one side of the action is taking over too much."
        )
    if windows:
        observations.append(
            "Your biggest misses come in the moments where the action shape changes just before release instead of staying tall and direct through the target."
        )

    issues = [
        "Your release position is changing more than it should from ball to ball.",
        f"The {front_leg} needs to give you a firmer block so the ball can leave the hand from a more stable base.",
        f"When the {front_side} opens too early, the chest and arm work around the line instead of straight through it.",
        "That is a normal stage in development, and it is usually fixed by repeatability work before anything more advanced.",
    ]

    workons = [
        f"Keep the head stacked over the base for longer so the {front_leg} can brace under a stable chest position.",
        f"Make the final two steps of the run-up look the same every time, so the {back_leg} and hips arrive in rhythm.",
        f"Let the {front_side} guide you through the target instead of opening away too early.",
        "Build stock-ball repeatability first, then add pace and variation once the release point feels trustworthy again.",
        "If you clean up the alignment, the rest of the spell should immediately feel calmer and more controlled.",
    ]

    drills = [
        "Target-corridor drill: 24 stock balls with a point only when the release and finish stay in the same channel.",
        f"Front-leg brace drill: bowl short sets focusing only on landing the {front_leg} firmly and finishing tall through the target.",
        "Rhythm pause drill: gather, pause for one beat, then bowl and check if the head and chest stay aligned through release.",
        "Two-speed set: 6 balls at control pace and 6 at match pace, keeping the action shape the same in both sets.",
    ]

    mental_cues = [
        "Stock ball first, variation later.",
        f"Brace the {front_leg}, then release through the target.",
        "Do not rush the release. Stay tall, stay aligned, and let the ball go from a stable base.",
    ]

    progress = [
        "In the next few sessions, look for more balls where the finish stays straight through the target.",
        "You should start feeling the stock ball come out with less effort and more trust.",
        "If the ball begins landing in the same channel without you forcing it, that is a strong sign the release shape is improving.",
    ]

    return {
        "mode": "bowling_video_analysis",
        "session_id": session["session_id"],
        "player_id": session["player_id"],
        "cv_status": cv_result.get("cv_status"),
        "cv_engine": cv_result.get("cv_engine"),
        "summary": summary,
        "primary_weakness": weakness,
        "cause": cause,
        "video_observations": observations,
        "execution_issues": issues,
        "technical_workons": workons,
        "recommended_drills": drills,
        "mental_cues": mental_cues,
        "progress_markers": progress,
        "video_metadata": metadata,
        "sampling_summary": sample,
        "movement_profile": movement,
        "motion_windows": windows,
        "limitations": limitations,
    }


def build_session_analysis(session: dict[str, Any], payload: Any) -> dict[str, Any]:
    stored_path = session.get("stored_path")
    if not stored_path:
        return {
            "mode": f"{session.get('role', 'batting')}_video_analysis",
            "session_id": session["session_id"],
            "player_id": session["player_id"],
            "cv_status": "missing_path",
            "summary": "Stored video path is missing, so frame analysis could not run.",
            "video_observations": ["This session record does not contain a readable stored_path."],
            "technical_workons": [],
            "recommended_drills": [],
            "mental_cues": [],
            "progress_markers": [],
            "limitations": ["Re-upload the video to create a valid session record."],
        }

    cv_result = analyze_video_file(
        video_path=Path(stored_path),
        role=session.get("role", "batting"),
        dominant_hand=getattr(payload, "dominant_hand", "right"),
        camera_angle=session.get("camera_angle", "side_on"),
    )

    if session.get("role") == "bowling":
        return _build_bowling_analysis(session, payload, cv_result)
    return _build_batting_analysis(session, payload, cv_result)
