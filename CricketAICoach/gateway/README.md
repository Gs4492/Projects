# Gateway service

Run:
uvicorn main:app --reload --port 8000

Env vars (optional):
- PLAYER_SERVICE_BASE (default: http://127.0.0.1:8001)
- MATCH_SERVICE_BASE (default: http://127.0.0.1:8002)
- ANALYTICS_SERVICE_BASE (default: http://127.0.0.1:8003)
- AI_SERVICE_BASE (default: http://127.0.0.1:8004)

Endpoints:
- GET /health
- GET /phase1/player/{player_id}/deliveries?last_matches=5
- GET /phase2/player/{player_id}/batting?last_matches=5
- GET /phase3/player/{player_id}/coaching?last_matches=5
- GET /history/player/{player_id}?phase=phase2|phase3&limit=20

Notes:
- Phase 2 and Phase 3 responses are persisted to gateway `history.db` table `analysis_history`.
