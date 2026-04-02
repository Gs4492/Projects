import json
import os
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None


BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"


def load_env_file() -> None:
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


load_env_file()

app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path="")

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "mistralai/mistral-small-24b-instruct")
NVIDIA_API_BASE_URL = os.getenv(
    "NVIDIA_API_BASE_URL", "https://integrate.api.nvidia.com/v1"
)


@app.get("/api/health")
def health():
    return jsonify(
        {
            "ok": True,
            "llmConfigured": bool(NVIDIA_API_KEY),
            "model": NVIDIA_MODEL,
        }
    )


@app.post("/api/generate-stack")
def generate_stack_route():
    payload = request.get_json(silent=True) or {}
    return jsonify(generate_stack(payload))


@app.post("/api/llm-suggestion")
def llm_suggestion_route():
    payload = request.get_json(silent=True) or {}
    deterministic = generate_stack(payload)

    if not NVIDIA_API_KEY:
        deterministic["llmEnabled"] = False
        deterministic["llmSummary"] = (
            "NVIDIA API key is not configured yet. The rule-based recommendation "
            "is still available."
        )
        return jsonify(deterministic)

    llm_result = fetch_llm_recommendation(payload, deterministic)
    llm_result["llmEnabled"] = True
    return jsonify(llm_result)


@app.post("/api/custom-builder")
def custom_builder_route():
    payload = request.get_json(silent=True) or {}
    deterministic = generate_stack(payload)
    result = fetch_custom_builder_result(payload, deterministic)
    return jsonify(result)


@app.post("/api/architecture-help")
def architecture_help_route():
    payload = request.get_json(silent=True) or {}
    result = fetch_architecture_help(payload)
    return jsonify(result)


@app.get("/")
def index():
    return send_from_directory(PUBLIC_DIR, "index.html")


@app.get("/<path:filename>")
def static_files(filename: str):
    return send_from_directory(PUBLIC_DIR, filename)


def normalize_answers(payload):
    features = payload.get("features") or {}
    return {
        "appTemplate": str(payload.get("appTemplate", "custom")).strip(),
        "productType": str(payload.get("productType", "C")).upper(),
      "priority": str(payload.get("priority", "A")).upper(),
      "frontendComfort": str(payload.get("frontendComfort", "A")).upper(),
      "backendPreference": str(payload.get("backendPreference", "C")).upper(),
      "region": "india" if payload.get("region") == "india" else "global",
      "features": {
          "login": bool(features.get("login")),
          "realtime": bool(features.get("realtime")),
          "ai": bool(features.get("ai")),
          "uploads": bool(features.get("uploads")),
          "payments": bool(features.get("payments")),
          "seo": bool(features.get("seo")),
      },
    }


def empty_builder_extras():
    return {
        "alternatives": [],
        "nextSteps": [],
        "notes": [],
        "architecture": {
            "style": "",
            "reason": "",
        },
        "projectStructure": [],
    }


def generate_stack(payload):
    answers = normalize_answers(payload)
    is_mvp = answers["priority"] == "A"
    is_scalable = answers["priority"] == "C"
    is_enterprise = answers["productType"] == "E"
    is_mobile = answers["productType"] == "D"

    frontend = "React"
    if answers["frontendComfort"] == "A":
        frontend = "HTML + Bootstrap"
    elif answers["frontendComfort"] == "C":
        frontend = "Next.js"

    if answers["features"]["seo"]:
        frontend = "Next.js"

    if is_mobile:
        frontend = "React Native"

    backend = "FastAPI"
    if answers["backendPreference"] == "A":
        backend = "Flask" if is_mvp else "FastAPI"
    elif answers["backendPreference"] == "B":
        backend = "NestJS" if is_scalable else "Express"

    if is_enterprise:
        backend = "NestJS"

    if answers["priority"] == "B":
        if answers["backendPreference"] == "A":
            backend = "FastAPI"
        elif answers["backendPreference"] == "B":
            backend = "Express"

    if not answers["features"]["login"]:
        auth = "Not needed"
    elif answers["backendPreference"] == "A" and answers["productType"] == "A":
        auth = "Session auth"
    elif is_enterprise:
        auth = "JWT with role-based access control"
    elif is_mvp:
        auth = "Clerk"
    else:
        auth = "JWT"

    database = "SQLite" if is_mvp else "PostgreSQL"
    if is_enterprise or answers["productType"] in {"B", "C"}:
        database = "PostgreSQL"
    if answers["features"]["ai"]:
        database += " + pgvector"

    realtime = "Not needed"
    if answers["features"]["realtime"]:
        realtime = (
            "Firebase / Supabase Realtime"
            if answers["frontendComfort"] == "A"
            else "WebSockets / Socket.io"
        )

    ai = "Not needed"
    if answers["features"]["ai"]:
        ai = "NVIDIA API"
        if is_scalable:
            ai += " + vector retrieval"

    storage = "Not needed"
    if answers["features"]["uploads"]:
        storage = "Cloudinary" if is_mvp else "S3 / Supabase Storage"

    payments = "Not needed"
    if answers["features"]["payments"]:
        payments = "Razorpay" if answers["region"] == "india" else "Stripe"

    deployment = "Frontend on Vercel, backend on Render" if is_mvp else "AWS / GCP / Azure"
    if answers["productType"] == "A" and is_mvp:
        deployment = "Vercel"
    if is_mobile:
        deployment = "Expo EAS for mobile, Render for backend"

    stack = {
        "frontend": frontend,
        "backend": backend,
        "auth": auth,
        "database": database,
        "realtime": realtime,
        "ai": ai,
        "storage": storage,
        "payments": payments,
        "deployment": deployment,
    }

    architecture = build_default_architecture(answers, stack)

    return {
        "answers": answers,
        "stack": stack,
        "summary": build_summary(answers, stack),
        **empty_builder_extras(),
        "architecture": architecture,
        "projectStructure": build_default_project_structure(
            stack, architecture["style"]
        ),
    }


