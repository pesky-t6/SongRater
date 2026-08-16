import json
import requests
import time

OLLAMA_URL = "http://localhost:11434/api/generate"

ratings_summary = """
General rating calibration:
- 95-100: legendary, exceptional replay value, major emotional or musical identity
- 90-94: elite song with strong structure, impact, and replay value
- 85-89: great song with clear strengths and minor limitations
- 75-84: good song with solid qualities but less standout identity
- 60-74: average or mixed song with noticeable weaknesses
- below 60: weak song with major issues in structure, replay value, or cohesion

Category ratings are out of 100.
Do not reward energy alone. Reward structure, contrast, emotional impact, lyrical cohesion, and replay value.
"""

output_schema = {
    "type": "object",
    "properties": {
        "review": {
            "type": "string"
        },
        "mood": {
            "type": "string"
        },
        "audio_observations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "input_signal": {"type": "string"},
                    "description": {"type": "string"}
                },
                "required": ["input_signal", "description"]
            }
        },
        "lyrical_observations": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["theme", "reason"]
            }
        },
        "standout_moments": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "section": {"type": "integer"},
                    "time": {"type": "string"},
                    "reason": {"type": "string"}
                },
                "required": ["section", "time", "reason"]
            }
        },
        "strengths": {
            "type": "array",
            "items": {"type": "string"}
        },
        "weaknesses": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 3
        },
        "ratings": {
            "type": "object",
            "properties": {
                "emotional_impact": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100
                },
                "energy_progression": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100
                },
                "lyrical_cohesion": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100
                },
                "replay_value": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100
                },
                "production_interest": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 100
                }
            },
            "required": [
                "emotional_impact",
                "energy_progression",
                "lyrical_cohesion",
                "replay_value",
                "production_interest"
            ],
            "additionalProperties": False
        },
        "rating_reason": {
            "type": "string"
        },
        "transcript_warnings": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": [
        "review",
        "mood",
        "audio_observations",
        "lyrical_observations",
        "standout_moments",
        "strengths",
        "weaknesses",
        "ratings",
        "rating_reason",
        "transcript_warnings"
    ],
    "additionalProperties": False
}

def calculate_final_rating(ratings):
    return round(
        ratings["emotional_impact"] * 0.25 +
        ratings["energy_progression"] * 0.25 +
        ratings["lyrical_cohesion"] * 0.20 +
        ratings["replay_value"] * 0.20 +
        ratings["production_interest"] * 0.10
    )

