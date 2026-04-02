# AppDesign

A simple Flask app that helps you choose a practical stack for a new product.

Instead of forcing you to overthink architecture from scratch, the app lets you:

- choose the kind of app you want to build
- pick from dropdowns for frontend, backend, auth, database, AI, storage, payments, and deployment
- get one clear recommended setup
- see better alternatives only when they are actually useful
- get first build steps
- get a suggested architecture style
- get a starter project structure

## What The App Does

The planner is designed to make app planning easier, not more complicated.

You choose things like:

- app type
- frontend
- backend
- auth
- database
- realtime
- AI provider
- storage
- payments
- deployment

Then the app returns:

- final stack recommendation
- short explanation of why it fits
- better alternatives when appropriate
- first build steps
- recommended architecture style
- starter folder structure
- watchouts

## Tech Stack

- Backend: Flask
- Frontend: plain HTML, CSS, and JavaScript
- AI provider: NVIDIA API
- Default configured model: `mistralai/mistral-small-24b-instruct`

The UI talks about `NVIDIA API` at the provider level so it does not feel locked to one model, but the backend can still use the configured model from `.env`.

## Project Structure

```text
AppDesign/
  app.py
  requirements.txt
  README.md
  .env.example
  .gitignore
  public/
    index.html
    app.js
    styles.css
```

## Local Setup

1. Open PowerShell in the project folder:

```powershell
cd C:\AgenticApps\AppDesign
```

2. Create your local environment file:

```powershell
Copy-Item .env.example .env
```

3. Edit `.env` and add your real NVIDIA API key.

Example:

```env
NVIDIA_API_KEY=your_real_key_here
NVIDIA_MODEL=mistralai/mistral-small-24b-instruct
NVIDIA_API_BASE_URL=https://integrate.api.nvidia.com/v1
PORT=3000
```

4. Install dependencies:

```powershell
pip install -r requirements.txt
```

5. Start the app:

```powershell
python app.py
```

6. Open the app:

```text
http://localhost:3000
```

## How To Use It

1. Choose what kind of app you are building.
2. Pick your preferred tools from the dropdowns.
3. Add an optional note if you want constraints like:
   - keep it cheap
   - beginner-friendly
   - easy to deploy
   - India payments
4. Click `Give Me The Simplest Good Setup`.

The app will then generate:

- your stack
- why it fits
- what to change only if needed
- first build steps
- architecture recommendation
- project structure

## Environment Variables

- `NVIDIA_API_KEY`
  Your real NVIDIA API key. Keep this only in `.env`.
- `NVIDIA_MODEL`
  The model used by the backend.
- `NVIDIA_API_BASE_URL`
  NVIDIA API base URL.
- `PORT`
  Local app port.

## Important Security Note

Do not upload `.env` to GitHub.

`.env` contains your real secret key.

Safe to upload:

- `.env.example`
- `.gitignore`
- `app.py`
- `requirements.txt`
- `README.md`
- `public/`

Do not upload:

- `.env`

If `.env` is accidentally uploaded, delete it immediately and rotate the API key.

## Uploading To GitHub

If you are uploading files manually to GitHub, upload the app files but skip `.env`.

Recommended upload list:

- `.env.example`
- `.gitignore`
- `README.md`
- `app.py`
- `requirements.txt`
- `public/index.html`
- `public/app.js`
- `public/styles.css`

## Notes

- The planner uses AI-backed output when the NVIDIA API key is configured.
- If the AI call fails, the app can still fall back to simpler logic.
- The app is intentionally designed to prefer one clear answer over too many choices.

5. Open `http://localhost:3000`

## Environment variables

- `NVIDIA_API_KEY`
- `NVIDIA_MODEL`
- `NVIDIA_API_BASE_URL`
- `PORT`
