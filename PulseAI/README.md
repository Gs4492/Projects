# PulseAI MVP

PulseAI is a voice-first mobile health assistant for Android backed by a FastAPI API.

## What It Does

- Accepts simple phone input about alcohol, food, blood pressure, sugar, and water
- Normalizes drinks such as small peg, large peg, small beer, and large beer
- Uses NVIDIA Llama for parsing and short guidance when available
- Uses a safety layer to keep risk and actions consistent
- Stores recent logs in SQLite
- Returns a result screen designed for older users with large text and clear actions
- Supports real speech-to-text on Android through `expo-speech-recognition`

## Project Structure

- `backend/` FastAPI API, parsing, retrieval, risk evaluation, SQLite logs
- `mobile/` React Native Expo Android app
- `.env` backend secrets and config
- `Dockerfile`, `Procfile`, `railway.toml` deployment files

## Backend Environment

Create or update `.env` in the project root:

```env
NVIDIA_API_KEY=your_real_key_here
NVIDIA_MODEL=meta/llama-3.1-8b-instruct
DATABASE_URL=sqlite:///./pulseai.db
```

## Backend Run

1. Create a Python virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the API:

```bash
uvicorn backend.main:app --reload
```

4. Check it:

```bash
GET /health
POST /analyze
GET /history
```

Example request:

```json
{
  "text": "2 small pegs whiskey, chips, BP 150/95, sugar 180"
}
```

## Mobile Run

1. Open the mobile app folder:

```bash
cd mobile
```

2. Install packages:

```bash
npm install
```

3. Create `mobile/.env` from `mobile/.env.example` and set your backend URL.

Local Wi-Fi example:

```env
EXPO_PUBLIC_API_URL=http://192.168.1.10:8000
```

Cloud example:

```env
EXPO_PUBLIC_API_URL=https://your-backend.up.railway.app
```

4. Because speech recognition uses a native module, create a development build or APK.

```bash
npx expo run:android
```

or later with EAS:

```bash
npx eas build -p android
```

5. Start the Metro server if needed:

```bash
npx expo start --dev-client
```

## Important Speech Note

Speech recognition will not work inside plain Expo Go for this setup. Use a development build or the final APK.

## APK Path

After the app works locally, build Android:

```bash
npm install -g eas-cli
cd mobile
npx eas build -p android
```

## Cloud Deploy Path

This repo includes `Dockerfile`, `Procfile`, and `railway.toml` so Railway is the easiest first deployment target.

Typical flow:

1. Push this repo to GitHub.
2. Create a Railway project from the repo.
3. Add environment variables from `.env`.
4. Deploy and copy the public backend URL.
5. Put that URL into `mobile/.env` as `EXPO_PUBLIC_API_URL`.
6. Build the APK.

## Current Limitations

- Runtime verification was limited in this shell because Python and Node were not available on PATH here.
- This is guidance only, not diagnosis.

## Suggested Next Practical Step

1. Run the backend locally.
2. Run `npm install` in `mobile`.
3. Run `npx expo run:android` for a dev build.
4. Test speech with 10 to 15 realistic phrases.
5. Deploy backend to Railway.
6. Build the APK.
