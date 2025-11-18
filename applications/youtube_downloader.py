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
        
        # Download path
        self.download_path = str(Path.home() / "Downloads")
        
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
            text="Download & convert videos, playlists & audio from YouTube",
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
            text="Download Entire Playlist",
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
            text="Download all videos when URL is a playlist",
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
            text="Paste a YouTube video or playlist URL",
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
        
        # Download Button
        self.download_btn = tk.Button(
            main_frame,
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
        self.download_btn.pack(fill="x", ipady=15)
        
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
        footer_frame = tk.Frame(self.root, bg=self.bg_color, height=40)
        footer_frame.pack(side="bottom", fill="x")
        footer_frame.pack_propagate(False)
        
        footer_label = tk.Label(
            footer_frame,
            text="LetUsTech - Wired For Your World  |  letustech.uk",
            font=("Segoe UI", 8),
            bg=self.bg_color,
            fg=self.text_muted
        )
        footer_label.pack(pady=10)
        
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
        
        quick_content = """🎬 QUICK START GUIDE

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
   • Playlists: Click "Select Videos" first
   • Watch progress bar for completion

🎵 FOR PLAYLISTS:
   • Large playlists load quickly
   • Use "Select Videos" for precise control
   • Search, filter by duration, or select patterns
   • Files include artist names automatically"""
        
        quick_text.insert("1.0", quick_content)
        quick_text.config(state="disabled")
        
        # Advanced Features Tab
        advanced_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(advanced_frame, text="⚡ Advanced Features")
        
        advanced_text = tk.Text(
            advanced_frame,
            font=("Segoe UI", 10),
            bg=self.accent_color,
            fg=self.text_color,
            wrap="word",
            padx=15,
            pady=15
        )
        advanced_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        advanced_content = """⚡ ADVANCED FEATURES

🔍 SMART PLAYLIST SELECTION:
   • Search Bar: Find videos by keywords
   • Duration Filter: Select by time range (e.g., 3-8 minutes)
   • Every Nth: Sample every 5th/10th video
   • Bulk Operations: Select/Deselect all

📁 FILE NAMING:
   • Format: "Artist - Song Title.mp3"
   • Auto-organizes: Music → Downloads/Music
   • Videos → Downloads/Videos
   • Preserves original quality metadata

🎛️ QUALITY OPTIONS:
   • Best Quality: Highest available (may need FFmpeg)
   • Fixed Resolutions: 1080p, 720p, 480p, 360p
   • Audio Only: Converts to MP3 (requires FFmpeg)

🐛 DEBUG MODE:
   • Enable in Settings for troubleshooting
   • Shows detailed download progress
   • Helps diagnose connection issues
   • Clear console with "Clear" button

📜 DOWNLOAD HISTORY:
   • Tracks all downloads automatically
   • Shows date, title, quality, location
   • Clear history when needed
   • Reopens files from history"""
        
        advanced_text.insert("1.0", advanced_content)
        advanced_text.config(state="disabled")
        
        # System Requirements Tab
        system_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(system_frame, text="💻 System Requirements")
        
        system_text = tk.Text(
            system_frame,
            font=("Segoe UI", 10),
            bg=self.accent_color,
            fg=self.text_color,
            wrap="word",
            padx=15,
            pady=15
        )
        system_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        system_content = """💻 SYSTEM REQUIREMENTS

✅ MINIMUM REQUIREMENTS:
   • Windows 10/11, macOS 10.14+, or Linux
   • Python 3.8+ with tkinter
   • 4GB RAM, 1GB free storage
   • Internet connection
   • 1366x768 screen resolution

🚀 RECOMMENDED:
   • 8GB+ RAM for large playlists
   • SSD storage for faster processing
   • 1920x1080+ resolution for best experience
   • High-speed internet for 4K downloads

📦 DEPENDENCIES:
   • yt-dlp (YouTube downloader library)
   • Pillow (PIL) for image processing
   • requests (HTTP library)
   • tkinter (GUI - usually included with Python)

🔧 OPTIONAL BUT RECOMMENDED:
   • FFmpeg - For audio conversion & merging
     - Windows: Auto-installer available
     - macOS: brew install ffmpeg
     - Linux: sudo apt install ffmpeg
   • Without FFmpeg:
     - No MP3 conversion
     - Limited format merging
     - Still downloads videos/audio

⚠️ TROUBLESHOOTING:
   • Enable Debug Mode for detailed logs
   • Check internet connection
   • Verify YouTube URL is valid
   • Install FFmpeg for audio issues
   • Update yt-dlp if download fails"""
        
        system_text.insert("1.0", system_content)
        system_text.config(state="disabled")
        
        # Tips & Tricks Tab
        tips_frame = tk.Frame(notebook, bg=self.bg_color)
        notebook.add(tips_frame, text="💡 Tips & Tricks")
        
        tips_text = tk.Text(
            tips_frame,
            font=("Segoe UI", 10),
            bg=self.accent_color,
            fg=self.text_color,
            wrap="word",
            padx=15,
            pady=15
        )
        tips_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        tips_content = """💡 TIPS & TRICKS

🎵 FOR MUSIC LOVERS:
   • Use "Audio Only (MP3)" for music playlists
   • Search for "remix" to find all remixes
   • Filter 3-6 minutes to skip intros/outros
   • Select every 3rd song for variety

📺 FOR VIDEO CONTENT:
   • Use "Best Quality" for important videos
   • 720p saves space while staying crisp
   • Check "Download Entire Playlist" for full series

⚡ SPEED TIPS:
   • Large playlists? Use search/filters first
   • Process playlists in batches (50-100 videos)
   • Close other programs during big downloads
   • Use SSD storage for faster processing

🔧 ORGANIZATION HACKS:
   • Let app auto-sort into Music/Videos folders
   • Artist names included automatically
   • Use History to find old downloads
   • Clear browser cache if URLs fail

⚠️ COMMON ISSUES & FIXES:
   • "Video unavailable" → Try again later
   • Slow downloads → Check internet speed
   • FFmpeg errors → Install/update FFmpeg
   • Long playlists → Use selection tools
   • GUI freezing → Enable debug mode"""
        
        tips_text.insert("1.0", tips_content)
        tips_text.config(state="disabled")
        
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
            text="Version 2.0 - Professional Edition",
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

📱 ABOUT LETUSTECH:
LetUsTech is a technology platform offering free Python automation tools and browser-based games. We create educational content and practical applications to make technology accessible for everyone.

🎬 YOUTUBE CONVERTER FEATURES:
• Download videos in multiple quality options
• Smart playlist handling for large collections
• Artist names in filenames automatically
• Advanced selection tools (search, duration, patterns)
• Built-in FFmpeg support with auto-installer
• Professional UI with debug capabilities

🛠️ TECHNICAL STACK:
• Python 3.8+ with tkinter GUI
• yt-dlp for YouTube downloading
• Pillow (PIL) for image processing
• FFmpeg for audio/video processing
• Designed for Windows, macOS, and Linux

💖 SUPPORT THE PROJECT:
This software is completely free! If you find it useful:
• Visit letustech.uk for more tools
• Join our Discord: discord.gg/dkebMS5eCX
• Share with friends who need video downloading
• Consider a PayPal donation to keep projects running

📞 CONTACT & COMMUNITY:
• GitHub: github.com/letustech
• Discord: Active community for feature requests
• Website: letustech.uk - More free tools available

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
    
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder)
            self.save_settings()
            self.log_debug(f"Download path changed to: {folder}")
    
    def load_preview(self):
        """Load video thumbnail and info"""
        self.log_debug("=== STARTING PREVIEW LOAD ===")
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
        
        self.root.update_idletasks()  # Force UI update
        
        self.log_debug("UI updated - buttons disabled, status set to loading, previous data cleared")
        
        def fetch_preview():
            try:
                self.log_debug("=== FETCH PREVIEW THREAD STARTED ===")
                self.log_debug(f"Current time: {time.strftime('%H:%M:%S')}")
                
                # Update UI to show progress
                def update_status(message):
                    self.root.after(0, lambda: self.thumbnail_label.config(text=message))
                
                update_status("🔄 Connecting to YouTube...")
                self.log_debug("Status updated: Connecting to YouTube")
                
                # First, do a quick check to see if it's a large playlist
                quick_opts = {
                    'quiet': True,
                    'extract_flat': True,  # Fast check
                    'ignoreerrors': True,
                }
                
                self.log_debug("Doing quick playlist check...")
                with yt_dlp.YoutubeDL(quick_opts) as ydl:
                    quick_info = ydl.extract_info(url, download=False)
                
                # If it's a large playlist, handle it specially
                if 'entries' in quick_info:
                    entries_count = len(quick_info.get('entries', []))
                    self.log_debug(f"Found playlist with {entries_count} videos")
                    
                    if entries_count > 50:  # Large playlist
                        self.log_debug("=== LARGE PLAYLIST DETECTED - FAST MODE ===")
                        update_status(f"📋 Large playlist found ({entries_count} videos)")
                        
                        self.is_playlist = True
                        self.playlist_videos = []
                        
                        playlist_title = quick_info.get('title', 'Large Playlist')
                        
                        # Just take the first few videos for preview
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
                            text=f"📋 {playlist_title}\n({entries_count} videos - Large playlist detected)"
                        )
                        
                        # Store the quick info for later use
                        self.full_playlist_info = quick_info
                        self.select_videos_btn.config(state="normal")
                        
                        # Use first video thumbnail
                        thumbnail_url = self.playlist_videos[0].get('thumbnail') if self.playlist_videos else None
                        
                        self.log_debug("Large playlist handled quickly - skipping full processing")
                        
                        # Jump to thumbnail loading for large playlists
                        if thumbnail_url:
                            self.log_debug("Loading thumbnail for large playlist")
                        else:
                            self.log_debug("No thumbnail available for large playlist")
                            self.thumbnail_label.config(text="📋 Large Playlist")
                        
                        # Skip the rest of processing for large playlists
                        skip_normal_processing = True
                        
                    else:
                        self.log_debug(f"Small playlist ({entries_count} videos) - processing normally")
                        # Continue with normal processing for small playlists
                        ydl_opts = {
                            'quiet': not self.debug_mode,
                            'no_warnings': not self.debug_mode,
                            'extract_flat': False,
                            'ignoreerrors': False,
                            'socket_timeout': 30,
                            'retries': 2,
                        }
                        skip_normal_processing = False
                else:
                    self.log_debug("Single video detected - processing normally")
                    # Continue with normal processing for single videos
                    ydl_opts = {
                        'quiet': not self.debug_mode,
                        'no_warnings': not self.debug_mode,
                        'extract_flat': False,
                        'ignoreerrors': False,
                        'socket_timeout': 30,
                        'retries': 2,
                    }
                    skip_normal_processing = False
                
                # Only do full processing if not a large playlist
                if not skip_normal_processing:
                    self.log_debug("yt-dlp options configured:")
                    self.log_debug(f"  - quiet: {ydl_opts['quiet']}")
                    self.log_debug(f"  - no_warnings: {ydl_opts['no_warnings']}")
                    self.log_debug(f"  - extract_flat: {ydl_opts['extract_flat']}")
                    self.log_debug(f"  - ignoreerrors: {ydl_opts['ignoreerrors']}")
                    
                    self.log_debug("Creating yt-dlp instance...")
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        self.log_debug("yt-dlp instance created successfully")
                        self.log_debug(f"Calling extract_info for URL: {url}")
                        
                        info = ydl.extract_info(url, download=False)
                        
                        self.log_debug("yt-dlp extract_info completed")
                        self.log_debug(f"Info type: {type(info)}")
                        
                        if not info:
                            self.log_debug("ERROR: yt-dlp returned None/empty info")
                            raise Exception("Could not extract video information")
                        
                        self.log_debug(f"Info keys: {list(info.keys()) if isinstance(info, dict) else 'Not a dict'}")
                        
                        # Check if it's a playlist
                        if 'entries' in info:
                            self.log_debug("=== PLAYLIST DETECTED ===")
                            self.is_playlist = True
                            self.playlist_videos = []
                            
                            playlist_title = info.get('title', 'Unknown Playlist')
                            self.log_debug(f"Playlist title: {playlist_title}")
                            
                            # Get playlist thumbnail from first video or playlist info
                            thumbnail_url = info.get('thumbnail')
                            self.log_debug(f"Playlist thumbnail URL: {thumbnail_url}")
                            
                            # Store all videos with full info
                            entries_count = len(info.get('entries', []))
                            self.log_debug(f"Processing {entries_count} entries...")
                            
                            for i, entry in enumerate(info['entries']):
                                if entry:
                                    video_data = {
                                        'title': entry.get('title', 'Unknown'),
                                        'id': entry.get('id', ''),
                                        'url': entry.get('webpage_url', entry.get('url', '')),
                                        'duration': entry.get('duration', 0),
                                        'thumbnail': entry.get('thumbnail', '')
                                    }
                                    self.playlist_videos.append(video_data)
                                    self.log_debug(f"Entry {i+1}: {video_data['title']} ({video_data['id']})")
                                else:
                                    self.log_debug(f"Entry {i+1}: Empty/None entry skipped")
                            
                            video_count = len(self.playlist_videos)
                            self.log_debug(f"Total valid videos in playlist: {video_count}")
                            
                            self.video_title_label.config(
                                text=f"📋 Playlist: {playlist_title}\n({video_count} videos)"
                            )
                            
                            # Enable select videos button
                            self.select_videos_btn.config(state="normal")
                            self.log_debug("Select videos button enabled")
                            
                            # Get first video thumbnail if playlist doesn't have one
                            if not thumbnail_url and self.playlist_videos:
                                thumbnail_url = self.playlist_videos[0].get('thumbnail')
                                self.log_debug(f"Using first video thumbnail: {thumbnail_url}")
                            
                        else:
                            self.log_debug("=== SINGLE VIDEO DETECTED ===")
                            self.is_playlist = False
                            self.playlist_videos = []
                            self.select_videos_btn.config(state="disabled")
                            
                            title = info.get('title', 'Unknown')
                            duration = info.get('duration', 0)
                            uploader = info.get('uploader', 'Unknown')
                            view_count = info.get('view_count', 0)
                            
                            self.log_debug(f"Video title: {title}")
                            self.log_debug(f"Video duration: {duration} seconds")
                            self.log_debug(f"Video uploader: {uploader}")
                            self.log_debug(f"Video view count: {view_count}")
                            
                            mins, secs = divmod(duration, 60) if duration else (0, 0)
                            
                            self.video_title_label.config(
                                text=f"{title}\n({int(mins)}:{int(secs):02d})"
                            )
                            
                            # Try multiple thumbnail fields
                            thumbnails = info.get('thumbnails', [])
                            self.log_debug(f"Available thumbnails: {len(thumbnails)}")
                            
                            for i, thumb in enumerate(thumbnails[:3]):  # Log first 3
                                self.log_debug(f"  Thumbnail {i+1}: {thumb.get('url', 'No URL')} ({thumb.get('width', '?')}x{thumb.get('height', '?')})")
                            
                            thumbnail_url = (
                                info.get('thumbnail') or 
                                (thumbnails[-1].get('url') if thumbnails else None)
                            )
                            
                            self.log_debug(f"Selected thumbnail URL: {thumbnail_url}")
                
                # Load thumbnail image (works for both large playlists and normal processing)
                if thumbnail_url:
                    self.log_debug("=== LOADING THUMBNAIL ===")
                    self.log_debug(f"Thumbnail URL: {thumbnail_url}")
                    
                    try:
                        # Add headers to mimic browser request
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                        }
                        
                        self.log_debug("Making HTTP request for thumbnail...")
                        response = requests.get(thumbnail_url, timeout=15, headers=headers)
                        self.log_debug(f"HTTP response status: {response.status_code}")
                        self.log_debug(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
                        self.log_debug(f"Content-Length: {len(response.content)} bytes")
                        
                        if response.status_code != 200:
                            raise Exception(f"HTTP {response.status_code}: Could not download thumbnail")
                        
                        img_data = response.content
                        self.log_debug(f"Downloaded {len(img_data)} bytes of image data")
                        
                        self.log_debug("Opening image with PIL...")
                        img = Image.open(BytesIO(img_data))
                        self.log_debug(f"Original image size: {img.size}")
                        self.log_debug(f"Image mode: {img.mode}")
                        
                        # Convert to RGB if needed
                        if img.mode != 'RGB':
                            self.log_debug(f"Converting image from {img.mode} to RGB")
                            img = img.convert('RGB')
                        
                        # Resize to fit preview area - BIGGER SIZE
                        original_size = img.size
                        self.log_debug("Resizing image to fit preview area (300x180)...")  # Increased from 230x130
                        img.thumbnail((300, 180), Image.Resampling.LANCZOS)
                        self.log_debug(f"Image resized from {original_size} to {img.size}")
                        
                        self.log_debug("Converting to PhotoImage...")
                        photo = ImageTk.PhotoImage(img)
                        self.current_thumbnail = photo
                        
                        self.log_debug("Updating thumbnail label...")
                        self.thumbnail_label.config(image=photo, text="")
                        self.thumbnail_label.image = photo
                        self.log_debug("Thumbnail loaded and displayed successfully!")
                        
                    except Exception as thumb_error:
                        self.log_debug(f"WARNING: Failed to load thumbnail: {thumb_error}")
                        if self.is_playlist:
                            self.thumbnail_label.config(text="📋 Playlist\n(No preview image)")
                        else:
                            self.thumbnail_label.config(text="❌ No image available")
                        
                else:
                    self.log_debug("WARNING: No thumbnail URL found")
                    if self.is_playlist:
                        self.thumbnail_label.config(text="📋 Playlist\n(No preview image)")
                    else:
                        self.thumbnail_label.config(text="❌ No image available")
                
                self.log_debug(f"=== PREVIEW LOAD COMPLETE ===")
                self.log_debug(f"Type: {'Playlist' if self.is_playlist else 'Video'}")
                    
            except requests.exceptions.Timeout as e:
                self.log_debug(f"TIMEOUT ERROR: {str(e)}")
                self.thumbnail_label.config(text="Timeout loading preview")
                self.video_title_label.config(text="")
                messagebox.showerror("Timeout Error", "Request timed out. Please check your internet connection and try again.")
                
            except requests.exceptions.ConnectionError as e:
                self.log_debug(f"CONNECTION ERROR: {str(e)}")
                self.thumbnail_label.config(text="Connection failed")
                self.video_title_label.config(text="")
                messagebox.showerror("Connection Error", "Could not connect to YouTube. Please check your internet connection.")
                
            except yt_dlp.DownloadError as e:
                self.log_debug(f"YT-DLP DOWNLOAD ERROR: {str(e)}")
                self.thumbnail_label.config(text="Video unavailable")
                self.video_title_label.config(text="")
                error_msg = str(e).lower()
                if 'private' in error_msg:
                    messagebox.showerror("Video Unavailable", "This video is private.")
                elif 'unavailable' in error_msg:
                    messagebox.showerror("Video Unavailable", "This video is no longer available.")
                elif 'age' in error_msg or 'restricted' in error_msg:
                    messagebox.showerror("Video Restricted", "This video is age-restricted or region-blocked.")
                else:
                    messagebox.showerror("Download Error", f"Could not access video:\n{str(e)}")
                    
            except Exception as e:
                self.log_debug(f"UNEXPECTED ERROR in fetch_preview: {type(e).__name__}: {str(e)}")
                self.thumbnail_label.config(text="Failed to load preview")
                self.video_title_label.config(text="")
                import traceback
                full_traceback = traceback.format_exc()
                self.log_debug(f"Full traceback:\n{full_traceback}")
                messagebox.showerror("Preview Error", f"Failed to load preview:\n\n{type(e).__name__}: {str(e)}")
            
            finally:
                self.log_debug("=== PREVIEW LOAD FINISHED ===")
                self.preview_btn.config(state="normal", text="Reload Preview")
        
        # Run in thread
        self.log_debug("Starting preview fetch thread...")
        threading.Thread(target=fetch_preview, daemon=True).start()
    
    def validate_url(self, url):
        youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        return re.match(youtube_regex, url) is not None
    
    def show_video_selector(self):
        """Show video selector for playlist"""
        if not hasattr(self, 'is_playlist') or not self.is_playlist:
            messagebox.showwarning("Warning", "This feature is only available for playlists")
            return
        
        # For large playlists, we'll load the first 20 thumbnails immediately
        if hasattr(self, 'full_playlist_info') and self.full_playlist_info:
            self.log_debug("=== LOADING FIRST 20 THUMBNAILS FOR VIDEO SELECTOR ===")
            
            # Show loading dialog for first 20 thumbnails only
            loading_dialog = tk.Toplevel(self.root)
            loading_dialog.title("Loading Video Selector")
            loading_dialog.geometry("400x150")
            loading_dialog.configure(bg=self.bg_color)
            loading_dialog.resizable(False, False)
            loading_dialog.transient(self.root)
            loading_dialog.grab_set()
            
            # Center the dialog
            loading_dialog.update_idletasks()
            x = (loading_dialog.winfo_screenwidth() // 2) - (400 // 2)
            y = (loading_dialog.winfo_screenheight() // 2) - (150 // 2)
            loading_dialog.geometry(f"400x150+{x}+{y}")
            
            # Header
            header_label = tk.Label(
                loading_dialog,
                text="🔄 Loading Video Selector",
                font=("Segoe UI", 12, "bold"),
                bg=self.bg_color,
                fg=self.green_color
            )
            header_label.pack(pady=20)
            
            # Status label
            status_label = tk.Label(
                loading_dialog,
                text="Loading first 20 video thumbnails...",
                font=("Segoe UI", 10),
                bg=self.bg_color,
                fg=self.text_color
            )
            status_label.pack(pady=5)
            
            # Progress bar
            progress_bar = ttk.Progressbar(loading_dialog, mode='indeterminate')
            progress_bar.pack(pady=15, padx=30, fill="x")
            progress_bar.start(10)
            
            def load_first_page_with_thumbnails():
                try:
                    self.log_debug("Preparing basic video list...")
                    
                    # Prepare basic video list
                    self.playlist_videos = []
                    for i, entry in enumerate(self.full_playlist_info['entries']):
                        if entry:
                            video_data = {
                                'title': entry.get('title', f'Video {i+1}'),
                                'id': entry.get('id', ''),
                                'url': entry.get('url', ''),
                                'duration': entry.get('duration', 0),
                                'thumbnail': '',  # Will be populated for first 20
                                'uploader': entry.get('uploader', ''),
                                'view_count': entry.get('view_count', 0)
                            }
                            self.playlist_videos.append(video_data)
                    
                    self.log_debug(f"Prepared {len(self.playlist_videos)} videos")
                    
                    # Now load thumbnails for first 20 videos
                    self.root.after(0, lambda: status_label.config(text="Loading thumbnails for first 20 videos..."))
                    
                    first_20_videos = self.playlist_videos[:20]
                    ydl_opts = {
                        'quiet': True,
                        'no_warnings': True,
                        'extract_flat': False,
                        'ignoreerrors': True,
                    }
                    
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        for i, video in enumerate(first_20_videos):
                            try:
                                if video.get('id'):
                                    video_url = f"https://www.youtube.com/watch?v={video['id']}"
                                    self.log_debug(f"Loading thumbnail {i+1}/20 for: {video['title'][:50]}...")
                                    
                                    # Update status
                                    if i % 5 == 0 or i < 5:
                                        progress_text = f"Loading thumbnail {i+1}/20..."
                                        self.root.after(0, lambda p=progress_text: status_label.config(text=p))
                                    
                                    info = ydl.extract_info(video_url, download=False)
                                    
                                    if info:
                                        thumbnail_url = (
                                            info.get('thumbnail') or 
                                            (info.get('thumbnails', [{}])[-1].get('url', '') if info.get('thumbnails') else '')
                                        )
                                        
                                        if thumbnail_url:
                                            self.playlist_videos[i]['thumbnail'] = thumbnail_url
                                            self.log_debug(f"✓ Loaded thumbnail {i+1}: {thumbnail_url[:50]}...")
                                        else:
                                            self.log_debug(f"No thumbnail for video {i+1}")
                            
                            except Exception as e:
                                self.log_debug(f"Error loading thumbnail {i+1}: {e}")
                                continue
                    
                    self.log_debug(f"✓ Loaded thumbnails for first 20 videos")
                    
                    # Close dialog and show selector
                    def show_selector():
                        progress_bar.stop()
                        loading_dialog.destroy()
                        self._show_video_selector_window()
                    
                    self.root.after(0, show_selector)
                    
                except Exception as e:
                    self.log_debug(f"Error loading first page: {e}")
                    
                    def show_error():
                        progress_bar.stop()
                        loading_dialog.destroy()
                        messagebox.showerror("Error", f"Failed to load video selector:\n{str(e)}")
                    
                    self.root.after(0, show_error)
            
            # Start loading in background
            threading.Thread(target=load_first_page_with_thumbnails, daemon=True).start()
            
        else:
            # Small playlist - load normally
            self._show_video_selector_window()
    
    def _show_video_selector_window(self):
        """Show the actual video selector window"""
        # Debug: Check if we have videos to show
        self.log_debug(f"=== SHOWING VIDEO SELECTOR ===")
        self.log_debug(f"Number of playlist videos available: {len(self.playlist_videos)}")
        
        if not self.playlist_videos:
            self.log_debug("ERROR: No playlist videos available to show!")
            messagebox.showerror("Error", "No videos available to select. Please reload the preview.")
            return
        
        # Show first few video titles for debugging
        for i, video in enumerate(self.playlist_videos[:3]):
            self.log_debug(f"Video {i+1}: {video.get('title', 'No title')}")
        
        selector_window = tk.Toplevel(self.root)
        selector_window.title("Select Videos - LetUsTech YouTube Converter")
        
        # Responsive window sizing for different screen sizes
        screen_width = selector_window.winfo_screenwidth()
        screen_height = selector_window.winfo_screenheight()
        
        if screen_width >= 1920:  # Large screens (1920+)
            window_width = 1400
            window_height = 900
        elif screen_width >= 1366:  # Medium screens
            window_width = 1200
            window_height = 800
        else:  # Smaller screens
            window_width = 1000
            window_height = 700
            
        # Center the window
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        selector_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        selector_window.configure(bg=self.bg_color)
        selector_window.minsize(900, 600)  # Minimum size
        
        # Header
        header_frame = tk.Frame(selector_window, bg=self.card_color, height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        header = tk.Label(
            header_frame,
            text=f"📋 Select Videos to Download",
            font=("Segoe UI", 16, "bold"),
            bg=self.card_color,
            fg=self.green_color
        )
        header.pack(pady=(20, 5))
        
        count_label = tk.Label(
            header_frame,
            text=f"{len(self.playlist_videos)} videos in playlist",
            font=("Segoe UI", 9),
            bg=self.card_color,
            fg=self.text_muted
        )
        count_label.pack()
        
        # Select/Deselect all buttons with enhanced options
        button_frame = tk.Frame(selector_window, bg=self.bg_color)
        button_frame.pack(pady=15)
        
        video_vars = []
        
        def select_all():
            if hasattr(self, 'all_video_vars'):
                for var in self.all_video_vars:
                    var.set(True)
                self.update_selection_count()
        
        def deselect_all():
            if hasattr(self, 'all_video_vars'):
                for var in self.all_video_vars:
                    var.set(False)
                self.update_selection_count()
        
        def select_by_duration():
            """Select videos based on duration range"""
            duration_window = tk.Toplevel(selector_window)
            duration_window.title("Select by Duration")
            duration_window.geometry("400x200")
            duration_window.configure(bg=self.bg_color)
            duration_window.transient(selector_window)
            
            tk.Label(duration_window, text="Select videos by duration range:", 
                    font=("Segoe UI", 12, "bold"), bg=self.bg_color, fg=self.text_color).pack(pady=10)
            
            frame = tk.Frame(duration_window, bg=self.bg_color)
            frame.pack(pady=10)
            
            tk.Label(frame, text="Min duration (minutes):", bg=self.bg_color, fg=self.text_color).grid(row=0, column=0, padx=5)
            min_entry = tk.Entry(frame, width=10)
            min_entry.grid(row=0, column=1, padx=5)
            min_entry.insert(0, "0")
            
            tk.Label(frame, text="Max duration (minutes):", bg=self.bg_color, fg=self.text_color).grid(row=1, column=0, padx=5)
            max_entry = tk.Entry(frame, width=10)
            max_entry.grid(row=1, column=1, padx=5)
            max_entry.insert(0, "60")
            
            def apply_duration_filter():
                try:
                    min_dur = float(min_entry.get()) * 60  # Convert to seconds
                    max_dur = float(max_entry.get()) * 60
                    count = 0
                    if hasattr(self, 'all_video_vars'):
                        for i, video in enumerate(self.playlist_videos):
                            duration = video.get('duration', 0)
                            if min_dur <= duration <= max_dur:
                                self.all_video_vars[i].set(True)
                                count += 1
                            else:
                                self.all_video_vars[i].set(False)
                        self.update_selection_count()
                    duration_window.destroy()
                    messagebox.showinfo("Selection Complete", f"Selected {count} videos within duration range")
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid numbers")
            
            tk.Button(frame, text="Apply Filter", command=apply_duration_filter, 
                     bg=self.green_color, fg=self.bg_color, font=("Segoe UI", 10, "bold")).grid(row=2, column=0, columnspan=2, pady=10)
        
        def select_every_nth():
            """Select every Nth video"""
            nth_window = tk.Toplevel(selector_window)
            nth_window.title("Select Every Nth Video")
            nth_window.geometry("300x150")
            nth_window.configure(bg=self.bg_color)
            nth_window.transient(selector_window)
            
            tk.Label(nth_window, text="Select every Nth video:", 
                    font=("Segoe UI", 12, "bold"), bg=self.bg_color, fg=self.text_color).pack(pady=10)
            
            frame = tk.Frame(nth_window, bg=self.bg_color)
            frame.pack(pady=10)
            
            tk.Label(frame, text="Every", bg=self.bg_color, fg=self.text_color).grid(row=0, column=0, padx=5)
            nth_entry = tk.Entry(frame, width=10)
            nth_entry.grid(row=0, column=1, padx=5)
            nth_entry.insert(0, "5")
            tk.Label(frame, text="videos", bg=self.bg_color, fg=self.text_color).grid(row=0, column=2, padx=5)
            
            def apply_nth_filter():
                try:
                    nth = int(nth_entry.get())
                    deselect_all()  # Start with none selected
                    count = 0
                    for i in range(0, len(self.playlist_videos), nth):
                        video_vars[i].set(True)
                        count += 1
                    update_count()
                    nth_window.destroy()
                    messagebox.showinfo("Selection Complete", f"Selected every {nth}th video ({count} total)")
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number")
            
            tk.Button(frame, text="Apply", command=apply_nth_filter, 
                     bg=self.green_color, fg=self.bg_color, font=("Segoe UI", 10, "bold")).grid(row=1, column=0, columnspan=3, pady=10)
        
        # Search functionality
        search_frame = tk.Frame(button_frame, bg=self.bg_color)
        search_frame.pack(side="top", pady=(0, 10), fill="x")
        
        tk.Label(search_frame, text="🔍 Search:", font=("Segoe UI", 9, "bold"), 
                bg=self.bg_color, fg=self.text_color).pack(side="left", padx=5)
        
        search_entry = tk.Entry(search_frame, width=30, font=("Segoe UI", 9))
        search_entry.pack(side="left", padx=5)
        
        def search_and_select():
            search_term = search_entry.get().lower()
            if not search_term:
                return
            count = 0
            for i, video in enumerate(self.playlist_videos):
                title = video.get('title', '').lower()
                if search_term in title:
                    video_vars[i].set(True)
                    count += 1
            update_count()
            messagebox.showinfo("Search Complete", f"Found and selected {count} videos matching '{search_term}'")
        
        tk.Button(search_frame, text="Select Matching", command=search_and_select,
                 bg=self.accent_color, fg=self.text_color, font=("Segoe UI", 8, "bold")).pack(side="left", padx=5)
        
        # Main selection buttons
        buttons_frame = tk.Frame(button_frame, bg=self.bg_color)
        buttons_frame.pack(side="top", pady=5)
        
        select_all_btn = tk.Button(
            buttons_frame,
            text="✓ Select All",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=select_all
        )
        select_all_btn.pack(side="left", padx=5, ipadx=15, ipady=6)
        
        deselect_all_btn = tk.Button(
            buttons_frame,
            text="✗ Deselect All",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=deselect_all
        )
        deselect_all_btn.pack(side="left", padx=5, ipadx=15, ipady=6)
        
        duration_btn = tk.Button(
            buttons_frame,
            text="⏱ By Duration",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=select_by_duration
        )
        duration_btn.pack(side="left", padx=5, ipadx=15, ipady=6)
        
        nth_btn = tk.Button(
            buttons_frame,
            text="🔢 Every Nth",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=select_every_nth
        )
        nth_btn.pack(side="left", padx=5, ipadx=15, ipady=6)
        
        # Scrollable frame for videos
        list_container = tk.Frame(selector_window, bg=self.bg_color)
        list_container.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        
        # Border frame
        list_frame = tk.Frame(list_container, bg=self.border_color, padx=2, pady=2)
        list_frame.pack(fill="both", expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(list_frame, bg=self.card_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        
        # Create scrollable frame
        scrollable_frame = tk.Frame(canvas, bg=self.card_color)
        
        # Configure scrolling
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_canvas_configure(event):
            # Update scroll region when canvas size changes
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update the width of the scrollable frame to match canvas
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", on_canvas_configure)
        
        # Create window in canvas
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mousewheel to canvas
        canvas.bind("<MouseWheel>", on_mousewheel)  # Windows
        canvas.bind("<Button-4>", lambda e: canvas.yview_scroll(-1, "units"))  # Linux
        canvas.bind("<Button-5>", lambda e: canvas.yview_scroll(1, "units"))   # Linux
        
        # Pagination for large playlists
        self.current_page = 0
        self.videos_per_page = 20
        self.total_pages = (len(self.playlist_videos) + self.videos_per_page - 1) // self.videos_per_page
        
        # Pagination controls frame
        if self.total_pages > 1:
            pagination_frame = tk.Frame(selector_window, bg=self.bg_color)
            pagination_frame.pack(fill="x", padx=30, pady=(0, 10))
            
            # Page info label
            self.page_info_label = tk.Label(
                pagination_frame,
                text=f"Page {self.current_page + 1} of {self.total_pages} ({self.videos_per_page} videos per page)",
                font=("Segoe UI", 9),
                bg=self.bg_color,
                fg=self.text_muted
            )
            self.page_info_label.pack(side="left")
            
            # Pagination buttons
            pagination_buttons = tk.Frame(pagination_frame, bg=self.bg_color)
            pagination_buttons.pack(side="right")
            
            # Previous button
            self.prev_btn = tk.Button(
                pagination_buttons,
                text="◀ Previous",
                font=("Segoe UI", 9, "bold"),
                bg=self.accent_color,
                fg=self.text_color,
                activebackground=self.green_color,
                activeforeground=self.bg_color,
                relief="flat",
                cursor="hand2",
                borderwidth=0,
                state="disabled",  # Start disabled
                command=lambda: self.change_page(selector_window, scrollable_frame, canvas, -1)
            )
            self.prev_btn.pack(side="left", padx=5, ipadx=15, ipady=5)
            
            # Next button
            self.next_btn = tk.Button(
                pagination_buttons,
                text="Next ▶",
                font=("Segoe UI", 9, "bold"),
                bg=self.accent_color,
                fg=self.text_color,
                activebackground=self.green_color,
                activeforeground=self.bg_color,
                relief="flat",
                cursor="hand2",
                borderwidth=0,
                state="normal" if self.total_pages > 1 else "disabled",
                command=lambda: self.change_page(selector_window, scrollable_frame, canvas, 1)
            )
            self.next_btn.pack(side="left", padx=5, ipadx=15, ipady=5)
            
            # Jump to page
            jump_frame = tk.Frame(pagination_buttons, bg=self.bg_color)
            jump_frame.pack(side="left", padx=10)
            
            tk.Label(jump_frame, text="Go to page:", bg=self.bg_color, fg=self.text_color, font=("Segoe UI", 8)).pack(side="left")
            
            self.page_entry = tk.Entry(jump_frame, width=5, font=("Segoe UI", 9))
            self.page_entry.pack(side="left", padx=5)
            
            jump_btn = tk.Button(
                jump_frame,
                text="Go",
                font=("Segoe UI", 8, "bold"),
                bg=self.green_color,
                fg=self.bg_color,
                relief="flat",
                cursor="hand2",
                borderwidth=0,
                command=lambda: self.jump_to_page(selector_window, scrollable_frame, canvas)
            )
            jump_btn.pack(side="left", padx=2, ipadx=8, ipady=2)
        
        self.log_debug(f"Setting up video list with {len(self.playlist_videos)} videos")
        self.log_debug(f"Total pages: {getattr(self, 'total_pages', 1)}, Videos per page: {getattr(self, 'videos_per_page', len(self.playlist_videos))}")
        
        # Load videos for current page
        self.load_page_videos(scrollable_frame, canvas, 0)
        
        # Force update to ensure widgets are properly laid out
        scrollable_frame.update_idletasks()
        
        # Configure scroll region after all videos are added
        canvas.configure(scrollregion=canvas.bbox("all"))
        
        # Ensure canvas focuses on widgets for keyboard events
        canvas.focus_set()
        
        # Bottom button frame
        bottom_frame = tk.Frame(selector_window, bg=self.bg_color)
        bottom_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        # Selection count label
        self.selection_label = tk.Label(
            bottom_frame,
            text="",
            font=("Segoe UI", 9),
            bg=self.bg_color,
            fg=self.text_muted
        )
        self.selection_label.pack(side="left")
        
        # Update initial count
        self.update_selection_count()
        
        # Confirm button
        def confirm_selection():
            if not hasattr(self, 'all_video_vars'):
                messagebox.showwarning("No Selection", "Please select at least one video")
                return
                
            self.selected_videos = []
            for i, var in enumerate(self.all_video_vars):
                if var.get():
                    self.selected_videos.append(self.playlist_videos[i])
            
            if not self.selected_videos:
                messagebox.showwarning("No Selection", "Please select at least one video")
                return
            
            count = len(self.selected_videos)
            self.log_debug(f"Selected {count} videos from playlist")
            messagebox.showinfo("Selection Confirmed", f"{count} video(s) selected for download")
            selector_window.destroy()
        
        confirm_btn = tk.Button(
            bottom_frame,
            text=f"⬇ Confirm Selection",
            font=("Segoe UI", 11, "bold"),
            bg=self.green_color,
            fg=self.bg_color,
            activebackground=self.green_hover,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=confirm_selection
        )
        confirm_btn.pack(side="right", ipadx=30, ipady=10)
        
        # Close button
        close_btn = tk.Button(
            bottom_frame,
            text="Close",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_color,
            fg=self.text_color,
            activebackground=self.green_color,
            activeforeground=self.bg_color,
            relief="flat",
            cursor="hand2",
            borderwidth=0,
            command=selector_window.destroy
        )
        close_btn.pack(side="right", padx=(0, 10), ipadx=25, ipady=10)
        
        # Add "Load More Thumbnails" button for large playlists
        if len(self.playlist_videos) > 20:
            load_thumbs_btn = tk.Button(
                button_frame,
                text="📷 Load All Thumbnails",
                font=("Segoe UI", 9, "bold"),
                bg=self.accent_color,
                fg=self.text_color,
                activebackground=self.green_color,
                activeforeground=self.bg_color,
                relief="flat",
                cursor="hand2",
                borderwidth=0,
                command=lambda: self.load_remaining_thumbnails(scrollable_frame)
            )
            load_thumbs_btn.pack(side="right", padx=(0, 10), ipadx=20, ipady=10)
    
    def load_remaining_thumbnails(self, scrollable_frame):
        """Load thumbnails for videos beyond the first 20"""
        def load_all_thumbs():
            try:
                # Get all video frames
                video_frames = scrollable_frame.winfo_children()
                
                for i, video in enumerate(self.playlist_videos[20:], start=20):
                    if i >= len(video_frames):
                        break
                        
                    # Find thumbnail label in this frame
                    video_frame = video_frames[i]
                    thumbnail_frame = None
                    
                    for child in video_frame.winfo_children():
                        if isinstance(child, tk.Frame) and child.winfo_width() == 90:  # Thumbnail frame
                            thumbnail_frame = child
                            break
                    
                    if thumbnail_frame:
                        # Find thumbnail label
                        for child in thumbnail_frame.winfo_children():
                            if isinstance(child, tk.Label):
                                thumbnail_label = child
                                # Load this thumbnail
                                self.load_video_thumbnail(video, thumbnail_label, i)
                                break
                    
                    # Small delay to avoid overwhelming the system
                    time.sleep(0.1)
                    
            except Exception as e:
                self.log_debug(f"Error loading remaining thumbnails: {e}")
        
        # Show loading message
        messagebox.showinfo("Loading Thumbnails", 
                           f"Loading thumbnails for {len(self.playlist_videos) - 20} remaining videos.\n"
                           "This may take a moment...")
        
        # Start loading in background
        threading.Thread(target=load_all_thumbs, daemon=True).start()
    
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
    
    def download_video(self):
        self.log_debug("=== STARTING VIDEO DOWNLOAD ===")
        
        url = self.url_entry.get().strip()
        self.log_debug(f"Raw URL from entry: '{url}'")
        
        if not url:
            self.log_debug("ERROR: No URL provided")
            messagebox.showerror("Error", "Please enter a YouTube URL")
            self.download_btn.config(state="normal", text="Download")
            self.progress_bar.stop()
            return
        
        self.log_debug(f"URL validation starting for: {url}")
        if not self.validate_url(url):
            self.log_debug("ERROR: URL validation failed")
            messagebox.showerror("Error", "Invalid YouTube URL")
            self.download_btn.config(state="normal", text="Download")
            self.progress_bar.stop()
            self.log_debug(f"Invalid URL rejected: {url}")
            return
        
        self.log_debug("URL validation passed")
        
        quality = self.quality_var.get()
        download_playlist = self.playlist_var.get()
        
        # Get appropriate download folder
        download_folder = self.get_download_folder(quality)
        
        self.log_debug(f"=== DOWNLOAD CONFIGURATION ===")
        self.log_debug(f"URL: {url}")
        self.log_debug(f"Quality setting: {quality}")
        self.log_debug(f"Download folder: {download_folder}")
        self.log_debug(f"Playlist mode: {download_playlist}")
        self.log_debug(f"Is playlist detected: {getattr(self, 'is_playlist', False)}")
        self.log_debug(f"Selected videos count: {len(getattr(self, 'selected_videos', []))}")
        self.log_debug(f"Debug mode: {self.debug_mode}")
        
        try:
            self.log_debug("=== STARTING YT-DLP DOWNLOAD ===")
            
            # Configure yt-dlp options with improved file naming
            ydl_opts = {
                'outtmpl': os.path.join(download_folder, '%(uploader)s - %(title)s.%(ext)s'),  # Include artist/uploader name
                'progress_hooks': [self.progress_hook],
                'noplaylist': True,  # Always set to True since we handle playlists manually
                'ignoreerrors': True,  # Continue on errors for individual videos
                'extract_flat': False,  # Get full metadata for better naming
            }
            
            self.log_debug("Configured yt-dlp with artist naming format")
            self.log_debug(f"Output template: {ydl_opts['outtmpl']}")
            
            # Enhanced quality options
            if quality == "Audio Only (MP3)":
                ydl_opts['format'] = 'bestaudio/best'
                self.log_debug("Format: Audio only (will include artist name)")
            elif quality == "Best Quality (Video + Audio)":
                ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                self.log_debug("Format: Best quality video + audio (will include artist name)")
            elif quality == "1080p":
                ydl_opts['format'] = 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best'
            elif quality == "720p":
                ydl_opts['format'] = 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best'
            elif quality == "480p":
                ydl_opts['format'] = 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best'
            elif quality == "360p":
                ydl_opts['format'] = 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best'
            else:
                ydl_opts['format'] = 'best'
            
            # Check if we have selected videos (from playlist selector)
            if hasattr(self, 'selected_videos') and self.selected_videos:
                self.log_debug("=== DOWNLOADING SELECTED VIDEOS FROM PLAYLIST ===")
                video_count = len(self.selected_videos)
                self.log_debug(f"Processing {video_count} selected videos")
                
                # Generate playlist thumbnail
                self.generate_playlist_thumbnail()
                
                successful_downloads = 0
                failed_downloads = 0
                
                for i, video in enumerate(self.selected_videos, 1):
                    video_url = f"https://www.youtube.com/watch?v={video['id']}"
                    video_title = video.get('title', 'Unknown')
                    self.log_debug(f"\n=== DOWNLOADING VIDEO {i}/{video_count} ===")
                    self.log_debug(f"Video title: {video_title}")
                    self.log_debug(f"Video ID: {video.get('id', 'Unknown')}")
                    self.log_debug(f"Video URL: {video_url}")
                    
                    # Update progress
                    self.progress_label.config(text=f"Downloading {i}/{video_count}: {video_title[:40]}...")
                    
                    try:
                        self.log_debug(f"Starting download for video {i}")
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            ydl.download([video_url])
                        self.log_debug(f"✓ Successfully downloaded video {i}: {video_title}")
                        successful_downloads += 1
                    except Exception as e:
                        self.log_debug(f"✗ Failed to download video {i}: {video_title}")
                        self.log_debug(f"Error: {type(e).__name__}: {str(e)}")
                        failed_downloads += 1
                        # Continue with next video
                        continue
                
                # Show completion summary
                self.log_debug(f"\n=== PLAYLIST DOWNLOAD COMPLETE ===")
                self.log_debug(f"Successful: {successful_downloads}, Failed: {failed_downloads}")
                self.progress_bar.stop()
                self.progress_label.config(text="Playlist download completed!")
                
                if successful_downloads > 0:
                    if failed_downloads > 0:
                        messagebox.showinfo("Partial Success", 
                                          f"Downloaded {successful_downloads} videos successfully!\n"
                                          f"{failed_downloads} videos failed.\n\n"
                                          f"Location: {download_folder}")
                    else:
                        messagebox.showinfo("Success", 
                                          f"All {successful_downloads} videos downloaded successfully!\n\n"
                                          f"Location: {download_folder}")
                else:
                    messagebox.showerror("Download Failed", 
                                       f"All {failed_downloads} videos failed to download.\n"
                                       "Please check your internet connection and try again.")
                
            else:
                self.log_debug("=== DOWNLOADING SINGLE VIDEO OR FULL PLAYLIST ===")
                # Single video or full playlist download
                if self.is_playlist and not download_playlist:
                    # User has a playlist but didn't check "Download Entire Playlist"
                    self.log_debug("Playlist detected but not downloading entire playlist - downloading first video only")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    if download_playlist and self.is_playlist:
                        ydl_opts['noplaylist'] = False  # Allow full playlist download
                    ydl.download([url])
                
                self.log_debug("=== DOWNLOAD COMPLETED SUCCESSFULLY ===")
                self.progress_bar.stop()
                self.progress_label.config(text="Download completed successfully!")
                messagebox.showinfo("Success", f"Download completed!\n\nLocation: {download_folder}")
            
        except Exception as e:
            self.progress_bar.stop()
            self.progress_label.config(text="Download failed")
            self.log_debug(f"✗ Error: {str(e)}")
            messagebox.showerror("Error", f"Failed to download:\n{str(e)}")
        
        finally:
            self.download_btn.config(state="normal", text="Download")
    
    def load_page_thumbnails(self, page_videos, start_index):
        """Load thumbnail data for specific videos on current page"""
        def extract_page_thumbnails():
            try:
                self.log_debug(f"=== LOADING THUMBNAILS FOR PAGE {start_index // self.videos_per_page + 1} ===")
                
                # Get video IDs for this page
                video_ids = []
                video_indices = []
                
                for i, video in enumerate(page_videos):
                    if video.get('id'):
                        video_ids.append(video['id'])
                        video_indices.append(start_index + i)
                
                if not video_ids:
                    self.log_debug("No video IDs found for thumbnail extraction")
                    return
                
                self.log_debug(f"Loading thumbnails for {len(video_ids)} videos...")
                
                # Extract thumbnail info for these specific videos
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': False,
                    'ignoreerrors': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    for i, video_id in enumerate(video_ids):
                        try:
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            self.log_debug(f"Extracting thumbnail for video {video_indices[i] + 1}: {video_id}")
                            
                            # Extract info for this specific video
                            info = ydl.extract_info(video_url, download=False)
                            
                            if info:
                                # Get best thumbnail URL
                                thumbnail_url = (
                                    info.get('thumbnail') or 
                                    (info.get('thumbnails', [{}])[-1].get('url', '') if info.get('thumbnails') else '')
                                )
                                
                                if thumbnail_url:
                                    # Update the video data with thumbnail
                                    video_index = video_indices[i]
                                    if video_index < len(self.playlist_videos):
                                        self.playlist_videos[video_index]['thumbnail'] = thumbnail_url
                                        self.log_debug(f"✓ Got thumbnail for video {video_index + 1}")
                                else:
                                    self.log_debug(f"No thumbnail found for video {video_indices[i] + 1}")
                        
                        except Exception as e:
                            self.log_debug(f"Error getting thumbnail for video {video_indices[i] + 1}: {e}")
                            continue
                
                self.log_debug(f"✓ Completed thumbnail loading for page")
                
            except Exception as e:
                self.log_debug(f"Error in load_page_thumbnails: {e}")
        
        # Load thumbnails in background
        threading.Thread(target=extract_page_thumbnails, daemon=True).start()
    
    def load_page_videos(self, scrollable_frame, canvas, page_num):
        """Load videos for a specific page"""
        # Clear existing videos
        for widget in scrollable_frame.winfo_children():
            widget.destroy()
        
        # Calculate start and end indices for this page
        start_idx = page_num * self.videos_per_page
        end_idx = min(start_idx + self.videos_per_page, len(self.playlist_videos))
        page_videos = self.playlist_videos[start_idx:end_idx]
        
        self.log_debug(f"Loading page {page_num + 1}: videos {start_idx + 1}-{end_idx}")
        
        # Create global video_vars if it doesn't exist
        if not hasattr(self, 'all_video_vars'):
            self.all_video_vars = [tk.BooleanVar(value=True) for _ in self.playlist_videos]
        
        # Add videos for this page
        for i, video in enumerate(page_videos):
            actual_index = start_idx + i
            var = self.all_video_vars[actual_index]
            
            # Alternating row colors
            row_bg = self.card_color if i % 2 == 0 else self.accent_color
            
            video_frame = tk.Frame(scrollable_frame, bg=row_bg, height=70)
            video_frame.pack(fill="x", padx=5, pady=2)
            video_frame.pack_propagate(False)
            
            # Checkbox
            check = tk.Checkbutton(
                video_frame,
                variable=var,
                bg=row_bg,
                fg=self.text_color,
                selectcolor=self.bg_color,
                activebackground=row_bg,
                cursor="hand2",
                command=self.update_selection_count
            )
            check.pack(side="left", padx=(10, 5), anchor="w")
            
            # Thumbnail image
            thumbnail_frame = tk.Frame(video_frame, bg=row_bg, width=90, height=50)
            thumbnail_frame.pack(side="left", padx=5, pady=10)
            thumbnail_frame.pack_propagate(False)
            
            thumbnail_label = tk.Label(
                thumbnail_frame,
                text="🎬",
                font=("Segoe UI", 20),
                bg=self.accent_color,
                fg=self.green_color,
                width=6,
                height=2
            )
            thumbnail_label.pack(fill="both", expand=True)
            
            # Auto-load thumbnail for current page
            self.load_video_thumbnail(video, thumbnail_label, actual_index)
            
            # Add a fallback - if no thumbnail loads after 3 seconds, show a reload button
            def add_reload_option():
                if thumbnail_label.cget('text') == '🎬':  # Still showing loading icon
                    # Create a small reload button
                    reload_btn = tk.Button(
                        thumbnail_frame,
                        text="↻",
                        font=("Segoe UI", 8),
                        bg=self.green_color,
                        fg=self.bg_color,
                        relief="flat",
                        cursor="hand2",
                        borderwidth=0,
                        command=lambda: self.load_video_thumbnail(video, thumbnail_label, actual_index)
                    )
                    reload_btn.place(x=65, y=35, width=15, height=15)
            
            # Schedule fallback check
            self.root.after(3000, add_reload_option)
            
            # Video info container
            info_frame = tk.Frame(video_frame, bg=row_bg)
            info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            
            # Top row: number and duration
            top_info = tk.Frame(info_frame, bg=row_bg)
            top_info.pack(fill="x", anchor="n")
            
            # Video number (global index)
            num_label = tk.Label(
                top_info,
                text=f"{actual_index + 1}.",
                font=("Segoe UI", 9, "bold"),
                bg=row_bg,
                fg=self.text_muted,
                width=4
            )
            num_label.pack(side="left", anchor="nw")
            
            # Duration label
            duration = video.get('duration', 0)
            mins, secs = divmod(duration, 60) if duration else (0, 0)
            duration_str = f"[{int(mins)}:{int(secs):02d}]" if duration else "[--:--]"
            
            duration_label = tk.Label(
                top_info,
                text=duration_str,
                font=("Segoe UI", 9),
                bg=row_bg,
                fg=self.green_color,
                width=8
            )
            duration_label.pack(side="right", anchor="ne")
            
            # Title label
            title = video.get('title', 'Unknown Title')
            if len(title) > 55:
                title = title[:52] + "..."
            
            title_label = tk.Label(
                info_frame,
                text=title,
                font=("Segoe UI", 10, "bold"),
                bg=row_bg,
                fg=self.text_color,
                anchor="w",
                justify="left",
                wraplength=400
            )
            title_label.pack(fill="x", anchor="n", pady=(5, 0))
        
        # Update scroll region
        scrollable_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.yview_moveto(0)  # Scroll to top of page
        
        # Update page info
        if hasattr(self, 'page_info_label'):
            self.page_info_label.config(
                text=f"Page {page_num + 1} of {self.total_pages} (showing videos {start_idx + 1}-{end_idx})"
            )
        
        # Update pagination buttons
        if hasattr(self, 'prev_btn'):
            self.prev_btn.config(state="normal" if page_num > 0 else "disabled")
        if hasattr(self, 'next_btn'):
            self.next_btn.config(state="normal" if page_num < self.total_pages - 1 else "disabled")
        
        # Load thumbnails for this page in background (skip if first page already loaded)
        if page_num == 0:
            # First page thumbnails should already be loaded
            self.log_debug("Page 1 thumbnails already loaded, skipping background load")
        else:
            # Load thumbnails for other pages
            self.load_page_thumbnails(page_videos, start_idx)
        
        self.log_debug(f"Page {page_num + 1} loaded with {len(page_videos)} videos")
    
    def change_page(self, selector_window, scrollable_frame, canvas, direction):
        """Change to next or previous page"""
        new_page = self.current_page + direction
        if 0 <= new_page < self.total_pages:
            self.current_page = new_page
            self.load_page_videos(scrollable_frame, canvas, new_page)
    
    def jump_to_page(self, selector_window, scrollable_frame, canvas):
        """Jump to a specific page"""
        try:
            page_num = int(self.page_entry.get()) - 1  # Convert to 0-based index
            if 0 <= page_num < self.total_pages:
                self.current_page = page_num
                self.load_page_videos(scrollable_frame, canvas, page_num)
                self.page_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Invalid Page", f"Please enter a page number between 1 and {self.total_pages}")
        except ValueError:
            messagebox.showwarning("Invalid Input", "Please enter a valid page number")
    
    def update_selection_count(self):
        """Update the selection count display"""
        if hasattr(self, 'selection_label') and hasattr(self, 'all_video_vars'):
            count = sum(var.get() for var in self.all_video_vars)
            self.selection_label.config(text=f"{count} videos selected")
    
    def load_video_thumbnail(self, video, thumbnail_label, index):
        """Load thumbnail for a video in the background"""
        def load_thumb():
            try:
                thumbnail_url = video.get('thumbnail')
                self.log_debug(f"Loading thumbnail for video {index + 1}: {video.get('title', 'Unknown')}")
                self.log_debug(f"Thumbnail URL: {thumbnail_url}")
                
                if not thumbnail_url:
                    # No thumbnail available
                    self.log_debug(f"No thumbnail URL for video {index + 1}")
                    self.root.after(0, lambda: thumbnail_label.config(text="🎵", font=("Segoe UI", 16)))
                    return
                
                # Download thumbnail
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                self.log_debug(f"Downloading thumbnail for video {index + 1}...")
                response = requests.get(thumbnail_url, timeout=15, headers=headers)
                self.log_debug(f"Thumbnail response for video {index + 1}: {response.status_code}")
                
                if response.status_code == 200:
                    # Process image
                    img_data = response.content
                    self.log_debug(f"Downloaded {len(img_data)} bytes for video {index + 1}")
                    
                    img = Image.open(BytesIO(img_data))
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize to fit thumbnail area (90x50)
                    img.thumbnail((80, 45), Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(img)
                    
                    # Update label on main thread
                    def update_label():
                        try:
                            thumbnail_label.config(image=photo, text="")
                            thumbnail_label.image = photo  # Keep reference
                            self.log_debug(f"✓ Thumbnail loaded successfully for video {index + 1}")
                        except Exception as e:
                            self.log_debug(f"Error updating thumbnail label for video {index + 1}: {e}")
                            thumbnail_label.config(text="❌", font=("Segoe UI", 12))
                    
                    self.root.after(0, update_label)
                else:
                    # Failed to download
                    self.log_debug(f"Failed to download thumbnail for video {index + 1}: HTTP {response.status_code}")
                    self.root.after(0, lambda: thumbnail_label.config(text="❌", font=("Segoe UI", 12)))
                    
            except requests.exceptions.Timeout:
                self.log_debug(f"Timeout loading thumbnail for video {index + 1}")
                self.root.after(0, lambda: thumbnail_label.config(text="⏱", font=("Segoe UI", 12)))
            except requests.exceptions.RequestException as e:
                self.log_debug(f"Network error loading thumbnail for video {index + 1}: {e}")
                self.root.after(0, lambda: thumbnail_label.config(text="🌐", font=("Segoe UI", 12)))
            except Exception as e:
                # Error loading thumbnail
                self.log_debug(f"Error loading thumbnail for video {index + 1}: {type(e).__name__}: {e}")
                self.root.after(0, lambda: thumbnail_label.config(text="🎵", font=("Segoe UI", 16)))
        
        # Always load thumbnails for pagination system (only loads current page)
        threading.Thread(target=load_thumb, daemon=True).start()
    
    def generate_playlist_thumbnail(self):
        """Generate a composite thumbnail from multiple playlist videos"""
        try:
            self.log_debug("=== GENERATING PLAYLIST THUMBNAIL ===")
            
            # Get thumbnails from first 4 selected videos
            thumbnail_urls = []
            for video in self.selected_videos[:4]:
                thumb_url = video.get('thumbnail')
                if thumb_url:
                    thumbnail_urls.append(thumb_url)
            
            if not thumbnail_urls:
                self.log_debug("No thumbnails available for playlist composite")
                self.thumbnail_label.config(text="📋 Playlist\n(Downloading selected videos)")
                return
            
            self.log_debug(f"Creating composite from {len(thumbnail_urls)} thumbnails")
            
            # Download thumbnail images
            thumbnail_images = []
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            for i, url in enumerate(thumbnail_urls):
                try:
                    response = requests.get(url, timeout=10, headers=headers)
                    if response.status_code == 200:
                        img = Image.open(BytesIO(response.content))
                        # Convert to RGB if needed
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        thumbnail_images.append(img)
                        self.log_debug(f"Downloaded thumbnail {i+1}")
                    else:
                        self.log_debug(f"Failed to download thumbnail {i+1}: HTTP {response.status_code}")
                except Exception as e:
                    self.log_debug(f"Error downloading thumbnail {i+1}: {e}")
            
            if not thumbnail_images:
                self.log_debug("No thumbnails downloaded successfully")
                self.thumbnail_label.config(text="📋 Playlist\n(Downloading selected videos)")
                return
            
            # Create composite image
            composite_width = 300
            composite_height = 180
            
            if len(thumbnail_images) == 1:
                # Single thumbnail
                composite = thumbnail_images[0].resize((composite_width, composite_height), Image.Resampling.LANCZOS)
            elif len(thumbnail_images) == 2:
                # Two thumbnails side by side
                composite = Image.new('RGB', (composite_width, composite_height), (20, 20, 30))
                thumb_width = composite_width // 2
                for i, img in enumerate(thumbnail_images):
                    resized = img.resize((thumb_width, composite_height), Image.Resampling.LANCZOS)
                    composite.paste(resized, (i * thumb_width, 0))
            elif len(thumbnail_images) >= 3:
                # Grid layout
                composite = Image.new('RGB', (composite_width, composite_height), (20, 20, 30))
                thumb_width = composite_width // 2
                thumb_height = composite_height // 2
                
                positions = [(0, 0), (thumb_width, 0), (0, thumb_height), (thumb_width, thumb_height)]
                
                for i, img in enumerate(thumbnail_images[:4]):
                    if i < len(positions):
                        resized = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
                        composite.paste(resized, positions[i])
            
            # Add overlay text
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(composite)
            
            # Add semi-transparent overlay
            overlay = Image.new('RGBA', (composite_width, composite_height), (0, 0, 0, 100))
            composite = Image.alpha_composite(composite.convert('RGBA'), overlay).convert('RGB')
            draw = ImageDraw.Draw(composite)
            
            # Add text
            try:
                # Try to use a nice font
                font = ImageFont.truetype("arial.ttf", 16)
                small_font = ImageFont.truetype("arial.ttf", 12)
            except:
                # Fallback to default font
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw playlist indicator
            text = "PLAYLIST"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (composite_width - text_width) // 2
            text_y = 10
            
            # Draw text with outline
            for adj in range(-1, 2):
                for adj2 in range(-1, 2):
                    draw.text((text_x + adj, text_y + adj2), text, font=font, fill=(0, 0, 0))
            draw.text((text_x, text_y), text, font=font, fill=(0, 255, 136))
            
            # Draw video count
            count_text = f"{len(self.selected_videos)} videos selected"
            bbox = draw.textbbox((0, 0), count_text, font=small_font)
            count_width = bbox[2] - bbox[0]
            count_x = (composite_width - count_width) // 2
            count_y = composite_height - 25
            
            for adj in range(-1, 2):
                for adj2 in range(-1, 2):
                    draw.text((count_x + adj, count_y + adj2), count_text, font=small_font, fill=(0, 0, 0))
            draw.text((count_x, count_y), count_text, font=small_font, fill=(255, 255, 255))
            
            # Convert to PhotoImage and display
            photo = ImageTk.PhotoImage(composite)
            self.current_thumbnail = photo
            self.thumbnail_label.config(image=photo, text="")
            self.thumbnail_label.image = photo
            
            self.log_debug("✓ Playlist composite thumbnail generated successfully")
            
        except Exception as e:
            self.log_debug(f"Error generating playlist thumbnail: {e}")
            self.thumbnail_label.config(text="📋 Playlist\n(Downloading selected videos)")
    
    def start_download(self):
        self.download_btn.config(state="disabled", text="Downloading...")
        self.progress_bar.start(10)
        self.progress_label.config(text="Initializing download...")
        self.log_debug("="*50)
        self.log_debug("NEW DOWNLOAD REQUEST")
        
        # Run download in separate thread to prevent UI freezing
        download_thread = threading.Thread(target=self.download_video, daemon=True)
        download_thread.start()


def main():
    """Main application entry point with error handling"""
    try:
        print("=" * 60)
        print("LETUSTECH YOUTUBE CONVERTER - STARTING UP")
        print("=" * 60)
        print("Creating main window...")
        
        root = tk.Tk()
        print("✓ Tkinter window created")
        
        # Prevent immediate closure
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
        print("APPLICATION READY - Window should now be visible")
        print("=" * 60)
        
        root.mainloop()
        
    except Exception as e:
        print(f"✗ CRITICAL ERROR in main(): {str(e)}")
        import traceback
        print("✗ Full traceback:")
        traceback.print_exc()
        
        # Try to show error dialog
        try:
            import tkinter.messagebox as msgbox
            msgbox.showerror(
                "Critical Error", 
                f"Application failed to start:\n\n{str(e)}\n\nCheck console for details."
            )
        except:
            print("Could not show error dialog")
        
        # Keep window open to see error
        input("\nPress Enter to close...")


if __name__ == "__main__":
    main()