def build_summary(answers, stack):
    reasons = []

    if answers["productType"] == "C":
        reasons.append(
            "AI product flow defaults toward a Python-friendly backend and vector-ready data layer."
        )
    if answers["priority"] == "A":
        reasons.append(
            "Fast MVP keeps the stack lighter so you can ship without too much setup."
        )
    if answers["frontendComfort"] == "A":
        reasons.append(
            "The frontend stays beginner-friendly to reduce setup and maintenance overhead."
        )
    if answers["features"]["ai"]:
        reasons.append(
            "AI support is included with a server-side NVIDIA integration so the API key stays off the client."
        )
    if answers["features"]["realtime"]:
        reasons.append(f"Realtime is included through {stack['realtime']}.")
    if answers["features"]["payments"]:
        reasons.append(
            f"Payments map to {stack['payments']} based on your target region."
        )

    return " ".join(reasons)


def build_default_alternatives(stack):
    alternatives = []

    if stack["database"] == "SQLite":
        alternatives.append(
            {
                "name": "PostgreSQL instead of SQLite",
                "whenToChoose": "Choose this when you expect multiple users, more writes, or production growth.",
                "stackFocus": "PostgreSQL is stronger long-term, while SQLite is lighter for a fast MVP.",
            }
        )

    if stack["frontend"] == "React":
        alternatives.append(
            {
                "name": "Next.js instead of React",
                "whenToChoose": "Choose this when you want built-in routing, SEO, or a more structured frontend setup.",
                "stackFocus": "React stays simpler, while Next.js gives more framework support as the app grows.",
            }
        )

    if stack["backend"] == "Flask":
        alternatives.append(
            {
                "name": "FastAPI instead of Flask",
                "whenToChoose": "Choose this when you want stronger typing, validation, and a cleaner API structure.",
                "stackFocus": "Flask is lighter to start, while FastAPI is usually better once the backend grows.",
            }
        )

    if stack["auth"] == "JWT":
        alternatives.append(
            {
                "name": "Clerk instead of custom JWT auth",
                "whenToChoose": "Choose this when you want faster setup and less auth maintenance.",
                "stackFocus": "JWT gives more control, while Clerk is usually faster to ship.",
            }
        )

    if stack["deployment"] in {"Vercel", "Vercel + Render"}:
        alternatives.append(
            {
                "name": "AWS or Azure instead of MVP hosting",
                "whenToChoose": "Choose this when infra control, scale, or enterprise requirements start to matter.",
                "stackFocus": "Vercel and Render are faster to launch, while cloud platforms offer more control later.",
            }
        )

    return alternatives[:3]


