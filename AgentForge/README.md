# AgentForge

AgentForge is an agentic AI app that takes a user's goal, breaks it into tasks, runs specialized agents step by step, and shows the workflow live.

## Stack

- Backend: FastAPI
- Frontend: React + Vite
- Realtime: WebSockets
- Model target: `nvidia/llama-3.3-nemotron-super-49b-v1.5`

## Project Structure

- `backend/` FastAPI orchestration service
- `frontend/` React dashboard

## Run

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Environment

Copy `.env.example` to `.env` inside `backend/` and add your NVIDIA API key.
