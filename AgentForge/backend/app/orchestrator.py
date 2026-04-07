from __future__ import annotations

import json
from textwrap import dedent

from app.models import AgentLog, TaskItem, TimelineEvent
from app.nvidia_client import nvidia_client
from app.store import store

MAX_EXECUTION_RETRIES = 2


class EventBroadcaster:
    def __init__(self) -> None:
        self.connections: dict[str, set] = {}

    def register(self, run_id: str, websocket) -> None:
        self.connections.setdefault(run_id, set()).add(websocket)

    def unregister(self, run_id: str, websocket) -> None:
        if run_id in self.connections:
            self.connections[run_id].discard(websocket)

    async def publish(self, run_id: str, event: dict) -> None:
        for websocket in list(self.connections.get(run_id, set())):
            await websocket.send_json(event)


broadcaster = EventBroadcaster()


async def emit_log(run_id: str, agent: str, message: str) -> None:
    log = AgentLog(agent=agent, message=message)
    store.add_log(run_id, log)
    await broadcaster.publish(run_id, {"type": "log", "payload": log.model_dump(mode="json")})


async def emit_timeline(run_id: str, event_type: str, title: str, body: str, agent: str | None = None) -> None:
    event = TimelineEvent(type=event_type, title=title, body=body, agent=agent)
    store.add_timeline_event(run_id, event)
    await broadcaster.publish(run_id, {"type": "timeline", "payload": event.model_dump(mode="json")})


async def emit_tasks(run_id: str) -> None:
    run = store.get_run(run_id)
    if not run:
        return
    await broadcaster.publish(
        run_id,
        {
            "type": "tasks",
            "payload": [task.model_dump(mode="json") for task in run.tasks],
        },
    )


async def emit_run(run_id: str) -> None:
    run = store.get_run(run_id)
    if not run:
        return
    await broadcaster.publish(
        run_id,
        {
            "type": "run",
            "payload": run.model_dump(mode="json"),
        },
    )


def parse_json_block(raw_text: str) -> dict | list | None:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            cleaned = "\n".join(lines[1:-1]).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start = min(
            [index for index in [cleaned.find("{"), cleaned.find("[")] if index != -1],
            default=-1,
        )
        if start == -1:
            return None
        trimmed = cleaned[start:]
        end_object = trimmed.rfind("}")
        end_array = trimmed.rfind("]")
        end = max(end_object, end_array)
        if end == -1:
            return None
        try:
            return json.loads(trimmed[: end + 1])
        except json.JSONDecodeError:
            return None


def memory_block(memories: list[dict[str, str]]) -> str:
    if not memories:
        return "- No prior lessons found"
    return "\n".join(f"- [{item['category']}] {item['note']}" for item in memories)


async def build_plan(goal: str, memories: list[dict[str, str]]) -> list[TaskItem]:
    plan_text = await nvidia_client.generate(
        dedent(
            """
            You are the Planner Agent for a software-building multi-agent system.
            Return JSON only in this exact shape:
            {
              "tasks": [
                {"title": "short task title", "owner": "planner|research|execution|critic", "details": "1-2 sentence description"}
              ]
            }
            Create exactly 4 tasks that move from understanding to research to execution to critique.
            """
        ).strip(),
        f"Goal: {goal}\nRelevant memory:\n{memory_block(memories)}",
    )

    parsed = parse_json_block(plan_text)
    if isinstance(parsed, dict) and isinstance(parsed.get("tasks"), list):
        tasks: list[TaskItem] = []
        for item in parsed["tasks"][:4]:
            if not isinstance(item, dict):
                continue
            owner = item.get("owner", "execution")
            if owner not in {"planner", "research", "execution", "critic"}:
                owner = "execution"
            tasks.append(
                TaskItem(
                    title=str(item.get("title", "Untitled task"))[:120],
                    owner=owner,
                    details=str(item.get("details", ""))[:1200] or f"Task for {goal}",
                )
            )
        if tasks:
            return tasks

    return [
        TaskItem(
            title="Clarify the product requirements",
            owner="planner",
            details=f"Define scope, user flow, and deliverables for: {goal}",
        ),
        TaskItem(
            title="Recommend the implementation approach",
            owner="research",
            details="Select the stack, libraries, and architecture to achieve the goal.",
        ),
        TaskItem(
            title="Produce the first implementation draft",
            owner="execution",
            details="Create a concrete build outline, code skeleton, and API/UI plan.",
        ),
        TaskItem(
            title="Review and improve the draft",
            owner="critic",
            details="Check for missing pieces, risks, and improvements before finalizing.",
        ),
    ]


