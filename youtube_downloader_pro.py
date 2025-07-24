import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import json
import os
import sys
import time
import re
from datetime import datetime
import webbrowser
from urllib.parse import urlparse, parse_qs
import subprocess

# Try to import yt-dlp
try:
    import yt_dlp
except ImportError:
    print("yt-dlp not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class YouTubeDownloaderPro:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("YouTube Downloader Pro")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        
        # Initialize variables
        self.download_path = os.path.expanduser("~/Downloads/YouTube")
        self.history = []
        self.current_downloads = {}
        self.settings = self.load_settings()
        self.clipboard_content = ""
        
        # Create download directory if it doesn't exist
        os.makedirs(self.download_path, exist_ok=True)
        
        self.setup_ui()
        self.start_clipboard_watcher()
        
    def load_settings(self):
        """Load settings from JSON file"""
        settings_file = "settings.json"
        default_settings = {
            "download_path": self.download_path,
            "theme": "dark",
            "auto_clipboard": True,
            "concurrent_downloads": 3,
            "default_video_quality": "best",
            "default_audio_format": "mp3"
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    # Update with any missing keys
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
        except:
            pass
        
        return default_settings
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open("settings.json", 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)
        
        # Sidebar title
        self.sidebar_title = ctk.CTkLabel(self.sidebar, text="YouTube Downloader Pro", 
                                         font=ctk.CTkFont(size=18, weight="bold"))
        self.sidebar_title.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Home", "🏠"),
            ("Video Download", "🎥"),
            ("Playlist Download", "📋"),
            ("Audio Extract", "🎵"),
            ("History", "📜"),
            ("Settings", "⚙️")
        ]
        
        for i, (name, icon) in enumerate(nav_items, 1):
            btn = ctk.CTkButton(self.sidebar, text=f"{icon} {name}", 
                               command=lambda n=name: self.show_tab(n),
                               height=40, anchor="w")
            btn.grid(row=i, column=0, padx=20, pady=5, sticky="ew")
            self.nav_buttons[name] = btn
        
        # Theme toggle
        self.theme_button = ctk.CTkButton(self.sidebar, text="🌙 Dark Mode", 
                                         command=self.toggle_theme, height=30)
        self.theme_button.grid(row=11, column=0, padx=20, pady=10, sticky="ew")
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Create all tabs
        self.create_tabs()
        
        # Show home tab by default
        self.show_tab("Home")
    
    def create_tabs(self):
        """Create all tab content"""
        self.tabs = {}
        
        # Home Tab
        self.create_home_tab()
        
        # Video Download Tab
        self.create_video_tab()
        
        # Playlist Download Tab  
        self.create_playlist_tab()
        
        # Audio Extract Tab
        self.create_audio_tab()
        
        # History Tab
        self.create_history_tab()
        
        # Settings Tab
        self.create_settings_tab()
    
    def create_home_tab(self):
        """Create home tab content"""
        home_frame = ctk.CTkFrame(self.main_frame)
        self.tabs["Home"] = home_frame
        
        # Welcome section
        welcome_label = ctk.CTkLabel(home_frame, text="Welcome to YouTube Downloader Pro", 
                                    font=ctk.CTkFont(size=32, weight="bold"))
        welcome_label.pack(pady=(50, 20))
        
        desc_label = ctk.CTkLabel(home_frame, 
                                 text="Download YouTube videos, playlists, and audio with ease",
                                 font=ctk.CTkFont(size=16))
        desc_label.pack(pady=(0, 40))
        
        # Quick actions
        quick_frame = ctk.CTkFrame(home_frame)
        quick_frame.pack(pady=20, padx=40, fill="x")
        
        quick_title = ctk.CTkLabel(quick_frame, text="Quick Actions", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        quick_title.pack(pady=(20, 10))
        
        # URL input for quick download
        url_frame = ctk.CTkFrame(quick_frame)
        url_frame.pack(pady=10, padx=20, fill="x")
        
        self.quick_url_entry = ctk.CTkEntry(url_frame, placeholder_text="Paste YouTube URL here...", 
                                           height=40)
        self.quick_url_entry.pack(side="left", fill="x", expand=True, padx=(10, 5), pady=10)
        
        quick_download_btn = ctk.CTkButton(url_frame, text="Quick Download", 
                                          command=self.quick_download, height=40, width=120)
        quick_download_btn.pack(side="right", padx=(5, 10), pady=10)
        
        # Statistics
        stats_frame = ctk.CTkFrame(home_frame)
        stats_frame.pack(pady=20, padx=40, fill="x")
        
        stats_title = ctk.CTkLabel(stats_frame, text="Statistics", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        stats_title.pack(pady=(20, 10))
        
        self.stats_label = ctk.CTkLabel(stats_frame, text="Downloads: 0 | Total Size: 0 MB", 
                                       font=ctk.CTkFont(size=14))
        self.stats_label.pack(pady=(0, 20))
    
    def create_video_tab(self):
        """Create video download tab"""
        video_frame = ctk.CTkFrame(self.main_frame)
        self.tabs["Video Download"] = video_frame
        video_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(video_frame, text="Single Video Download", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # URL input
        url_label = ctk.CTkLabel(video_frame, text="Video URL:")
        url_label.grid(row=1, column=0, sticky="w", padx=20, pady=(10, 5))
        
        self.video_url_entry = ctk.CTkEntry(video_frame, placeholder_text="https://www.youtube.com/watch?v=...")
        self.video_url_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Info button
        info_btn = ctk.CTkButton(video_frame, text="Get Video Info", 
                                command=self.get_video_info, height=35)
        info_btn.grid(row=3, column=0, sticky="w", padx=20, pady=5)
        
        # Video info display
        self.video_info_frame = ctk.CTkFrame(video_frame, height=200)
        self.video_info_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        self.video_info_frame.grid_columnconfigure(1, weight=1)
        
        # Quality selection
        quality_label = ctk.CTkLabel(video_frame, text="Quality:")
        quality_label.grid(row=5, column=0, sticky="w", padx=20, pady=(10, 5))
        
        self.video_quality = ctk.CTkOptionMenu(video_frame, 
                                              values=["best", "worst", "720p", "1080p", "480p", "360p"])
        self.video_quality.grid(row=6, column=0, sticky="w", padx=20, pady=(0, 10))
        
        # Format selection
        format_label = ctk.CTkLabel(video_frame, text="Format:")
        format_label.grid(row=7, column=0, sticky="w", padx=20, pady=(10, 5))
        
        self.video_format = ctk.CTkOptionMenu(video_frame, 
                                             values=["mp4", "webm", "mkv"])
        self.video_format.grid(row=8, column=0, sticky="w", padx=20, pady=(0, 10))
        
        # Download button
        download_btn = ctk.CTkButton(video_frame, text="Download Video", 
                                    command=self.download_video, height=40)
        download_btn.grid(row=9, column=0, sticky="w", padx=20, pady=20)
        
        # Progress section
        self.video_progress_frame = ctk.CTkFrame(video_frame)
        self.video_progress_frame.grid(row=10, column=0, sticky="ew", padx=20, pady=10)
        self.video_progress_frame.grid_columnconfigure(0, weight=1)
    
    def create_playlist_tab(self):
        """Create playlist download tab"""
        playlist_frame = ctk.CTkFrame(self.main_frame)
        self.tabs["Playlist Download"] = playlist_frame
        playlist_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(playlist_frame, text="Playlist Download", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # URL input
        url_label = ctk.CTkLabel(playlist_frame, text="Playlist URL:")
        url_label.grid(row=1, column=0, sticky="w", padx=20, pady=(10, 5))
        
        self.playlist_url_entry = ctk.CTkEntry(playlist_frame, 
                                              placeholder_text="https://www.youtube.com/playlist?list=...")
        self.playlist_url_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Get playlist info
        info_btn = ctk.CTkButton(playlist_frame, text="Get Playlist Info", 
                                command=self.get_playlist_info, height=35)
        info_btn.grid(row=3, column=0, sticky="w", padx=20, pady=5)
        
        # Playlist info
        self.playlist_info_frame = ctk.CTkFrame(playlist_frame, height=150)
        self.playlist_info_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        
        # Range selection
        range_frame = ctk.CTkFrame(playlist_frame)
        range_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        range_frame.grid_columnconfigure(1, weight=1)
        range_frame.grid_columnconfigure(3, weight=1)
        
        range_label = ctk.CTkLabel(range_frame, text="Download Range:")
        range_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.range_start = ctk.CTkEntry(range_frame, placeholder_text="Start (1)", width=80)
        self.range_start.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        
        to_label = ctk.CTkLabel(range_frame, text="to")
        to_label.grid(row=0, column=2, padx=5, pady=10)
        
        self.range_end = ctk.CTkEntry(range_frame, placeholder_text="End (all)", width=80)
        self.range_end.grid(row=0, column=3, padx=5, pady=10, sticky="w")
        
        # Options
        options_frame = ctk.CTkFrame(playlist_frame)
        options_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=10)
        
        self.playlist_audio_only = ctk.CTkCheckBox(options_frame, text="Audio Only")
        self.playlist_audio_only.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Quality selection
        quality_label = ctk.CTkLabel(options_frame, text="Quality:")
        quality_label.grid(row=0, column=1, padx=(20, 5), pady=10)
        
        self.playlist_quality = ctk.CTkOptionMenu(options_frame, 
                                                 values=["best", "worst", "720p", "1080p"])
        self.playlist_quality.grid(row=0, column=2, padx=5, pady=10)
        
        # Download button
        download_btn = ctk.CTkButton(playlist_frame, text="Download Playlist", 
                                    command=self.download_playlist, height=40)
        download_btn.grid(row=7, column=0, sticky="w", padx=20, pady=20)
        
        # Progress
        self.playlist_progress_frame = ctk.CTkFrame(playlist_frame)
        self.playlist_progress_frame.grid(row=8, column=0, sticky="ew", padx=20, pady=10)
        self.playlist_progress_frame.grid_columnconfigure(0, weight=1)
    
    def create_audio_tab(self):
        """Create audio extraction tab"""
        audio_frame = ctk.CTkFrame(self.main_frame)
        self.tabs["Audio Extract"] = audio_frame
        audio_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(audio_frame, text="Audio Extraction", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # URL input
        url_label = ctk.CTkLabel(audio_frame, text="Video/Playlist URL:")
        url_label.grid(row=1, column=0, sticky="w", padx=20, pady=(10, 5))
        
        self.audio_url_entry = ctk.CTkEntry(audio_frame, 
                                           placeholder_text="https://www.youtube.com/watch?v=... or playlist URL")
        self.audio_url_entry.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Options
        options_frame = ctk.CTkFrame(audio_frame)
        options_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=10)
        options_frame.grid_columnconfigure(1, weight=1)
        
        format_label = ctk.CTkLabel(options_frame, text="Audio Format:")
        format_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.audio_format = ctk.CTkOptionMenu(options_frame, 
                                             values=["mp3", "m4a", "wav", "flac"])
        self.audio_format.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        quality_label = ctk.CTkLabel(options_frame, text="Quality:")
        quality_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.audio_quality = ctk.CTkOptionMenu(options_frame, 
                                              values=["best", "320k", "256k", "192k", "128k"])
        self.audio_quality.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Metadata options
        self.embed_metadata = ctk.CTkCheckBox(options_frame, text="Embed Metadata")
        self.embed_metadata.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.embed_metadata.select()
        
        self.embed_thumbnail = ctk.CTkCheckBox(options_frame, text="Embed Thumbnail")
        self.embed_thumbnail.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Download button
        download_btn = ctk.CTkButton(audio_frame, text="Extract Audio", 
                                    command=self.extract_audio, height=40)
        download_btn.grid(row=4, column=0, sticky="w", padx=20, pady=20)
        
        # Progress
        self.audio_progress_frame = ctk.CTkFrame(audio_frame)
        self.audio_progress_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
        self.audio_progress_frame.grid_columnconfigure(0, weight=1)
    
    def create_history_tab(self):
        """Create history tab"""
        history_frame = ctk.CTkFrame(self.main_frame)
        self.tabs["History"] = history_frame
        history_frame.grid_columnconfigure(0, weight=1)
        history_frame.grid_rowconfigure(1, weight=1)
        
        # Title
        title = ctk.CTkLabel(history_frame, text="Download History", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # History list
        self.history_frame = ctk.CTkScrollableFrame(history_frame)
        self.history_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.history_frame.grid_columnconfigure(0, weight=1)
        
        # Clear history button
        clear_btn = ctk.CTkButton(history_frame, text="Clear History", 
                                 command=self.clear_history, height=35)
        clear_btn.grid(row=2, column=0, sticky="w", padx=20, pady=10)
    
    def create_settings_tab(self):
        """Create settings tab"""
        settings_frame = ctk.CTkFrame(self.main_frame)
        self.tabs["Settings"] = settings_frame
        settings_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        title = ctk.CTkLabel(settings_frame, text="Settings", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.grid(row=0, column=0, pady=(20, 10), sticky="w", padx=20)
        
        # Download path
        path_frame = ctk.CTkFrame(settings_frame)
        path_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        path_frame.grid_columnconfigure(1, weight=1)
        
        path_label = ctk.CTkLabel(path_frame, text="Download Path:")
        path_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.path_entry = ctk.CTkEntry(path_frame)
        self.path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.path_entry.insert(0, self.settings["download_path"])
        
        browse_btn = ctk.CTkButton(path_frame, text="Browse", 
                                  command=self.browse_download_path, width=80)
        browse_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Other settings
        other_frame = ctk.CTkFrame(settings_frame)
        other_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        self.auto_clipboard_var = ctk.BooleanVar(value=self.settings["auto_clipboard"])
        auto_clipboard_cb = ctk.CTkCheckBox(other_frame, text="Auto-detect clipboard URLs", 
                                           variable=self.auto_clipboard_var)
        auto_clipboard_cb.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # Concurrent downloads
        concurrent_label = ctk.CTkLabel(other_frame, text="Max Concurrent Downloads:")
        concurrent_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        
        self.concurrent_downloads = ctk.CTkSlider(other_frame, from_=1, to=5, number_of_steps=4)
        self.concurrent_downloads.set(self.settings["concurrent_downloads"])
        self.concurrent_downloads.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Save settings button
        save_btn = ctk.CTkButton(settings_frame, text="Save Settings", 
                                command=self.save_settings_gui, height=40)
        save_btn.grid(row=3, column=0, sticky="w", padx=20, pady=20)
        
        # About section
        about_frame = ctk.CTkFrame(settings_frame)
        about_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        
        about_title = ctk.CTkLabel(about_frame, text="About", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        about_title.pack(pady=(10, 5))
        
        about_text = ctk.CTkLabel(about_frame, 
                                 text="YouTube Downloader Pro v1.0\nBuilt with Python, CustomTkinter, and yt-dlp")
        about_text.pack(pady=(0, 10))
    
    def show_tab(self, tab_name):
        """Show selected tab"""
        # Hide all tabs
        for tab in self.tabs.values():
            tab.grid_forget()
        
        # Show selected tab
        if tab_name in self.tabs:
            self.tabs[tab_name].grid(row=0, column=0, sticky="nsew")
        
        # Update button states
        for name, btn in self.nav_buttons.items():
            if name == tab_name:
                btn.configure(fg_color=("gray75", "gray25"))
            else:
                btn.configure(fg_color=["#3B8ED0", "#1F6AA5"])
    
    def toggle_theme(self):
        """Toggle between dark and light theme"""
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_button.configure(text="☀️ Light Mode")
            self.settings["theme"] = "light"
        else:
            ctk.set_appearance_mode("dark")
            self.theme_button.configure(text="🌙 Dark Mode")
            self.settings["theme"] = "dark"
        self.save_settings()
    
    def start_clipboard_watcher(self):
        """Start watching clipboard for YouTube URLs"""
        def watch_clipboard():
            while True:
                try:
                    current = self.root.clipboard_get()
                    if (current != self.clipboard_content and 
                        self.auto_clipboard_var.get() and
                        ("youtube.com" in current or "youtu.be" in current)):
                        self.clipboard_content = current
                        # Auto-fill the current tab's URL field
                        self.root.after(0, lambda: self.auto_fill_url(current))
                except:
                    pass
                time.sleep(1)
        
        thread = threading.Thread(target=watch_clipboard, daemon=True)
        thread.start()
    
    def auto_fill_url(self, url):
        """Auto-fill URL in current tab"""
        # Simple auto-fill logic - you can make this smarter
        if hasattr(self, 'quick_url_entry') and self.quick_url_entry.get() == "":
            self.quick_url_entry.insert(0, url)
    
    def quick_download(self):
        """Quick download from home tab"""
        url = self.quick_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        # Determine if it's a playlist or single video
        if "playlist" in url:
            self.show_tab("Playlist Download")
            self.playlist_url_entry.delete(0, tk.END)
            self.playlist_url_entry.insert(0, url)
        else:
            self.show_tab("Video Download")
            self.video_url_entry.delete(0, tk.END)
            self.video_url_entry.insert(0, url)
    
    def get_video_info(self):
        """Get video information"""
        url = self.video_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return
        
        def fetch_info():
            try:
                ydl_opts = {'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.display_video_info(info))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get video info: {str(e)}"))
        
        threading.Thread(target=fetch_info, daemon=True).start()
    
    def display_video_info(self, info):
        """Display video information"""
        # Clear previous info
        for widget in self.video_info_frame.winfo_children():
            widget.destroy()
        
        # Title
        title_label = ctk.CTkLabel(self.video_info_frame, text="Title:", 
                                  font=ctk.CTkFont(weight="bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        title_text = ctk.CTkLabel(self.video_info_frame, text=info.get('title', 'N/A'))
        title_text.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Duration
        duration_label = ctk.CTkLabel(self.video_info_frame, text="Duration:", 
                                     font=ctk.CTkFont(weight="bold"))
        duration_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        duration = info.get('duration', 0)
        duration_text = f"{duration//60}:{duration%60:02d}" if duration else "N/A"
        duration_display = ctk.CTkLabel(self.video_info_frame, text=duration_text)
        duration_display.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # View count
        views_label = ctk.CTkLabel(self.video_info_frame, text="Views:", 
                                  font=ctk.CTkFont(weight="bold"))
        views_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        views = info.get('view_count', 0)
        views_text = f"{views:,}" if views else "N/A"
        views_display = ctk.CTkLabel(self.video_info_frame, text=views_text)
        views_display.grid(row=2, column=1, sticky="w", padx=10, pady=5)
    
    def get_playlist_info(self):
        """Get playlist information"""
        url = self.playlist_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a playlist URL")
            return
        
        def fetch_info():
            try:
                ydl_opts = {'quiet': True, 'no_warnings': True, 'extract_flat': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    # Update UI in main thread
                    self.root.after(0, lambda: self.display_playlist_info(info))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to get playlist info: {str(e)}"))
        
        threading.Thread(target=fetch_info, daemon=True).start()
    
    def display_playlist_info(self, info):
        """Display playlist information"""
        # Clear previous info
        for widget in self.playlist_info_frame.winfo_children():
            widget.destroy()
        
        # Title
        title_label = ctk.CTkLabel(self.playlist_info_frame, text="Playlist:", 
                                  font=ctk.CTkFont(weight="bold"))
        title_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        title_text = ctk.CTkLabel(self.playlist_info_frame, text=info.get('title', 'N/A'))
        title_text.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Video count
        count_label = ctk.CTkLabel(self.playlist_info_frame, text="Videos:", 
                                  font=ctk.CTkFont(weight="bold"))
        count_label.grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        entries = info.get('entries', [])
        count_text = str(len(entries))
        count_display = ctk.CTkLabel(self.playlist_info_frame, text=count_text)
        count_display.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Estimated duration (simplified)
        duration_label = ctk.CTkLabel(self.playlist_info_frame, text="Est. Duration:", 
                                     font=ctk.CTkFont(weight="bold"))
        duration_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        
        # Rough estimate based on average video length
        avg_duration = 4 * 60  # 4 minutes average
        total_seconds = len(entries) * avg_duration
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        duration_text = f"~{hours}h {minutes}m"
        duration_display = ctk.CTkLabel(self.playlist_info_frame, text=duration_text)
        duration_display.grid(row=2, column=1, sticky="w", padx=10, pady=5)
    
    def download_video(self):
        """Download single video"""
        url = self.video_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a video URL")
            return
        
        quality = self.video_quality.get()
        format_ext = self.video_format.get()
        
        def download():
            try:
                # Clear previous progress
                for widget in self.video_progress_frame.winfo_children():
                    widget.destroy()
                
                # Create progress bar
                progress_label = ctk.CTkLabel(self.video_progress_frame, text="Downloading...")
                progress_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
                
                progress_bar = ctk.CTkProgressBar(self.video_progress_frame)
                progress_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
                progress_bar.set(0)
                
                status_label = ctk.CTkLabel(self.video_progress_frame, text="Starting download...")
                status_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
                
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        if 'total_bytes' in d:
                            percent = d['downloaded_bytes'] / d['total_bytes']
                            self.root.after(0, lambda: progress_bar.set(percent))
                            self.root.after(0, lambda: status_label.configure(
                                text=f"Downloaded: {d['downloaded_bytes']//1024//1024}MB / {d['total_bytes']//1024//1024}MB"))
                    elif d['status'] == 'finished':
                        self.root.after(0, lambda: progress_bar.set(1))
                        self.root.after(0, lambda: status_label.configure(text="Download completed!"))
                        self.add_to_history(url, "Video", d.get('filename', 'Unknown'))
                
                # Configure yt-dlp options
                ydl_opts = {
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'format': self.get_format_string(quality, format_ext),
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Download failed: {str(e)}"))
        
        threading.Thread(target=download, daemon=True).start()
    
    def download_playlist(self):
        """Download playlist"""
        url = self.playlist_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a playlist URL")
            return
        
        start_range = self.range_start.get().strip()
        end_range = self.range_end.get().strip()
        audio_only = self.playlist_audio_only.get()
        quality = self.playlist_quality.get()
        
        def download():
            try:
                # Clear previous progress
                for widget in self.playlist_progress_frame.winfo_children():
                    widget.destroy()
                
                # Create progress display
                progress_label = ctk.CTkLabel(self.playlist_progress_frame, text="Downloading playlist...")
                progress_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
                
                progress_bar = ctk.CTkProgressBar(self.playlist_progress_frame)
                progress_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
                progress_bar.set(0)
                
                status_label = ctk.CTkLabel(self.playlist_progress_frame, text="Starting...")
                status_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
                
                current_video = 0
                total_videos = 0
                
                def progress_hook(d):
                    nonlocal current_video
                    if d['status'] == 'downloading':
                        if 'total_bytes' in d and total_videos > 0:
                            video_progress = current_video / total_videos
                            self.root.after(0, lambda: progress_bar.set(video_progress))
                            self.root.after(0, lambda: status_label.configure(
                                text=f"Video {current_video + 1}/{total_videos}: {d['filename'].split('/')[-1][:50]}..."))
                    elif d['status'] == 'finished':
                        current_video += 1
                        if total_videos > 0:
                            progress = current_video / total_videos
                            self.root.after(0, lambda: progress_bar.set(progress))
                
                # Build format string
                if audio_only:
                    format_str = 'bestaudio/best'
                else:
                    format_str = self.get_format_string(quality, 'mp4')
                
                # Build playlist selection
                playlist_items = ""
                if start_range and end_range:
                    playlist_items = f"{start_range}-{end_range}"
                elif start_range:
                    playlist_items = f"{start_range}-"
                
                ydl_opts = {
                    'outtmpl': os.path.join(self.download_path, 'Playlists/%(playlist)s/%(title)s.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'format': format_str,
                }
                
                if playlist_items:
                    ydl_opts['playlist_items'] = playlist_items
                
                if audio_only:
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                
                # Get total count first
                with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    entries = info.get('entries', [])
                    if playlist_items:
                        # Calculate actual range
                        start_idx = int(start_range) - 1 if start_range else 0
                        end_idx = int(end_range) if end_range else len(entries)
                        total_videos = end_idx - start_idx
                    else:
                        total_videos = len(entries)
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                self.root.after(0, lambda: status_label.configure(text="Playlist download completed!"))
                self.add_to_history(url, "Playlist", f"{total_videos} videos")
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Playlist download failed: {str(e)}"))
        
        threading.Thread(target=download, daemon=True).start()
    
    def extract_audio(self):
        """Extract audio from video/playlist"""
        url = self.audio_url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        audio_format = self.audio_format.get()
        quality = self.audio_quality.get()
        embed_metadata = self.embed_metadata.get()
        embed_thumbnail = self.embed_thumbnail.get()
        
        def download():
            try:
                # Clear previous progress
                for widget in self.audio_progress_frame.winfo_children():
                    widget.destroy()
                
                # Create progress display
                progress_label = ctk.CTkLabel(self.audio_progress_frame, text="Extracting audio...")
                progress_label.grid(row=0, column=0, sticky="w", padx=10, pady=5)
                
                progress_bar = ctk.CTkProgressBar(self.audio_progress_frame)
                progress_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
                progress_bar.set(0)
                
                status_label = ctk.CTkLabel(self.audio_progress_frame, text="Starting...")
                status_label.grid(row=2, column=0, sticky="w", padx=10, pady=5)
                
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        if 'total_bytes' in d:
                            percent = d['downloaded_bytes'] / d['total_bytes']
                            self.root.after(0, lambda: progress_bar.set(percent))
                            self.root.after(0, lambda: status_label.configure(
                                text=f"Extracting: {d['filename'].split('/')[-1][:50]}..."))
                    elif d['status'] == 'finished':
                        self.root.after(0, lambda: progress_bar.set(1))
                        self.root.after(0, lambda: status_label.configure(text="Audio extraction completed!"))
                
                # Configure quality
                quality_map = {'best': '0', '320k': '320', '256k': '256', '192k': '192', '128k': '128'}
                audio_quality = quality_map.get(quality, '192')
                
                postprocessors = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': audio_format,
                    'preferredquality': audio_quality,
                }]
                
                if embed_metadata:
                    postprocessors.append({'key': 'FFmpegMetadata'})
                
                if embed_thumbnail:
                    postprocessors.append({'key': 'EmbedThumbnail'})
                
                ydl_opts = {
                    'outtmpl': os.path.join(self.download_path, 'Audio/%(title)s.%(ext)s'),
                    'progress_hooks': [progress_hook],
                    'format': 'bestaudio/best',
                    'postprocessors': postprocessors,
                    'writethumbnail': embed_thumbnail,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                self.add_to_history(url, "Audio", f"{audio_format.upper()} extraction")
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Audio extraction failed: {str(e)}"))
        
        threading.Thread(target=download, daemon=True).start()
    
    def get_format_string(self, quality, format_ext):
        """Generate format string for yt-dlp"""
        if quality == "best":
            return f"best[ext={format_ext}]/best"
        elif quality == "worst":
            return f"worst[ext={format_ext}]/worst"
        else:
            height = quality.replace('p', '')
            return f"best[height<={height}][ext={format_ext}]/best[height<={height}]/best"
    
    def add_to_history(self, url, type_str, info):
        """Add download to history"""
        entry = {
            'url': url,
            'type': type_str,
            'info': info,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history.append(entry)
        self.update_history_display()
        self.update_stats()
    
    def update_history_display(self):
        """Update history display"""
        # Clear existing items
        for widget in self.history_frame.winfo_children():
            widget.destroy()
        
        # Add history items
        for i, entry in enumerate(reversed(self.history[-20:])):  # Show last 20
            item_frame = ctk.CTkFrame(self.history_frame)
            item_frame.grid(row=i, column=0, sticky="ew", padx=5, pady=2)
            item_frame.grid_columnconfigure(1, weight=1)
            
            # Type icon
            type_icons = {'Video': '🎥', 'Playlist': '📋', 'Audio': '🎵'}
            icon_label = ctk.CTkLabel(item_frame, text=type_icons.get(entry['type'], '📄'), 
                                     font=ctk.CTkFont(size=16))
            icon_label.grid(row=0, column=0, padx=10, pady=5)
            
            # Info
            info_text = f"{entry['type']}: {entry['info']}\n{entry['timestamp']}"
            info_label = ctk.CTkLabel(item_frame, text=info_text, justify="left")
            info_label.grid(row=0, column=1, sticky="w", padx=5, pady=5)
            
            # URL button
            url_btn = ctk.CTkButton(item_frame, text="🔗", width=30, height=30,
                                   command=lambda u=entry['url']: webbrowser.open(u))
            url_btn.grid(row=0, column=2, padx=5, pady=5)
    
    def clear_history(self):
        """Clear download history"""
        if messagebox.askyesno("Confirm", "Clear all download history?"):
            self.history.clear()
            self.update_history_display()
            self.update_stats()
    
    def update_stats(self):
        """Update statistics display"""
        total_downloads = len(self.history)
        # Simplified stats - in a real app you'd track actual file sizes
        estimated_size = total_downloads * 50  # 50MB average
        stats_text = f"Downloads: {total_downloads} | Est. Total Size: {estimated_size} MB"
        if hasattr(self, 'stats_label'):
            self.stats_label.configure(text=stats_text)
    
    def browse_download_path(self):
        """Browse for download directory"""
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)
    
    def save_settings_gui(self):
        """Save settings from GUI"""
        self.settings["download_path"] = self.path_entry.get()
        self.settings["auto_clipboard"] = self.auto_clipboard_var.get()
        self.settings["concurrent_downloads"] = int(self.concurrent_downloads.get())
        
        self.download_path = self.settings["download_path"]
        os.makedirs(self.download_path, exist_ok=True)
        
        self.save_settings()
        messagebox.showinfo("Success", "Settings saved successfully!")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

# Main execution
if __name__ == "__main__":
    app = YouTubeDownloaderPro()
    app.run()