def build_default_architecture(answers, stack):
    if answers["productType"] == "E":
        style = "Modular monolith"
        reason = "This keeps one deployable backend while separating domains cleanly for enterprise complexity."
    elif answers["productType"] == "D":
        style = "Mobile client + API backend"
        reason = "A separate mobile app with one backend keeps delivery simple without over-engineering services."
    elif answers["features"]["ai"] or answers["productType"] in {"B", "C"}:
        style = "Monolith with clear modules"
        reason = "This is the simplest good structure for an app that needs auth, API routes, AI logic, and a database without jumping to microservices."
    else:
        style = "Simple monolith"
        reason = "One codebase and one backend is the fastest way to build and maintain an MVP."

    if answers["priority"] == "C":
        reason += " You can split parts into services later only if scale or team size demands it."

    return {
        "style": style,
        "reason": reason,
    }


def build_default_project_structure(stack, architecture_style):
    frontend_dir = "frontend/"
    if stack["frontend"] in {"Next.js", "React"}:
        frontend_dir = "frontend/\n  src/\n  components/\n  pages/ or app/\n  services/\n  styles/"
    elif stack["frontend"] == "React Native":
        frontend_dir = "mobile/\n  src/\n  screens/\n  components/\n  services/"
    elif stack["frontend"] == "HTML + Bootstrap":
        frontend_dir = "templates/\nstatic/\n  css/\n  js/\n  images/"

    backend_dir = "backend/"
    if stack["backend"] in {"FastAPI", "Flask"}:
        backend_dir = "backend/\n  app/\n    api/\n    services/\n    models/\n    schemas/\n    core/\n  tests/"
    elif stack["backend"] == "Django":
        backend_dir = "backend/\n  project/\n  apps/\n    users/\n    billing/\n    core/\n  templates/"
    elif stack["backend"] in {"Express", "NestJS"}:
        backend_dir = "backend/\n  src/\n    modules/\n    routes/ or controllers/\n    services/\n    db/\n  tests/"

    structure = [
        f"Architecture style: {architecture_style}",
        frontend_dir,
        backend_dir,
        "shared/\n  env/\n  docs/\n  scripts/",
    ]

    if stack["ai"] != "Not needed":
        structure.append("backend/app/services/ai/\n  prompts/\n  retrieval/\n  providers/")
    if stack["storage"] != "Not needed":
        structure.append("backend/app/services/storage/")
    if stack["auth"] != "Not needed":
        structure.append("backend/app/services/auth/ or apps/users/")

    return structure


def fetch_llm_recommendation(payload, deterministic):
    if requests is None:
        deterministic["llmSummary"] = (
            "The requests package is not installed yet, so the app is showing the "
            "rule-based recommendation only."
        )
        return deterministic

    prompt = "\n".join(
        [
            "You are a practical startup architect helping a founder choose a lightweight app stack.",
            "Given the user's answers and the deterministic stack output, return the best structured recommendation.",
            "Stay close to the deterministic stack unless there is a very strong reason to improve one field.",
            "Keep it lightweight, practical, and beginner-friendly.",
            "Return valid JSON only with this exact shape:",
            '{"stack":{"frontend":"","backend":"","auth":"","database":"","realtime":"","ai":"","storage":"","payments":"","deployment":""},"summary":""}',
            "The summary should be 2-4 sentences and read like the 'Why this fits' section.",
            "",
            f"User answers: {json.dumps(normalize_answers(payload))}",
            f"Deterministic stack: {json.dumps(deterministic['stack'])}",
        ]
    )

    response = requests.post(
        f"{NVIDIA_API_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": NVIDIA_MODEL,
            "temperature": 0.3,
            "max_tokens": 220,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert app architect. Return only valid JSON. "
                        "No markdown, no code fences, no extra commentary."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=30,
    )

    if not response.ok:
        deterministic["llmSummary"] = (
            f"NVIDIA API request failed with status {response.status_code}."
        )
        return deterministic

    data = response.json()
    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )

    if not content:
        deterministic["llmSummary"] = "The NVIDIA model did not return a recommendation."
        return deterministic

    normalized_content = strip_code_fence(content)

    try:
        parsed = json.loads(normalized_content)
        stack = parsed.get("stack") or {}
        summary = parsed.get("summary") or deterministic["summary"]

        merged_stack = {
            "frontend": stack.get("frontend") or deterministic["stack"]["frontend"],
            "backend": stack.get("backend") or deterministic["stack"]["backend"],
            "auth": stack.get("auth") or deterministic["stack"]["auth"],
            "database": stack.get("database") or deterministic["stack"]["database"],
            "realtime": stack.get("realtime") or deterministic["stack"]["realtime"],
            "ai": stack.get("ai") or deterministic["stack"]["ai"],
            "storage": stack.get("storage") or deterministic["stack"]["storage"],
            "payments": stack.get("payments") or deterministic["stack"]["payments"],
            "deployment": stack.get("deployment") or deterministic["stack"]["deployment"],
        }

        return {
            "answers": deterministic["answers"],
            "stack": merged_stack,
            "summary": summary,
            "llmSummary": summary,
            "alternatives": parsed.get("alternatives") or build_default_alternatives(merged_stack),
            "nextSteps": parsed.get("nextSteps", []),
            "notes": parsed.get("notes", []),
            "architecture": parsed.get("architecture")
            or build_default_architecture(deterministic["answers"], merged_stack),
            "projectStructure": parsed.get("projectStructure")
            or build_default_project_structure(
                merged_stack,
                (
                    parsed.get("architecture") or build_default_architecture(
                        deterministic["answers"], merged_stack
                    )
                )["style"],
            ),
        }
    except json.JSONDecodeError:
        deterministic["llmSummary"] = content
        return deterministic


