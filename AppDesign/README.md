# Pick Your Stack Generator

A lightweight Flask web app that turns a short product form into a recommended app stack.

## What it includes

- Rule-based stack selection based on your form logic
- Optional NVIDIA LLM explanation using `mistralai/mistral-small-24b-instruct`
- Static HTML frontend plus a tiny Flask server

## Run it

1. Copy `.env.example` to `.env`
2. Set `NVIDIA_API_KEY`
3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Start the app:

```powershell
python app.py
```

5. Open `http://localhost:3000`

## Environment variables

- `NVIDIA_API_KEY`
- `NVIDIA_MODEL`
- `NVIDIA_API_BASE_URL`
- `PORT`
