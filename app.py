import streamlit as st
import re
import time
import pandas as pd
import logging
from spotify_service import get_playlist_id_from_url, get_playlist_tracks, get_playlist_details
from gemini_service import analyze_playlist, get_song_recommendations
from visualization import create_bpm_chart, create_key_chart, create_instruments_chart, create_mood_and_genre_chart
from utils import format_duration
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
# load_dotenv()

# # Print API keys for debugging (without exposing full keys)
# gemini_key = os.getenv('GEMINI_API_KEY')
# spotify_id = os.getenv('SPOTIPY_CLIENT_ID')
# spotify_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
gemini_key = st.secrets["gemini"]["api_key"]
spotify_id = st.secrets["spotify"]["client_id"]
spotify_secret = st.secrets["spotify"]["client_secret"]

if gemini_key:
    logger.info(f"Gemini API key loaded (starts with: {gemini_key[:5]}...)")
else:
    logger.error("GEMINI_API_KEY not found")

if spotify_id and spotify_secret:
    logger.info(f"Spotify credentials loaded (ID starts with: {spotify_id[:5]}...)")
else:
    logger.error("Spotify credentials missing or incomplete")

# Page configuration
st.set_page_config(
    page_title="Spotify Song Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Spotify-themed custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #191414;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #1DB954;
        color: #FFFFFF;
    }
    .css-1kyxreq, .css-10trblm, .css-81oif8 {
        color: #FFFFFF;
    }
    .css-1vencpc, .css-1cpxqw2 {
        background-color: #121212;
        border-radius: 8px;
        padding: 20px;
    }
    .block-container {
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'playlist_data' not in st.session_state:
    st.session_state.playlist_data = None
if 'playlist_analysis' not in st.session_state:
    st.session_state.playlist_analysis = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'playlist_details' not in st.session_state:
    st.session_state.playlist_details = None
if 'processing_error' not in st.session_state:
    st.session_state.processing_error = None
if 'clear_url_input' not in st.session_state:
    st.session_state.clear_url_input = False

def validate_spotify_url(url):
    """Validate if the URL is a legitimate Spotify playlist URL."""
    pattern = r'https:\/\/open\.spotify\.com\/playlist\/[a-zA-Z0-9]+'
    return bool(re.match(pattern, url))

def main():
    # Custom CSS for banner container and sound wave animation
    st.markdown("""
    <style>
        .banner-container {
            max-height: 200px;
            overflow: hidden;
            margin-bottom: 20px;
            border-radius: 10px;
        }
        
        /* Sound wave animation */
        .sound-wave-container {
            height: 100px;
            display: flex;
            align-items: center;
            justify-content: center;
            background-color: #191414;
            border-radius: 10px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        
        .sound-wave {
            display: flex;
            align-items: center;
            height: 100%;
            width: 100%;
            justify-content: center;
            gap: 3px;
        }
        
        .sound-wave .bar {
            background-color: #1DB954;
            width: 10px;
            border-radius: 5px;
            animation: soundWave 1.5s infinite ease-in-out;
        }
        
        .sound-wave .bar:nth-child(1) { animation-delay: 0.1s; height: 20px; }
        .sound-wave .bar:nth-child(2) { animation-delay: 0.2s; height: 40px; }
        .sound-wave .bar:nth-child(3) { animation-delay: 0.3s; height: 60px; }
        .sound-wave .bar:nth-child(4) { animation-delay: 0.4s; height: 80px; }
        .sound-wave .bar:nth-child(5) { animation-delay: 0.5s; height: 60px; }
        .sound-wave .bar:nth-child(6) { animation-delay: 0.6s; height: 40px; }
        .sound-wave .bar:nth-child(7) { animation-delay: 0.7s; height: 20px; }
        .sound-wave .bar:nth-child(8) { animation-delay: 0.8s; height: 40px; }
        .sound-wave .bar:nth-child(9) { animation-delay: 0.9s; height: 60px; }
        .sound-wave .bar:nth-child(10) { animation-delay: 1.0s; height: 80px; }
        .sound-wave .bar:nth-child(11) { animation-delay: 1.1s; height: 60px; }
        .sound-wave .bar:nth-child(12) { animation-delay: 1.2s; height: 40px; }
        
        @keyframes soundWave {
            0%, 100% {
                transform: scaleY(0.5);
                opacity: 0.5;
            }
            50% {
                transform: scaleY(1);
                opacity: 1;
            }
        }
        
        .app-title {
            text-align: center;
            color: white;
            font-size: 28px;
            font-weight: bold;
            margin-top: 10px;
            margin-bottom: 20px;
            letter-spacing: 1px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Sound wave animation instead of the image
    st.markdown("""
    <div class="sound-wave-container">
        <div class="sound-wave">
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
        </div>
    </div>
    <h1 class="app-title">🎵 Spotify Playlist Analyzer & Recommender</h1>
    """, unsafe_allow_html=True)
    
    # Introduction (title already in custom header)
    
    st.markdown("""
    Discover the musical DNA of your favorite playlists and get personalized recommendations.
    Just paste a Spotify playlist link below to get started!
    """)
    
    # Display any previous errors
    if st.session_state.processing_error:
        st.error(st.session_state.processing_error)
        if st.button("Clear Error"):
            st.session_state.processing_error = None
            st.rerun()
    
    # Playlist URL input with a mechanism to clear the input
    if 'clear_url_input' in st.session_state and st.session_state.clear_url_input:
        # Reset the flag
        st.session_state.clear_url_input = False
        # Show empty input
        playlist_url = st.text_input("Enter a public Spotify playlist URL:", 
                                  placeholder="https://open.spotify.com/playlist/...",
                                  key="playlist_url_input", value="")
    else:
        playlist_url = st.text_input("Enter a public Spotify playlist URL:", 
                                  placeholder="https://open.spotify.com/playlist/...",
                                  key="playlist_url_input")
    
    # Add columns for buttons
    col1, col2 = st.columns([1, 3])
    
    # Process the playlist when a valid URL is provided
    with col1:
        analyze_button = st.button("Analyze Playlist")
    
    with col2:
        if st.button("Clear Analysis"):
            # Reset all state variables
            st.session_state.processing_error = None
            st.session_state.playlist_data = None
            st.session_state.playlist_details = None
            st.session_state.playlist_analysis = None
            st.session_state.recommendations = None
            # Set the flag to clear URL input on next rerun
            st.session_state.clear_url_input = True
            st.rerun()
    
    if playlist_url and analyze_button:
        if not validate_spotify_url(playlist_url):
            st.error("Please enter a valid Spotify playlist URL")
        else:
            try:
                # Reset all previous results to ensure fresh analysis
                st.session_state.processing_error = None
                st.session_state.playlist_data = None
                st.session_state.playlist_details = None
                st.session_state.playlist_analysis = None
                st.session_state.recommendations = None
                
                with st.spinner("Fetching playlist data from Spotify..."):
                    # Extract playlist ID from URL
                    playlist_id = get_playlist_id_from_url(playlist_url)
                    logger.info(f"Processing playlist ID: {playlist_id}")
                    
                    # Get playlist details and tracks
                    playlist_details = get_playlist_details(playlist_id)
                    playlist_tracks = get_playlist_tracks(playlist_id)
                    
                    if playlist_tracks and len(playlist_tracks) > 0:
                        logger.info(f"Retrieved {len(playlist_tracks)} tracks from playlist")
                        st.session_state.playlist_data = playlist_tracks
                        st.session_state.playlist_details = playlist_details
                        
                        # Analyze the playlist with Gemini
                        with st.spinner("Analyzing playlist with Gemini AI..."):
                            try:
                                analysis = analyze_playlist(playlist_tracks)
                                if analysis:
                                    st.session_state.playlist_analysis = analysis
                                    logger.info("Playlist analysis complete")
                                else:
                                    logger.warning("Analysis returned empty result")
                                    st.session_state.playlist_analysis = {
                                        "general_description": "Unable to analyze this playlist. Please try with a different playlist.",
                                        "bpm_range": {"min": 80, "max": 160, "most_common": 120},
                                        "instruments": {"Vocals": "high", "Guitar": "medium", "Drums": "medium"},
                                        "key_distribution": {"C Major": 2, "G Major": 1},
                                        "mood_description": "Analysis unavailable.",
                                        "genre_analysis": "Analysis unavailable."
                                    }
                            
                                # Get song recommendations
                                with st.spinner("Generating song recommendations..."):
                                    try:
                                        logger.info("Starting recommendation generation")
                                        recommendations = get_song_recommendations(analysis)
                                        st.session_state.recommendations = recommendations
                                        logger.info(f"Generated {len(recommendations)} recommendations")
                                    except Exception as rec_error:
                                        logger.error(f"Error generating recommendations: {str(rec_error)}")
                                        st.session_state.recommendations = []
                            
                            except Exception as analysis_error:
                                logger.error(f"Error in analysis: {str(analysis_error)}")
                                st.session_state.processing_error = f"Error analyzing playlist: {str(analysis_error)}"
                                st.error(st.session_state.processing_error)
                        
                        st.success("Analysis complete!")
                        st.rerun()
                    else:
                        error_msg = "Unable to fetch tracks from this playlist. It might be private or empty."
                        logger.error(error_msg)
                        st.session_state.processing_error = error_msg
                        st.error(error_msg)
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                logger.error(error_msg)
                st.session_state.processing_error = error_msg
                st.error(error_msg)
    
    # Display analysis if available
    if st.session_state.playlist_data and st.session_state.playlist_analysis:
        display_results()

def display_results():
    """Display the playlist analysis and recommendations."""
    try:
        # Get data from session state
        playlist_data = st.session_state.playlist_data
        analysis = st.session_state.playlist_analysis
        recommendations = st.session_state.recommendations
        playlist_details = st.session_state.playlist_details
        
        # Display playlist information
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if playlist_details and playlist_details.get('images') and len(playlist_details['images']) > 0:
                st.image(playlist_details['images'][0]['url'], width=250)
            else:
                st.image("https://images.unsplash.com/photo-1611484550037-d5a0da2b1446", width=250)
        
        with col2:
            st.subheader(playlist_details.get('name', 'Playlist') if playlist_details else 'Playlist')
            
            if playlist_details:
                st.write(f"Created by: {playlist_details.get('owner', {}).get('display_name', 'Unknown')}")
                if playlist_details.get('description'):
                    st.write(f"Description: {playlist_details['description']}")
            
            st.write(f"Tracks: {len(playlist_data)}")
            total_duration_ms = sum(track.get('duration_ms', 0) for track in playlist_data)
            st.write(f"Total duration: {format_duration(total_duration_ms)}")
        
        # Create tabs for organization
        tab1, tab2, tab3 = st.tabs(["Playlist Analysis", "Song Recommendations", "Track List"])
        
        # Tab 1: Playlist Analysis
        with tab1:
            st.header("Playlist Insights")
            
            # Display the general analysis
            st.subheader("Musical Attributes")
            st.write(analysis.get('general_description', 'Analysis not available.'))
            
            # Create the visualization row
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.subheader("Tempo Distribution")
                tempo_chart = create_bpm_chart(analysis.get('bpm_range', {}))
                st.plotly_chart(tempo_chart, use_container_width=True)
            
            with col2:
                st.subheader("Key Distribution")
                key_chart = create_key_chart(analysis.get('key_distribution', {}))
                st.plotly_chart(key_chart, use_container_width=True)
            
            with col3:
                st.subheader("Common Instruments")
                instruments_chart = create_instruments_chart(analysis.get('instruments', {}))
                st.plotly_chart(instruments_chart, use_container_width=True)
            
            # Add mood and genre visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Mood and Energy")
                mood_chart = create_mood_and_genre_chart(analysis.get('mood_description', ''))
                st.plotly_chart(mood_chart, use_container_width=True)
            
            with col2:
                st.subheader("Genre Analysis")
                genre_chart = create_mood_and_genre_chart(analysis.get('genre_analysis', ''))
                st.plotly_chart(genre_chart, use_container_width=True)
        
        # Tab 2: Recommendations
        with tab2:
            st.header("Recommended Songs")
            
            if recommendations and len(recommendations) > 0:
                for i, rec in enumerate(recommendations):
                    if not isinstance(rec, dict):
                        continue
                        
                    title = rec.get('title', 'Recommendation')
                    artist = rec.get('artist', 'Unknown Artist')
                    
                    with st.expander(f"💫 {title} by {artist}"):
                        cols = st.columns([3, 1])
                        
                        with cols[0]:
                            st.subheader(f"{title}")
                            st.write(f"**Artist:** {artist}")
                            
                            reasoning = rec.get('reasoning', '')
                            if reasoning and reasoning != "No explanation available":
                                st.write(f"**Why you'll like it:** {reasoning}")
                            
                            # Musical attributes
                            attributes = rec.get('attributes', {})
                            if attributes and isinstance(attributes, dict) and len(attributes) > 0:
                                st.write("**Musical Attributes:**")
                                for attr, value in attributes.items():
                                    if value:  # Only show non-empty values
                                        st.write(f"- **{attr.capitalize()}:** {value}")
                        
                        with cols[1]:
                            st.write("**Listen on Spotify:**")
                            spotify_url = rec.get('spotify_url', '#')
                            if spotify_url and spotify_url != '#':
                                st.markdown(f'''
                                <a href="{spotify_url}" target="_blank">
                                    <img src="https://i.imgur.com/UDGWrM9.png" width="50">
                                </a>
                                ''', unsafe_allow_html=True)
            else:
                st.info("No recommendations available. Try analyzing a different playlist.")
        
        # Tab 3: Track List
        with tab3:
            st.header("Tracks in This Playlist")
            
            # Create a table with track information
            track_data = []
            for i, track in enumerate(playlist_data):
                track_data.append({
                    "#": i + 1,
                    "Title": track.get('name', 'Unknown'),
                    "Artist": track.get('artist', 'Unknown'),
                    "Album": track.get('album', 'Unknown'),
                    "Duration": format_duration(track.get('duration_ms', 0))
                })
            
            # Convert to pandas DataFrame and display
            if track_data:
                df = pd.DataFrame(track_data)
                st.dataframe(df, use_container_width=True, height=400)
            else:
                st.warning("No track data available.")
    
    except Exception as e:
        logger.error(f"Error displaying results: {str(e)}")
        st.error(f"Error displaying results: {str(e)}")

# Run the application
if __name__ == "__main__":
    main()
