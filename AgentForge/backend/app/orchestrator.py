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
    event = TimelineEvent(type=event_type, title=title, body=body[:2000], agent=agent)
    store.add_timeline_event(run_id, event)
    await broadcaster.publish(run_id, {"type": "timeline", "payload": event.model_dump(mode="json")})


async def emit_tasks(run_id: str) -> None:
    run = store.get_run(run_id)
    if not run:
        return
    await broadcaster.publish(run_id, {"type": "tasks", "payload": [task.model_dump(mode="json") for task in run.tasks]})


async def emit_run(run_id: str) -> None:
    run = store.get_run(run_id)
    if not run:
        return
    await broadcaster.publish(run_id, {"type": "run", "payload": run.model_dump(mode="json")})


def parse_json_block(raw_text: str) -> dict | list | None:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            cleaned = "\n".join(lines[1:-1]).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        for opener, closer in (("{", "}"), ("[", "]")):
            start = cleaned.find(opener)
            end = cleaned.rfind(closer)
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(cleaned[start : end + 1])
                except json.JSONDecodeError:
                    continue
    return None


def memory_block(memories: list[dict[str, str]]) -> str:
    if not memories:
        return "- No prior lessons found"
    return "\n".join(f"- [{item['category']}] {item['note']}" for item in memories)


def shorten(text: str, limit: int = 240) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else compact[: limit - 3] + "..."


