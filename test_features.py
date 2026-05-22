from extractor import analyze_song
from review_generator import generate_review

song_data = analyze_song("songs/Black Hole Sun.mp3")
review = generate_review(song_data)

print(song_data)
print("\n-------------------------\n")
print(review)

