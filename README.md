# SongRater

An AI-powered music rating system that analyzes song metadata, lyrics, and audio-derived features to generate structured ratings across categories such as vocals, production, replay value, and overall score.

## What It Does

SongRater extracts measurable song features and sends them to a local LLM through Ollama. The model uses calibration examples from a rating dataset to learn how different rating categories relate, while still judging each new song independently.

## Tech Stack

- Python
- Ollama
- Librosa
- Whisper
- Pandas
- CSV-based rating calibration

## Key Features

- Audio feature extraction using tempo, energy, brightness, and section-based analysis
- Lyric transcription support through Whisper
- Structured AI-generated song reviews
- Calibration from existing ratings without using the dataset as an answer key
- Local model workflow with no dependency on paid APIs

## Current Status

In active development. Core rating prompt and feature extraction pipeline are being tested and refined.
