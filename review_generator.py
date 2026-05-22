import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

# prompt
def build_review_prompt(song_data):
    return f"""
You are an AI music review assistant.

Use only the song data provided below.
Do not look up the song online.
Do not use outside knowledge about the artist, song, album, popularity, awards, or public opinion.

Important:
- The audio analysis is the main evidence.
- The lyrics are supporting evidence.
- If lyrics were automatically transcribed, they may contain errors. Transcription mistakes should not lower the song's rating.
- Do not quote lyrics directly.
- Ignore transcript lines that seem like video artifacts, outro speech, captions, or unrelated phrases.
- Do not make claims about vocals, guitar, drums, production quality, or musicianship unless the provided data supports it.
- The review must mention at least one audio-based observation.
- The standout moments must come from the energy profile, section data, or clear song structure.
- The tempo_bpm in overall is the only tempo value that should be used.
- Do not claim the song changes BPM unless song_data includes a specific tempo_change_summary.
- Section-level tempo estimates are intentionally omitted because short-window BPM detection can be noisy.
- The review must be 3-5 sentences and must explain how the audio energy profile and lyrics work together.

Song data:
{json.dumps(song_data, indent = 2)}

Return only a JSON object with these exact fields:
{{
    "review": "",
    "mood": "",
    "audio_observations": [],
    "lyrical_observations": ["Describe broad themes only. No quoted lyric phrases."],
    "standout_moments": [
        {{
            "section": 0,
            "time": "",
            "reason": ""
        }}
    ],
    "strengths": [],
    "weaknesses": [],
    "rating_out_of_100": 0,
    "rating_reason": "",
    "transcript_warnings": []
}}
"""


def generate_review(song_data, model = "llama3.2"):
    prompt = build_review_prompt(song_data)

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }

    try:
        response = requests.post(OLLAMA_URL, json = payload, timeout = 300)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        return {
            "error": "Could not connect to Ollama. Make sure Ollama is running on http://localhost:11434."
        }
    except requests.exceptions.Timeout:
        return {
            "error": "Ollama connected, but the model took too long to respond. Try a shorter prompt or smaller model."
        }

    result = response.json()
    review_text = result.get("response", "{}")

    try:
        return json.loads(review_text)
    except json.JSONDecodeError:
        return {
            "review": review_text,
            "warning": "The model did not return valid JSON."
        }