async def run_agent(agent: str, goal: str, task: TaskItem, artifacts: dict, memories: list[dict[str, str]], feedback: str = "") -> str:
    artifact_text = json.dumps(artifacts, indent=2) if artifacts else "{}"
    prompts = {
        "planner": (
            "You are the Planner Agent. Produce a concise markdown brief with scope, key features, user flow, and success criteria.",
            f"Goal: {goal}\nTask: {task.title}\nTask details: {task.details}\nMemory:\n{memory_block(memories)}",
        ),
        "research": (
            "You are the Research Agent. Recommend the best technical approach, libraries, data flow, and architecture tradeoffs in markdown.",
            f"Goal: {goal}\nTask: {task.title}\nTask details: {task.details}\nAvailable artifacts:\n{artifact_text}\nMemory:\n{memory_block(memories)}",
        ),
        "execution": (
            dedent(
                """
                You are the Execution Agent.
                Produce markdown with these sections:
                1. Build Plan
                2. Backend Outline
                3. Frontend Outline
                4. Example API Contract
                5. Starter Code
                6. Risk Assessment And Improvement Roadmap
                Keep it practical and specific to the goal.
                If feedback is provided, directly improve the previous draft.
                """
            ).strip(),
            f"Goal: {goal}\nTask: {task.title}\nTask details: {task.details}\nAvailable artifacts:\n{artifact_text}\nFeedback to apply:\n{feedback or 'No feedback yet.'}",
        ),
        "critic": (
            dedent(
                """
                You are the Critic Agent.
                Return valid JSON only with no markdown fences and keep values concise:
                {
                  "approved": true,
                  "summary": "short verdict",
                  "improvements": ["improvement 1", "improvement 2"],
                  "final_result": "clean final response for the user",
                  "lesson": "short reusable lesson for future runs"
                }
                Approve only if the work is coherent and useful.
                """
            ).strip(),
            f"Goal: {goal}\nTask: {task.title}\nTask details: {task.details}\nAvailable artifacts:\n{artifact_text}",
        ),
    }

    system_prompt, user_prompt = prompts[agent]
    return await nvidia_client.generate(system_prompt, user_prompt)


async def process_non_execution_task(run_id: str, task: TaskItem, goal: str, memories: list[dict[str, str]]) -> None:
    run = store.get_run(run_id)
    if not run:
        return
    store.update_task(run_id, task.id, "in_progress", increment_attempt=True)
    await emit_tasks(run_id)
    await emit_log(run_id, task.owner, f"{task.owner.title()} agent is working on '{task.title}'.")
    output = await run_agent(task.owner, goal, task, run.artifacts, memories)
    artifact_key = f"{task.owner}_output"
    store.set_artifact(run_id, artifact_key, output)
    store.update_task(run_id, task.id, "completed", output)
    await emit_timeline(run_id, "artifact", f"{task.owner.title()} output ready", output[:700], task.owner)
    await emit_log(run_id, task.owner, f"{task.owner.title()} agent finished '{task.title}'.")
    await emit_tasks(run_id)
    await emit_run(run_id)


