# SongRater

Analyze a song locally: upload an audio file, see its energy curve, and get a written review with per-category ratings.

## How it works

The frontend is a React app that sends your audio file (and optional lyrics) to a local backend running on `http://127.0.0.1:8000`. The backend does two things:

- `POST /analyze-energy` — returns energy-over-time data points and the detected peak
- `POST /generate-review` — returns a written review, mood, category ratings, strengths/weaknesses, and (if lyrics or transcription are available) lyrical themes and standout moments

Nothing is uploaded anywhere else unless you choose to.

## Requirements

- Node.js
- A backend running locally on port 8000 that implements the two endpoints above

## Setup

```bash
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate

# MacOS:
source venv/bin/activate

pip install -r requirements.txt

# Ollama needs seperate installation, then:
ollama pull qwen3:8b

# Run the backend
uvicorn backend_api:app --reload --host 127.0.0.1 --port 8000

# New terminal:
cd frontend
npm install
npm run dev
```

Make sure your backend is running before analyzing a song, or requests will fail.

## Project structure

- `App.jsx` — main UI and fetch logic
- `App.css` — styling

## Notes

This is a local-first tool. If the backend isn't running, the app will show an error instead of failing silently.
