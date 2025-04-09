import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
#import os
import re
import time
import streamlit as st

def get_spotify_client():
    """Initialize and return a Spotify client."""
    try:
        # client_id = os.getenv('SPOTIPY_CLIENT_ID')
        # client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
        client_id = st.secrets["spotify"]["client_id"]
        client_secret = st.secrets["spotify"]["client_secret"]
        
        if not client_id or not client_secret:
            raise ValueError("Spotify credentials not found in environment variables")
        
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        return spotipy.Spotify(auth_manager=auth_manager)
    
    except Exception as e:
        raise Exception(f"Failed to initialize Spotify client: {str(e)}")

def get_playlist_id_from_url(playlist_url):
    """Extract the playlist ID from a Spotify playlist URL."""
    # Pattern to match playlist ID in Spotify URL
    pattern = r'playlist\/([a-zA-Z0-9]+)'
    match = re.search(pattern, playlist_url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid Spotify playlist URL format")

def get_playlist_details(playlist_id):
    """Get basic information about a Spotify playlist."""
    try:
        sp = get_spotify_client()
        playlist = sp.playlist(playlist_id, fields='name,description,images,owner(display_name),followers(total)')
        return playlist
    except Exception as e:
        raise Exception(f"Error fetching playlist details: {str(e)}")

def get_playlist_tracks(playlist_id):
    """Fetches all tracks from a Spotify playlist, handling pagination."""
    all_tracks_data = []
    offset = 0
    limit = 100  # Max items per request
    sp = get_spotify_client()

    while True:
        try:
            # Make the API call
            response = sp.playlist_items(
                playlist_id,
                fields='items(track(id,name,artists(name),album(name),duration_ms,popularity)), next',
                additional_types=['track'],
                offset=offset,
                limit=limit
            )

            if not response or 'items' not in response:
                break

            items = response.get('items', [])
            if not items:
                break

            for item in items:
                track_info = item.get('track')
                if track_info:
                    # Skip tracks with no ID (local files, etc.)
                    if not track_info.get('id'):
                        continue
                        
                    track_name = track_info.get('name', 'N/A')
                    # Handle multiple artists
                    artist_names = ', '.join([artist.get('name', 'N/A') for artist in track_info.get('artists', [])])
                    album_name = track_info.get('album', {}).get('name', 'N/A')
                    duration_ms = track_info.get('duration_ms', 0)
                    popularity = track_info.get('popularity', 0)

                    all_tracks_data.append({
                        'id': track_info.get('id'),
                        'name': track_name,
                        'artist': artist_names,
                        'album': album_name,
                        'duration_ms': duration_ms,
                        'popularity': popularity
                    })

            # Check if there are more pages
            if response.get('next'):
                offset += limit
                time.sleep(0.5)  # Add a small delay to be kind to the API
            else:
                break

        except spotipy.exceptions.SpotifyException as e:
            # Handle specific errors like rate limiting (429)
            if e.http_status == 429:
                retry_after = int(e.headers.get('Retry-After', 5))
                time.sleep(retry_after)
            else:
                raise Exception(f"Spotify API Error: {e.http_status} - {e.msg}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred while fetching tracks: {str(e)}")

    return all_tracks_data

def get_audio_features(track_ids):
    """Get audio features for tracks from Spotify API."""
    try:
        sp = get_spotify_client()
        
        # Split track_ids into chunks of 100 (Spotify API limit)
        chunks = [track_ids[i:i + 100] for i in range(0, len(track_ids), 100)]
        
        all_features = []
        for chunk in chunks:
            features = sp.audio_features(chunk)
            all_features.extend(features)
            time.sleep(0.5)  # Be kind to the API
            
        return all_features
    
    except Exception as e:
        raise Exception(f"Error fetching audio features: {str(e)}")
