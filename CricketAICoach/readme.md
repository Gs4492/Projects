# CricketCoach

CricketCoach is a local multi-service cricket analysis app built with FastAPI and a simple frontend. It helps coaches and players create player records, upload match deliveries, run batting or bowling analytics, generate coaching suggestions, and store session history. It also includes an MVP practice-video workflow for uploading net-session videos and returning structured feedback.

## What This App Does

- Create and load player profiles
- Create matches and upload ball-by-ball delivery data
- Run batting analytics
- Run bowling analytics
- Generate coaching recommendations from recent data
- Store analysis history in the gateway service
- Upload practice videos and return structured batting or bowling feedback

## Current Features

### Player management
- Create a player
- Load an existing player by ID
- Store player data locally in SQLite

### Match and delivery tracking
- Create a match
- Upload deliveries in bulk
- Fetch a player's recent deliveries

### Analytics
- Batting analytics for recent matches
- Bowling analytics for recent matches
- Phase-based risk and performance summaries
- Visual support in the frontend for trends and key clusters

### Coaching layer
- Converts analytics into practical coaching suggestions
- Provides evidence points, improvements, drills, and match-plan style guidance

### Video workflow
- Upload one practice session video
- Save the file and create a reusable session record
- Run a first-pass structured batting or bowling video analysis response

## Important Note About Video Analysis

The video feature is currently an MVP scaffold.

- Uploading a video works
- Creating a video session works
- Running the video analysis endpoint works
- The current analysis does **not** perform real computer vision or frame-by-frame video understanding yet

Right now, the video service returns heuristic, coaching-style JSON based on the session metadata and selected mode. It is designed so real CV models can be added later.

## Architecture

This repo is split into small local services:

- `player_service` on port `8001`
- `match_service` on port `8002`
- `analytics_service` on port `8003`
- `ai_service` on port `8004`
- `video_service` on port `8005`
- `gateway` on port `8000`
- `frontend` static UI

The `gateway` service acts as the main entry point for combined workflows and history.

## Project Structure

```text
CricketCoach/
├─ frontend/
├─ player_service/
├─ match_service/
├─ analytics_service/
├─ ai_service/
├─ video_service/
├─ gateway/
├─ start_phase1.ps1
├─ start_phase2.ps1
└─ start_phase3.ps1
Tech Stack
Python
FastAPI
SQLite
HTML / CSS / JavaScript
HTTP-based service-to-service communication
How To Run
1. Start all services
From the project root:

.\start_phase3.ps1
This starts:

player_service on http://127.0.0.1:8001
match_service on http://127.0.0.1:8002
analytics_service on http://127.0.0.1:8003
ai_service on http://127.0.0.1:8004
video_service on http://127.0.0.1:8005
gateway on http://127.0.0.1:8000
2. Open the frontend
Open:

frontend/index.html
You can open it directly in a browser or serve the folder using any static file server.

Frontend Flow
Create or load a player
Create a match
Add deliveries manually or load sample data
Upload deliveries
Run analytics
Generate coaching
Optionally upload a practice video
Run video analysis
Main API Endpoints
Gateway
GET /health
GET /phase1/player/{player_id}/deliveries?last_matches=5
GET /phase2/player/{player_id}/batting?last_matches=5
GET /phase2/player/{player_id}/bowling?last_matches=5
GET /phase3/player/{player_id}/coaching?last_matches=5
GET /phase3/player/{player_id}/bowling/coaching?last_matches=5
GET /history/player/{player_id}?phase=phase2|phase3&limit=20
Video via Gateway
POST /video/player/{player_id}/sessions
GET /video/player/{player_id}/sessions
GET /video/sessions/{session_id}
POST /video/sessions/{session_id}/analyze
Local Data Storage
The app stores data locally in SQLite / local JSON-backed storage depending on the service:

players in player_service
matches and deliveries in match_service
analysis history in gateway/history.db
uploaded videos and session records in video_service/storage
Known Limitations
The current video analysis is placeholder logic, not real CV
There is no hard-coded app-level upload size limit for videos
Large video uploads may be unstable because files are currently buffered in memory during upload forwarding
AI coaching quality depends on the configured model and environment setup
This project is designed primarily for local development / MVP use
Future Improvements
Real computer vision for cricket practice videos
Ball-by-ball video segmentation
Pose estimation
Shot classification
Better upload streaming and file-size controls
Authentication and production deployment setup
More advanced dashboards and coaching reports
Why This Project Exists
This app is meant to turn raw cricket data into coaching-ready insight. Instead of only storing balls or score events, it tries to connect player data, analytics, and practical training guidance in one workflow that coaches can use locally.
