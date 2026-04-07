# AgentForge

AgentForge is an agentic AI app that turns a product idea into a structured starter project.

Instead of giving one chatbot-style answer, it runs a small AI workflow:
- a planner defines the scope
- a research agent recommends the approach
- an execution agent creates concrete deliverables
- a critic reviews the result and suggests improvements
- a memory layer saves reusable lessons from past runs

## What The App Does

You enter a goal such as:

`Design a production-ready expense tracker app with Flask backend, dashboard UI, REST API, SQLite schema, starter files, test plan, deployment checklist, and a risk review.`

AgentForge then:
- breaks the goal into tasks
- shows live agent progress
- generates architecture decisions
- creates API contract suggestions
- drafts starter files
- produces a test plan and deployment checklist
- reviews the output for gaps and risks
- saves a reusable lesson for future runs

In simple terms:

`AgentForge helps turn an app idea into a structured, reviewed starter project.`

## Current State

AgentForge is a strong MVP.

It already supports:
- live multi-agent workflow visualization
- planner, research, execution, critic, and memory roles
- timeline playback for each run
- structured deliverables instead of one long text blob
- critic feedback with improvements and release-readiness labels
- SQLite-backed reusable memory
- NVIDIA-hosted model integration

What it does not fully do yet:
- generate a complete runnable project automatically
- export all generated files directly into a scaffold folder
- provide human approval/edit controls inside the workflow

## Tech Stack

- Backend: FastAPI
- Frontend: React + Vite
- Realtime updates: WebSockets
- Memory: SQLite
- Model provider: NVIDIA API
- Current model target: `nvidia/llama-3.3-nemotron-super-49b-v1.5`

## Project Structure

```text
backend/
  app/
    main.py
    models.py
    nvidia_client.py
    orchestrator.py
    store.py
  .env.example
  requirements.txt
frontend/
  src/
    App.tsx
    main.tsx
    styles.css
    types.ts
README.md
```

## How It Works

A run moves through these stages:

1. `Planner`
   Turns the goal into a task graph.
2. `Research`
   Recommends architecture, libraries, and patterns.
3. `Execution`
   Produces concrete deliverables such as routes, file tree, starter files, and test plans.
4. `Critic`
   Reviews the draft, identifies weaknesses, and may request a retry.
5. `Memory`
   Saves a reusable lesson from the run.

## Setup

### Backend

```powershell
cd C:\AgenticApps\AgentForge\backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```powershell
cd C:\AgenticApps\AgentForge\frontend
npm install
npm run dev
```

Open the frontend in your browser, usually:

[http://localhost:5173](http://localhost:5173)

## Environment Variables

Create `backend/.env` from `backend/.env.example` and add your NVIDIA API key.

Example:

```env
NVIDIA_API_KEY=your_key_here
NVIDIA_MODEL=nvidia/llama-3.3-nemotron-super-49b-v1.5
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
```

## Good Demo Prompts

Try one of these:

- `Design and scaffold a production-ready expense tracker app with Flask backend, dashboard UI, REST API, SQLite schema, starter files, test plan, deployment checklist, and a risk review.`
- `Design a production-ready AI resume analyzer app with Flask backend, file upload flow, dashboard UI, REST API, starter code files, evaluation plan, deployment checklist, and improvement suggestions.`
- `Design a production-ready to-do app with Flask backend, React dashboard, REST API, SQLite schema, starter files, test plan, deployment checklist, and a risk review.`

## What You Should See

For a good run, AgentForge should show:
- task breakdown from the planner
- research notes and technical recommendations
- concrete deliverables from execution
- a critic verdict with strengths and improvements
- a release-readiness label such as `prototype` or `solid_mvp`
- a reusable memory lesson saved from the run

## Why This Project Is Interesting

Most AI demos stop at a single answer.

AgentForge is different because it focuses on:
- workflow instead of one-shot output
- visible agent coordination
- self-review and improvement
- reusable memory
- concrete project deliverables

This makes it closer to an AI product-building assistant than a normal chatbot.

## Next Steps

High-impact future upgrades:
- generate scaffold files directly to disk
- compare draft 1 vs draft 2 visually
- add human approval or correction steps
- export deliverables as a starter project package
- support multiple model configurations by role
