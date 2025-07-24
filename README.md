# YouTube Downloader Pro

YouTube Downloader Pro is a desktop application built with Python, CustomTkinter, and yt-dlp. It allows you to download YouTube videos, playlists, and extract audio with a modern GUI.

## Features

- Download single videos in various qualities and formats
- Download entire playlists with range selection
- Extract audio from videos or playlists (supports mp3, m4a, wav, flac)
- Embed metadata and thumbnails in audio files
- Download history tracking
- Customizable download path and concurrent downloads
- Auto-detect YouTube URLs from clipboard
- Dark and light theme support

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/Trishan0/youtube-downloader-pro.git
   cd youtube-downloader-pro
   ```

2. **Install dependencies:**
   - Python 3.8+
   - [yt-dlp](https://github.com/yt-dlp/yt-dlp)
   - [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

   You can install dependencies with pip:
   ```sh
   pip install yt-dlp customtkinter
   ```

3. **Run the application:**
   ```sh
   python youtube_downloader_pro.py
   ```

## Usage

- **Home Tab:** Quick download by pasting a YouTube URL.
- **Video Download Tab:** Download a single video with quality and format options.
- **Playlist Download Tab:** Download playlists, select range, and choose audio-only mode.
- **Audio Extract Tab:** Extract audio from videos/playlists with format, quality, and metadata options.
- **History Tab:** View and clear your download history.
- **Settings Tab:** Change download path, theme, and concurrent download settings.

## Settings

Settings are saved in `settings.json` in the project directory. You can change the download path, theme, and other options from the Settings tab.

## License

This project is licensed under the MIT License.

## Credits

- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

---

**Note:** This project is not affiliated with YouTube.