def fetch_custom_builder_result(payload, deterministic):
    if requests is None or not NVIDIA_API_KEY:
        deterministic["summary"] = (
            "The app builder works best with the NVIDIA key configured, so the "
            "system is showing the default recommendation for now."
        )
        deterministic["notes"] = [
            "Add a product description and use the NVIDIA-backed mode for better alternatives and tradeoffs."
        ]
        return deterministic

    product_brief = str(payload.get("productBrief", "")).strip()
    must_haves = str(payload.get("mustHaves", "")).strip()
    template_key = str(payload.get("appTemplate", "custom")).strip()
    template_context = get_template_context(template_key)

    prompt = "\n".join(
        [
            "You are helping a founder design a lightweight but realistic application architecture.",
            "Use the form answers, selected app template, and custom product description to recommend a stack.",
            "Return valid JSON only.",
            "Use this exact shape:",
            '{"stack":{"frontend":"","backend":"","auth":"","database":"","realtime":"","ai":"","storage":"","payments":"","deployment":""},"summary":"","alternatives":[{"name":"","whenToChoose":"","stackFocus":""}],"nextSteps":[""],"notes":[""],"architecture":{"style":"","reason":""},"projectStructure":[""]}',
            "The summary should be 3-5 sentences and explain why the recommendation fits.",
            "Provide 2 or 3 alternatives with clear tradeoffs.",
            "Alternatives should say what is better than what, and when to switch.",
            "Use comparison language like 'X instead of Y' or 'choose X when...'.",
            "Provide 3 or 4 next steps.",
            "Choose an architecture style such as simple monolith, modular monolith, mobile client plus API backend, or microservices only if truly justified.",
            "Provide a practical starter project structure as a list of folder blocks.",
            "Notes should mention practical cautions or constraints.",
            "",
            f"Structured answers: {json.dumps(normalize_answers(payload))}",
            f"Product brief: {product_brief or 'Not provided'}",
            f"Must-have features or constraints: {must_haves or 'Not provided'}",
            f"Baseline stack: {json.dumps(deterministic['stack'])}",
        ]
    )

    response = requests.post(
        f"{NVIDIA_API_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": NVIDIA_MODEL,
            "temperature": 0.35,
            "max_tokens": 700,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert app architect. Return only valid JSON. "
                        "Keep recommendations practical, lightweight, and specific."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=45,
    )

    if not response.ok:
        deterministic["notes"] = [
            f"NVIDIA API request failed with status {response.status_code}."
        ]
        return deterministic

    content = (
        response.json()
        .get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )
    normalized_content = strip_code_fence(content)

    try:
        parsed = json.loads(normalized_content)
        stack = parsed.get("stack") or {}
        merged_stack = {
            "frontend": stack.get("frontend") or deterministic["stack"]["frontend"],
            "backend": stack.get("backend") or deterministic["stack"]["backend"],
            "auth": stack.get("auth") or deterministic["stack"]["auth"],
            "database": stack.get("database") or deterministic["stack"]["database"],
            "realtime": stack.get("realtime") or deterministic["stack"]["realtime"],
            "ai": stack.get("ai") or deterministic["stack"]["ai"],
            "storage": stack.get("storage") or deterministic["stack"]["storage"],
            "payments": stack.get("payments") or deterministic["stack"]["payments"],
            "deployment": stack.get("deployment") or deterministic["stack"]["deployment"],
        }
        architecture = parsed.get("architecture") or build_default_architecture(
            deterministic["answers"], merged_stack
        )
        return {
            "answers": deterministic["answers"],
            "stack": merged_stack,
            "summary": parsed.get("summary") or deterministic["summary"],
            "alternatives": parsed.get("alternatives") or build_default_alternatives(
                merged_stack
            ),
            "nextSteps": parsed.get("nextSteps") or [],
            "notes": parsed.get("notes") or [],
            "architecture": architecture,
            "projectStructure": parsed.get("projectStructure")
            or build_default_project_structure(merged_stack, architecture["style"]),
        }
    except json.JSONDecodeError:
        deterministic["summary"] = content or deterministic["summary"]
        deterministic["alternatives"] = build_default_alternatives(deterministic["stack"])
        deterministic["architecture"] = build_default_architecture(
            deterministic["answers"], deterministic["stack"]
        )
        deterministic["projectStructure"] = build_default_project_structure(
            deterministic["stack"], deterministic["architecture"]["style"]
        )
        deterministic["notes"] = [
            "The model returned an unstructured answer, so the app kept the main stack output."
        ]
        return deterministic


