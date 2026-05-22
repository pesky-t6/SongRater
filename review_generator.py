import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

def build_review_prompt(song_data):
    return f"""
You are an AI music review assistant.

Use only the song data provided below.
Do not look up the song online.
Do not use outside knowledge about the artist, song, album, popularity, awards, or public opinion.
The lyrics were automatically transcribed and may contain errors, these innaccuracies hurt the song's rating.
Use the transcript only for broad lyrical themes.
Do not quote lyrics directly.
Ignore transcript lines that seem like video artifacts, outro speech, captions, or unrelated phrases.

Song data:
{json.dumps(song_data, indent = 2)}

Return a JSON object with these fields:
- review
- mood
- standout_moments
- strengths
- weaknesses
- rating_out_of_100
- rating_reason
- transcript_warnings
"""


def generate_review(song_data, model = "llama3.2"):
    prompt = build_review_prompt(song_data)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    response = requests.post(OLLAMA_URL, json = payload, timeout = 120)
    response.raise_for_status()

    result = response.json()
    review_text = result.get("response", "{}")

    try:
        return json.loads(review_text)
    except json.JSONDecodeError:
        return {
            "review": review_text,
            "warning": "The model did not return valid JSON."
        }