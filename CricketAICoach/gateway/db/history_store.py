import json
import sqlite3
from typing import Any, Optional

DB_NAME = "history.db"


def _conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_history_db() -> None:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id INTEGER NOT NULL,
            phase TEXT NOT NULL,
            last_matches INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def save_history(player_id: int, phase: str, last_matches: int, payload: dict[str, Any]) -> int:
    conn = _conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO analysis_history (player_id, phase, last_matches, payload_json)
        VALUES (?, ?, ?, ?)
        """,
        (player_id, phase, last_matches, json.dumps(payload)),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def list_history(player_id: int, phase: Optional[str] = None, limit: int = 20) -> list[dict[str, Any]]:
    conn = _conn()
    cur = conn.cursor()

    if phase:
        cur.execute(
            """
            SELECT id, player_id, phase, last_matches, payload_json, created_at
            FROM analysis_history
            WHERE player_id = ? AND phase = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (player_id, phase, limit),
        )
    else:
        cur.execute(
            """
            SELECT id, player_id, phase, last_matches, payload_json, created_at
            FROM analysis_history
            WHERE player_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (player_id, limit),
        )

    rows = cur.fetchall()
    conn.close()

    out = []
    for r in rows:
        out.append(
            {
                "id": r["id"],
                "player_id": r["player_id"],
                "phase": r["phase"],
                "last_matches": r["last_matches"],
                "payload": json.loads(r["payload_json"]),
                "created_at": r["created_at"],
            }
        )
    return out
