from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from schemas.video import SessionAnalyzeRequest
from services.video_analysis import build_session_analysis
from services.video_store import (
    create_session_record,
    get_player_sessions,
    get_session,
    save_upload,
    store_analysis,
)

router = APIRouter(prefix="/video", tags=["Video"])


@router.post("/sessions")
async def create_video_session(
    player_id: int = Form(...),
    role: str = Form(default="batting"),
    session_name: str = Form(default="Net Session"),
    camera_angle: str = Form(default="side_on"),
    notes: str = Form(default=""),
    expected_balls: int = Form(default=24),
    video: UploadFile = File(...),
):
    if role not in {"batting", "bowling"}:
        raise HTTPException(status_code=400, detail="role must be batting or bowling")

    saved = await save_upload(video)
    session = create_session_record(
        player_id=player_id,
        role=role,
        session_name=session_name,
        camera_angle=camera_angle,
        notes=notes,
        expected_balls=expected_balls,
        original_filename=video.filename or "session.mp4",
        stored_filename=saved["stored_filename"],
        stored_path=saved["stored_path"],
        content_type=video.content_type or "application/octet-stream",
        file_size=saved["file_size"],
    )
    return session


@router.get("/sessions/{session_id}")
def video_session_detail(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    return session


@router.get("/players/{player_id}/sessions")
def player_video_sessions(player_id: int):
    return {"player_id": player_id, "sessions": get_player_sessions(player_id)}


@router.post("/sessions/{session_id}/analyze")
def analyze_video_session(session_id: str, payload: SessionAnalyzeRequest):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")

    analysis = build_session_analysis(session=session, payload=payload)
    store_analysis(session_id, analysis)
    return analysis
