from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
import httpx

from services.service_clients import (
    analyze_video_session,
    create_video_session,
    get_player,
    get_player_video_sessions,
    get_video_session,
)

router = APIRouter(tags=["Video"])


@router.post("/video/player/{player_id}/sessions")
async def gateway_create_video_session(
    player_id: int,
    role: str = Form(default="batting"),
    session_name: str = Form(default="Net Session"),
    camera_angle: str = Form(default="side_on"),
    notes: str = Form(default=""),
    expected_balls: int = Form(default=24),
    video: UploadFile = File(...),
):
    try:
        await get_player(player_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"player_service error: {exc.response.text}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"player_service unavailable: {exc}") from exc

    try:
        return await create_video_session(
            player_id=player_id,
            role=role,
            session_name=session_name,
            camera_angle=camera_angle,
            notes=notes,
            expected_balls=expected_balls,
            video=video,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"video_service error: {exc.response.text}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"video_service unavailable: {exc}") from exc


@router.get("/video/player/{player_id}/sessions")
async def gateway_player_video_sessions(player_id: int):
    try:
        await get_player(player_id)
        sessions = await get_player_video_sessions(player_id)
        return {"player_id": player_id, "sessions": sessions}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"service error: {exc.response.text}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"service unavailable: {exc}") from exc


@router.get("/video/sessions/{session_id}")
async def gateway_video_session_detail(session_id: str):
    try:
        return await get_video_session(session_id)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"video_service error: {exc.response.text}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"video_service unavailable: {exc}") from exc


@router.post("/video/sessions/{session_id}/analyze")
async def gateway_analyze_video_session(
    session_id: str,
    dominant_hand: str = Query(default="right"),
    practice_type: str = Query(default="nets"),
    surface_type: str = Query(default="turf"),
    bowling_type: str = Query(default="mixed"),
    focus_area: str = Query(default="shot selection"),
):
    try:
        return await analyze_video_session(
            session_id=session_id,
            dominant_hand=dominant_hand,
            practice_type=practice_type,
            surface_type=surface_type,
            bowling_type=bowling_type,
            focus_area=focus_area,
        )
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"video_service error: {exc.response.text}") from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"video_service unavailable: {exc}") from exc