# prompt
def build_review_prompt(song_data, song_name = None, artist = None):
    try:
        with open("data/base_ratings.csv", "r", encoding = "utf-8") as file:
            base_ratings = file.read()
    except Exception:
        base_ratings = "(Could not load data/base_ratings.csv)"

    song_json = json.dumps(song_data, indent = 2)

    prompt = f"""
    You are an AI music review assistant.

    Rate the song using only:
    1. The rating scale summary
    2. The extracted song data

    Do not use outside knowledge.
    Do not identify the song title, artist, album, or popularity from the lyrics.
    Do not mention specific songs from the rating scale.
    Do not quote or closely paraphrase lyrics.
    Do not invent instruments, vocals, guitar, drums, mixing quality, or production polish unless directly supported by the input.

    Replay value is an interpretive rating. Base it on structural variation, lyrical cohesion, dynamic contrast, and overall consistency. Do not claim that the input directly measures replay value.

    Tempo rule:
    Do not say tempo varies, ranges, shifts, changes, or fluctuates unless song_data includes tempo_change_summary.
    If only tempo_bpm is provided, describe it as a single estimated tempo.

    Vocal rule:
    Do not mention vocal range, vocal delivery, singing quality, or artist performance unless song_data includes explicit vocal analysis.

    Lyrics rule:
    Do not quote lyrics. Do not put transcript phrases in quotation marks. Summarize lyrical themes only.

    Rating completeness rule:
    The ratings object must include exactly:
    emotional_impact, energy_progression, lyrical_cohesion, replay_value, production_interest.
    Each must be an integer from 1 to 100.

    Grounding rule:
    Each audio observation must reference an actual field name and value from song_data, such as intro_energy=0.0609 or peak_time=2:02.
    Do not use vague input signals like "Dynamic Range" unless that exact field exists.

    The extracted audio fields are valid evidence.
    Use relevant evidence from the energy profile, peak time, top energy sections, tempo, and lyric themes.
    Do not force an observation about a field when it does not meaningfully contribute to the review.

    Evidence hierarchy:

    MEASURED FACTS:
    Audio fields such as energy, brightness, tempo_bpm, peak_time, and section values are direct measurements and may be stated as facts.

    SUPPORTED INTERPRETATIONS:
    You may describe high measured energy as dynamically intense, energetic, or a strong contrast when the surrounding values support it.

    UNSUPPORTED INTERPRETATIONS:
    Do not infer emotional intensity, emotional climax, instrumentation, vocal performance, tempo changes, production quality, or listener response solely from energy or brightness measurements.

    The highest-energy section is not automatically the emotional climax of the song.

    Weakness rules:
    - Give 0 to 3 weaknesses.
    - Only include a weakness when it is supported by the provided song data.
    - Do not invent criticism simply to provide a weakness.
    - Subjective statements such as "may not resonate with every listener" are not valid weaknesses.

    Transcript warning rules:
    - Repeated lyrics, choruses, refrains, and short repeated phrases are normal and are NOT transcription errors.
    - Audio energy and brightness are unrelated to transcription accuracy and must never be mentioned in transcript_warnings.
    - Only add a warning when the transcript contains likely recognition errors such as:
    - grammatically broken phrases
    - isolated foreign/unexpected characters
    - nonsensical wording
    - abrupt fragments that do not form meaningful sentences
    - Describe the issue generally. Do not quote the lyrics.
    - If there are no obvious transcription problems, return an empty list.

    Rating rules:
    - rating_out_of_100 must be an integer from 1 to 100.
    - Never return 0 unless the song data is empty or unusable.
    - Never return placeholder text like "<insert rating>".
    - Never leave review, mood, strengths, weaknesses, standout_moments, or rating_reason empty.
    - Give at least 2 strengths.
    - Every strength and weakness must reference a specific input signal.
    - If the rating reason mentions a weakness, it must also appear in weaknesses.

    Rating scale summary:
    {ratings_summary}

    Song data:
    {song_json}

    Return only valid JSON with exactly these keys:

    review: string, 3 to 5 sentences
    mood: string
    audio_observations: list of objects with input_signal and description
    lyrical_observations: list of objects with theme and reason
    standout_moments: list of objects with section, time, and reason
    strengths: list of strings
    weaknesses: list of strings
    ratings: object with emotional_impact, energy_progression, lyrical_cohesion, replay_value, production_interest as integers from 1 to 100
    rating_out_of_100: integer from 1 to 100
    rating_reason: string
    transcript_warnings: list of strings

    Return JSON only."""
    return prompt

# models: llama3.2, qwen3:8b, qwen3:14b, gpt-oss:20b
def get_review(song_data, model = "qwen3:8b"):
    startTime = time.perf_counter()
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
    except requests.exceptions.HTTPError:
        return {
            "error": "Issue with the model most likely, try running ollama pull <model_name>"
        }
    
    elapsed_time = time.perf_counter() - startTime
    print(f"total time: {elapsed_time:.3f}s")


    result = response.json()
    review_text = result.get("response", "{}")

    try:
        review_json = json.loads(review_text)
    except json.JSONDecodeError:
        return {
            "review": review_text,
            "warning": "The model did not return valid JSON."
        }

    review_json["rating_out_of_100"] = calculate_final_rating(review_json["ratings"])
    review_json["lyrics"] = song_data.get("lyrics", "")
    review_json["review time"] = round(elapsed_time, 3)

    return review_json