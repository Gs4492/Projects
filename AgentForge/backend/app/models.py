from __future__ import annotations

from datetime import datetime
from typing import Any
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


AgentName = Literal["planner", "research", "execution", "critic", "memory"]
TaskStatus = Literal["pending", "in_progress", "completed", "needs_revision"]
RunStatus = Literal["queued", "running", "completed"]
EventType = Literal["log", "task_update", "artifact", "retry", "memory"]


class GoalRequest(BaseModel):
    goal: str = Field(min_length=3, max_length=500)


class TaskItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    owner: AgentName
    status: TaskStatus = "pending"
    details: str
    output: str | None = None
    attempts: int = 0


class AgentLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    agent: AgentName
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TimelineEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: EventType
    title: str
    body: str
    agent: AgentName | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RunState(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    goal: str
    status: RunStatus = "queued"
    tasks: list[TaskItem] = Field(default_factory=list)
    logs: list[AgentLog] = Field(default_factory=list)
    timeline: list[TimelineEvent] = Field(default_factory=list)
    result: str | None = None
    artifacts: dict[str, Any] = Field(default_factory=dict)
