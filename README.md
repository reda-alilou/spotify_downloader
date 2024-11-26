# Spotify Playlist Downloader

A Python project that allows users to download tracks from their Spotify playlists by searching for the tracks on YouTube and downloading them as MP3 files.

## Features

- **Spotify Authentication:** Authenticate using your Spotify account to access your playlists.
- **View Playlists:** Fetch and display all playlists in your Spotify account.
- **Select Tracks:** Choose specific tracks from a playlist or select all tracks.
- **Download Tracks:** Search YouTube for the selected tracks and download them as MP3 files.

## Technologies Used

- **Python:** For scripting and handling Spotify API calls.
- **Spotipy:** A lightweight Python library for the Spotify Web API.
- **yt-dlp:** A YouTube downloader tool for retrieving MP3 versions of the selected tracks.
- **Environment Variables:** Used to securely handle Spotify API credentials.

## How to Run the Project

1. **Clone the repository:**
   ```bash
   git clone https://github.com/reda-alilou/spotify_downloader.git
2. **Navigate to the project directory:**
   ```bash
   cd spotify-downloader
3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
4. **Set up your environment variables:**
   Create a .env file in the root of your project and add your Spotify API credentials like this:
    ```bash
    SPOTIPY_CLIENT_ID=your_spotify_client_id
    SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
    SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
5. **Run the script:**
    ```bash
    python spotify_downloader.py

## How to Use the Spotify Playlist Downloader

1. **Authenticate:** After running the script, you'll be provided with a Spotify authentication URL. Visit the URL, authorize the app, and paste the redirect URL back into the terminal.

2. **Select a Playlist:**
- View a list of your Spotify playlists with numbered options.
- Enter the corresponding number to select a playlist.

3. **Select Tracks:**
- You can choose specific tracks by entering their numbers separated by commas (e.g., 1,3,5), or type 'all' to select all tracks.

4. **Download Tracks:**
- Once you've selected the tracks, the script will search YouTube for each song and download them as MP3 files into a `SpotifyDownloads` folder.
- Each track is downloaded with its name and artist in the file name.

## Future Improvements

- Implement a graphical user interface (GUI) using Tkinter or PyQt.
- Improve the accuracy of YouTube search results for better track matching.
- Add support for more file formats beyond MP3 (e.g., WAV or FLAC).
- Include a progress bar or notification for the download process.

## Contributing

Contributions are welcome! If you have suggestions or improvements, feel free to open an issue or submit a pull request.

## License
This project is open-source and available under the MIT License.

## Author
**Reda Alilou**

- [LinkedIn](https://www.linkedin.com/in/reda-alilou-b7a085330/)
- [GitHub](https://github.com/Redaaaaaaaaaaa)
