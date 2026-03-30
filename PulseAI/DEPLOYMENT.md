# PulseAI Deployment Guide

## 1. Push To GitHub

From the repo root:

```bash
git add .
git commit -m "Your update message"
git push
```

For the first setup, the repo was connected with:

```bash
git init
git add .
git commit -m "Add PulseAI app"
git remote add origin https://github.com/Gs4492/Projects.git
git branch -M main
git pull origin main --allow-unrelated-histories
git push -u origin main
```

## 2. Project Structure

The PulseAI app now lives inside:

```text
PulseAI/
```

Important paths:

- Backend/app root: `PulseAI`
- Mobile app: `PulseAI/mobile`

## 3. Render Backend

Render service:

- Service name: `pulseai-api`
- Repo: `Gs4492/Projects`
- Branch: `main`
- Language: `Docker`
- Root Directory: `PulseAI`

### Environment Variables

Add these in Render:

```text
NVIDIA_API_KEY=your_real_key
NVIDIA_MODEL=meta/llama-3.1-8b-instruct
DATABASE_URL=sqlite:///./pulseai.db
```

### Backend Check

After deploy, test:

```text
https://pulseai-api.onrender.com/health
```

Expected response:

```json
{"status":"ok","service":"PulseAI API"}
```

## 4. Render Update Flow

After backend changes:

```bash
git add .
git commit -m "Update backend"
git push
```

Render auto-deploys the latest commit.

If the project folder changes again, update:

- Render -> `Settings` -> `Root Directory`

## 5. Mobile App

Go to the mobile app folder:

```bash
cd PulseAI/mobile
```

Local preview:

```bash
npx expo start -c
```

## 6. Android APK Build

Install and log in to EAS:

```bash
npm install -g eas-cli
eas login
eas build:configure
```

Build APK:

```bash
eas build -p android --profile preview
```

The app uses `eas.json` with an APK preview profile.

## 7. Mobile Backend URL

For local Expo use:

```env
EXPO_PUBLIC_API_URL=https://pulseai-api.onrender.com
```

The mobile app also has a default production fallback in:

`PulseAI/mobile/src/services/api.js`

## 8. Notes

- Render free instances can sleep when inactive.
- SQLite is fine for testing, but data can be less reliable than a managed database.
- Expo Go is good for UI preview, but native speech features need a development build or APK.
