import os
from typing import Any

import httpx


PLAYER_SERVICE_BASE = os.getenv("PLAYER_SERVICE_BASE", "http://127.0.0.1:8001")
MATCH_SERVICE_BASE = os.getenv("MATCH_SERVICE_BASE", "http://127.0.0.1:8002")
ANALYTICS_SERVICE_BASE = os.getenv("ANALYTICS_SERVICE_BASE", "http://127.0.0.1:8003")
AI_SERVICE_BASE = os.getenv("AI_SERVICE_BASE", "http://127.0.0.1:8004")
VIDEO_SERVICE_BASE = os.getenv("VIDEO_SERVICE_BASE", "http://127.0.0.1:8005")


async def get_player(player_id: int) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{PLAYER_SERVICE_BASE}/players/{player_id}")
    response.raise_for_status()
    return response.json()


async def get_player_deliveries(player_id: int, last_matches: int) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(
            f"{MATCH_SERVICE_BASE}/players/{player_id}/deliveries",
            params={"last_matches": last_matches},
        )
    response.raise_for_status()
    return response.json()


async def get_batting_analytics(player_id: int, last_matches: int) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{ANALYTICS_SERVICE_BASE}/analytics/batting/{player_id}",
            params={"last_matches": last_matches},
        )
    response.raise_for_status()
    return response.json()


async def get_bowling_analytics(player_id: int, last_matches: int) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{ANALYTICS_SERVICE_BASE}/analytics/bowling/{player_id}",
            params={"last_matches": last_matches},
        )
    response.raise_for_status()
    return response.json()


async def get_ai_coaching(player_id: int, last_matches: int) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(
            f"{AI_SERVICE_BASE}/ai/batting/{player_id}",
            params={"last_matches": last_matches},
        )
    response.raise_for_status()
    return response.json()


async def get_ai_bowling_coaching(player_id: int, last_matches: int) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(
            f"{AI_SERVICE_BASE}/ai/bowling/{player_id}",
            params={"last_matches": last_matches},
        )
    response.raise_for_status()
    return response.json()


async def create_video_session(
    player_id: int,
    role: str,
    session_name: str,
    camera_angle: str,
    notes: str,
    expected_balls: int,
    video,
) -> dict[str, Any]:
    video.file.seek(0)
    files = {
        "video": (
            video.filename or "session.mp4",
            video.file,
            video.content_type or "application/octet-stream",
        )
    }
    data = {
        "player_id": str(player_id),
        "role": role,
        "session_name": session_name,
        "camera_angle": camera_angle,
        "notes": notes,
        "expected_balls": str(expected_balls),
    }
    timeout = httpx.Timeout(connect=30.0, read=1800.0, write=1800.0, pool=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(f"{VIDEO_SERVICE_BASE}/video/sessions", data=data, files=files)
    response.raise_for_status()
    return response.json()


async def get_player_video_sessions(player_id: int) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{VIDEO_SERVICE_BASE}/video/players/{player_id}/sessions")
    response.raise_for_status()
    payload = response.json()
    return payload.get("sessions", [])


async def get_video_session(session_id: str) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{VIDEO_SERVICE_BASE}/video/sessions/{session_id}")
    response.raise_for_status()
    return response.json()


async def analyze_video_session(
    session_id: str,
    dominant_hand: str,
    practice_type: str,
    surface_type: str,
    bowling_type: str,
    focus_area: str,
) -> dict[str, Any]:
    payload = {
        "dominant_hand": dominant_hand,
        "practice_type": practice_type,
        "surface_type": surface_type,
        "bowling_type": bowling_type,
        "focus_area": focus_area,
    }
    timeout = httpx.Timeout(connect=30.0, read=1800.0, write=1800.0, pool=30.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(f"{VIDEO_SERVICE_BASE}/video/sessions/{session_id}/analyze", json=payload)
    response.raise_for_status()
    return response.json()

