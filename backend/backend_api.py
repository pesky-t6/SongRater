import os
import tempfile
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from extractor import analyze_song

from review_generator import get_review

from data_visualizer import get_energy_curve

# use this to run backend
# uvicorn backend_api:app --reload --host 127.0.0.1 --port 8000

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze-energy")
async def analyze_energy(
    file: UploadFile = File(...),
    lyrics: str = Form(""),
):
    suffix = os.path.splitext(file.filename or "")[1] or ".mp3"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_path = temp_file.name
        temp_file.write(await file.read())

    try:
        data = get_energy_curve(temp_path)
        return data
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/generate-review")
async def generate_review(
    file: UploadFile = File(...),
    lyrics: str = Form(""),
):
    suffix = os.path.splitext(file.filename or "")[1] or ".mp3"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_path = temp_file.name
        temp_file.write(await file.read())

    try:
        data = get_review(analyze_song(temp_path, lyrics))
        return data
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)