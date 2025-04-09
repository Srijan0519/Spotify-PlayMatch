def format_duration(duration_ms):
    """Format duration in milliseconds to a human-readable format.
    
    Args:
        duration_ms (int): Duration in milliseconds
        
    Returns:
        str: Formatted duration string (e.g., "3:45")
    """
    if not duration_ms:
        return "0:00"
    
    # Convert milliseconds to seconds
    total_seconds = int(duration_ms / 1000)
    
    # Calculate hours, minutes, and seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    # Format based on length
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def extract_playlist_id_from_url(url):
    """Extract playlist ID from Spotify URL."""
    if '/playlist/' in url:
        parts = url.split('/playlist/')
        if len(parts) > 1:
            playlist_id = parts[1].split('?')[0]
            return playlist_id
    return None
