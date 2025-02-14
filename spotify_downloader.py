import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
import yt_dlp
import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QComboBox, 
    QProgressBar, QMessageBox, QListWidgetItem
)
from PyQt6.QtCore import QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(filename='download_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Spotify Authentication
def authenticate_spotify():
    sp_oauth = SpotifyOAuth(
        client_id=os.getenv('SPOTIPY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIPY_REDIRECT_URI'),
        scope='playlist-read-private'
    )
    token_info = sp_oauth.get_cached_token()
    if token_info:
        return spotipy.Spotify(auth=token_info['access_token'])
    else:
        QMessageBox.critical(None, "Error", "Spotify authentication failed.")
        sys.exit()

# Get all playlists
def get_user_playlists(sp):
    return sp.current_user_playlists()['items']

# Get tracks from playlist
def get_tracks_from_playlist(sp, playlist_id):
    tracks = []
    results = sp.playlist_tracks(playlist_id)
    
    while results:
        for item in results['items']:
            track = item['track']
            if track:
                tracks.append((track['name'], track['artists'][0]['name'], track['album']['name'], track['duration_ms'] // 1000))
        results = sp.next(results) if results.get('next') else None

    return tracks

# Search YouTube for a track
def search_youtube(track_name, artist_name):
    search_query = f'ytsearch5:"{track_name} {artist_name} audio"'
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'noplaylist': True}
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(search_query, download=False)
            if 'entries' in info_dict and info_dict['entries']:
                return info_dict['entries'][0]['webpage_url']
        except Exception as e:
            logging.error(f"⚠️ Error searching YouTube for {track_name}: {e}")
            return None

# Background Thread for Downloads
class DownloadThread(QThread):
    progress_signal = pyqtSignal(int)

    def __init__(self, tracks):
        super().__init__()
        self.tracks = tracks

    def run(self):
        with ThreadPoolExecutor(max_workers=3) as executor:
            for i, track in enumerate(self.tracks):
                youtube_url = search_youtube(track[0], track[1])
                if youtube_url:
                    self.download_track(youtube_url, track[0], track[1])
                self.progress_signal.emit(int((i + 1) / len(self.tracks) * 100))

    def download_track(self, youtube_url, track_name, artist_name):
        download_folder = "SpotifyDownloads"
        os.makedirs(download_folder, exist_ok=True)

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{download_folder}/{track_name} - {artist_name}.mp3',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
            'quiet': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
                logging.info(f"✅ Downloaded {track_name} - {artist_name}")
        except Exception as e:
            logging.error(f"❌ Failed to download {track_name} - {artist_name}: {e}")

# GUI Window with Better Styling
class SpotifyDownloaderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Spotify Playlist Downloader")
        self.setGeometry(300, 200, 750, 600)

        self.sp = authenticate_spotify()
        self.playlists = get_user_playlists(self.sp)
        self.track_list = []

        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
                font-size: 14px;
            }
            QLabel {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 10px;
            }
            QComboBox, QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #2a2a2a;
                padding: 5px;
                color: white;
            }
            QPushButton {
                background-color: #1DB954;
                color: black;
                font-weight: bold;
                padding: 10px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1ed760;
            }
            QProgressBar {
                border: 1px solid #333;
                background: #222;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #1DB954;
            }
        """)

        self.layout = QVBoxLayout()

        # Title
        self.title_label = QLabel("🎵 Spotify Playlist Downloader")
        self.layout.addWidget(self.title_label)

        # Playlist Selection
        self.playlist_label = QLabel("Select a Playlist:")
        self.layout.addWidget(self.playlist_label)

        self.playlist_dropdown = QComboBox()
        self.playlist_dropdown.addItems([p['name'] for p in self.playlists])
        self.layout.addWidget(self.playlist_dropdown)

        self.load_tracks_button = QPushButton("Load Tracks")
        self.load_tracks_button.clicked.connect(self.load_tracks)
        self.layout.addWidget(self.load_tracks_button)

        # Track List
        self.track_list_widget = QListWidget()
        self.track_list_widget.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.layout.addWidget(self.track_list_widget)

        # Track Count Display
        self.track_count_label = QLabel("Total Tracks: 0")
        self.layout.addWidget(self.track_count_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)

        # Buttons Layout
        self.download_button = QPushButton("Download Selected Tracks")
        self.download_button.clicked.connect(self.download_tracks)
        self.layout.addWidget(self.download_button)

        self.download_all_button = QPushButton("Download All Tracks")
        self.download_all_button.clicked.connect(self.download_all_tracks)
        self.layout.addWidget(self.download_all_button)

        self.setLayout(self.layout)

    def load_tracks(self):
        self.track_list_widget.clear()
        selected_index = self.playlist_dropdown.currentIndex()
        playlist_id = self.playlists[selected_index]['id']
        self.track_list = get_tracks_from_playlist(self.sp, playlist_id)

        for track in self.track_list:
            item = QListWidgetItem(f"{track[0]} - {track[1]}")
            self.track_list_widget.addItem(item)

        self.track_count_label.setText(f"Total Tracks: {len(self.track_list)}")

    def download_tracks(self):
        selected_tracks = [self.track_list[i.row()] for i in self.track_list_widget.selectedIndexes()]
        self.start_download(selected_tracks)

    def download_all_tracks(self):
        self.start_download(self.track_list)

    def start_download(self, tracks):
        self.download_thread = DownloadThread(tracks)
        self.download_thread.progress_signal.connect(self.progress_bar.setValue)
        self.download_thread.start()
        QMessageBox.information(self, "Download Started", "Downloading selected tracks...")

# Run the GUI
app = QApplication(sys.argv)
window = SpotifyDownloaderGUI()
window.show()
sys.exit(app.exec())
