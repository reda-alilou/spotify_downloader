from flask import Flask, redirect, request, session, url_for, render_template
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import time
from spotify_downloader import search_youtube, download_track

app = Flask(__name__)
app.secret_key = os.urandom(24)  # A random secret key for session management

sp_oauth = SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
    scope="user-library-read playlist-read-private"
)

@app.route('/')
def index():
    if not session.get('token_info'):
        return redirect(url_for('login'))
    
    token_info = session.get('token_info')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    playlists = sp.current_user_playlists()
    playlist_items = playlists['items']

    return render_template('index.html', playlists=playlist_items)

@app.route('/login')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    
    return redirect(url_for('index'))

@app.route('/select_playlist/<playlist_id>')
def select_playlist(playlist_id):
    token_info = session.get('token_info')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    # Fetch the first batch of tracks
    results = sp.playlist_tracks(playlist_id, limit=100)
    all_tracks = results['items']

    # Check if there are more tracks to fetch
    while results['next']:
        results = sp.next(results)
        all_tracks.extend(results['items'])

    # Fetch playlist details to get the name
    playlist_info = sp.playlist(playlist_id)
    playlist_name = playlist_info['name']

    return render_template('tracks.html', tracks=all_tracks, playlist_name=playlist_name, playlist_id=playlist_id)


@app.route('/download_tracks/<playlist_id>', methods=['POST'])
def download_tracks(playlist_id):
    print("Download request received")  # Debug statement
    token_info = session.get('token_info')
    
    if not token_info:
        print("No token info found")  # Debug statement
        return "No token info found!", 400

    sp = spotipy.Spotify(auth=token_info['access_token'])
    
    selected_track_ids = request.form.getlist('track')
    if not selected_track_ids:
        print("No tracks selected!")  # Debug statement
        return "No tracks selected!", 400
    
    selected_tracks = []
    for track_id in selected_track_ids:
        try:
            track_info = sp.track(track_id)
            selected_tracks.append(track_info)
        except Exception as e:
            print(f"Error fetching track info for {track_id}: {e}")  # Debug statement
    
    for song in selected_tracks:
        try:
            youtube_url = search_youtube(song['name'], song['artists'][0]['name'])
            print(f"Found YouTube URL: {youtube_url} for {song['name']}")  # Debug statement
            download_track(youtube_url, song['name'], song['artists'][0]['name'])
            time.sleep(1)  # To avoid overloading requests
        except Exception as e:
            print(f"Error downloading {song['name']} by {song['artists'][0]['name']}: {e}")  # Debug statement
    
    return "Selected tracks have been downloaded successfully!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