async def process_execution_and_critique(run_id: str, execution_task: TaskItem, critic_task: TaskItem, goal: str, memories: list[dict[str, str]]) -> None:
    run = store.get_run(run_id)
    if not run:
        return

    feedback = ""
    final_review: dict | None = None

    for attempt in range(1, MAX_EXECUTION_RETRIES + 2):
        store.update_task(run_id, execution_task.id, "in_progress", increment_attempt=True)
        await emit_tasks(run_id)
        await emit_log(run_id, "execution", f"Execution agent is building attempt {attempt} for '{execution_task.title}'.")
        await emit_timeline(run_id, "task_update", f"Execution attempt {attempt}", feedback or "Creating the first implementation draft.", "execution")

        execution_output = await run_agent("execution", goal, execution_task, run.artifacts, memories, feedback)
        artifact_key = f"execution_attempt_{attempt}"
        store.set_artifact(run_id, artifact_key, execution_output)
        store.set_artifact(run_id, "execution_output", execution_output)
        store.update_task(run_id, execution_task.id, "completed", execution_output)
        await emit_timeline(run_id, "artifact", f"Execution draft {attempt}", execution_output[:900], "execution")
        await emit_tasks(run_id)
        await emit_run(run_id)

        store.update_task(run_id, critic_task.id, "in_progress", increment_attempt=True)
        await emit_tasks(run_id)
        await emit_log(run_id, "critic", f"Critic is reviewing execution attempt {attempt}.")
        review_raw = await run_agent("critic", goal, critic_task, run.artifacts, memories)
        parsed_review = parse_json_block(review_raw)

        if not isinstance(parsed_review, dict):
            parsed_review = {
                "approved": False,
                "summary": "Critic output was malformed and needs another pass.",
                "improvements": [
                    "Return valid JSON with approved, summary, improvements, final_result, and lesson.",
                    "Keep the review concise so it does not get truncated.",
                ],
                "final_result": run.artifacts.get("execution_output", "No final result available."),
                "lesson": "Keep critic output short and strictly valid JSON.",
            }

        improvements = parsed_review.get("improvements", [])
        summary = str(parsed_review.get("summary", review_raw))
        approved = bool(parsed_review.get("approved", False))
        store.set_artifact(run_id, "critic_review", parsed_review)
        if isinstance(improvements, list) and improvements:
            store.set_artifact(run_id, "critic_improvements", improvements)
        store.update_task(
            run_id,
            critic_task.id,
            "completed" if approved else "needs_revision",
            summary,
        )
        await emit_timeline(run_id, "artifact", f"Critic review {attempt}", summary, "critic")
        await emit_tasks(run_id)
        await emit_run(run_id)

        if approved:
            final_review = parsed_review
            await emit_log(run_id, "critic", "Critic approved the improved output.")
            break

        feedback = "\n".join(f"- {item}" for item in improvements) if isinstance(improvements, list) else str(improvements)
        await emit_log(run_id, "critic", "Critic requested another pass from execution.")
        await emit_timeline(run_id, "retry", f"Retry requested after attempt {attempt}", feedback or summary, "critic")

        if attempt == MAX_EXECUTION_RETRIES + 1:
            final_review = parsed_review

    if final_review is None:
        final_review = {
            "final_result": run.artifacts.get("execution_output", "No final result available."),
            "lesson": "No reusable lesson captured.",
            "summary": "Execution completed without a structured critic result.",
            "approved": True,
        }

    run.result = str(final_review.get("final_result", run.artifacts.get("execution_output", "")))
    lesson = str(final_review.get("lesson", "Focus on clear scope and concrete deliverables."))
    store.set_artifact(run_id, "memory_lesson", lesson)
    store.save_memory(goal, lesson, "lesson")
    store.save_memory(goal, f"Final result: {run.result[:300]}", "result")
    await emit_timeline(run_id, "memory", "Lesson saved to memory", lesson, "memory")
    await emit_log(run_id, "memory", "Saved a reusable lesson and final result to SQLite memory.")


async def process_run(run_id: str) -> None:
    run = store.get_run(run_id)
    if not run:
        return

    run.status = "running"
    memories = store.get_memory(run.goal)
    if memories:
        memory_message = f"Loaded {len(memories)} reusable memory item(s) for similar goals."
        memory_preview = "\n".join(item["note"] for item in memories[:2])
    else:
        memory_message = "No prior memory found for similar goals."
        memory_preview = "Starting with a clean slate."
    await emit_log(run_id, "memory", memory_message)
    await emit_timeline(run_id, "memory", "Memory loaded", memory_preview[:700], "memory")

    tasks = await build_plan(run.goal, memories)
    store.set_tasks(run_id, tasks)
    await emit_log(run_id, "planner", "Planner created the initial task graph.")
    await emit_timeline(run_id, "task_update", "Task graph created", json.dumps([task.model_dump(mode='json') for task in tasks], indent=2)[:900], "planner")
    await emit_tasks(run_id)
    await emit_run(run_id)

    execution_task = next((task for task in tasks if task.owner == "execution"), None)
    critic_task = next((task for task in tasks if task.owner == "critic"), None)

    for task in tasks:
        if task.owner in {"execution", "critic"}:
            continue
        await process_non_execution_task(run_id, task, run.goal, memories)

    if execution_task and critic_task:
        await process_execution_and_critique(run_id, execution_task, critic_task, run.goal, memories)

    run.status = "completed"
    if not run.result:
        run.result = f"Goal '{run.goal}' was processed by the multi-agent workflow."
    await emit_run(run_id)
    await broadcaster.publish(
        run_id,
        {
            "type": "run_completed",
            "payload": {
                "runId": run.id,
                "status": run.status,
                "result": run.result,
                "artifacts": run.artifacts,
                "timeline": [event.model_dump(mode="json") for event in run.timeline],
            },
        },
    )
