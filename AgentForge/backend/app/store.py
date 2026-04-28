from __future__ import annotations

import sqlite3
from pathlib import Path

from app.models import AgentLog, RunState, TaskItem, TimelineEvent


class RunStore:
    def __init__(self) -> None:
        self.runs: dict[str, RunState] = {}
        self.db_path = Path(__file__).resolve().parents[1] / "agent_memory.db"
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal TEXT NOT NULL,
                    note TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'lesson',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            columns = {row["name"] for row in connection.execute("PRAGMA table_info(memory_entries)").fetchall()}
            if "category" not in columns:
                connection.execute(
                    "ALTER TABLE memory_entries ADD COLUMN category TEXT NOT NULL DEFAULT 'lesson'"
                )

    def create_run(self, goal: str) -> RunState:
        run = RunState(goal=goal)
        self.runs[run.id] = run
        return run

    def get_run(self, run_id: str) -> RunState | None:
        return self.runs.get(run_id)

    def add_log(self, run_id: str, log: AgentLog) -> None:
        self.runs[run_id].logs.append(log)

    def add_timeline_event(self, run_id: str, event: TimelineEvent) -> None:
        self.runs[run_id].timeline.append(event)

    def set_tasks(self, run_id: str, tasks: list[TaskItem]) -> None:
        self.runs[run_id].tasks = tasks

    def update_task(self, run_id: str, task_id: str, status: str, output: str | None = None, increment_attempt: bool = False) -> None:
        run = self.runs[run_id]
        for task in run.tasks:
            if task.id == task_id:
                task.status = status
                if output is not None:
                    task.output = output
                if increment_attempt:
                    task.attempts += 1
                return

    def set_artifact(self, run_id: str, key: str, value: object) -> None:
        self.runs[run_id].artifacts[key] = value

    def save_memory(self, goal: str, note: str, category: str = "lesson") -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO memory_entries (goal, note, category) VALUES (?, ?, ?)",
                (goal, note, category),
            )

    def get_memory(self, goal: str) -> list[dict[str, str]]:
        tokens = [token for token in goal.lower().split() if len(token) > 3][:3]
        query = "SELECT note, category FROM memory_entries"
        params: list[str] = []
        if tokens:
            query += " WHERE " + " OR ".join(["LOWER(goal) LIKE ?" for _ in tokens])
            params = [f"%{token}%" for token in tokens]
        query += " ORDER BY id DESC LIMIT 8"
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [{"note": row["note"], "category": row["category"]} for row in rows]


store = RunStore()
