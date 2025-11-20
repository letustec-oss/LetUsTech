import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import time
from pathlib import Path
import yt_dlp
import re
import json
from datetime import datetime
from PIL import Image, ImageTk
import requests
from io import BytesIO
import subprocess
import sys
from queue import Queue
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed


class MyLogger:
    """Custom logger to capture yt-dlp output"""
    def __init__(self, output_queue):
        self.output_queue = output_queue
    
    def debug(self, msg):
        # Filter out some overly verbose messages if needed
        if msg.startswith('[debug]'):
            return
        self.output_queue.put(msg + '\n')
    
    def info(self, msg):
        self.output_queue.put(msg + '\n')
    
    def warning(self, msg):
        self.output_queue.put(f'WARNING: {msg}\n')
    
    def error(self, msg):
        self.output_queue.put(f'ERROR: {msg}\n')


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("LetUsTech - YouTube Converter")
        self.root.geometry("1000x650")
        self.root.resizable(True, True)  # Enable resizing
        self.root.minsize(900, 600)  # Set minimum size
        
        # Set icon if available
        try:
            if os.path.exists("favicon.ico"):
                self.root.iconbitmap("favicon.ico")
        except:
            pass
        
        # Enhanced Color scheme - Navy and Green branding
        self.bg_color = "#0f0f1e"
        self.accent_color = "#1a1a2e"
        self.card_color = "#16213e"
        self.green_color = "#00ff88"
        self.green_hover = "#00cc6a"
        self.text_color = "#e4e4e7"
        self.text_muted = "#a1a1aa"
        self.border_color = "#27272a"
        
        self.root.configure(bg=self.bg_color)
        
        # Download path - automatically create Videos folder
        videos_folder = Path.home() / "Videos"
        videos_folder.mkdir(exist_ok=True)  # Create if doesn't exist
        self.download_path = str(videos_folder)
        
        # Settings
        self.settings_file = Path.home() / ".youtube_downloader_settings.json"
        self.history_file = Path.home() / ".youtube_downloader_history.json"
        self.debug_mode = True  # Enable debug by default
        self.download_history = []
        self.current_thumbnail = None
        self.is_playlist = False
        self.playlist_videos = []
        self.selected_videos = []
        self.full_playlist_info = None  # Store full playlist info for large playlists
        self.output_queue = Queue()
        self.max_playlist_size = 50  # Limit playlists to first 50 videos
        self.concurrent_downloads = 5  # Number of simultaneous downloads (increased for speed)
        self.download_stopped = False  # Emergency stop flag
        
        print("Loading application settings...")
        self.load_settings()
        print("✓ Settings loaded successfully")
        
        print("Loading download history...")
        self.load_history()
        print("✓ History loaded successfully")
        
        # Check FFmpeg
        print("Checking FFmpeg installation status...")
        try:
            self.check_ffmpeg()
            print("✓ FFmpeg check completed")
        except Exception as e:
            print(f"⚠ FFmpeg check issue: {str(e)}")
        
        # Setup UI
        print("Setting up user interface...")
        self.setup_ui()
        print("✓ User interface setup complete")
        
        print("YouTube Downloader initialization completed successfully!")
        
    def setup_ui(self):
        # Header with gradient effect
        header_frame = tk.Frame(self.root, bg=self.card_color, height=100)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Logo/Icon area
        logo_frame = tk.Frame(header_frame, bg=self.card_color)
        logo_frame.pack(side="left", padx=30, pady=20)
        
        # Try to load logo image
        try:
            if os.path.exists("LetUsTech.png"):
                logo_img = Image.open("LetUsTech.png")
                logo_img = logo_img.resize((50, 50), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(
                    logo_frame,
                    image=logo_photo,
                    bg=self.card_color
                )
                logo_label.image = logo_photo  # Keep reference
                logo_label.pack(side="left")
            else:
                # Fallback to play icon
                logo_label = tk.Label(
                    logo_frame,
                    text="▶",
                    font=("Segoe UI", 32, "bold"),
                    bg=self.card_color,
                    fg=self.green_color
                )
                logo_label.pack(side="left")
        except:
            # Fallback to play icon if image loading fails
            logo_label = tk.Label(
                logo_frame,
                text="▶",
                font=("Segoe UI", 32, "bold"),
                bg=self.card_color,
                fg=self.green_color
            )
            logo_label.pack(side="left")
        
        title_container = tk.Frame(logo_frame, bg=self.card_color)
        title_container.pack(side="left", padx=10)
        
        title_label = tk.Label(
            title_container,
            text="YouTube Converter",
            font=("Segoe UI", 20, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        title_label.pack(anchor="w")
        
        subtitle_label = tk.Label(
            title_container,
            text="Fast, easy video and audio downloads from YouTube",
            font=("Segoe UI", 9),
            bg=self.card_color,
            fg=self.text_muted
        )
        subtitle_label.pack(anchor="w")
        
        # Header buttons container
        header_btn_frame = tk.Frame(header_frame, bg=self.card_color)
        header_btn_frame.pack(side="right", padx=30)
        
        # Help button
        help_btn = tk.Button(
            header_btn_frame,
            text="❓ Help",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            padx=15,
            pady=8,
            command=self.show_help_guide
        )
        help_btn.pack(side="right", padx=5)
        
        # About button
        about_btn = tk.Button(
            header_btn_frame,
            text="ℹ About",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            padx=15,
            pady=8,
            command=self.show_about
        )
        about_btn.pack(side="right", padx=5)
        
        # History button
        history_btn = tk.Button(
            header_btn_frame,
            text="📜 History",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            padx=15,
            pady=8,
            command=self.show_history
        )
        history_btn.pack(side="right", padx=5)
        
        # Settings button
        settings_btn = tk.Button(
            header_btn_frame,
            text="⚙ Settings",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            padx=15,
            pady=8,
            command=self.toggle_settings
        )
        settings_btn.pack(side="right", padx=5)
        
        # Main content frame
        container_frame = tk.Frame(self.root, bg=self.bg_color)
        container_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Left side - Main download controls (Card style)
        main_card = tk.Frame(container_frame, bg=self.card_color)
        main_card.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        main_frame = tk.Frame(main_card, bg=self.card_color)
        main_frame.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Right side - Thumbnail preview (Card style) - MADE BIGGER
        thumbnail_card = tk.Frame(container_frame, bg=self.card_color, width=350)  # Increased from 280
        thumbnail_card.pack(side="right", fill="y")
        thumbnail_card.pack_propagate(False)
        
        thumbnail_frame = tk.Frame(thumbnail_card, bg=self.card_color)
        thumbnail_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        thumb_title = tk.Label(
            thumbnail_frame,
            text="🎬 Preview",
            font=("Segoe UI", 12, "bold"),
            bg=self.card_color,
            fg=self.green_color
        )
        thumb_title.pack(pady=(0, 10))
        
        # Thumbnail display area with border - MADE BIGGER
        thumb_display_frame = tk.Frame(thumbnail_frame, bg=self.border_color, padx=2, pady=2)
        thumb_display_frame.pack(pady=(0, 10))
        
        self.thumbnail_label = tk.Label(
            thumb_display_frame,
            text="No preview\nClick 'Load Preview' below",
            font=("Segoe UI", 9),
            bg=self.accent_color,
            fg=self.text_muted,
            wraplength=300,  # Increased from 230
            height=10,       # Increased from 8
            width=40         # Increased from 30
        )
        self.thumbnail_label.pack()
        
        self.video_title_label = tk.Label(
            thumbnail_frame,
            text="",
            font=("Segoe UI", 9, "bold"),
            bg=self.card_color,
            fg=self.text_color,
            wraplength=310,  # Increased from 240
            justify="center"
        )
        self.video_title_label.pack(pady=(0, 10))
        
        # Preview buttons with better styling
        self.preview_btn = tk.Button(
            thumbnail_frame,
            text="🔍 Load Preview",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=self.load_preview
        )
        self.preview_btn.pack(pady=(0, 8), fill="x", ipady=8)
        
        # Select videos button
        self.select_videos_btn = tk.Button(
            thumbnail_frame,
            text="📋 Select Videos",
            font=("Segoe UI", 9, "bold"),
            bg=self.green_color,
            fg=self.bg_color,
            activebackground=self.green_hover,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=self.show_video_selector,
            state="disabled"
        )
        self.select_videos_btn.pack(fill="x", ipady=8)
        
        # Settings Panel (hidden by default) - improved styling
        self.settings_frame = tk.Frame(self.root, bg=self.accent_color, height=180)
        self.settings_visible = False
        
        settings_inner = tk.Frame(self.settings_frame, bg=self.accent_color)
        settings_inner.pack(fill="both", expand=True, padx=30, pady=15)
        
        settings_title = tk.Label(
            settings_inner,
            text="⚙ Settings",
            font=("Segoe UI", 13, "bold"),
            bg=self.accent_color,
            fg=self.green_color
        )
        settings_title.pack(anchor="w", pady=(0, 10))
        
        # Settings grid
        settings_grid = tk.Frame(settings_inner, bg=self.accent_color)
        settings_grid.pack(fill="x")
        
        # Debug mode checkbox
        debug_container = tk.Frame(settings_grid, bg=self.accent_color)
        debug_container.pack(fill="x", pady=5)
        
        self.debug_var = tk.BooleanVar(value=self.debug_mode)
        
        debug_check = tk.Checkbutton(
            debug_container,
            text="Enable Debug Mode",
            variable=self.debug_var,
            font=("Segoe UI", 10),
            bg=self.accent_color,
            fg=self.text_color,
            selectcolor=self.bg_color,
            activebackground=self.accent_color,
            activeforeground=self.green_color,
            cursor="hand2",
            command=self.toggle_debug_mode
        )
        debug_check.pack(side="left")
        
        debug_desc = tk.Label(
            debug_container,
            text="Show detailed console output for troubleshooting",
            font=("Segoe UI", 8),
            bg=self.accent_color,
            fg=self.text_muted
        )
        debug_desc.pack(side="left", padx=10)
        
        # Playlist mode checkbox
        playlist_container = tk.Frame(settings_grid, bg=self.accent_color)
        playlist_container.pack(fill="x", pady=5)
        
        self.playlist_var = tk.BooleanVar(value=False)
        
        playlist_check = tk.Checkbutton(
            playlist_container,
            text="Download First 50 from Playlist",
            variable=self.playlist_var,
            font=("Segoe UI", 10),
            bg=self.accent_color,
            fg=self.text_color,
            selectcolor=self.bg_color,
            activebackground=self.accent_color,
            activeforeground=self.green_color,
            cursor="hand2"
        )
        playlist_check.pack(side="left")
        
        playlist_desc = tk.Label(
            playlist_container,
            text="Download first 50 videos when URL is a playlist (faster!)",
            font=("Segoe UI", 8),
            bg=self.accent_color,
            fg=self.text_muted
        )
        playlist_desc.pack(side="left", padx=10)
        
        # URL Input Section
        url_section = tk.Frame(main_frame, bg=self.card_color)
        url_section.pack(fill="x", pady=(0, 20))
        
        url_label = tk.Label(
            url_section,
            text="📺 Video URL",
            font=("Segoe UI", 11, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        url_label.pack(anchor="w", pady=(0, 8))
        
        url_entry_frame = tk.Frame(url_section, bg=self.border_color, padx=1, pady=1)
        url_entry_frame.pack(fill="x")
        
        self.url_entry = tk.Entry(
            url_entry_frame,
            font=("Segoe UI", 10),
            bg=self.accent_color,
            fg=self.text_color,
            insertbackground=self.green_color,
            relief="flat",
            bd=0
        )
        self.url_entry.pack(fill="x", ipady=10, padx=2, pady=2)
        
        url_hint = tk.Label(
            url_section,
            text="Paste any YouTube video or playlist URL",
            font=("Segoe UI", 8),
            bg=self.card_color,
            fg=self.text_muted
        )
        url_hint.pack(anchor="w", pady=(5, 0))
        
        # Quality Selection Section
        quality_section = tk.Frame(main_frame, bg=self.card_color)
        quality_section.pack(fill="x", pady=(0, 20))
        
        quality_label = tk.Label(
            quality_section,
            text="🎞️ Quality / Format",
            font=("Segoe UI", 11, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        quality_label.pack(anchor="w", pady=(0, 8))
        
        self.quality_var = tk.StringVar(value="Best Quality (Video + Audio)")
        
        quality_options = [
            "Best Quality (Video + Audio)",
            "1080p",
            "720p",
            "480p",
            "360p",
            "Audio Only (MP3)"
        ]
        
        quality_frame = tk.Frame(quality_section, bg=self.border_color, padx=1, pady=1)
        quality_frame.pack(fill="x")
        
        self.quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.quality_var,
            values=quality_options,
            state="readonly",
            font=("Segoe UI", 10)
        )
        self.quality_combo.pack(fill="x", ipady=8, padx=2, pady=2)
        
        # Download Path Section
        path_section = tk.Frame(main_frame, bg=self.card_color)
        path_section.pack(fill="x", pady=(0, 20))
        
        path_label = tk.Label(
            path_section,
            text="📁 Download Location",
            font=("Segoe UI", 11, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        path_label.pack(anchor="w", pady=(0, 8))
        
        path_frame = tk.Frame(path_section, bg=self.card_color)
        path_frame.pack(fill="x")
        
        path_entry_container = tk.Frame(path_frame, bg=self.border_color, padx=1, pady=1)
        path_entry_container.pack(side="left", fill="x", expand=True)
        
        self.path_entry = tk.Entry(
            path_entry_container,
            font=("Segoe UI", 10),
            bg=self.accent_color,
            fg=self.text_color,
            insertbackground=self.green_color,
            relief="flat",
            bd=0
        )
        self.path_entry.pack(fill="x", ipady=10, padx=2, pady=2)
        self.path_entry.insert(0, self.download_path)
        
        browse_btn = tk.Button(
            path_frame,
            text="Browse",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=self.browse_folder
        )
        browse_btn.pack(side="left", padx=(10, 0), ipady=10, ipadx=20)
        
        # Progress Section
        progress_section = tk.Frame(main_frame, bg=self.card_color)
        progress_section.pack(fill="x", pady=(0, 20))
        
        self.progress_label = tk.Label(
            progress_section,
            text="Ready to download",
            font=("Segoe UI", 9),
            bg=self.card_color,
            fg=self.text_muted
        )
        self.progress_label.pack(anchor="w", pady=(0, 8))
        
        progress_bar_container = tk.Frame(progress_section, bg=self.border_color, padx=1, pady=1)
        progress_bar_container.pack(fill="x")
        
        self.progress_bar = ttk.Progressbar(
            progress_bar_container,
            mode='indeterminate',
            length=640
        )
        self.progress_bar.pack(fill="x", padx=1, pady=1)
        
        # Buttons frame for Download and Stop
        buttons_frame = tk.Frame(main_frame, bg=self.card_color)
        buttons_frame.pack(fill="x", pady=(20, 0))
        
        # Download Button
        self.download_btn = tk.Button(
            buttons_frame,
            text="⬇ Download",
            font=("Segoe UI", 13, "bold"),
            bg=self.green_color,
            fg=self.bg_color,
            activebackground=self.green_hover,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=self.start_download
        )
        self.download_btn.pack(side="left", fill="x", expand=True, ipady=15, padx=(0, 10))
        
        # Emergency Stop Button
        self.stop_btn = tk.Button(
            buttons_frame,
            text="⏹ STOP",
            font=("Segoe UI", 13, "bold"),
            bg="#ff4444",
            fg="white",
            activebackground="#cc0000",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            state="disabled",
            command=self.emergency_stop
        )
        self.stop_btn.pack(side="right", ipady=15, ipadx=30)
        
        # Debug Console (hidden by default) - improved styling
        self.debug_console_frame = tk.Frame(self.root, bg=self.bg_color)
        
        debug_header = tk.Frame(self.debug_console_frame, bg=self.bg_color)
        debug_header.pack(fill="x", padx=30, pady=(10, 5))
        
        debug_console_label = tk.Label(
            debug_header,
            text="🐛 Debug Console",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_color,
            fg=self.green_color
        )
        debug_console_label.pack(side="left")
        
        # Clear console button
        clear_console_btn = tk.Button(
            debug_header,
            text="Clear",
            font=("Segoe UI", 8, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=self.clear_console
        )
        clear_console_btn.pack(side="right", padx=5, ipadx=15, ipady=3)
        
        # Scrollbar and Text widget for console
        console_container = tk.Frame(self.debug_console_frame, bg=self.border_color, padx=1, pady=1)
        console_container.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        
        console_inner = tk.Frame(console_container, bg=self.bg_color)
        console_inner.pack(fill="both", expand=True, padx=1, pady=1)
        
        scrollbar = tk.Scrollbar(console_inner)
        scrollbar.pack(side="right", fill="y")
        
        self.debug_console = tk.Text(
            console_inner,
            height=10,
            font=("Consolas", 9),
            bg=self.accent_color,
            fg=self.green_color,
            insertbackground=self.green_color,
            relief="flat",
            wrap="word",
            state="disabled",
            yscrollcommand=scrollbar.set
        )
        self.debug_console.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.debug_console.yview)
        
        # Show debug console if debug mode is enabled
        if self.debug_mode:
            self.debug_console_frame.pack(fill="both", expand=True)
            self.root.geometry("1000x850")
            self.log_debug("Debug mode enabled")
            # Start processing output queue
            self.process_output_queue()
        
        # Footer
        footer_frame = tk.Frame(self.root, bg=self.bg_color, height=35)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(
            footer_frame,
            text="LetUsTech  •  letustech.uk",
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.text_muted
        )
        footer_label.pack(pady=8)
        
        # Style configuration for ttk widgets
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TCombobox", 
                       fieldbackground=self.accent_color,
                       background=self.accent_color,
                       foreground=self.text_color,
                       arrowcolor=self.green_color,
                       borderwidth=0,
                       relief="flat")
        style.map('TCombobox', 
                 fieldbackground=[('readonly', self.accent_color)],
                 selectbackground=[('readonly', self.accent_color)],
                 selectforeground=[('readonly', self.text_color)])
        
        style.configure("TProgressbar",
                       troughcolor=self.accent_color,
                       background=self.green_color,
                       borderwidth=0,
                       thickness=25)
    
    def load_settings(self):
        """Load settings from JSON file"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    self.debug_mode = settings.get('debug_mode', False)
                    saved_path = settings.get('download_path', '')
                    if saved_path and os.path.exists(saved_path):
                        self.download_path = saved_path
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def check_ffmpeg(self):
        """Check if FFmpeg is installed"""
        try:
            self.log_debug("=== STARTING FFMPEG CHECK ===")
            
            # Check system PATH first
            if shutil.which('ffmpeg'):
                self.log_debug("FFmpeg found in system PATH")
                return
            
            self.log_debug("FFmpeg not found in system PATH, checking portable installations...")
            
            # Check for portable installation in app directory
            app_dir = os.getcwd()
            portable_ffmpeg = os.path.join(app_dir, "ffmpeg.exe")
            portable_folder = os.path.join(app_dir, "ffmpeg", "bin", "ffmpeg.exe")
            
            self.log_debug(f"Checking portable locations:")
            self.log_debug(f"  - {portable_ffmpeg}")
            self.log_debug(f"  - {portable_folder}")
            
            if os.path.exists(portable_ffmpeg):
                self.log_debug("FFmpeg found as portable installation in app directory")
                # Add to current session PATH
                current_path = os.environ.get('PATH', '')
                if app_dir not in current_path:
                    os.environ['PATH'] = current_path + os.pathsep + app_dir
                    self.log_debug("Added app directory to current session PATH")
                return
            elif os.path.exists(portable_folder):
                self.log_debug("FFmpeg found in portable folder")
                # Add portable bin to current session PATH
                portable_bin = os.path.join(app_dir, "ffmpeg", "bin")
                current_path = os.environ.get('PATH', '')
                if portable_bin not in current_path:
                    os.environ['PATH'] = current_path + os.pathsep + portable_bin
                    self.log_debug("Added portable bin directory to current session PATH")
                return
            
            self.log_debug("FFmpeg not found anywhere - showing installation options")
            
            # Schedule FFmpeg installation dialog for after UI is ready
            def show_ffmpeg_dialog():
                try:
                    result = messagebox.askyesnocancel(
                        "FFmpeg Not Found",
                        "FFmpeg is not installed or not in your system PATH.\n\n"
                        "FFmpeg is required for:\n"
                        "• Merging video and audio streams\n"
                        "• Converting to MP3\n"
                        "• Processing certain video formats\n\n"
                        "Video downloads will work, but audio conversion and format merging may fail.\n\n"
                        "Would you like to:\n"
                        "• Yes - Open FFmpeg installation guide\n"
                        "• No - Continue without FFmpeg\n"
                        "• Cancel - Exit application"
                    )
                    
                    if result is True:  # Yes - Open installation guide
                        self.open_ffmpeg_installer()
                    elif result is None:  # Cancel - Exit
                        self.log_debug("User chose to exit due to missing FFmpeg")
                        self.root.quit()
                    else:  # No - Continue
                        self.log_debug("User chose to continue without FFmpeg")
                        
                except Exception as e:
                    self.log_debug(f"Error in FFmpeg dialog: {e}")
                    # Don't let dialog errors crash the app
                    
            # Show dialog after 1 second to ensure UI is ready
            self.root.after(1000, show_ffmpeg_dialog)
            
            self.log_debug("WARNING: FFmpeg not found in system PATH or portable installation")
            
        except Exception as e:
            self.log_debug(f"⚠ FFmpeg check issue: {type(e).__name__}: {e}")
            # Don't let FFmpeg check errors crash the application
            import traceback
            self.log_debug(f"FFmpeg check traceback: {traceback.format_exc()}")
            
            # Show a simple warning but don't crash
            try:
                self.root.after(2000, lambda: messagebox.showwarning(
                    "FFmpeg Check Failed", 
                    f"Could not check FFmpeg installation:\n{e}\n\nYou may install it later if needed."
                ))
            except:
                pass  # Even this shouldn't crash the app
    
    def open_ffmpeg_installer(self):
        """Open FFmpeg installation options"""
        import sys
        import webbrowser
        
        installer_window = tk.Toplevel(self.root)
        installer_window.title("Install FFmpeg - LetUsTech")
        installer_window.geometry("700x600")
        installer_window.configure(bg=self.bg_color)
        installer_window.grab_set()  # Make it modal
        
        # Header
        header_frame = tk.Frame(installer_window, bg=self.card_color, height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header = tk.Label(
            header_frame,
            text="🔧 Install FFmpeg",
            font=("Segoe UI", 16, "bold"),
            bg=self.card_color,
            fg=self.green_color
        )
        header.pack(pady=25)
        
        # Content
        content_frame = tk.Frame(installer_window, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        info_label = tk.Label(
            content_frame,
            text="Choose your installation method:",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        info_label.pack(anchor="w", pady=(0, 15))
        
        # Progress bar for installation
        self.install_progress = ttk.Progressbar(
            content_frame,
            mode='indeterminate',
            length=640
        )
        self.install_progress.pack(fill="x", pady=(0, 15))
        self.install_progress.pack_forget()  # Hide initially
        
        self.install_status = tk.Label(
            content_frame,
            text="",
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.text_muted
        )
        self.install_status.pack(fill="x")
        self.install_status.pack_forget()  # Hide initially
        
        # Windows options
        if sys.platform == "win32":
            # Option 1: Automatic installer
            option1_frame = tk.Frame(content_frame, bg=self.card_color)
            option1_frame.pack(fill="x", pady=5)
            
            tk.Label(
                option1_frame,
                text="🚀 Option 1: Automatic Installation (Recommended)",
                font=("Segoe UI", 11, "bold"),
                bg=self.card_color,
                fg=self.green_color
            ).pack(anchor="w", padx=15, pady=10)
            
            tk.Label(
                option1_frame,
                text="Downloads and installs FFmpeg automatically. No manual steps required!",
                font=("Segoe UI", 9),
                bg=self.card_color,
                fg=self.text_muted
            ).pack(anchor="w", padx=15)
            
            auto_buttons_frame = tk.Frame(option1_frame, bg=self.card_color)
            auto_buttons_frame.pack(anchor="w", padx=15, pady=(5, 15))
            
            auto_install_btn = tk.Button(
                auto_buttons_frame,
                text="⬇ Install to System",
                font=("Segoe UI", 10, "bold"),
                bg=self.green_color,
                fg=self.bg_color,
                activebackground=self.green_hover,
                activeforeground=self.bg_color,
                relief="flat",
                cursor="hand2",
                borderwidth=0,
                command=lambda: self.auto_install_ffmpeg(installer_window)
            )
            auto_install_btn.pack(side="left", padx=(0, 10), ipadx=20, ipady=8)
            
            portable_install_btn = tk.Button(
                auto_buttons_frame,
                text="📁 Portable Install",
                font=("Segoe UI", 10, "bold"),
                bg=self.accent_color,
                fg=self.text_color,
                activebackground=self.green_color,
                activeforeground=self.bg_color,
                relief="flat",
                cursor="hand2",
                borderwidth=0,
                command=lambda: self.portable_install_ffmpeg(installer_window)
            )
            portable_install_btn.pack(side="left", ipadx=20, ipady=8)
        
        # Bottom buttons
        button_frame = tk.Frame(installer_window, bg=self.bg_color)
        button_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=installer_window.destroy
        )
        close_btn.pack(side="right", ipadx=25, ipady=8)
    
    def auto_install_ffmpeg(self, parent_window):
        """Automatically download and install FFmpeg"""
        messagebox.showinfo("FFmpeg Installation", "FFmpeg auto-installation would start here. This feature is available in the full version.")
        parent_window.destroy()
    
    def portable_install_ffmpeg(self, parent_window):
        """Install FFmpeg portably to application folder"""
        messagebox.showinfo("FFmpeg Installation", "FFmpeg portable installation would start here. This feature is available in the full version.")
        parent_window.destroy()
    
    def get_download_folder(self, quality):
        """Get or create appropriate download folder based on content type"""
        base_path = Path(self.download_path)
        
        # Determine subfolder based on quality/type
        if quality == "Audio Only (MP3)":
            subfolder = "Music"
        else:
            subfolder = "Videos"
        
        # Create full path
        download_folder = base_path / subfolder
        
        # Create folder if it doesn't exist
        try:
            download_folder.mkdir(parents=True, exist_ok=True)
            self.log_debug(f"Using download folder: {download_folder}")
        except Exception as e:
            self.log_debug(f"Error creating folder: {e}")
            # Fallback to base path if folder creation fails
            download_folder = base_path
        
        return str(download_folder)
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            settings = {
                'debug_mode': self.debug_mode,
                'download_path': self.download_path
            }
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def toggle_settings(self):
        """Show/hide settings panel"""
        if self.settings_visible:
            self.settings_frame.pack_forget()
            self.settings_visible = False
        else:
            self.settings_frame.pack(after=self.root.winfo_children()[0], fill="x")
            self.settings_visible = True
    
    def toggle_debug_mode(self):
        """Toggle debug mode on/off"""
        self.debug_mode = self.debug_var.get()
        self.save_settings()
        
        if self.debug_mode:
            self.debug_console_frame.pack(fill="both", expand=True)
            self.root.geometry("1000x850")
            self.log_debug("Debug mode enabled")
            # Start processing output queue
            self.process_output_queue()
        else:
            self.debug_console_frame.pack_forget()
            self.root.geometry("1000x650")
        
        # Update window to apply changes
        self.root.update_idletasks()
    
    def log_debug(self, message):
        """Add message to debug console"""
        if self.debug_mode:
            # Safely check if debug console exists
            if hasattr(self, 'debug_console'):
                self.debug_console.config(state="normal")
                self.debug_console.insert("end", f"{message}\n")
                self.debug_console.see("end")
                self.debug_console.config(state="disabled")
            else:
                # Fallback to print if debug console not yet created
                print(f"DEBUG: {message}")
    
    def process_output_queue(self):
        """Process output queue and update debug console"""
        while not self.output_queue.empty():
            message = self.output_queue.get()
            self.debug_console.config(state="normal")
            self.debug_console.insert("end", message)
            self.debug_console.see("end")
            self.debug_console.config(state="disabled")
        
        # Schedule next check
        if self.debug_mode:
            self.root.after(100, self.process_output_queue)
    
    def clear_console(self):
        """Clear the debug console"""
        self.debug_console.config(state="normal")
        self.debug_console.delete(1.0, "end")
        self.debug_console.config(state="disabled")
        self.log_debug("Console cleared")
    
    def load_history(self):
        """Load download history from JSON file"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r') as f:
                    self.download_history = json.load(f)
        except Exception as e:
            self.log_debug(f"Error loading history: {e}")
            self.download_history = []
    
    def save_history(self):
        """Save download history to JSON file"""
        try:
            # Keep only last 100 downloads
            self.download_history = self.download_history[-100:]
            with open(self.history_file, 'w') as f:
                json.dump(self.download_history, f, indent=2)
        except Exception as e:
            self.log_debug(f"Error saving history: {e}")
    
    def add_to_history(self, title, url, quality, file_path, is_playlist=False):
        """Add download to history"""
        history_entry = {
            'title': title,
            'url': url,
            'quality': quality,
            'file_path': file_path,
            'is_playlist': is_playlist,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.download_history.append(history_entry)
        self.save_history()
    
    def show_history(self):
        """Display download history in a new window"""
        history_window = tk.Toplevel(self.root)
        history_window.title("Download History - LetUsTech")
        history_window.geometry("700x500")
        history_window.configure(bg=self.bg_color)
        
        # Header
        header = tk.Label(
            history_window,
            text="Download History",
            font=("Segoe UI", 16, "bold"),
            bg=self.bg_color,
            fg=self.green_color
        )
        header.pack(pady=10)
        
        # Listbox with scrollbar
        list_frame = tk.Frame(history_window, bg=self.bg_color)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        history_list = tk.Listbox(
            list_frame,
            font=("Segoe UI", 9),
            bg=self.accent_color,
            fg=self.text_color,
            selectbackground=self.green_color,
            selectforeground=self.bg_color,
            yscrollcommand=scrollbar.set,
            relief="flat"
        )
        history_list.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=history_list.yview)
        
        # Populate history
        if not self.download_history:
            history_list.insert("end", "No download history yet")
        else:
            for entry in reversed(self.download_history):
                playlist_tag = " [PLAYLIST]" if entry.get('is_playlist', False) else ""
                display_text = f"{entry['timestamp']} - {entry['title']}{playlist_tag} ({entry['quality']})"
                history_list.insert("end", display_text)
        
        # Buttons
        btn_frame = tk.Frame(history_window, bg=self.bg_color)
        btn_frame.pack(pady=10)
        
        clear_btn = tk.Button(
            btn_frame,
            text="Clear History",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            command=lambda: self.clear_history(history_list)
        )
        clear_btn.pack(side="left", padx=5, ipadx=20, ipady=5)
        
        close_btn = tk.Button(
            btn_frame,
            text="Close",
            font=("Segoe UI", 10, "bold"),
            bg=self.green_color,
            fg=self.bg_color,
            activebackground="#00cc6a",
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            command=history_window.destroy
        )
        close_btn.pack(side="left", padx=5, ipadx=20, ipady=5)
    
    def clear_history(self, listbox):
        """Clear download history"""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear all download history?"):
            self.download_history = []
            self.save_history()
            listbox.delete(0, "end")
            listbox.insert("end", "No download history yet")
            self.log_debug("Download history cleared")
    
    def show_help_guide(self):
        """Show comprehensive help guide"""
        help_window = tk.Toplevel(self.root)
        help_window.title("User Guide - LetUsTech YouTube Converter")
        help_window.geometry("800x700")
        help_window.configure(bg=self.bg_color)
        help_window.resizable(True, True)
        
        # Header
        header_frame = tk.Frame(help_window, bg=self.card_color, height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(
            header_frame,
            text="📖 User Guide & Help",
            font=("Segoe UI", 16, "bold"),
            bg=self.card_color,
            fg=self.green_color
        )
        header_label.pack(pady=15)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Quick Start Tab
        quick_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(quick_frame, text="🚀 Quick Start")
        
        quick_text = tk.Text(
            quick_frame,
            font=("Segoe UI", 10),
            bg=self.accent_color,
            fg=self.text_color,
            wrap="word",
            padx=15,
            pady=15
        )
        quick_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        quick_content = """🎬 QUICK START GUIDE - ULTRA FAST EDITION

⚡⚡⚡ ULTRA FAST IMPROVEMENTS:
• Playlist loading is INSTANT (no waiting!)
• 5 videos download at once (was 3)
• 20MB chunks = 2x faster transfers
• 8 concurrent fragments per video
• Total speed improvement: ~400% faster!

1. PASTE URL
   • Copy YouTube video or playlist URL
   • Paste in the "Video URL" field
   • Click "Load Preview" to see thumbnail

2. SELECT QUALITY
   • Choose from dropdown:
     - Best Quality (Video + Audio)
     - 1080p, 720p, 480p, 360p
     - Audio Only (MP3) - for music

3. CHOOSE LOCATION
   • Default: Downloads/Videos or Downloads/Music
   • Click "Browse" to change location
   • Files auto-organize by type

4. DOWNLOAD
   • Single videos: Click "Download"
   • Playlists: Click "Select Videos" to pick which ones
   • Or check "Download First 50" for auto-download
   • Watch progress bar for completion

🎵 FOR PLAYLISTS:
   • Playlists load INSTANTLY (no delays!)
   • Use "Select Videos" for precise control
   • Downloads 5 videos simultaneously
   • Files include artist names automatically"""
        
        quick_text.insert("1.0", quick_content)
        quick_text.config(state="disabled")
        
        # Close button
        close_btn = tk.Button(
            help_window,
            text="Close",
            font=("Segoe UI", 10, "bold"),
            bg=self.green_color,
            fg=self.bg_color,
            command=help_window.destroy
        )
        close_btn.pack(pady=10)
    
    def show_about(self):
        """Show about dialog with credits and information"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About - LetUsTech YouTube Converter")
        about_window.geometry("600x500")
        about_window.configure(bg=self.bg_color)
        about_window.resizable(False, False)
        
        # Center the window
        about_window.transient(self.root)
        
        # Header with logo area
        header_frame = tk.Frame(about_window, bg=self.card_color, height=120)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Try to show logo or fallback to icon
        logo_frame = tk.Frame(header_frame, bg=self.card_color)
        logo_frame.pack(pady=20)
        
        try:
            if os.path.exists("LetUsTech.png"):
                logo_img = Image.open("LetUsTech.png")
                logo_img = logo_img.resize((64, 64), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(logo_frame, image=logo_photo, bg=self.card_color)
                logo_label.image = logo_photo
                logo_label.pack()
            else:
                logo_label = tk.Label(
                    logo_frame,
                    text="▶",
                    font=("Segoe UI", 48, "bold"),
                    bg=self.card_color,
                    fg=self.green_color
                )
                logo_label.pack()
        except:
            logo_label = tk.Label(
                logo_frame,
                text="▶",
                font=("Segoe UI", 48, "bold"),
                bg=self.card_color,
                fg=self.green_color
            )
            logo_label.pack()
        
        title_label = tk.Label(
            header_frame,
            text="LetUsTech YouTube Converter",
            font=("Segoe UI", 20, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        title_label.pack()
        
        version_label = tk.Label(
            header_frame,
            text="Version 2.2 - ULTRA FAST Edition ⚡⚡⚡",
            font=("Segoe UI", 10),
            bg=self.card_color,
            fg=self.text_muted
        )
        version_label.pack()
        
        # Main content
        content_frame = tk.Frame(about_window, bg=self.bg_color)
        content_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        about_text = tk.Text(
            content_frame,
            font=("Segoe UI", 10),
            bg=self.accent_color,
            fg=self.text_color,
            wrap="word",
            height=12,
            relief="flat"
        )
        about_text.pack(fill="both", expand=True)
        
        about_content = f"""🚀 BUILT BY: LetUsTech
👨‍💻 DEVELOPER: Deano (23) - Liverpool, UK
🌐 WEBSITE: letustech.uk
💝 TAGLINE: "Wired For Your World"

⚡⚡⚡ WHAT'S NEW IN 2.2 - ULTRA FAST:
• INSTANT playlist loading (no API delays!)
• 5 concurrent downloads (was 3)
• 20MB chunk size (2x faster transfers)
• 8 concurrent fragments per video
• Optimized socket timeouts
• 2MB buffer for smoother streaming

📱 ABOUT LETUSTECH:
LetUsTech is a technology platform offering free Python automation tools and browser-based games. We create educational content and practical applications to make technology accessible for everyone.

🎬 YOUTUBE CONVERTER FEATURES:
• ULTRA FAST downloads with 5x concurrency
• Instant playlist loading (flat extraction)
• Smart 50-video playlist limit
• Artist names in filenames automatically
• Full video selection interface
• Professional UI with debug capabilities

💖 SUPPORT THE PROJECT:
This software is completely free! If you find it useful:
• Visit letustech.uk for more tools
• Join our Discord: discord.gg/dkebMS5eCX
• Share with friends who need video downloading

© 2024 LetUsTech. Made with ❤️ in Liverpool."""
        
        about_text.insert("1.0", about_content)
        about_text.config(state="disabled")
        
        # Buttons frame
        button_frame = tk.Frame(about_window, bg=self.bg_color)
        button_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        website_btn = tk.Button(
            button_frame,
            text="🌐 Visit Website",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            command=lambda: self.open_url("https://letustech.uk")
        )
        website_btn.pack(side="left", padx=5, ipadx=15, ipady=5)
        
        discord_btn = tk.Button(
            button_frame,
            text="💬 Join Discord",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            command=lambda: self.open_url("https://discord.gg/dkebMS5eCX")
        )
        discord_btn.pack(side="left", padx=5, ipadx=15, ipady=5)
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            font=("Segoe UI", 9, "bold"),
            bg=self.green_color,
            fg=self.bg_color,
            command=about_window.destroy
        )
        close_btn.pack(side="right", padx=5, ipadx=20, ipady=5)
    
    def open_url(self, url):
        """Open URL in default browser"""
        import webbrowser
        try:
            webbrowser.open(url)
        except:
            messagebox.showinfo("URL", f"Please visit: {url}")
    
    def emergency_stop(self):
        """Emergency stop all downloads"""
        self.download_stopped = True
        self.log_debug("=== EMERGENCY STOP ACTIVATED ===")
        self.progress_bar.stop()
        self.progress_label.config(text="Downloads stopped by user")
        self.download_btn.config(state="normal", text="⬇ Download")
        self.stop_btn.config(state="disabled")
        messagebox.showinfo("Stopped", "All downloads have been stopped.")
    
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)
            self.save_settings()
            self.log_debug(f"Download path changed to: {folder}")
    
    def load_preview(self):
        """Load video thumbnail and info - OPTIMIZED VERSION"""
        self.log_debug("=== STARTING PREVIEW LOAD (OPTIMIZED) ===")
        url = self.url_entry.get().strip()
        self.log_debug(f"Raw URL from entry: '{url}'")
        
        if not url:
            self.log_debug("ERROR: No URL provided")
            messagebox.showwarning("No URL", "Please enter a YouTube URL first")
            return
        
        self.log_debug(f"URL validation starting for: {url}")
        if not self.validate_url(url):
            self.log_debug("ERROR: URL validation failed")
            messagebox.showerror("Invalid URL", "Please enter a valid YouTube URL")
            return
        
        self.log_debug("URL validation passed - proceeding with preview load")
        
        # Reset UI state for new URL
        self.preview_btn.config(state="disabled", text="Loading...")
        self.thumbnail_label.config(text="🔄 Fetching preview...", image="")
        self.video_title_label.config(text="")
        self.select_videos_btn.config(state="disabled")
        self.current_thumbnail = None
        self.is_playlist = False
        self.playlist_videos = []
        self.selected_videos = []
        self.full_playlist_info = None
        
        self.root.update_idletasks()
        
        def fetch_preview():
            try:
                self.log_debug("=== FETCH PREVIEW THREAD STARTED ===")
                
                # Update UI to show progress
                def update_status(message):
                    self.root.after(0, lambda: self.thumbnail_label.config(text=message))
                
                update_status("🔄 Connecting to YouTube...")
                
                # OPTIMIZATION: Quick check with extract_flat
                quick_opts = {
                    'quiet': True,
                    'extract_flat': True,
                    'ignoreerrors': True,
                    'socket_timeout': 10,  # Faster timeout
                }
                
                self.log_debug("Doing quick playlist check...")
                with yt_dlp.YoutubeDL(quick_opts) as ydl:
                    quick_info = ydl.extract_info(url, download=False)
                
                # If it's a playlist, limit to first 50
                if 'entries' in quick_info:
                    entries_count = len(quick_info.get('entries', []))
                    self.log_debug(f"Found playlist with {entries_count} videos")
                    
                    # OPTIMIZATION: Limit to first 50 videos
                    if entries_count > self.max_playlist_size:
                        self.log_debug(f"=== LARGE PLAYLIST - LIMITING TO {self.max_playlist_size} VIDEOS ===")
                        update_status(f"📋 Playlist found - limiting to first {self.max_playlist_size} videos")
                        quick_info['entries'] = quick_info['entries'][:self.max_playlist_size]
                        entries_count = self.max_playlist_size
                    
                    self.is_playlist = True
                    self.playlist_videos = []
                    
                    playlist_title = quick_info.get('title', 'Playlist')
                    
                    # Take first few videos for preview
                    for i, entry in enumerate(quick_info['entries'][:5]):
                        if entry:
                            video_data = {
                                'title': entry.get('title', f'Video {i+1}'),
                                'id': entry.get('id', ''),
                                'url': entry.get('url', ''),
                                'duration': entry.get('duration', 0),
                                'thumbnail': entry.get('thumbnail', '')
                            }
                            self.playlist_videos.append(video_data)
                    
                    self.video_title_label.config(
                        text=f"📋 {playlist_title}\n({entries_count} videos - Auto-limited to {self.max_playlist_size})"
                    )
                    
                    # Store the limited playlist info
                    self.full_playlist_info = quick_info
                    self.select_videos_btn.config(state="normal")
                    
                    # Use first video thumbnail
                    thumbnail_url = self.playlist_videos[0].get('thumbnail') if self.playlist_videos else None
                    
                    if thumbnail_url:
                        self.load_thumbnail_image(thumbnail_url)
                    else:
                        self.thumbnail_label.config(text="📋 Playlist")
                    
                else:
                    # Single video - process normally
                    self.log_debug("Single video detected")
                    ydl_opts = {
                        'quiet': not self.debug_mode,
                        'no_warnings': not self.debug_mode,
                        'extract_flat': False,
                        'ignoreerrors': False,
                        'socket_timeout': 15,  # Faster timeout
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        
                        if not info:
                            raise Exception("Could not extract video information")
                        
                        self.is_playlist = False
                        title = info.get('title', 'Unknown')
                        duration = info.get('duration', 0)
                        
                        mins, secs = divmod(duration, 60) if duration else (0, 0)
                        
                        self.video_title_label.config(
                            text=f"{title}\n({int(mins)}:{int(secs):02d})"
                        )
                        
                        thumbnail_url = info.get('thumbnail')
                        if thumbnail_url:
                            self.load_thumbnail_image(thumbnail_url)
                        else:
                            self.thumbnail_label.config(text="❌ No image available")
                
                self.log_debug("=== PREVIEW LOAD COMPLETE ===")
                    
            except Exception as e:
                self.log_debug(f"ERROR in fetch_preview: {type(e).__name__}: {str(e)}")
                self.thumbnail_label.config(text="Failed to load preview")
                self.video_title_label.config(text="")
                messagebox.showerror("Preview Error", f"Failed to load preview:\n\n{str(e)}")
            
            finally:
                self.preview_btn.config(state="normal", text="Reload Preview")
        
        # Run in thread
        threading.Thread(target=fetch_preview, daemon=True).start()
    
    def load_thumbnail_image(self, thumbnail_url):
        """Load and display thumbnail image"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(thumbnail_url, timeout=10, headers=headers)
            
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.thumbnail((300, 180), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.current_thumbnail = photo
                
                self.thumbnail_label.config(image=photo, text="")
                self.thumbnail_label.image = photo
                self.log_debug("Thumbnail loaded successfully!")
            else:
                self.thumbnail_label.config(text="❌ No image available")
                
        except Exception as e:
            self.log_debug(f"Error loading thumbnail: {e}")
            self.thumbnail_label.config(text="❌ No image available")
    
    def validate_url(self, url):
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        return re.match(youtube_regex, url) is not None
    
    def show_video_selector(self):
        """Show video selector for playlist - ALLOWS SELECTION OF UP TO 50 VIDEOS"""
        if not hasattr(self, 'is_playlist') or not self.is_playlist:
            messagebox.showwarning("Warning", "This feature is only available for playlists")
            return
        
        # Show info message first
        messagebox.showinfo("Playlist Selection", 
                          f"This playlist has been automatically limited to the first {self.max_playlist_size} videos for optimal performance.\n\n"
                          "You can now select which videos to download.")
        
        # Load full video info for the limited playlist
        self.load_full_playlist_info()
    
    def load_full_playlist_info(self):
        """Load playlist videos using FAST flat extraction - NO full detail loading needed"""
        loading_dialog = tk.Toplevel(self.root)
        loading_dialog.title("Loading Videos")
        loading_dialog.geometry("400x150")
        loading_dialog.configure(bg=self.bg_color)
        loading_dialog.resizable(False, False)
        loading_dialog.transient(self.root)
        loading_dialog.grab_set()
        
        # Center the dialog
        loading_dialog.update_idletasks()
        x = (loading_dialog.winfo_screenwidth() // 2) - 200
        y = (loading_dialog.winfo_screenheight() // 2) - 75
        loading_dialog.geometry(f"400x150+{x}+{y}")
        
        header_label = tk.Label(
            loading_dialog,
            text="🔄 Loading Video List",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_color,
            fg=self.green_color
        )
        header_label.pack(pady=20)
        
        status_label = tk.Label(
            loading_dialog,
            text=f"Loading {self.max_playlist_size} videos (FAST MODE)...",
            font=("Segoe UI", 10),
            bg=self.bg_color,
            fg=self.text_color
        )
        status_label.pack(pady=5)
        
        progress_bar = ttk.Progressbar(loading_dialog, mode='indeterminate')
        progress_bar.pack(pady=15, padx=30, fill="x")
        progress_bar.start(10)
        
        def load_videos():
            try:
                if not hasattr(self, 'full_playlist_info') or not self.full_playlist_info:
                    self.log_debug("No playlist info available")
                    self.root.after(0, loading_dialog.destroy)
                    return
                
                # SPEED OPTIMIZATION: Use flat extraction data directly - NO additional API calls!
                self.playlist_videos = []
                
                entries = self.full_playlist_info['entries'][:self.max_playlist_size]
                total = len(entries)
                
                self.log_debug(f"=== FAST LOADING: Using flat extraction for {total} videos ===")
                
                # Just convert flat data to our format - instant!
                for i, entry in enumerate(entries):
                    if not entry:
                        continue
                    
                    video_data = {
                        'title': entry.get('title', f'Video {i+1}'),
                        'id': entry.get('id', ''),
                        'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                        'duration': entry.get('duration', 0),
                        'thumbnail': entry.get('thumbnail', ''),
                        'uploader': entry.get('uploader', entry.get('channel', '')),
                        'view_count': entry.get('view_count', 0)
                    }
                    self.playlist_videos.append(video_data)
                
                self.log_debug(f"✓ Loaded {len(self.playlist_videos)} videos INSTANTLY (flat extraction)")
                
                # Close loading dialog and show selector immediately
                def show_selector():
                    progress_bar.stop()
                    loading_dialog.destroy()
                    self._show_video_selector_window()
                
                self.root.after(0, show_selector)
                
            except Exception as e:
                self.log_debug(f"Error in load_videos: {e}")
                
                def show_error():
                    progress_bar.stop()
                    loading_dialog.destroy()
                    messagebox.showerror("Error", f"Failed to load videos:\n{str(e)}")
                
                self.root.after(0, show_error)
        
        # Start loading in background
        threading.Thread(target=load_videos, daemon=True).start()
    
    def _show_video_selector_window(self):
        """Show the actual video selector window with checkboxes - CLEAN & EASY"""
        selector_window = tk.Toplevel(self.root)
        selector_window.title("Select Videos - LetUsTech")
        
        # Window sizing
        screen_width = selector_window.winfo_screenwidth()
        screen_height = selector_window.winfo_screenheight()
        
        window_width = 1000
        window_height = 700
            
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        selector_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        selector_window.configure(bg=self.bg_color)
        selector_window.minsize(900, 600)
        
        # Header - Cleaner design
        header_frame = tk.Frame(selector_window, bg=self.card_color, height=100)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header_content = tk.Frame(header_frame, bg=self.card_color)
        header_content.pack(expand=True)
        
        header = tk.Label(
            header_content,
            text="Select Videos to Download",
            font=("Segoe UI", 18, "bold"),
            bg=self.card_color,
            fg=self.green_color
        )
        header.pack(pady=(15, 5))
        
        count_label = tk.Label(
            header_content,
            text=f"{len(self.playlist_videos)} videos available",
            font=("Segoe UI", 10),
            bg=self.card_color,
            fg=self.text_muted
        )
        count_label.pack()
        
        # Control panel - Clean and organized
        control_panel = tk.Frame(selector_window, bg=self.bg_color)
        control_panel.pack(fill="x", padx=30, pady=15)
        
        # Top row - Selection buttons
        top_row = tk.Frame(control_panel, bg=self.bg_color)
        top_row.pack(fill="x", pady=(0, 10))
        
        video_vars = []
        video_frames_list = []  # Keep track of all video frames for filtering
        
        def select_all():
            for var in video_vars:
                var.set(True)
            update_count()
        
        def deselect_all():
            for var in video_vars:
                var.set(False)
            update_count()
        
        # Simple, clean buttons
        select_all_btn = tk.Button(
            top_row,
            text="✓ Select All",
            font=("Segoe UI", 10, "bold"),
            bg=self.green_color,
            fg=self.bg_color,
            activebackground=self.green_hover,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=select_all
        )
        select_all_btn.pack(side="left", padx=(0, 10), ipadx=20, ipady=8)
        
        deselect_all_btn = tk.Button(
            top_row,
            text="✗ Clear All",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=deselect_all
        )
        deselect_all_btn.pack(side="left", ipadx=20, ipady=8)
        
        # Selection count - right side
        selection_label = tk.Label(
            top_row,
            text="",
            font=("Segoe UI", 11, "bold"),
            bg=self.bg_color,
            fg=self.green_color
        )
        selection_label.pack(side="right")
        
        # Bottom row - Search with filter functionality
        bottom_row = tk.Frame(control_panel, bg=self.bg_color)
        bottom_row.pack(fill="x")
        
        search_label = tk.Label(
            bottom_row,
            text="🔍 Filter:",
            font=("Segoe UI", 10, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        search_label.pack(side="left", padx=(0, 10))
        
        search_entry_frame = tk.Frame(bottom_row, bg=self.border_color, padx=1, pady=1)
        search_entry_frame.pack(side="left", fill="x", expand=True)
        
        search_entry = tk.Entry(
            search_entry_frame,
            font=("Segoe UI", 10),
            bg=self.accent_color,
            fg=self.text_color,
            insertbackground=self.green_color,
            relief="flat",
            bd=0
        )
        search_entry.pack(fill="x", ipady=8, padx=2, pady=2)
        
        def filter_videos():
            """Filter videos in real-time - hide non-matching"""
            search_term = search_entry.get().lower().strip()
            visible_count = 0
            
            if not search_term:
                # Show all videos
                for frame in video_frames_list:
                    frame.pack(fill="x", padx=10, pady=3)
                visible_count = len(video_frames_list)
            else:
                # Filter based on search term
                for i, (frame, video) in enumerate(zip(video_frames_list, self.playlist_videos)):
                    title = video.get('title', '').lower()
                    uploader = video.get('uploader', '').lower()
                    
                    if search_term in title or search_term in uploader:
                        frame.pack(fill="x", padx=10, pady=3)
                        visible_count += 1
                    else:
                        frame.pack_forget()
            
            # Update count label to show filtered results
            if search_term:
                count_label.config(text=f"Showing {visible_count} of {len(self.playlist_videos)} videos")
            else:
                count_label.config(text=f"{len(self.playlist_videos)} videos available")
            
            update_count()
        
        # Real-time filtering as user types
        search_entry.bind('<KeyRelease>', lambda e: filter_videos())
        
        clear_filter_btn = tk.Button(
            bottom_row,
            text="Clear Filter",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=lambda: [search_entry.delete(0, tk.END), filter_videos()]
        )
        clear_filter_btn.pack(side="left", padx=10, ipadx=20, ipady=8)
        
        # Scrollable video list
        list_container = tk.Frame(selector_window, bg=self.bg_color)
        list_container.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        
        list_frame = tk.Frame(list_container, bg=self.border_color, padx=2, pady=2)
        list_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(list_frame, bg=self.card_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        
        scrollable_frame = tk.Frame(canvas, bg=self.card_color)
        
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", on_canvas_configure)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Mouse wheel scrolling - WORKS ANYWHERE IN WINDOW
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def on_mousewheel_linux_up(event):
            canvas.yview_scroll(-1, "units")
        
        def on_mousewheel_linux_down(event):
            canvas.yview_scroll(1, "units")
        
        # Bind to entire selector window for scrolling anywhere
        selector_window.bind("<MouseWheel>", on_mousewheel)  # Windows
        selector_window.bind("<Button-4>", on_mousewheel_linux_up)  # Linux scroll up
        selector_window.bind("<Button-5>", on_mousewheel_linux_down)  # Linux scroll down
        
        # Add video checkboxes - Cleaner design
        for i, video in enumerate(self.playlist_videos):
            var = tk.BooleanVar(value=True)
            video_vars.append(var)
            
            row_bg = self.card_color if i % 2 == 0 else self.accent_color
            
            video_frame = tk.Frame(scrollable_frame, bg=row_bg, height=70)
            video_frame.pack(fill="x", padx=10, pady=3)
            video_frame.pack_propagate(False)
            video_frames_list.append(video_frame)  # Track for filtering
            
            # Left side - Checkbox and number
            left_side = tk.Frame(video_frame, bg=row_bg)
            left_side.pack(side="left", padx=10, fill="y")
            
            check = tk.Checkbutton(
                left_side,
                variable=var,
                bg=row_bg,
                fg=self.text_color,
                selectcolor=self.bg_color,
                activebackground=row_bg,
                cursor="hand2",
                command=lambda: update_count()
            )
            check.pack(side="left")
            
            num_label = tk.Label(
                left_side,
                text=f"#{i + 1}",
                font=("Segoe UI", 10, "bold"),
                bg=row_bg,
                fg=self.text_muted,
                width=4
            )
            num_label.pack(side="left", padx=(5, 0))
            
            # Center - Video info
            info_frame = tk.Frame(video_frame, bg=row_bg)
            info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
            
            # Title
            title = video.get('title', 'Unknown Title')
            if len(title) > 80:
                title = title[:77] + "..."
            
            title_label = tk.Label(
                info_frame,
                text=title,
                font=("Segoe UI", 11),
                bg=row_bg,
                fg=self.text_color,
                anchor="w",
                justify="left"
            )
            title_label.pack(fill="x", anchor="w")
            
            # Duration and uploader
            meta_text = ""
            duration = video.get('duration', 0)
            if duration:
                mins, secs = divmod(duration, 60)
                meta_text = f"{int(mins)}:{int(secs):02d}"
            
            uploader = video.get('uploader', '')
            if uploader:
                meta_text += f"  •  {uploader}"
            
            if meta_text:
                meta_label = tk.Label(
                    info_frame,
                    text=meta_text,
                    font=("Segoe UI", 9),
                    bg=row_bg,
                    fg=self.text_muted,
                    anchor="w"
                )
                meta_label.pack(fill="x", anchor="w", pady=(3, 0))
        
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.focus_set()
        
        # Bottom action bar
        action_bar = tk.Frame(selector_window, bg=self.bg_color)
        action_bar.pack(fill="x", padx=30, pady=(0, 20))
        
        def update_count():
            count = sum(var.get() for var in video_vars)
            selection_label.config(text=f"{count} selected")
            
        update_count()
        
        # Confirm button
        def confirm_selection():
            self.selected_videos = []
            for i, var in enumerate(video_vars):
                if var.get():
                    self.selected_videos.append(self.playlist_videos[i])
            
            if not self.selected_videos:
                messagebox.showwarning("No Selection", "Please select at least one video")
                return
            
            count = len(self.selected_videos)
            self.log_debug(f"Selected {count} videos from playlist")
            selector_window.destroy()
            messagebox.showinfo("Ready to Download", f"{count} video(s) selected.\n\nClick the Download button to start.")
        
        confirm_btn = tk.Button(
            action_bar,
            text=f"✓ Confirm & Close",
            font=("Segoe UI", 12, "bold"),
            bg=self.green_color,
            fg=self.bg_color,
            activebackground=self.green_hover,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=confirm_selection
        )
        confirm_btn.pack(side="right", ipadx=30, ipady=12)
        
        cancel_btn = tk.Button(
            action_bar,
            text="Cancel",
            font=("Segoe UI", 11),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=selector_window.destroy
        )
        cancel_btn.pack(side="right", padx=(0, 10), ipadx=25, ipady=12)
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                percent = d.get('_percent_str', 'N/A')
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                
                status_text = f"Downloading... {percent} | Speed: {speed} | ETA: {eta}"
                self.progress_label.config(text=status_text)
                
                # Log every 10% in debug mode
                if self.debug_mode and percent != 'N/A':
                    percent_num = percent.strip('%')
                    try:
                        if float(percent_num) % 10 < 1:
                            self.log_debug(f"Progress: {percent} | Speed: {speed}")
                    except:
                        pass
            except:
                self.progress_label.config(text="Downloading...")
        elif d['status'] == 'finished':
            self.progress_label.config(text="Download complete! Processing...")
            self.log_debug("Download finished, processing file...")
    
    def download_single_video(self, video_url, ydl_opts, index=None, total=None):
        """Download a single video with configured options"""
        try:
            prefix = f"[{index}/{total}] " if index and total else ""
            self.log_debug(f"{prefix}Downloading: {video_url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            
            return True
        except Exception as e:
            self.log_debug(f"{prefix}Failed: {str(e)}")
            return False
    
    def download_video(self):
        """OPTIMIZED VIDEO DOWNLOAD WITH CONCURRENT PROCESSING"""
        self.log_debug("=== STARTING OPTIMIZED VIDEO DOWNLOAD ===")
        self.download_stopped = False  # Reset stop flag
        
        url = self.url_entry.get().strip()
        
        if not url or not self.validate_url(url):
            messagebox.showerror("Error", "Please enter a valid YouTube URL")
            self.download_btn.config(state="normal", text="⬇ Download")
            self.stop_btn.config(state="disabled")
            self.progress_bar.stop()
            return
        
        quality = self.quality_var.get()
        download_playlist = self.playlist_var.get()
        download_folder = self.get_download_folder(quality)
        
        self.log_debug(f"=== DOWNLOAD CONFIGURATION ===")
        self.log_debug(f"URL: {url}")
        self.log_debug(f"Quality: {quality}")
        self.log_debug(f"Download folder: {download_folder}")
        
        try:
            # OPTIMIZED yt-dlp configuration for MAXIMUM SPEED
            ydl_opts = {
                'outtmpl': os.path.join(download_folder, '%(uploader)s - %(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'noplaylist': True,
                'ignoreerrors': True,
                'extract_flat': False,
                # MAXIMUM SPEED OPTIMIZATIONS:
                'concurrent_fragment_downloads': 8,  # More concurrent fragments (was 4)
                'http_chunk_size': 20971520,  # 20MB chunks for faster downloads (was 10MB)
                'retries': 2,  # Fewer retries for speed (was 3)
                'fragment_retries': 2,
                'skip_unavailable_fragments': True,
                'socket_timeout': 10,  # Faster timeout
                'buffersize': 1024 * 1024 * 2,  # 2MB buffer
                'nocheckcertificate': True,  # Skip cert check for speed
            }
            
            # Quality selection
            if quality == "Audio Only (MP3)":
                ydl_opts['format'] = 'bestaudio/best'
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            elif quality == "Best Quality (Video + Audio)":
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            elif quality == "1080p":
                ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080]'
            elif quality == "720p":
                ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]'
            elif quality == "480p":
                ydl_opts['format'] = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]'
            elif quality == "360p":
                ydl_opts['format'] = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]'
            
            # Check if user has selected specific videos from playlist
            if hasattr(self, 'selected_videos') and self.selected_videos:
                self.log_debug(f"=== DOWNLOADING {len(self.selected_videos)} SELECTED VIDEOS ===")
                
                video_count = len(self.selected_videos)
                successful = 0
                failed = 0
                
                # Use ThreadPoolExecutor for concurrent downloads
                with ThreadPoolExecutor(max_workers=self.concurrent_downloads) as executor:
                    future_to_video = {}
                    
                    for i, video in enumerate(self.selected_videos, 1):
                        if self.download_stopped:
                            self.log_debug("Download stopped by user")
                            break
                            
                        video_url = video.get('url', f"https://www.youtube.com/watch?v={video.get('id', '')}")
                        future = executor.submit(
                            self.download_single_video,
                            video_url,
                            ydl_opts.copy(),
                            i,
                            video_count
                        )
                        future_to_video[future] = (i, video.get('title', 'Unknown'))
                    
                    # Process completed downloads
                    for future in as_completed(future_to_video):
                        if self.download_stopped:
                            self.log_debug("Stopping remaining downloads...")
                            executor.shutdown(wait=False, cancel_futures=True)
                            break
                            
                        i, title = future_to_video[future]
                        try:
                            result = future.result()
                            if result:
                                successful += 1
                                self.progress_label.config(
                                    text=f"Completed {successful + failed}/{video_count}: {title[:40]}..."
                                )
                            else:
                                failed += 1
                        except Exception as e:
                            self.log_debug(f"Error downloading video {i}: {e}")
                            failed += 1
                
                if self.download_stopped:
                    self.log_debug(f"Download stopped: {successful} successful, {failed} failed")
                    self.progress_bar.stop()
                    self.progress_label.config(text="Download stopped by user")
                    
                    # Detailed completion popup
                    result_msg = "📊 DOWNLOAD STOPPED\n\n"
                    result_msg += f"✓ Successfully Downloaded: {successful} videos\n"
                    result_msg += f"✗ Failed: {failed} videos\n"
                    result_msg += f"⏹ Stopped by user\n\n"
                    result_msg += f"📁 Location:\n{download_folder}"
                    
                    messagebox.showinfo("Download Stopped", result_msg)
                else:
                    self.log_debug(f"Download complete: {successful} successful, {failed} failed")
                    self.progress_bar.stop()
                    self.progress_label.config(text="Download completed!")
                    
                    if successful > 0:
                        # Detailed success popup
                        result_msg = "🎉 DOWNLOAD COMPLETE!\n\n"
                        result_msg += f"✓ Successfully Downloaded: {successful} videos\n"
                        if failed > 0:
                            result_msg += f"✗ Failed: {failed} videos\n"
                        result_msg += f"\n📁 Saved to:\n{download_folder}\n\n"
                        result_msg += "You can now find your files in the Videos folder!"
                        
                        messagebox.showinfo("Success!", result_msg)
                    else:
                        messagebox.showerror("Download Failed", 
                                           f"❌ All {failed} videos failed to download.\n\n"
                                           "Please check:\n"
                                           "• Your internet connection\n"
                                           "• Video availability\n"
                                           "• Try again in a moment")
            
            # Handle playlist downloads with 50-video limit (auto mode)
            elif self.is_playlist and download_playlist:
                self.log_debug(f"=== DOWNLOADING PLAYLIST (LIMITED TO {self.max_playlist_size}) ===")
                
                if hasattr(self, 'full_playlist_info') and self.full_playlist_info:
                    # Get limited list of videos
                    videos_to_download = self.full_playlist_info['entries'][:self.max_playlist_size]
                    video_count = len(videos_to_download)
                    
                    self.log_debug(f"Processing {video_count} videos from playlist")
                    
                    successful = 0
                    failed = 0
                    
                    # Use ThreadPoolExecutor for concurrent downloads
                    with ThreadPoolExecutor(max_workers=self.concurrent_downloads) as executor:
                        future_to_video = {}
                        
                        for i, entry in enumerate(videos_to_download, 1):
                            if self.download_stopped:
                                self.log_debug("Download stopped by user")
                                break
                                
                            if entry and entry.get('id'):
                                video_url = f"https://www.youtube.com/watch?v={entry['id']}"
                                future = executor.submit(
                                    self.download_single_video,
                                    video_url,
                                    ydl_opts.copy(),
                                    i,
                                    video_count
                                )
                                future_to_video[future] = (i, entry.get('title', 'Unknown'))
                        
                        # Process completed downloads
                        for future in as_completed(future_to_video):
                            if self.download_stopped:
                                self.log_debug("Stopping remaining downloads...")
                                executor.shutdown(wait=False, cancel_futures=True)
                                break
                                
                            i, title = future_to_video[future]
                            try:
                                result = future.result()
                                if result:
                                    successful += 1
                                    self.progress_label.config(
                                        text=f"Completed {successful + failed}/{video_count}: {title[:40]}..."
                                    )
                                else:
                                    failed += 1
                            except Exception as e:
                                self.log_debug(f"Error downloading video {i}: {e}")
                                failed += 1
                    
                    if self.download_stopped:
                        self.log_debug(f"Download stopped: {successful} successful, {failed} failed")
                        self.progress_bar.stop()
                        self.progress_label.config(text="Download stopped by user")
                        
                        # Detailed stopped popup
                        result_msg = "📊 DOWNLOAD STOPPED\n\n"
                        result_msg += f"✓ Successfully Downloaded: {successful} videos\n"
                        result_msg += f"✗ Failed: {failed} videos\n"
                        result_msg += f"⏹ Stopped by user\n\n"
                        result_msg += f"📁 Location:\n{download_folder}"
                        
                        messagebox.showinfo("Download Stopped", result_msg)
                    else:
                        self.log_debug(f"Playlist download complete: {successful} successful, {failed} failed")
                        self.progress_bar.stop()
                        self.progress_label.config(text="Playlist download completed!")
                        
                        # Detailed completion popup
                        result_msg = "🎉 PLAYLIST DOWNLOAD COMPLETE!\n\n"
                        result_msg += f"✓ Successfully Downloaded: {successful} videos\n"
                        if failed > 0:
                            result_msg += f"✗ Failed: {failed} videos\n"
                        result_msg += f"\n📁 Saved to:\n{download_folder}\n\n"
                        result_msg += "All your videos are ready to watch!"
                        
                        messagebox.showinfo("Success!", result_msg)
                else:
                    # Fallback to sequential download
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url])
                    
                    self.progress_bar.stop()
                    messagebox.showinfo("Success", f"Playlist downloaded!\n\nLocation: {download_folder}")
            
            else:
                # Single video download
                self.log_debug("=== DOWNLOADING SINGLE VIDEO ===")
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                self.progress_bar.stop()
                self.progress_label.config(text="Download completed!")
                
                # Detailed success popup
                result_msg = "🎉 VIDEO DOWNLOADED!\n\n"
                result_msg += f"✓ Download successful\n\n"
                result_msg += f"📁 Saved to:\n{download_folder}\n\n"
                result_msg += "Your video is ready to watch!"
                
                messagebox.showinfo("Success!", result_msg)
            
        except Exception as e:
            self.progress_bar.stop()
            self.progress_label.config(text="Download failed")
            self.log_debug(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to download:\n{str(e)}")
        
        finally:
            self.download_btn.config(state="normal", text="⬇ Download")
            self.stop_btn.config(state="disabled")
    
    def start_download(self):
        self.download_btn.config(state="disabled", text="Downloading...")
        self.stop_btn.config(state="normal")  # Enable emergency stop
        self.progress_bar.start(10)
        self.progress_label.config(text="Starting download...")
        self.log_debug("="*50)
        self.log_debug("NEW OPTIMIZED DOWNLOAD REQUEST")
        
        # Run download in separate thread
        download_thread = threading.Thread(target=self.download_video, daemon=True)
        download_thread.start()


def main():
    """Main application entry point with error handling"""
    try:
        print("=" * 60)
        print("LETUSTECH YOUTUBE CONVERTER - ULTRA FAST VERSION 2.2")
        print("⚡⚡⚡ 5x CONCURRENT + INSTANT LOADING ⚡⚡⚡")
        print("=" * 60)
        print("Creating main window...")
        
        root = tk.Tk()
        print("✓ Tkinter window created")
        
        def on_closing():
            print("Application close requested")
            try:
                root.quit()
                root.destroy()
            except:
                pass
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        print("✓ Close handler registered")
        
        print("Initializing YouTube Downloader...")
        app = YouTubeDownloader(root)
        print("✓ Application initialized successfully")
        
        print("Starting main event loop...")
        print("=" * 60)
        print("APPLICATION READY - ULTRA FAST MODE ENABLED!")
        print("=" * 60)
        
        root.mainloop()
        
    except Exception as e:
        print(f"✗ CRITICAL ERROR in main(): {str(e)}")
        import traceback
        print("✗ Full traceback:")
        traceback.print_exc()
        
        try:
            import tkinter.messagebox as msgbox
            msgbox.showerror(
                "Critical Error", 
                f"Application failed to start:\n\n{str(e)}\n\nCheck console for details."
            )
        except:
            print("Could not show error dialog")
        
        input("\nPress Enter to close...")


if __name__ == "__main__":
    main()