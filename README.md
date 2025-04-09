# 🎵 Spotify Playlist Analyzer & Recommender

A powerful Streamlit web application that leverages Spotify's API and Google's Gemini AI to analyze playlists and recommend similar songs that match the musical DNA of your favorite playlists.

Link to application- https://carmgjzwg2wgv85savvjxj.streamlit.app/

![Spotify Playlist Analyzer](static/new_banner.jpg)

## 🚀 Features

- **Playlist Analysis**: Extract detailed insights about your playlists including:
  - Tempo/BPM range analysis
  - Key distribution visualization
  - Instrument detection
  - Mood and energy profiling
  - Genre analysis

- **Intelligent Recommendations**: Get personalized song recommendations based on:
  - Acoustic attributes and musical linguistics
  - Genre and mood matching
  - Region-specific recommendations (Bollywood, K-Pop, Latin, etc.)
  - Decade-based matching to recommend songs from similar eras

- **Interactive UI**:
  - Animated sound wave visualization in the header
  - Clean, responsive interface with Spotify's branding
  - Detailed charts and visualizations
  - Expandable recommendation cards with song details

## 📋 Requirements

- Python 3.8+
- Spotify Developer Account (for API credentials)
- Google Gemini API key

## 🔧 Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/spotify-playlist-analyzer.git
cd spotify-playlist-analyzer
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your API credentials:
```
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
GEMINI_API_KEY=your_gemini_api_key
```

## 🏃‍♂️ Running the App

Launch the application with:
```bash
streamlit run app.py
```

The app will be available at http://localhost:5000

## 🎮 Usage

1. Enter a public Spotify playlist URL in the input field
2. Click "Analyze Playlist"
3. View your playlist insights in the "Playlist Analysis" tab
4. Explore personalized song recommendations in the "Recommendations" tab
5. Browse track information in the "Track List" tab

## 📂 Project Structure

- `app.py`: Main Streamlit application
- `spotify_service.py`: Handles Spotify API integration
- `gemini_service.py`: Integrates with Google's Gemini AI
- `visualization.py`: Data visualization components
- `utils.py`: Utility functions

## 🔄 How It Works

1. **Data Fetching**: Retrieves playlist data from Spotify API including tracks, artists, and audio features
2. **AI Analysis**: Processes playlist data with Google's Gemini AI to identify musical patterns and attributes
3. **Recommendation Generation**: Uses AI to generate personalized song recommendations
4. **Visualization**: Creates interactive charts and displays the analysis and recommendations

## 🔍 Advanced Features

- **Fallback Mechanism**: Graceful degradation if API limits are reached or services are unavailable
- **Culturally Appropriate Recommendations**: Region-specific music suggestions
- **Decade-Based Matching**: Recommendations that respect the era of your playlist's music
- **Session State Management**: Persistent analysis results between app interactions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Spotify Web API](https://developer.spotify.com/documentation/web-api/)
- [Google Gemini AI](https://ai.google.dev/)
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/)
