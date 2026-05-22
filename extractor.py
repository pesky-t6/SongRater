import librosa
import whisper
import numpy as np
import shutil


whisper_model = None

# get the average value of a list of values
def get_average(values):
    return float(np.mean(values))

# get the median value of a list of values
def get_median(values):
    return float(np.median(values))

# get the song's lyrics
def get_lyrics(audio_file):
    if shutil.which("ffmpeg") is None:
        return {
            "transcript": "",
            "words": [],
            "model": "whisper_medium",
            "warning": "ffmpeg was not found. Whisper needs ffmpeg to transcribe audio."
        }
    global whisper_model

    if whisper_model is None:
        whisper_model = whisper.load_model("medium")
    try:
        lyrics = whisper_model.transcribe(audio_file, fp16=False, word_timestamps=True)
    except (FileNotFoundError, RuntimeError) as error:
        return f"Error when transcribing: {error}"

    words = []

    for segment in lyrics.get("segments", []):
        for word_info in segment.get("words", []):
            word = {
                "word": word_info.get("word", "").strip(),
                "start": float(word_info.get("start")),
                "end": float(word_info.get("end")),
                "probability": float(word_info.get("probability", 0))
            }

            if word["word"] != "" and word["start"] is not None and word["end"] is not None:
                words.append(word)

    return {
        "transcript": lyrics.get("text", ""),
        "words": words,
        "model": "whisper_medium",
        "warning": "Lyrics were automatically transcribed and word timestamps are approximate."
    }

# add the timestaps to each of the words
def lyric_timing_by_section(words, sections):
    lyric_sections = []

    for section in sections:
        start_time = section["start_time"]
        end_time = section["end_time"]
        section_duration = end_time - start_time

        section_words = []

        for word in words:
            if word["start"] >= start_time and word["start"] < end_time:
                section_words.append(word)

        word_count = len(section_words)

        if word_count > 0:
            word_durations = []

            for word in section_words:
                duration = word["end"] - word["start"]

                if duration > 0:
                    word_durations.append(duration)

            avg_word_duration = get_average(word_durations) if len(word_durations) > 0 else 0
            lyric_density = word_count / section_duration

            longest_word = max(
                section_words,
                key = lambda word: word["end"] - word["start"]
            )

            longest_word_duration = longest_word["end"] - longest_word["start"]
        else:
            avg_word_duration = 0
            lyric_density = 0
            longest_word_duration = 0

        lyric_sections.append({
            "section": section["section"],
            "start_time": start_time,
            "end_time": end_time,
            "word_count": word_count,
            "lyric_density": round(lyric_density, 2),
            "avg_word_duration": round(avg_word_duration, 2),
            "longest_word_duration": round(longest_word_duration, 2)
        })

    return lyric_sections

# calculates the change in energy over the song's length
def energy_change(sections):
    if len(sections) < 2:
        return "Song isn't long enough to analyze energy changes."

    first_energy = sections[0]["energy"]
    last_energy = sections[-1]["energy"]
    peak_section = max(sections, key = lambda section: section["energy"])
    peak_time = (peak_section["start_time"] + peak_section["end_time"]) / 2

    minutes = int(peak_time // 60)
    seconds = int(peak_time % 60)

    if peak_section["energy"] > first_energy * 2:
        peak_str = f"The song starts quietly and builds strongly, reaching its peak around section {peak_section['section']} or {minutes}:{seconds:02}."
    else:
        peak_str = f"The song reaches its highest energy around section {peak_section['section']} or {minutes}:{seconds:02}."

    if last_energy < peak_section["energy"] * 0.6:
        return peak_str + " The song becomes calmer toward the end."
    else:
        return peak_str + " The song keeps a fairly steady energy level after its peak."

# full analysis of the song
def analyze_song(audio_file, section_length = 5):
    y, sr = librosa.load(audio_file, sr = 22050, mono = True)

    # length of song
    duration = librosa.get_duration(y = y, sr = sr)
    section_samples = int(section_length * sr)

    # song-wide features
    tempo_bpm = librosa.feature.tempo(y = y, sr = sr, aggregate=None)
    tempo_bpm = round(float(get_median(tempo_bpm)), 2)

    # brightness of the sound
    spectral_centroid = librosa.feature.spectral_centroid(y = y, sr = sr)
    avg_spectral_centroid = get_average(spectral_centroid)

    # energy of the sound
    rms = librosa.feature.rms(y = y)
    avg_rms = get_average(rms)

    # harmony / pitch profile
    chroma = librosa.feature.chroma_stft(y = y, sr = sr)
    avg_chroma = get_average(chroma)

    # general sound texture
    mfcc = librosa.feature.mfcc(y = y, sr = sr, n_mfcc = 13)
    avg_mfcc = get_average(mfcc)

    sections = []

    start_sample = 0
    section_number = 1

    # analyze section by section
    while start_sample < len(y):
        end_sample = start_sample + section_samples
        section_audio = y[start_sample:end_sample]

        if len(section_audio) < section_samples / 2:
            break

        start_time = start_sample / sr
        end_time = min(end_sample / sr, duration)

        # the root-mean-square. basically total energy of the section
        section_rms = librosa.feature.rms(y = section_audio)
        avg_section_rms = get_average(section_rms)

        # section brightness
        section_spectral_centroid = librosa.feature.spectral_centroid(y = section_audio, sr = sr)
        avg_brightness = get_average(section_spectral_centroid)

        tempo = librosa.feature.tempo(y = section_audio, sr = sr, aggregate=None)
        tempo = float(get_median(tempo))

        # section info
        section = {
            "section": section_number,
            "start_time": round(start_time, 2),
            "end_time": round(end_time, 2),
            "tempo_bpm": round(tempo, 2),
            "energy": round(avg_section_rms, 4),
            "brightness": round(avg_brightness, 2)
        }

        sections.append(section)

        start_sample = end_sample
        section_number += 1

    avg_results = {
        "duration_seconds": round(duration, 2),
        "tempo_bpm": tempo_bpm,
        "energy": round(avg_rms, 4),
        "brightness": round(avg_spectral_centroid, 2),
        "chroma": round(avg_chroma, 4),
        "texture": round(avg_mfcc, 4)
    }

    energy_analysis = energy_change(sections)
    lyrics = get_lyrics(audio_file)

    
    song_data = {
        "overall": avg_results,
        "sections_summary": {
            "section_length_seconds": section_length,
            "number_of_sections": len(sections)
        },
        "energy_analysis": energy_analysis,
        "lyrics": {
            "transcript": lyrics["transcript"],
            "model": lyrics["model"],
            "warning": lyrics["warning"]
    }
}

    return song_data