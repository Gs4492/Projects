# AI Service

Create `.env` in this folder using `.env.example`.

Required env vars:
- NVIDIA_API_KEY

Optional env vars:
- NVIDIA_MODEL (default: meta/llama-3.3-70b-instruct)
- NVIDIA_BASE_URL (default: https://integrate.api.nvidia.com/v1)
- ANALYTICS_URL (default: http://127.0.0.1:8003)

Run:
uvicorn main:app --reload --port 8004

Endpoint:
GET /ai/batting/{player_id}?last_matches=5
