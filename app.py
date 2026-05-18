import streamlit as st
from extractor import analyze_song

st.title("AI Music Listener")

uploaded_file = st.file_uploader("Upload a song clip", type = ["mp3", "wav"])

if uploaded_file is not None:
    st.audio(uploaded_file)

    results, sections = analyze_song(uploaded_file)

    st.subheader("Song Analysis")
    st.write(results)
    st.subheader("Section-by-Section Analysis")
    st.write(sections)