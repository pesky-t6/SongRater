from extractor import analyze_song
from review_generator import generate_review
import json

song_data = analyze_song("songs/Thick Of It.mp3")
review = generate_review(song_data)

print(json.dumps(song_data, indent = 4))
print("\n-------------------------\n")
print(json.dumps(review, indent = 4))