def normalize_string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def normalize_object_list(value: object, expected_keys: list[str]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                normalized.append({key: str(item.get(key, "")).strip() for key in expected_keys})
    return [entry for entry in normalized if any(entry.values())]


def infer_domain(goal: str) -> str:
    lowered = goal.lower()
    if "expense" in lowered or "budget" in lowered or "finance" in lowered:
        return "expense tracker"
    if "resume" in lowered or "cv" in lowered:
        return "resume analyzer"
    if "sentiment" in lowered:
        return "sentiment analysis"
    if "todo" in lowered or "task manager" in lowered:
        return "task management"
    return "software product"


def build_domain_fallback(goal: str, domain: str) -> dict:
    if domain == "expense tracker":
        return {
            "solution_summary": "A production-ready expense tracker with a Flask API, SQLite persistence, a dashboard for totals and trends, and starter files for auth, expenses, and reporting.",
            "architecture_decisions": [
                {"title": "Flask app factory", "details": "Use an app factory with blueprints for auth, expenses, categories, and dashboard routes."},
                {"title": "SQLite plus SQLAlchemy", "details": "Store users, categories, and expenses with foreign keys and indexed date/category queries."},
            ],
            "api_contract": [
                {"method": "POST", "path": "/api/auth/login", "purpose": "Authenticate a user", "request": '{"email":"demo@example.com","password":"secret"}', "response": '{"access_token":"jwt-token"}'},
                {"method": "GET", "path": "/api/expenses", "purpose": "List expenses with optional filters", "request": "Query params: month, category", "response": '[{"id":1,"amount":42.5,"category":"Travel"}]'},
                {"method": "POST", "path": "/api/expenses", "purpose": "Create an expense", "request": '{"amount":42.5,"category_id":2,"spent_at":"2026-04-07"}', "response": '{"id":12,"status":"created"}'},
                {"method": "GET", "path": "/api/dashboard/summary", "purpose": "Return totals and trends for the dashboard", "request": "No body", "response": '{"monthly_total":1200,"top_categories":[...]}'},
            ],
            "starter_files": [
                {"path": "backend/app.py", "description": "Flask app factory and blueprint registration", "code": "from flask import Flask\n\nfrom routes.expenses import expenses_bp\n\ndef create_app():\n    app = Flask(__name__)\n    app.config.from_object('config.Config')\n    app.register_blueprint(expenses_bp, url_prefix='/api/expenses')\n    return app\n"},
                {"path": "backend/models.py", "description": "SQLite models for users, categories, and expenses", "code": "from flask_sqlalchemy import SQLAlchemy\n\ndb = SQLAlchemy()\n\nclass Expense(db.Model):\n    id = db.Column(db.Integer, primary_key=True)\n    amount = db.Column(db.Float, nullable=False)\n    spent_at = db.Column(db.Date, nullable=False)\n    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))\n"},
                {"path": "backend/templates/dashboard.html", "description": "Dashboard shell for totals and recent expenses", "code": "<section>\n  <h1>Expense Tracker</h1>\n  <div id='summary-cards'></div>\n  <table id='recent-expenses'></table>\n</section>\n"},
            ],
            "file_tree": [
                "backend/app.py",
                "backend/config.py",
                "backend/models.py",
                "backend/routes/auth.py",
                "backend/routes/expenses.py",
                "backend/templates/dashboard.html",
                "tests/test_expenses_api.py",
            ],
            "test_plan": [
                "Validate login, token expiry, and unauthorized expense creation.",
                "Verify expense totals and category filters across multiple months.",
                "Test dashboard summary responses and CSV export behavior.",
            ],
            "deployment_checklist": [
                "Run Gunicorn behind Nginx and mount a persistent SQLite volume or switch to Postgres for scale.",
                "Set secret keys, JWT settings, and environment-specific config through env vars.",
                "Enable request logging, backups, and health checks before release.",
            ],
            "risks": [
                "SQLite write contention can become a bottleneck under heavy concurrent usage.",
                "Incorrect currency and timezone handling can distort reports and summaries.",
            ],
            "next_steps": [
                "Expand the starter files into a runnable scaffold.",
                "Add export features and monthly budget alerts.",
            ],
            "raw_markdown": goal,
        }

    return {
        "solution_summary": f"A production-ready {domain} app with a Flask backend, dashboard UI, defined routes, starter files, tests, and deployment checks.",
        "architecture_decisions": [
            {"title": "Modular backend", "details": f"Separate the {domain} backend into blueprints or modules for easier testing and scaling."},
            {"title": "Dashboard-first UX", "details": "Keep the core user workflow visible through summary cards, filtered lists, and status feedback."},
        ],
        "api_contract": [
            {"method": "GET", "path": "/health", "purpose": "Report service readiness", "request": "No body", "response": '{"status":"ok"}'},
            {"method": "POST", "path": "/api/items", "purpose": "Create the primary domain object", "request": '{"name":"example"}', "response": '{"id":1,"status":"created"}'},
        ],
        "starter_files": [
            {"path": "backend/app.py", "description": "Flask entrypoint", "code": "from flask import Flask\n\ndef create_app():\n    app = Flask(__name__)\n    return app\n"},
        ],
        "file_tree": ["backend/app.py", "backend/routes.py", "backend/templates/dashboard.html", "tests/test_api.py"],
        "test_plan": ["Validate core create/read/update/delete flows.", "Test dashboard rendering and error states."],
        "deployment_checklist": ["Externalize config.", "Enable logging and health checks."],
        "risks": ["Scope drift can introduce unrelated features.", "Missing validation can cause inconsistent data."],
        "next_steps": ["Generate a runnable scaffold.", "Refine the most important workflow."],
        "raw_markdown": goal,
    }


def normalize_execution_artifact(goal: str, raw_text: str, parsed: dict | None) -> dict:
    domain = infer_domain(goal)
    if isinstance(parsed, dict):
        summary = str(parsed.get("solution_summary", "")).strip() or shorten(raw_text, 320)
        architecture = normalize_object_list(parsed.get("architecture_decisions"), ["title", "details"])
        api_contract = normalize_object_list(parsed.get("api_contract"), ["method", "path", "purpose", "request", "response"])
        starter_files = normalize_object_list(parsed.get("starter_files"), ["path", "description", "code"])
        file_tree = normalize_string_list(parsed.get("file_tree"))
        test_plan = normalize_string_list(parsed.get("test_plan"))
        deployment = normalize_string_list(parsed.get("deployment_checklist"))
        risks = normalize_string_list(parsed.get("risks"))
        next_steps = normalize_string_list(parsed.get("next_steps"))

        banned_tokens = ["/predict", "sentiment", "distilbert", "model bias", "cold start"] if domain == "expense tracker" else []
        combined = " ".join([summary] + file_tree + [route.get("path", "") for route in api_contract] + risks + next_steps).lower()
        scope_mismatch = any(token in combined for token in banned_tokens)

        if summary and (architecture or api_contract or starter_files or file_tree) and not scope_mismatch:
            return {
                "solution_summary": summary,
                "architecture_decisions": architecture,
                "api_contract": api_contract,
                "starter_files": starter_files,
                "file_tree": file_tree,
                "test_plan": test_plan,
                "deployment_checklist": deployment,
                "risks": risks,
                "next_steps": next_steps,
                "raw_markdown": raw_text,
            }

    return build_domain_fallback(goal, domain)


def summarize_execution_artifact(artifact: dict) -> str:
    file_count = len(artifact.get("starter_files", []))
    endpoint_count = len(artifact.get("api_contract", []))
    risk_count = len(artifact.get("risks", []))
    return f"Prepared {file_count} starter files, {endpoint_count} API endpoints, and {risk_count} highlighted risks."


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
            tasks.append(TaskItem(title=str(item.get("title", "Untitled task"))[:120], owner=owner, details=str(item.get("details", ""))[:1200] or f"Task for {goal}"))
        if tasks:
            return tasks

    return [
        TaskItem(title="Clarify the product requirements", owner="planner", details=f"Define scope, user flow, and deliverables for: {goal}"),
        TaskItem(title="Recommend the implementation approach", owner="research", details="Select the stack, libraries, and architecture to achieve the goal."),
        TaskItem(title="Produce concrete deliverables", owner="execution", details="Create architecture decisions, API contracts, starter files, and a test-ready implementation draft."),
        TaskItem(title="Review and improve the draft", owner="critic", details="Check for missing pieces, risks, and improvements before finalizing."),
    ]


async def run_agent(agent: str, goal: str, task: TaskItem, artifacts: dict, memories: list[dict[str, str]], feedback: str = "") -> str:
    artifact_text = json.dumps(artifacts, indent=2) if artifacts else "{}"
    domain = infer_domain(goal)
    prompts = {
        "planner": (
            "You are the Planner Agent. Produce a concise markdown brief with scope, key features, user flow, and success criteria.",
            f"Goal: {goal}\nTask: {task.title}\nTask details: {task.details}\nMemory:\n{memory_block(memories)}",
        ),
        "research": (
            "You are the Research Agent. Recommend the best technical approach, libraries, data flow, and architecture tradeoffs in markdown with concrete recommendations.",
            f"Goal: {goal}\nTask: {task.title}\nTask details: {task.details}\nAvailable artifacts:\n{artifact_text}\nMemory:\n{memory_block(memories)}",
        ),
        "execution": (
            dedent(
                f"""
                You are the Execution Agent.
                The product domain is: {domain}.
                Stay strictly within that domain and do not introduce unrelated AI, sentiment, prediction, or model-serving features unless the goal explicitly asks for them.
                Return valid JSON only with this shape:
                {{
                  "solution_summary": "1 short paragraph",
                  "architecture_decisions": [{{"title": "", "details": ""}}],
                  "api_contract": [{{"method": "", "path": "", "purpose": "", "request": "", "response": ""}}],
                  "starter_files": [{{"path": "", "description": "", "code": ""}}],
                  "file_tree": ["path/one", "path/two"],
                  "test_plan": ["test item"],
                  "deployment_checklist": ["checklist item"],
                  "risks": ["risk item"],
                  "next_steps": ["next step"]
                }}
                Keep it compact.
                Include exactly 3 starter files and 4 API routes maximum.
                Keep each code snippet under 20 lines.
                If feedback is provided, fix those issues explicitly.
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
                  "strengths": ["strength"],
                  "improvements": ["improvement 1", "improvement 2"],
                  "final_result": "clean final response for the user",
                  "lesson": "short reusable lesson for future runs",
                  "release_readiness": "prototype|solid_mvp|production_candidate"
                }
                Approve only if the work is coherent, specific, and contains concrete deliverables aligned with the exact product domain.
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
    store.set_artifact(run_id, f"{task.owner}_output", output)
    store.update_task(run_id, task.id, "completed", shorten(output, 260))
    await emit_timeline(run_id, "artifact", f"{task.owner.title()} output ready", shorten(output, 700), task.owner)
    await emit_log(run_id, task.owner, f"{task.owner.title()} agent finished '{task.title}'.")
    await emit_tasks(run_id)
    await emit_run(run_id)


async def process_execution_and_critique(run_id: str, execution_task: TaskItem, critic_task: TaskItem, goal: str, memories: list[dict[str, str]]) -> None:
    run = store.get_run(run_id)
    if not run:
        return

    feedback = ""
    final_review: dict | None = None
    attempt_artifacts: list[dict] = []

    for attempt in range(1, MAX_EXECUTION_RETRIES + 2):
        store.update_task(run_id, execution_task.id, "in_progress", increment_attempt=True)
        await emit_tasks(run_id)
        await emit_log(run_id, "execution", f"Execution agent is building attempt {attempt} for '{execution_task.title}'.")
        await emit_timeline(run_id, "task_update", f"Execution attempt {attempt}", feedback or "Creating concrete deliverables.", "execution")

        execution_raw = await run_agent("execution", goal, execution_task, run.artifacts, memories, feedback)
        execution_structured = normalize_execution_artifact(goal, execution_raw, parse_json_block(execution_raw))
        attempt_artifacts.append(execution_structured)
        store.set_artifact(run_id, "execution_attempts", attempt_artifacts)
        store.set_artifact(run_id, f"execution_attempt_{attempt}", execution_structured)
        store.set_artifact(run_id, "execution_output", execution_structured)
        store.update_task(run_id, execution_task.id, "completed", summarize_execution_artifact(execution_structured))
        await emit_timeline(run_id, "artifact", f"Execution draft {attempt}", summarize_execution_artifact(execution_structured), "execution")
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
                "strengths": [],
                "improvements": [
                    "Return valid JSON with approved, summary, strengths, improvements, final_result, lesson, and release_readiness.",
                    "Keep the review concise so it does not get truncated.",
                ],
                "final_result": execution_structured.get("solution_summary", "No final result available."),
                "lesson": "Keep critic output short and strictly valid JSON.",
                "release_readiness": "prototype",
            }

        approved = bool(parsed_review.get("approved", False))
        improvements = normalize_string_list(parsed_review.get("improvements"))
        strengths = normalize_string_list(parsed_review.get("strengths"))
        summary = str(parsed_review.get("summary", review_raw)).strip() or "Critic completed a review."
        parsed_review["improvements"] = improvements
        parsed_review["strengths"] = strengths
        store.set_artifact(run_id, "critic_review", parsed_review)
        store.set_artifact(run_id, "critic_improvements", improvements)
        store.set_artifact(run_id, "critic_strengths", strengths)
        store.update_task(run_id, critic_task.id, "completed" if approved else "needs_revision", summary)
        await emit_timeline(run_id, "artifact", f"Critic review {attempt}", summary, "critic")
        await emit_tasks(run_id)
        await emit_run(run_id)

        if approved:
            final_review = parsed_review
            await emit_log(run_id, "critic", "Critic approved the improved output.")
            break

        feedback = "\n".join(f"- {item}" for item in improvements) or summary
        await emit_log(run_id, "critic", "Critic requested another pass from execution.")
        await emit_timeline(run_id, "retry", f"Retry requested after attempt {attempt}", feedback, "critic")
        if attempt == MAX_EXECUTION_RETRIES + 1:
            final_review = parsed_review

    if final_review is None:
        final_review = {
            "final_result": run.artifacts.get("execution_output", {}).get("solution_summary", "No final result available."),
            "lesson": "No reusable lesson captured.",
            "summary": "Execution completed without a structured critic result.",
            "approved": True,
            "strengths": [],
            "improvements": [],
            "release_readiness": "prototype",
        }

    run.result = str(final_review.get("final_result", run.artifacts.get("execution_output", {}).get("solution_summary", "")))
    lesson = str(final_review.get("lesson", "Focus on clear scope and concrete deliverables."))
    store.set_artifact(run_id, "memory_lesson", lesson)
    store.set_artifact(run_id, "release_readiness", str(final_review.get("release_readiness", "prototype")))
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
    await emit_timeline(run_id, "task_update", "Task graph created", json.dumps([task.model_dump(mode="json") for task in tasks], indent=2)[:900], "planner")
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
    await broadcaster.publish(run_id, {"type": "run_completed", "payload": {"runId": run.id, "status": run.status, "result": run.result, "artifacts": run.artifacts, "timeline": [event.model_dump(mode="json") for event in run.timeline]}})
