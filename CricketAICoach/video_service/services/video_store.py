import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOAD_DIR = STORAGE_DIR / "uploads"
SESSION_DIR = STORAGE_DIR / "sessions"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SESSION_DIR.mkdir(parents=True, exist_ok=True)

CHUNK_SIZE = 1024 * 1024


async def save_upload(video: UploadFile) -> dict:
    session_id = str(uuid4())
    suffix = Path(video.filename or "session.mp4").suffix or ".mp4"
    stored_filename = f"{session_id}{suffix}"
    stored_path = UPLOAD_DIR / stored_filename

    file_size = 0
    with stored_path.open("wb") as handle:
        while True:
            chunk = await video.read(CHUNK_SIZE)
            if not chunk:
                break
            handle.write(chunk)
            file_size += len(chunk)

    await video.close()
    return {
        "session_id": session_id,
        "stored_filename": stored_filename,
        "stored_path": str(stored_path),
        "file_size": file_size,
    }


def _session_path(session_id: str) -> Path:
    return SESSION_DIR / f"{session_id}.json"


def create_session_record(**kwargs) -> dict:
    session_id = Path(kwargs["stored_filename"]).stem
    record = {
        "session_id": session_id,
        "created_at": datetime.utcnow().isoformat() + "Z",
        **kwargs,
        "analysis": None,
    }
    _session_path(session_id).write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def get_session(session_id: str) -> dict | None:
    path = _session_path(session_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def get_player_sessions(player_id: int) -> list[dict]:
    sessions: list[dict] = []
    for path in sorted(SESSION_DIR.glob("*.json"), reverse=True):
        data = json.loads(path.read_text(encoding="utf-8"))
        if int(data.get("player_id", -1)) == player_id:
            sessions.append(data)
    return sessions


def store_analysis(session_id: str, analysis: dict) -> None:
    session = get_session(session_id)
    if not session:
        return
    session["analysis"] = analysis
    _session_path(session_id).write_text(json.dumps(session, indent=2), encoding="utf-8")
