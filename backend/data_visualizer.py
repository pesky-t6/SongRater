import librosa
import numpy as np


def moving_average(values, window_size=15):
    if len(values) < window_size:
        return values

    return np.convolve(
        values,
        np.ones(window_size) / window_size,
        mode="same"
    )

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds:02}"


def get_energy_curve(audio_file, sr=22050, hop_length=512, smooth_window=15, section_length=5):
    y, sr = librosa.load(audio_file, sr=sr, mono=True)

    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    times = librosa.frames_to_time(
        np.arange(len(rms)),
        sr=sr,
        hop_length=hop_length
    )

    smoothed_rms = moving_average(rms, smooth_window)

    graph_points = []

    for time_value, raw_energy, smooth_energy in zip(times, rms, smoothed_rms):
        graph_points.append({
            "time": round(float(time_value), 2),
            "energy": round(float(raw_energy), 5),
            "smoothed_energy": round(float(smooth_energy), 5)
        })

    duration = librosa.get_duration(y=y, sr=sr)
    section_samples = int(section_length * sr)

    sections = []
    start_sample = 0
    section_number = 1

    while start_sample < len(y):
        end_sample = start_sample + section_samples
        section_audio = y[start_sample:end_sample]

        if len(section_audio) < section_samples / 2:
            break

        start_time = start_sample / sr
        end_time = min(end_sample / sr, duration)

        section_rms = librosa.feature.rms(y=section_audio)
        avg_section_rms = float(np.mean(section_rms))

        sections.append({
            "section": section_number,
            "start_time": round(start_time, 2),
            "end_time": round(end_time, 2),
            "time": f"{format_time(start_time)} - {format_time(end_time)}",
            "energy": round(avg_section_rms, 4)
        })

        start_sample = end_sample
        section_number += 1

    peak_section = max(sections, key=lambda section: section["energy"])
    
    return {
        "graph_points": graph_points,
        "sections": sections,
        "peak": {
            "section": peak_section["section"],
            "start_time": peak_section["start_time"],
            "end_time": peak_section["end_time"],
            "time": peak_section["time"],
            "mid_time": (peak_section["start_time"] + peak_section["end_time"]) / 2,
            "energy": peak_section["energy"]
        }
    }