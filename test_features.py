from extractor import analyze_song

results, sections, energy_analysis = analyze_song("songs/Billie Jean.mp3")

for section in sections:
    print(section, "\n")
print(results, "\n")
print(energy_analysis)