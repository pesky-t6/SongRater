from extractor import analyze_song
from review_generator import get_review
import json
import time

startTime = time.time()
song_data = analyze_song("songs/Billie Jean.mp3", "Test")
review = get_review(song_data)
endTime = time.time()

print(json.dumps(song_data, indent = 4))
print("\n-------------------------\n")
print(json.dumps(review, indent = 4))
print("total time: ", endTime-startTime)

