from __future__ import annotations

from pathlib import Path
from typing import Any


def _safe_round(value: float, digits: int = 3) -> float:
    return round(float(value), digits)


def analyze_video_file(video_path: str | Path, role: str, dominant_hand: str, camera_angle: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "cv_status": "unavailable",
        "cv_engine": None,
        "video_metadata": {},
        "sampling_summary": {},
        "motion_windows": [],
        "movement_profile": {},
        "limitations": [],
    }

    try:
        import cv2  # type: ignore
    except ImportError:
        result["limitations"] = [
            "OpenCV is not installed in the runtime environment, so frame-level video analysis could not run.",
            "Install opencv-python in the video_service environment to enable real footage analysis.",
        ]
        return result

    path = Path(video_path)
    if not path.exists():
        result["cv_status"] = "missing_file"
        result["limitations"] = [f"Stored video file was not found: {path}"]
        return result

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        result["cv_status"] = "open_failed"
        result["limitations"] = ["OpenCV could not open the uploaded video file."]
        return result

    fps = float(capture.get(cv2.CAP_PROP_FPS) or 0.0)
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
    duration_seconds = (frame_count / fps) if fps > 0 else 0.0

    result["video_metadata"] = {
        "fps": _safe_round(fps, 2),
        "frame_count": frame_count,
        "duration_seconds": _safe_round(duration_seconds, 2),
        "width": width,
        "height": height,
        "camera_angle": camera_angle,
        "role": role,
        "dominant_hand": dominant_hand,
    }

    if frame_count <= 0 or width <= 0 or height <= 0:
        capture.release()
        result["cv_status"] = "invalid_video"
        result["limitations"] = ["Video metadata could not be read cleanly from the uploaded file."]
        return result

    target_samples = 180
    sample_interval = max(1, frame_count // target_samples)
    motion_series: list[dict[str, float]] = []
    centroid_series: list[dict[str, float]] = []
    prev_gray = None
    processed_frames = 0
    sampled_frames = 0
    center_samples = 0
    left_energy_total = 0.0
    center_energy_total = 0.0
    right_energy_total = 0.0

    while True:
        ok, frame = capture.read()
        if not ok:
            break

        processed_frames += 1
        if processed_frames % sample_interval != 0:
            continue

        sampled_frames += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        gray = cv2.resize(gray, (96, 54))

        if prev_gray is None:
            prev_gray = gray
            continue

        diff = cv2.absdiff(gray, prev_gray)
        _, thresh = cv2.threshold(diff, 22, 255, cv2.THRESH_BINARY)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        total_energy = float(thresh.mean() / 255.0)
        h, w = thresh.shape
        third = max(1, w // 3)
        left_energy = float(thresh[:, :third].mean() / 255.0)
        center_energy = float(thresh[:, third:2 * third].mean() / 255.0)
        right_energy = float(thresh[:, 2 * third:].mean() / 255.0)

        left_energy_total += left_energy
        center_energy_total += center_energy
        right_energy_total += right_energy

        moments = cv2.moments(thresh)
        if moments["m00"] > 0:
            cx = float(moments["m10"] / moments["m00"]) / float(w)
            cy = float(moments["m01"] / moments["m00"]) / float(h)
            centroid_series.append({"x": cx, "y": cy, "energy": total_energy})
            if 0.38 <= cx <= 0.62:
                center_samples += 1

        time_sec = processed_frames / fps if fps > 0 else float(processed_frames)
        motion_series.append(
            {
                "time": _safe_round(time_sec, 2),
                "energy": _safe_round(total_energy, 4),
                "left": _safe_round(left_energy, 4),
                "center": _safe_round(center_energy, 4),
                "right": _safe_round(right_energy, 4),
            }
        )
        prev_gray = gray

    capture.release()

    if not motion_series:
        result["cv_status"] = "no_samples"
        result["sampling_summary"] = {
            "processed_frames": processed_frames,
            "sampled_frames": sampled_frames,
            "sample_interval": sample_interval,
        }
        result["limitations"] = ["No usable sampled frames were extracted from the uploaded video."]
        return result

    energies = [point["energy"] for point in motion_series]
    avg_energy = sum(energies) / len(energies)
    peak_energy = max(energies)
    energy_sorted = sorted(energies)
    peak_threshold = energy_sorted[max(0, int(len(energy_sorted) * 0.85) - 1)]
    low_threshold = energy_sorted[max(0, int(len(energy_sorted) * 0.20) - 1)]

    windows: list[dict[str, float]] = []
    current: dict[str, Any] | None = None
    for point in motion_series:
        if point["energy"] >= peak_threshold and point["energy"] > 0:
            if current is None:
                current = {
                    "start_time": point["time"],
                    "end_time": point["time"],
                    "peak_energy": point["energy"],
                    "samples": 1,
                }
            else:
                current["end_time"] = point["time"]
                current["peak_energy"] = max(float(current["peak_energy"]), float(point["energy"]))
                current["samples"] = int(current["samples"]) + 1
        elif current is not None:
            windows.append(current)
            current = None
    if current is not None:
        windows.append(current)

    if centroid_series:
        mean_x = sum(item["x"] for item in centroid_series) / len(centroid_series)
        mean_y = sum(item["y"] for item in centroid_series) / len(centroid_series)
        x_variance = sum((item["x"] - mean_x) ** 2 for item in centroid_series) / len(centroid_series)
        y_variance = sum((item["y"] - mean_y) ** 2 for item in centroid_series) / len(centroid_series)
        lateral_spread = x_variance ** 0.5
        vertical_spread = y_variance ** 0.5
    else:
        mean_x = 0.5
        mean_y = 0.5
        lateral_spread = 0.0
        vertical_spread = 0.0

    total_side_energy = left_energy_total + center_energy_total + right_energy_total
    if total_side_energy > 0:
        left_ratio = left_energy_total / total_side_energy
        center_ratio = center_energy_total / total_side_energy
        right_ratio = right_energy_total / total_side_energy
    else:
        left_ratio = center_ratio = right_ratio = 0.0

    if max(left_ratio, center_ratio, right_ratio) == left_ratio:
        dominant_side = "left"
    elif max(left_ratio, center_ratio, right_ratio) == right_ratio:
        dominant_side = "right"
    else:
        dominant_side = "center"

    stability_score = max(0.0, min(100.0, 100.0 - ((lateral_spread * 130.0) + (vertical_spread * 90.0))))
    action_density = len(windows) / max(duration_seconds, 1.0)
    center_corridor_ratio = center_samples / max(len(centroid_series), 1)
    camera_confidence = 0.35
    if width >= 960 and height >= 540:
        camera_confidence += 0.2
    if duration_seconds >= 15:
        camera_confidence += 0.15
    if sampled_frames >= 40:
        camera_confidence += 0.15
    if camera_angle in {"side_on", "front_on"}:
        camera_confidence += 0.15
    camera_confidence = max(0.0, min(0.95, camera_confidence))

    result["cv_status"] = "ready"
    result["cv_engine"] = "opencv"
    result["sampling_summary"] = {
        "processed_frames": processed_frames,
        "sampled_frames": sampled_frames,
        "sample_interval": sample_interval,
        "average_motion_energy": _safe_round(avg_energy, 4),
        "peak_motion_energy": _safe_round(peak_energy, 4),
        "peak_threshold": _safe_round(peak_threshold, 4),
        "baseline_threshold": _safe_round(low_threshold, 4),
    }
    result["movement_profile"] = {
        "dominant_motion_side": dominant_side,
        "left_energy_ratio": _safe_round(left_ratio, 3),
        "center_energy_ratio": _safe_round(center_ratio, 3),
        "right_energy_ratio": _safe_round(right_ratio, 3),
        "average_centroid_x": _safe_round(mean_x, 3),
        "average_centroid_y": _safe_round(mean_y, 3),
        "lateral_spread": _safe_round(lateral_spread, 3),
        "vertical_spread": _safe_round(vertical_spread, 3),
        "stability_score": _safe_round(stability_score, 1),
        "center_corridor_ratio": _safe_round(center_corridor_ratio, 3),
        "action_density": _safe_round(action_density, 3),
        "camera_confidence": _safe_round(camera_confidence, 2),
    }
    result["motion_windows"] = [
        {
            "start_time": _safe_round(float(window["start_time"]), 2),
            "end_time": _safe_round(float(window["end_time"]), 2),
            "peak_energy": _safe_round(float(window["peak_energy"]), 4),
            "samples": int(window["samples"]),
        }
        for window in windows[:8]
    ]
    result["limitations"] = [
        "This version reads motion and body-shape changes from frames, but it does not yet perform ball tracking or exact line-length detection.",
        "Single-camera practice footage works best when the batter or bowler stays clearly visible through the full action.",
    ]
    return result