def fetch_architecture_help(payload):
    question = str(payload.get("question", "")).strip()
    if not question:
        return {
            "answer": "Ask a frontend/backend question and the app will suggest a structure.",
            "sections": [],
        }

    if requests is None or not NVIDIA_API_KEY:
        return {
            "answer": (
                "Architecture Q&A needs the NVIDIA key configured. Once enabled, "
                "you can ask how to split frontend, backend, auth, database, and deployment."
            ),
            "sections": [],
        }

    prompt = "\n".join(
        [
            "You are an architecture advisor for lightweight web apps.",
            "Answer the user's question clearly and practically.",
            "Return valid JSON only with this exact shape:",
            '{"answer":"","sections":[{"title":"","content":""}]}',
            "The answer should be concise but useful.",
            "Use sections for frontend, backend, data flow, deployment, or tradeoffs when helpful.",
            "",
            f"User question: {question}",
        ]
    )

    response = requests.post(
        f"{NVIDIA_API_BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {NVIDIA_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": NVIDIA_MODEL,
            "temperature": 0.3,
            "max_tokens": 700,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are an expert architect. Return only valid JSON and "
                        "keep the guidance implementation-oriented."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=45,
    )

    if not response.ok:
        return {
            "answer": f"NVIDIA API request failed with status {response.status_code}.",
            "sections": [],
        }

    content = (
        response.json()
        .get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
        .strip()
    )

    try:
        parsed = json.loads(strip_code_fence(content))
        return {
            "answer": parsed.get("answer") or "No answer returned.",
            "sections": parsed.get("sections") or [],
        }
    except json.JSONDecodeError:
        return {
            "answer": content or "The model did not return a valid answer.",
            "sections": [],
        }


def strip_code_fence(content):
    text = content.strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].strip() == "```":
        return "\n".join(lines[1:-1]).strip()

    return text



def get_template_context(template_key):
    templates = {
        "custom": {
            "name": "Custom idea",
            "description": "Flexible starting point for a product that does not fit a single known template.",
            "defaults": "Prefer lightweight full-stack choices and adapt to the user's brief.",
        },
        "marketplace": {
            "name": "Marketplace",
            "description": "Multi-sided app with listings, search, seller flows, transactions, moderation, and payments.",
            "defaults": "Prioritize auth, payments, search and filtering, media uploads, and admin tooling.",
        },
        "saas-dashboard": {
            "name": "SaaS dashboard",
            "description": "Authenticated product with team accounts, dashboards, CRUD flows, billing, and admin settings.",
            "defaults": "Prioritize maintainable frontend structure, API design, auth, billing, and analytics.",
        },
        "ai-chat-app": {
            "name": "AI chat app",
            "description": "Conversational app with model calls, prompt flows, chat history, file context, and optional retrieval.",
            "defaults": "Prioritize chat UX, token-efficient backend design, history storage, and AI orchestration.",
        },
        "internal-admin-tool": {
            "name": "Internal admin tool",
            "description": "Ops-focused interface for internal teams with forms, tables, approvals, and role-based access.",
            "defaults": "Prioritize delivery speed, reliability, simple auth, CRUD, and audit-friendly structure.",
        },
        "mobile-companion": {
            "name": "Mobile companion app",
            "description": "Mobile-first companion for an existing service with notifications, auth, and lightweight backend integration.",
            "defaults": "Prioritize mobile UX, shared APIs, sync, push notifications, and simple deployment paths.",
        },
    }
    return templates.get(template_key, templates["custom"])

if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    app.run(host="0.0.0.0", port=port, debug=True)





