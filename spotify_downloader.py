import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import yt_dlp
import time

# 1. Authentication with Spotify API
def authenticate_spotify():
    # Set up Spotify OAuth using client credentials from environment variables
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv('SPOTIPY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
        scope='user-library-read playlist-read-private'
    )

    # Step 1: Generate authorization URL
    auth_url = sp_oauth.get_authorize_url()
    print(f'Please go to the following URL to authorize the application: {auth_url}')

    # Step 2: Ask user to provide the URL they were redirected to after authorization
    response = input('Paste the URL you were redirected to: ')

    # Step 3: Extract the authorization code from the redirected URL
    code = sp_oauth.parse_response_code(response)

    # Step 4: Use the authorization code to obtain an access token
    token_info = sp_oauth.get_access_token(code)

    # Check if token is obtained successfully and return authenticated Spotify client
    if token_info:
        print('Access token successfully obtained!')
        return spotipy.Spotify(auth=token_info['access_token'])
    else:
        print('Failed to obtain access token.')
        exit()

# 2. Fetch and display Spotify playlists for the current user
def get_user_playlists(sp):
    playlists = sp.current_user_playlists()  # Fetch user playlists
    all_playlists = []

    # Loop through paginated playlist results and print playlist names
    while playlists:
        for idx, playlist in enumerate(playlists['items'], start=len(all_playlists) + 1):
            print(f"{idx}. {playlist['name']} - ID: {playlist['id']}")
            all_playlists.append(playlist)
        
        # Check if there are more playlists to fetch
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    
    return all_playlists

# 3. Let the user select a playlist from the displayed list
def select_playlist(sp, playlists):
    while True:
        choice = input('Choose the playlist you want to select: ')
        if choice.isdigit() and 1 <= int(choice) <= len(playlists):
            selected_playlist = playlists[int(choice) - 1]
            print(f"Selected Playlist: {selected_playlist['name']}")
            return selected_playlist['id']  # Return selected playlist ID
        else:
            print('Please enter a valid number!')

# 4. Get all tracks from a selected playlist
def get_tracks_from_playlist(sp, playlist_id):
    tracks = sp.playlist_tracks(playlist_id)  # Fetch tracks from selected playlist
    all_tracks = []

    # Loop through paginated track results and print track names and artists
    while tracks:
        for idx, item in enumerate(tracks['items'], start=len(all_tracks) + 1):
            track_name = item['track']['name']
            artist_name = item['track']['artists'][0]['name']
            print(f"{idx}. {track_name} - Artist: {artist_name}")
            all_tracks.append(item)

        # Check if there are more tracks to fetch
        if tracks['next']:
            tracks = sp.next(tracks)
        else:
            tracks = None

    return all_tracks

# 5. Allow the user to select specific tracks or download all
def select_tracks(all_tracks):
    while True:
        choice = input("Enter numbers separated by commas (e.g., 1,2,3) or 'all' to select all: ").strip()
        if choice.lower() == 'all':
            return all_tracks  # Select all tracks if user enters 'all'
        choice_list = choice.split(',')
        valid_choices = []
        for number in choice_list:
            if number.isdigit() and 1 <= int(number) <= len(all_tracks):
                valid_choices.append(int(number))
            else:
                print("Please enter valid numbers separated by commas or 'all'!")
                break
        else:
            return [all_tracks[i - 1] for i in valid_choices]  # Return selected tracks

# 6. Search for a track on YouTube
def search_youtube(track_name, artist_name):
    search_query = f'ytsearch5:"{track_name}" "{artist_name}"'  # Search query for YouTube
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True
    }
    
    # Use yt-dlp to search for the track on YouTube
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(search_query, download=False)
        if 'entries' in info_dict and info_dict['entries']:
            for entry in info_dict['entries']:
                video_title = entry.get('title', '').lower()
                if track_name.lower() in video_title and artist_name.lower() in video_title:
                    return entry['webpage_url']

        return info_dict['entries'][0]['webpage_url'] if info_dict['entries'] else None

# 7. Download the track from YouTube as MP3
def download_track(youtube_url, track_name, artist_name):
    if not youtube_url:
        print(f"Could not find a YouTube link for {track_name} by {artist_name}. Skipping download.")
        return

    download_folder = "SpotifyDownloads"
    os.makedirs(download_folder, exist_ok=True)  # Create the download folder if it doesn't exist

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_folder}/{track_name} - {artist_name}.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    # Use yt-dlp to download the track
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f'Downloading: {track_name} by {artist_name}...')
            ydl.download([youtube_url])
            print(f'Download completed: {track_name} by {artist_name}')
    except Exception as e:
        print(f"Error downloading {track_name} by {artist_name}: {e}")

# Main program execution
if __name__ == "__main__":
    # Authenticate with Spotify
    sp = authenticate_spotify()

    # Get user's playlists and let them select one
    playlists = get_user_playlists(sp)
    selected_playlist_id = select_playlist(sp, playlists)
    
    # Fetch and select tracks from the selected playlist
    all_tracks = get_tracks_from_playlist(sp, selected_playlist_id)
    selected_tracks = select_tracks(all_tracks)

    # Search and download the selected tracks from YouTube
    for song in selected_tracks:
        youtube_url = search_youtube(song['track']['name'], song['track']['artists'][0]['name'])
        download_track(youtube_url, song['track']['name'], song['track']['artists'][0]['name'])
        time.sleep(1)  # Add a delay between downloads
