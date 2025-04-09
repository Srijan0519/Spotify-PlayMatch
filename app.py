import streamlit as st
import logging
import pandas as pd
from utils import extract_playlist_id_from_url, format_duration
from gemini_service import analyze_playlist, get_song_recommendations
from visualization import create_bpm_chart, create_key_chart, create_instruments_chart, create_mood_and_genre_chart

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Setup page
st.set_page_config(page_title="Spotify Recommender", layout="wide")
st.markdown("""
<style>
body { background-color: #191414; color: white; }
.stButton > button { background-color: #1DB954; color: white; }
</style>
""", unsafe_allow_html=True)

# Session state setup
for key in ["playlist_data", "playlist_analysis", "recommendations", "playlist_details", "processing_error"]:
    if key not in st.session_state:
        st.session_state[key] = None

# URL validation
def is_valid_spotify_url(url):
    return url.startswith("https://open.spotify.com/playlist/")

# Main app logic
def main():
    st.title("🎵 Spotify Playlist Analyzer & Recommender")
    st.write("Paste a public Spotify playlist link to get insights and personalized recommendations.")

    url = st.text_input("Spotify Playlist URL:", placeholder="https://open.spotify.com/playlist/...")
    col1, col2 = st.columns([1, 3])
    analyze = col1.button("Analyze Playlist")
    reset = col2.button("Reset")

    if reset:
      for key in st.session_state:
        st.session_state[key] = None
    st.rerun()  # ✅ new




    if analyze and url:
        if not is_valid_spotify_url(url):
            st.error("Invalid Spotify playlist URL.")
            return

        playlist_id = extract_playlist_id_from_url(url)
        logger.info(f"Processing Playlist ID: {playlist_id}")

        try:
            from spotify_service import get_playlist_details, get_playlist_tracks
            with st.spinner("Fetching playlist details..."):
                details = get_playlist_details(playlist_id)
                tracks = get_playlist_tracks(playlist_id)

            if not tracks:
                st.error("No tracks found or playlist is private.")
                return

            st.session_state["playlist_data"] = tracks
            st.session_state["playlist_details"] = details

            with st.spinner("Analyzing with Gemini..."):
                analysis = analyze_playlist(tracks)
                if "error" in analysis:
                    st.warning("Analysis failed: " + analysis["error"])
                st.session_state["playlist_analysis"] = analysis

            with st.spinner("Generating recommendations..."):
                recs = get_song_recommendations(analysis)
                st.session_state["recommendations"] = recs

            st.success("Done! Scroll down to explore the results.")

        except Exception as e:
            logger.error(f"Error: {e}")
            st.error(f"Failed: {e}")

    if st.session_state["playlist_data"] and st.session_state["playlist_analysis"]:
        show_results()

# Display results
def show_results():
    data = st.session_state["playlist_data"]
    analysis = st.session_state["playlist_analysis"]
    recs = st.session_state["recommendations"]
    details = st.session_state["playlist_details"]

    st.subheader("📋 Playlist Info")
    if details:
        st.image(details["images"][0]["url"] if details.get("images") else None, width=200)
        st.write(f"**{details.get('name', 'No title')}** by {details.get('owner', {}).get('display_name', 'Unknown')}")
        st.write(f"Description: {details.get('description', 'N/A')}")
        st.write(f"Tracks: {len(data)}")
        duration = sum(t.get('duration_ms', 0) for t in data)
        st.write(f"Total Duration: {format_duration(duration)}")

    st.subheader("🔍 Analysis")
    st.write(analysis.get("general_description", "N/A"))

    col1, col2, col3 = st.columns(3)
    with col1:
        st.plotly_chart(create_bpm_chart(analysis.get("bpm_range", {})), use_container_width=True, key="bpm_chart")
    with col2:
        st.plotly_chart(create_key_chart(analysis.get("key_distribution", {})), use_container_width=True, key="key_chart")
    with col3:
        st.plotly_chart(create_instruments_chart(analysis.get("instruments", {})), use_container_width=True, key="instruments_chart")

    st.subheader("🧠 Mood & Genre")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(create_mood_and_genre_chart(analysis.get("mood_description", "")), use_container_width=True, key="mood_chart")
    with col2:
        st.plotly_chart(create_mood_and_genre_chart(analysis.get("genre_analysis", "")), use_container_width=True, key="genre_chart")

    st.subheader("🎧 Recommendations")
    if recs:
        for i, r in enumerate(recs):
            if not isinstance(r, dict) or "error" in r:
                st.warning("Skipping invalid recommendation.")
                continue
            with st.expander(f"{r.get('title', 'Unknown')} - {r.get('artist', 'Unknown')}"):
                st.write(r.get("reasoning", "No explanation provided."))
                st.write("Attributes:")
                for k, v in r.get("attributes", {}).items():
                    st.write(f"- **{k}**: {v}")
                url = r.get("spotify_url")
                if url:
                    st.markdown(f"[Listen on Spotify]({url})")

    st.subheader("📃 Track List")
    df = pd.DataFrame([{
        "#": i + 1,
        "Title": t.get("name", "Unknown"),
        "Artist": t.get("artist", "Unknown"),
        "Album": t.get("album", "Unknown"),
        "Duration": format_duration(t.get("duration_ms", 0))
    } for i, t in enumerate(data)])
    st.dataframe(df, use_container_width=True)


# Run
if __name__ == "__main__":
    main()

