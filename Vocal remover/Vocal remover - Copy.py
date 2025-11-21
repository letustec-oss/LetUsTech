#!/usr/bin/env python3
"""
LetUsTech Vocal Remover - Enhanced Version with Stop Button & Error Handling
- Auto-installs FFmpeg (FULL build) to C:\ffmpeg
- Auto-installs demucs and yt-dlp via pip if missing
- ⏹ STOP BUTTON: Cancel processing at any time
- 🌐 NETWORK ERROR DETECTION: Automatic connection checking
- ⏱️ TIMEOUT HANDLING: Prevents stuck downloads
- 📊 BETTER PROGRESS FEEDBACK: Real-time status updates
- 🧹 GRACEFUL CLEANUP: Proper cleanup on stop/error
- Runs demucs in CPU mode with better error handling
- Export options: WAV, MP3, FLAC, M4A (audio in mp4 container), OGG
- Optional MP4 video outputs (merge isolated audio into original video)

OPTIONAL: For better process management, install psutil:
    pip install psutil
    (The app works without it, but process termination is more reliable with it)
"""

import sys
import subprocess
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import shutil
from datetime import datetime
import urllib.request
import zipfile
import tempfile
import time
import webbrowser
import base64
import io
import re

# ----------------------------
# LetUsTech Icon (Base64 encoded .ico file)
# ----------------------------
# Icon removed for cleaner implementation


# ----------------------------
# Stop/Cancel and Error Handling Utilities
# ----------------------------
def kill_process_tree(pid):
    """Kill a process and all its children."""
    if not psutil:
        try:
            if sys.platform == 'win32':
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(pid)], check=False)
            else:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
        except:
            pass
        return
    
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        
        for child in children:
            try:
                child.kill()
            except:
                pass
        
        try:
            parent.kill()
        except:
            pass
            
        try:
            gone, alive = psutil.wait_procs(children + [parent], timeout=3)
        except:
            pass
            
    except (psutil.NoSuchProcess, AttributeError):
        pass
    except Exception as e:
        print(f"Error killing process tree: {e}")

def check_internet_connection():
    """Check if internet connection is available."""
    try:
        urllib.request.urlopen('https://www.google.com', timeout=5)
        return True
    except:
        return False

# Timeout settings (in seconds)
DOWNLOAD_TIMEOUT = 600  # 10 minutes for downloads
NETWORK_CHECK_TIMEOUT = 10  # 10 seconds for network checks

# ----------------------------
# Configuration (adjust if desired)
# ----------------------------
FFMPEG_INSTALL_DIR = Path("C:/ffmpeg")
FFMPEG_BIN = FFMPEG_INSTALL_DIR / "bin"
FFMPEG_DOWNLOAD_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.zip"
FFMPEG_ZIP_NAME = "ffmpeg-full.zip"

PIP_PACKAGES = ["torch", "torchaudio", "demucs", "yt-dlp"]

# Output formats mapping for ffmpeg encoders/extensions
OUTPUT_FORMATS = {
    "WAV (.wav)": {"ext": ".wav", "ffmpeg_args": ["-c:a", "pcm_s16le"]},
    "MP3 (.mp3)": {"ext": ".mp3", "ffmpeg_args": ["-c:a", "libmp3lame", "-q:a", "2"]},
    "FLAC (.flac)": {"ext": ".flac", "ffmpeg_args": ["-c:a", "flac"]},
    "M4A (audio .m4a / mp4 container)": {"ext": ".m4a", "ffmpeg_args": ["-c:a", "aac", "-b:a", "192k"]},
    "OGG (.ogg)": {"ext": ".ogg", "ffmpeg_args": ["-c:a", "libvorbis", "-q:a", "5"]},
    "MP4 (audio in mp4 container .mp4)": {"ext": ".mp4", "ffmpeg_args": ["-c:a", "aac", "-b:a", "192k"]},
}

# ----------------------------
# Utility helpers
# ----------------------------
def run_subprocess(cmd, timeout=None, capture=False):
    """Run a subprocess command. Return (returncode, stdout, stderr)."""
    try:
        if capture:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout, shell=False)
            return proc.returncode, proc.stdout, proc.stderr
        else:
            proc = subprocess.run(cmd, timeout=timeout, shell=False)
            return proc.returncode, None, None
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except FileNotFoundError as e:
        return -1, "", f"Not found: {e}"
    except Exception as e:
        return -1, "", str(e)

def ffmpeg_exists():
    try:
        rc, out, err = run_subprocess(["ffmpeg", "-version"], timeout=8, capture=True)
        return rc == 0 or ("ffmpeg version" in (out or err or ""))
    except Exception:
        return False

def add_ffmpeg_to_env():
    p = str(FFMPEG_BIN)
    os.environ["PATH"] = p + os.pathsep + os.environ.get("PATH", "")

def persist_ffmpeg_path():
    """Persist ffmpeg bin to user PATH using setx (Windows)."""
    try:
        if str(FFMPEG_BIN) not in os.environ.get("PATH", ""):
            # Use setx to append to user PATH. setx expands %PATH% in new shells.
            cmd = ['setx', 'PATH', f'{str(FFMPEG_BIN)};%PATH%']
            # running with shell=True to let setx parse %PATH% - but prefer subprocess.run
            subprocess.run(" ".join(cmd), shell=True)
    except Exception:
        pass

def download_with_progress(url, dest_path, gui_logger=None, chunk_size=1024*32):
    with urllib.request.urlopen(url, timeout=30) as resp:
        total = resp.getheader('Content-Length')
        total = int(total) if total and total.isdigit() else None
        with open(dest_path, "wb") as out:
            downloaded = 0
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                out.write(chunk)
                downloaded += len(chunk)
                if gui_logger:
                    if total:
                        pct = int(downloaded * 100 / total)
                        gui_logger(f"  Downloaded {downloaded}/{total} bytes ({pct}%)")
                    else:
                        gui_logger(f"  Downloaded {downloaded} bytes")
    return dest_path

def extract_ffmpeg_zip(zip_path, dest_dir, gui_logger=None):
    with zipfile.ZipFile(zip_path, 'r') as z:
        tmpdir = tempfile.mkdtemp()
        z.extractall(tmpdir)
        bin_candidate = None
        for root, dirs, files in os.walk(tmpdir):
            if 'ffmpeg.exe' in files:
                bin_candidate = Path(root)
                break
        if not bin_candidate:
            shutil.rmtree(tmpdir, ignore_errors=True)
            raise Exception("ffmpeg.exe not found inside archive")
        dest_bin = Path(dest_dir) / "bin"
        dest_bin.mkdir(parents=True, exist_ok=True)
        # move all files from candidate to dest_bin
        for item in bin_candidate.iterdir():
            target = dest_bin / item.name
            if item.is_file():
                shutil.move(str(item), str(target))
            else:
                if target.exists():
                    shutil.rmtree(target, ignore_errors=True)
                shutil.move(str(item), str(target))
        shutil.rmtree(tmpdir, ignore_errors=True)
        if gui_logger:
            gui_logger(f"Extracted ffmpeg to {dest_bin}")
        return dest_bin

def install_ffmpeg_if_missing(gui_logger=None, persist=True):
    """Download & install full ffmpeg build if not available."""
    if ffmpeg_exists():
        if gui_logger: gui_logger("✓ FFmpeg found")
        add_ffmpeg_to_env()
        return True
    if gui_logger: gui_logger("FFmpeg not found. Downloading FULL build (~180MB)...")
    FFMPEG_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    tmp_zip = FFMPEG_INSTALL_DIR / FFMPEG_ZIP_NAME
    try:
        download_with_progress(FFMPEG_DOWNLOAD_URL, tmp_zip, gui_logger=gui_logger)
        if gui_logger: gui_logger("Download complete. Extracting...")
        extract_ffmpeg_zip(tmp_zip, FFMPEG_INSTALL_DIR, gui_logger=gui_logger)
        try:
            tmp_zip.unlink()
        except Exception:
            pass
        add_ffmpeg_to_env()
        if persist:
            persist_ffmpeg_path()
        if gui_logger: gui_logger(f"✓ FFmpeg installed to {FFMPEG_INSTALL_DIR}")
        return True
    except Exception as e:
        if gui_logger:
            gui_logger(f"FFmpeg install failed: {e}")
        raise

def pip_install_packages(packages, gui_logger=None):
    """Install pip packages using the running interpreter. Returns True if success."""
    try:
        # Install packages one at a time for better progress tracking
        for package in packages:
            if gui_logger:
                gui_logger(f"Installing {package}... (this may take a few minutes)")
            
            cmd = [sys.executable, "-m", "pip", "install", "--break-system-packages", package]
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=600)
            
            if proc.returncode != 0:
                if gui_logger:
                    gui_logger(f"Failed to install {package}. Output:")
                    for line in (proc.stdout + proc.stderr).splitlines()[:30]:
                        gui_logger("  " + line)
                return False
            else:
                if gui_logger:
                    gui_logger(f"✓ {package} installed successfully")
        
        if gui_logger:
            gui_logger("✓ All Python packages installed")
        return True
    except Exception as e:
        if gui_logger:
            gui_logger(f"pip install exception: {e}")
        return False

def ffmpeg_probe(audio_path):
    """Return (ok:bool, msg:string) after probing file with ffmpeg."""
    try:
        cmd = ["ffmpeg", "-v", "error", "-i", str(audio_path), "-f", "null", "-"]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60)
        if proc.returncode == 0:
            return True, ""
        else:
            return False, (proc.stderr or proc.stdout or "ffmpeg probe failed")
    except Exception as e:
        return False, str(e)

def safe_remove(path):
    try:
        if Path(path).is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            Path(path).unlink(missing_ok=True)
    except Exception:
        pass

# ----------------------------
# GUI Application
# ----------------------------
class VocalRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LetUsTech - Vocal Remover")
        self.root.geometry("920x800")
        
        # Modern dark theme colors matching YouTube Converter
        self.bg_dark = '#0a1628'  # Dark navy background
        self.bg_medium = '#1a2332'  # Medium navy for panels
        self.bg_light = '#2a3545'  # Lighter navy for inputs
        self.accent_green = '#00ff88'  # Bright green accent
        self.text_white = '#ffffff'
        self.text_gray = '#8892a6'
        
        self.root.configure(bg=self.bg_dark)
        
        # Icon removed for cleaner look

        # Variables
        self.input_file = tk.StringVar()
        self.youtube_url = tk.StringVar()
        self.output_folder = tk.StringVar(value=str(Path.home() / "Music" / "Instrumentals"))
        self.processing = False
        self.selected_format = tk.StringVar(value="WAV (.wav)")
        self.create_video_output = tk.BooleanVar(value=True)
        self.auto_install_pip = tk.BooleanVar(value=True)
        self.persist_ffmpeg = tk.BooleanVar(value=True)
        self.demucs_model = tk.StringVar(value="htdemucs_ft (Best Quality)")
        self.enhance_separation = tk.BooleanVar(value=False)  # Enhanced vocal removal disabled
        self.debug_mode = tk.BooleanVar(value=False)  # Debug console visibility
        
        # Progress tracking
        self.current_progress = 0
        self.start_time = None
        self.total_steps = 0
        self.current_step = 0
        self.progress_label_var = tk.StringVar(value="Ready")
        
        # Stop/Cancel functionality
        self.should_stop = False
        self.current_process = None
        self.current_thread = None

        Path(self.output_folder.get()).mkdir(parents=True, exist_ok=True)
        self.create_menu()
        self.create_widgets()

    def cleanup_temp_icon(self, icon_path):
        """Clean up temporary icon file"""
        try:
            if icon_path.exists():
                icon_path.unlink()
        except Exception:
            pass

    def create_menu(self):
        """Create menu bar (currently empty - using buttons instead)"""
        # Menu bar removed - using top-right buttons (Settings, About, Help) instead
        pass

    def show_settings(self):
        """Show settings dialog with debug mode toggle"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x250")
        settings_window.configure(bg=self.bg_dark)
        settings_window.resizable(False, False)
        
        # Center window
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Main container
        container = tk.Frame(settings_window, bg=self.bg_dark, padx=30, pady=20)
        container.pack(fill='both', expand=True)
        
        # Title
        tk.Label(container, text="⚙ Settings", font=('Segoe UI', 18, 'bold'), 
                bg=self.bg_dark, fg=self.text_white).pack(pady=(0, 20))
        
        # Settings frame
        settings_frame = tk.Frame(container, bg=self.bg_medium, padx=20, pady=20)
        settings_frame.pack(fill='both', expand=True)
        
        # Debug mode checkbox
        tk.Label(settings_frame, text="Developer Options:", font=('Segoe UI', 11, 'bold'), 
                bg=self.bg_medium, fg=self.text_white).pack(anchor='w', pady=(0, 10))
        
        debug_check = tk.Checkbutton(settings_frame, 
                                     text="🐞 Show debug console (for troubleshooting)", 
                                     variable=self.debug_mode, 
                                     bg=self.bg_medium, fg=self.text_white, 
                                     selectcolor=self.bg_dark, font=('Segoe UI', 10),
                                     activebackground=self.bg_medium,
                                     command=self.toggle_debug_console)
        debug_check.pack(anchor='w', pady=5)
        
        tk.Label(settings_frame, 
                text="Enable this to see detailed processing logs\nand diagnostic information.",
                font=('Segoe UI', 9), bg=self.bg_medium, fg=self.text_gray,
                justify='left').pack(anchor='w', padx=(25, 0), pady=(0, 10))
        
        # Close button
        close_btn = tk.Button(container, text="Close", command=settings_window.destroy,
                            bg=self.accent_green, fg=self.bg_dark, font=('Segoe UI', 11, 'bold'),
                            cursor='hand2', padx=30, pady=8)
        close_btn.pack(pady=(15, 0))
    
    def toggle_debug_console(self):
        """Show or hide the debug console based on debug_mode"""
        if self.debug_mode.get():
            self.console_frame.pack(fill='both', expand=True, pady=(10, 0))
            self.progress_frame.config(text="  📊 Progress & Debug Console  ")
        else:
            self.console_frame.pack_forget()
            self.progress_frame.config(text="  📊 Progress  ")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """LetUsTech Vocal Remover - Quick Help

🎬 YouTube URL:
• Paste any YouTube video or playlist URL
• Click Download to process

📁 Local File:
• Click Browse to select audio/video file
• Supports MP3, MP4, WAV, M4A, FLAC, OGG

⚙️ Settings:
• Export Format: Choose output audio format
• Separation Quality: Best/Balanced/Fast
• Enhanced Vocal Removal: 10x processing for cleanest results (recommended!)

📂 Output Location:
• Choose where to save your instrumental tracks
• Files are saved with timestamp

⏱️ First Run:
• Downloads ~650MB of AI models (one-time)
• May take 5-15 minutes on first use

Need more help? Visit letustech.uk"""
        
        messagebox.showinfo("Help", help_text)
    
    def show_about(self):
        """Display About dialog with LetUsTech.uk information"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About LetUsTech")
        about_window.geometry("600x550")
        about_window.configure(bg='#001f3f')
        about_window.resizable(False, False)
        
        # Center the window
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Main container
        container = tk.Frame(about_window, bg='#001f3f', padx=30, pady=20)
        container.pack(fill='both', expand=True)
        
        # Logo/Header
        header_frame = tk.Frame(container, bg='#001f3f')
        header_frame.pack(pady=(0, 15))
        
        tk.Label(header_frame, text="🎵 LetUsTech", font=('Arial', 28, 'bold'), 
                bg='#001f3f', fg='#00ff00').pack()
        tk.Label(header_frame, text="Vocal Remover", font=('Arial', 16), 
                bg='#001f3f', fg='white').pack()
        tk.Label(header_frame, text="Wired For Your World", font=('Arial', 12, 'italic'), 
                bg='#001f3f', fg='#00ff00').pack(pady=(5, 0))
        
        # Separator
        separator = tk.Frame(container, height=2, bg='#00ff00')
        separator.pack(fill='x', pady=15)
        
        # Info section
        info_frame = tk.Frame(container, bg='#003366', padx=20, pady=20)
        info_frame.pack(fill='both', expand=True, pady=(0, 15))
        
        info_text = """LetUsTech is your gateway to free Python automation tools, 
browser-based games, and innovative technology solutions.

This Vocal Remover uses AI-powered audio separation to 
extract instrumentals and vocals from any audio or video file.

Features:
• YouTube video/audio downloading
• Multiple export formats (WAV, MP3, FLAC, M4A, OGG)
• Video output with isolated audio tracks
• High-quality AI separation models
• Automatic dependency installation

Created with ❤️ by the LetUsTech community"""
        
        tk.Label(info_frame, text=info_text, font=('Arial', 10), 
                bg='#003366', fg='white', justify='left').pack(anchor='w')
        
        # Links section
        links_frame = tk.Frame(container, bg='#001f3f')
        links_frame.pack(fill='x', pady=(0, 10))
        
        def create_link_button(parent, text, url):
            btn = tk.Button(parent, text=text, font=('Arial', 10, 'underline'), 
                          bg='#001f3f', fg='#00ff00', bd=0, cursor='hand2',
                          activebackground='#001f3f', activeforeground='#00cc00')
            btn.config(command=lambda: webbrowser.open(url))
            return btn
        
        tk.Label(links_frame, text="Connect with us:", font=('Arial', 11, 'bold'), 
                bg='#001f3f', fg='white').pack(anchor='w', pady=(0, 8))
        
        link_container = tk.Frame(links_frame, bg='#001f3f')
        link_container.pack(anchor='w')
        
        create_link_button(link_container, "🌐 Website: letustech.uk", 
                          "https://letustech.uk").pack(anchor='w', pady=2)
        create_link_button(link_container, "💻 GitHub: github.com/LetUsTech", 
                          "https://github.com/LetUsTech").pack(anchor='w', pady=2)
        create_link_button(link_container, "💬 Discord Community", 
                          "https://discord.gg/letustech").pack(anchor='w', pady=2)
        
        # Close button
        close_btn = tk.Button(container, text="Close", command=about_window.destroy,
                            bg='#00ff00', fg='#001f3f', font=('Arial', 11, 'bold'),
                            cursor='hand2', padx=30, pady=8)
        close_btn.pack(pady=(10, 0))
        
        # Footer
        tk.Label(container, text="© 2024 LetUsTech | Free Tools & Games", 
                font=('Arial', 8), bg='#001f3f', fg='#00cc00').pack(pady=(10, 0))

    def create_widgets(self):
        # Top header bar with text logo (simpler, no image dependency issues)
        header_frame = tk.Frame(self.root, bg=self.bg_dark, height=100)
        header_frame.pack(fill='x', pady=(0, 0))
        header_frame.pack_propagate(False)
        
        # Logo and title section
        title_section = tk.Frame(header_frame, bg=self.bg_dark)
        title_section.pack(side='left', padx=30, pady=20)
        
        # Text-based logo with coding icon
        logo_frame = tk.Frame(title_section, bg=self.bg_dark)
        logo_frame.pack(side='left', padx=(0, 15))
        tk.Label(logo_frame, text="</>\n🎵", font=('Courier New', 20, 'bold'), 
                bg=self.bg_dark, fg=self.accent_green, justify='center').pack()
        
        # Title text
        title_text_frame = tk.Frame(title_section, bg=self.bg_dark)
        title_text_frame.pack(side='left')
        tk.Label(title_text_frame, text="LetUsTech Vocal Remover", font=('Segoe UI', 20, 'bold'), 
                bg=self.bg_dark, fg=self.text_white).pack(anchor='w')
        tk.Label(title_text_frame, text="Fast, easy vocal separation powered by AI", 
                font=('Segoe UI', 10), bg=self.bg_dark, fg=self.text_gray).pack(anchor='w')
        
        # Top right buttons
        top_buttons = tk.Frame(header_frame, bg=self.bg_dark)
        top_buttons.pack(side='right', padx=30, pady=20)
        
        btn_style = {'bg': self.bg_medium, 'fg': self.text_white, 'font': ('Segoe UI', 10), 
                    'bd': 0, 'padx': 15, 'pady': 8, 'cursor': 'hand2', 'activebackground': self.bg_light}
        
        tk.Button(top_buttons, text="⚙ Settings", command=self.show_settings, **btn_style).pack(side='left', padx=5)
        tk.Button(top_buttons, text="ℹ About", command=self.show_about, **btn_style).pack(side='left', padx=5)
        tk.Button(top_buttons, text="? Help", command=self.show_help, **btn_style).pack(side='left', padx=5)

        # Main content area
        main_frame = tk.Frame(self.root, bg=self.bg_dark)
        main_frame.pack(padx=30, pady=20, fill='both', expand=True)

        # Input method section with modern styling
        method_frame = tk.LabelFrame(main_frame, text="  🎬 Video URL  ", font=('Segoe UI', 12, 'bold'), 
                                    bg=self.bg_medium, fg=self.text_white, bd=0, padx=20, pady=20)
        method_frame.pack(fill='x', pady=(0, 15))

        # URL input row
        url_label = tk.Label(method_frame, text="Paste any YouTube video or playlist URL", 
                            font=('Segoe UI', 9), bg=self.bg_medium, fg=self.text_gray)
        url_label.pack(anchor='w', pady=(0, 8))
        
        url_input_frame = tk.Frame(method_frame, bg=self.bg_medium)
        url_input_frame.pack(fill='x', pady=(0, 10))
        
        url_entry = tk.Entry(url_input_frame, textvariable=self.youtube_url, font=('Segoe UI', 11), 
                            bg=self.bg_light, fg=self.text_white, insertbackground=self.text_white,
                            bd=0, relief='flat')
        url_entry.pack(side='left', fill='x', expand=True, ipady=8, padx=(0, 10))
        
        tk.Button(url_input_frame, text="Paste", command=self.paste_url, bg=self.accent_green, 
                 fg=self.bg_dark, font=('Segoe UI', 10, 'bold'), cursor='hand2', bd=0, 
                 padx=20, pady=8).pack(side='left', padx=(0,5))
        tk.Button(url_input_frame, text="Clear", command=self.clear_url, bg='#ff4757', 
                 fg='white', font=('Segoe UI', 10, 'bold'), cursor='hand2', bd=0, 
                 padx=20, pady=8).pack(side='left')

        # OR divider
        tk.Label(method_frame, text="─── OR ───", font=('Segoe UI', 10, 'bold'), 
                bg=self.bg_medium, fg=self.text_gray).pack(pady=15)

        # Local file section
        file_label = tk.Label(method_frame, text="Local File (MP3, MP4, WAV, M4A, FLAC, OGG)", 
                             font=('Segoe UI', 9), bg=self.bg_medium, fg=self.text_gray)
        file_label.pack(anchor='w', pady=(0, 8))
        
        file_input_frame = tk.Frame(method_frame, bg=self.bg_medium)
        file_input_frame.pack(fill='x')
        
        tk.Entry(file_input_frame, textvariable=self.input_file, font=('Segoe UI', 11), 
                bg=self.bg_light, fg=self.text_white, insertbackground=self.text_white,
                bd=0, relief='flat').pack(side='left', fill='x', expand=True, ipady=8, padx=(0,10))
        tk.Button(file_input_frame, text="Browse", command=self.browse_file, bg=self.accent_green, 
                 fg=self.bg_dark, font=('Segoe UI', 10, 'bold'), cursor='hand2', bd=0, 
                 padx=20, pady=8).pack(side='left')

        # Output settings with modern styling
        output_frame = tk.LabelFrame(main_frame, text="  ⚙ Quality / Format  ", font=('Segoe UI', 12, 'bold'), 
                                    bg=self.bg_medium, fg=self.text_white, bd=0, padx=20, pady=20)
        output_frame.pack(fill='x', pady=(0, 15))
        
        # First row: Format and Model dropdowns
        settings_row1 = tk.Frame(output_frame, bg=self.bg_medium)
        settings_row1.pack(fill='x', pady=(0, 15))
        
        # Export format
        format_col = tk.Frame(settings_row1, bg=self.bg_medium)
        format_col.pack(side='left', fill='x', expand=True, padx=(0, 10))
        tk.Label(format_col, text="Export Format:", font=('Segoe UI', 9), 
                bg=self.bg_medium, fg=self.text_gray).pack(anchor='w', pady=(0, 5))
        format_menu = ttk.Combobox(format_col, textvariable=self.selected_format, 
                                   values=list(OUTPUT_FORMATS.keys()), state='readonly', 
                                   font=('Segoe UI', 10))
        format_menu.pack(fill='x', ipady=5)
        
        # Separation quality
        model_col = tk.Frame(settings_row1, bg=self.bg_medium)
        model_col.pack(side='left', fill='x', expand=True)
        tk.Label(model_col, text="Separation Quality:", font=('Segoe UI', 9), 
                bg=self.bg_medium, fg=self.text_gray).pack(anchor='w', pady=(0, 5))
        model_options = ["htdemucs_ft (Best Quality)", "htdemucs (Balanced)", "htdemucs_6s (Fast)"]
        model_menu = ttk.Combobox(model_col, textvariable=self.demucs_model, 
                                  values=model_options, state='readonly', 
                                  font=('Segoe UI', 10))
        model_menu.pack(fill='x', ipady=5)
        
        # Download location
        location_label = tk.Label(output_frame, text="Download Location:", 
                                 font=('Segoe UI', 9), bg=self.bg_medium, fg=self.text_gray)
        location_label.pack(anchor='w', pady=(0, 5))
        
        location_frame = tk.Frame(output_frame, bg=self.bg_medium)
        location_frame.pack(fill='x', pady=(0, 15))
        tk.Entry(location_frame, textvariable=self.output_folder, font=('Segoe UI', 10), 
                bg=self.bg_light, fg=self.text_white, insertbackground=self.text_white,
                bd=0, relief='flat').pack(side='left', fill='x', expand=True, ipady=8, padx=(0,10))
        tk.Button(location_frame, text="Browse", command=self.browse_output_folder, 
                 bg=self.accent_green, fg=self.bg_dark, font=('Segoe UI', 10, 'bold'), 
                 cursor='hand2', bd=0, padx=20, pady=8).pack(side='left')
        
        # Checkboxes with modern styling
        checkbox_frame = tk.Frame(output_frame, bg=self.bg_medium)
        checkbox_frame.pack(fill='x')
        
        tk.Checkbutton(checkbox_frame, text="Create MP4 video outputs", 
                      variable=self.create_video_output, bg=self.bg_medium, fg=self.text_white, 
                      selectcolor=self.bg_dark, font=('Segoe UI', 9), activebackground=self.bg_medium).pack(anchor='w', pady=3)
        tk.Checkbutton(checkbox_frame, text="Auto-install dependencies", 
                      variable=self.auto_install_pip, bg=self.bg_medium, fg=self.text_white, 
                      selectcolor=self.bg_dark, font=('Segoe UI', 9), activebackground=self.bg_medium).pack(anchor='w', pady=3)

        # Button container for process and stop buttons
        button_frame = tk.Frame(main_frame, bg=self.bg_medium)
        button_frame.pack(pady=(0, 15), fill='x')
        
        # Large process button with modern green styling
        self.process_btn = tk.Button(button_frame, text="⬇ Download", command=self.start_processing, 
                                     bg=self.accent_green, fg=self.bg_dark, 
                                     font=('Segoe UI', 14, 'bold'), cursor='hand2', bd=0, 
                                     pady=15, activebackground='#00dd77')
        self.process_btn.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # Stop button (initially disabled)
        self.stop_btn = tk.Button(button_frame, text="⏹ Stop", command=self.stop_processing,
                                  bg='#ff4444', fg=self.text_white,
                                  font=('Segoe UI', 14, 'bold'), cursor='hand2', bd=0,
                                  pady=15, activebackground='#cc0000', state='disabled')
        self.stop_btn.pack(side='left', padx=(5, 0))

        # Progress section with modern styling
        self.progress_frame = tk.LabelFrame(main_frame, text="  📊 Progress  ", font=('Segoe UI', 11, 'bold'), 
                                      bg=self.bg_medium, fg=self.text_white, bd=0, padx=20, pady=15)
        self.progress_frame.pack(fill='both', expand=True)

        # Progress label for status and ETA
        self.progress_label = tk.Label(self.progress_frame, textvariable=self.progress_label_var,
                                      font=('Segoe UI', 10, 'bold'), bg=self.bg_medium, fg=self.accent_green)
        self.progress_label.pack(pady=(0, 5), anchor='w')

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate', length=520, maximum=100)
        self.progress_bar.pack(pady=(0, 10), fill='x')

        # Console text area with dark styling (hidden by default)
        self.console_frame = tk.Frame(self.progress_frame, bg=self.bg_dark, bd=0)
        # Don't pack it yet - only show when debug mode is enabled
        
        tk.Label(self.console_frame, text="Debug Console:", font=('Segoe UI', 9, 'bold'),
                bg=self.bg_dark, fg=self.text_gray).pack(anchor='w', pady=(5, 5))
        
        console_text_frame = tk.Frame(self.console_frame, bg=self.bg_dark, bd=0)
        console_text_frame.pack(fill='both', expand=True)
        
        self.status_text = tk.Text(console_text_frame, height=10, font=('Consolas', 8), 
                                   bg=self.bg_dark, fg=self.accent_green, wrap='word', 
                                   bd=0, padx=10, pady=10, insertbackground=self.accent_green)
        self.status_text.pack(side='left', fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(console_text_frame, command=self.status_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        # Enable mouse wheel scrolling for debug console
        def on_mousewheel(event):
            self.status_text.yview_scroll(int(-1*(event.delta/120)), "units")
        
        # Bind mouse wheel to text widget and its parent frame
        self.status_text.bind("<MouseWheel>", on_mousewheel)
        console_text_frame.bind("<MouseWheel>", on_mousewheel)
        self.console_frame.bind("<MouseWheel>", on_mousewheel)

        # No bottom tip needed anymore

    def log_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert('end', f"[{timestamp}] {message}\n")
        self.status_text.see('end')
        self.root.update()

    def check_should_stop(self):
        """Check if processing should stop."""
        return self.should_stop
    
    def stop_processing(self):
        """Stop the current processing."""
        if not self.processing:
            return
        
        response = messagebox.askyesno(
            "Stop Processing",
            "Are you sure you want to stop the current process?\n\n"
            "Any progress will be lost."
        )
        
        if response:
            self.should_stop = True
            self.log_status("\n" + "=" * 60)
            self.log_status("⏹ STOP REQUESTED - Cancelling process...")
            self.log_status("=" * 60)
            self.root.after(0, lambda: self.progress_label_var.set("Stopping..."))
            self.root.after(0, lambda: self.progress_bar.config(value=0))
            
            # Kill current process if exists
            if self.current_process:
                try:
                    kill_process_tree(self.current_process.pid)
                    self.log_status("✓ Process terminated")
                except Exception as e:
                    self.log_status(f"⚠ Error terminating process: {e}")

    def update_progress(self, step_name, step_number=None):
        """Update progress bar and show estimated time remaining"""
        try:
            if self.debug_mode.get():
                print(f"DEBUG: update_progress called - {step_name}, step: {step_number}")  # Debug
            if step_number is not None:
                self.current_step = step_number
            else:
                self.current_step += 1
            
            if self.total_steps > 0:
                progress_pct = int((self.current_step / self.total_steps) * 100)
                if self.debug_mode.get():
                    print(f"DEBUG: Setting progress to {progress_pct}%")  # Debug
                # Use config() instead of dictionary access for ttk widgets
                self.progress_bar.config(value=progress_pct)
                
                # Calculate estimated time remaining
                if self.start_time:
                    elapsed = time.time() - self.start_time
                    if self.current_step > 0:
                        avg_time_per_step = elapsed / self.current_step
                        remaining_steps = self.total_steps - self.current_step
                        eta_seconds = avg_time_per_step * remaining_steps
                        
                        # Format time nicely
                        if eta_seconds < 60:
                            eta_str = f"{int(eta_seconds)}s"
                        elif eta_seconds < 3600:
                            minutes = int(eta_seconds / 60)
                            seconds = int(eta_seconds % 60)
                            eta_str = f"{minutes}m {seconds}s"
                        else:
                            hours = int(eta_seconds / 3600)
                            minutes = int((eta_seconds % 3600) / 60)
                            eta_str = f"{hours}h {minutes}m"
                        
                        status_text = f"{step_name} - {progress_pct}% (ETA: {eta_str})"
                    else:
                        status_text = f"{step_name} - {progress_pct}%"
                else:
                    status_text = f"{step_name} - {progress_pct}%"
            else:
                status_text = step_name
            
            if self.debug_mode.get():
                print(f"DEBUG: Setting status text: {status_text}")  # Debug
            self.progress_label_var.set(status_text)
            self.root.update()
            if self.debug_mode.get():
                print("DEBUG: update_progress complete")  # Debug
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Exception in update_progress: {e}")  # Debug
                import traceback
                traceback.print_exc()

    def start_demucs_animation(self):
        """Animate the progress label during long demucs processing"""
        animation_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.animation_index = 0
        
        def animate():
            if hasattr(self, 'demucs_animation_active') and self.demucs_animation_active:
                char = animation_chars[self.animation_index % len(animation_chars)]
                self.animation_index += 1
                
                # Get current progress info
                current_text = self.progress_label_var.get()
                if "AI vocal separation" in current_text:
                    # Add spinner to the text
                    base_text = current_text.split(" ")[0:5]  # Get first parts
                    base_text = " ".join(base_text)
                    if "%" in current_text:
                        pct_part = current_text.split("-")[1] if "-" in current_text else ""
                        self.progress_label_var.set(f"{char} {base_text} - {pct_part}")
                    else:
                        self.progress_label_var.set(f"{char} {base_text}")
                
                # Schedule next animation frame
                self.root.after(100, animate)
        
        animate()

    def browse_file(self):
        filename = filedialog.askopenfilename(title="Select Audio/Video File", filetypes=[("Media Files", "*.mp3 *.mp4 *.wav *.m4a *.flac *.ogg *.webm *.mov"), ("All Files", "*.*")])
        if filename:
            self.input_file.set(filename)
            self.youtube_url.set("")

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)

    def paste_url(self):
        """Paste URL from clipboard into YouTube URL field"""
        try:
            clipboard_content = self.root.clipboard_get()
            self.youtube_url.set(clipboard_content.strip())
            self.input_file.set("")  # Clear local file when pasting URL
            self.log_status("✓ URL pasted from clipboard")
        except Exception as e:
            messagebox.showwarning("Paste Error", "Could not paste from clipboard. Please ensure you have copied a URL.")

    def clear_url(self):
        """Clear the YouTube URL field"""
        self.youtube_url.set("")
        self.log_status("YouTube URL cleared")

    # ----------------------------
    # Download & validation
    # ----------------------------
    def download_youtube(self, url):
        """Downloads audio or full video depending on 'create_video_output' flag."""
        try:
            # Check internet connection first
            self.log_status("Checking internet connection...")
            if not check_internet_connection():
                raise Exception("No internet connection detected. Please check your network and try again.")
            self.log_status("✓ Internet connection OK")
            
            # Check if stop was requested
            if self.check_should_stop():
                raise InterruptedError("Download stopped by user")
            
            self.log_status("📥 Starting YouTube download with yt-dlp...")
            # Ensure yt-dlp present
            if self.auto_install_pip.get():
                pip_install_packages(PIP_PACKAGES, gui_logger=self.log_status)
            # check yt-dlp on PATH
            rc, out, err = run_subprocess(["yt-dlp", "--version"], timeout=10, capture=True)
            if rc != 0:
                raise Exception("yt-dlp is not available. Try installing with: pip install yt-dlp")
            self.log_status("✓ yt-dlp available")

            temp_dir = Path(self.output_folder.get()) / "temp_download"
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            temp_dir.mkdir(parents=True, exist_ok=True)
            self.log_status(f"Temp download dir: {temp_dir}")

            # If we want video outputs and source is from YouTube, download bestvideo+bestaudio; else download audio only
            if self.create_video_output.get():
                # download best video+audio into a single .mp4 (mux) if possible
                outtmpl = str(temp_dir / "%(title)s.%(ext)s")
                cmd = [
                    "yt-dlp",
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
                    "-o", outtmpl,
                    url
                ]
            else:
                # audio-only extraction to mp3 (demucs accepts mp3/m4a/wav)
                cmd = [
                    "yt-dlp",
                    "-x", "--audio-format", "mp3", "--audio-quality", "0",
                    "-o", str(temp_dir / "%(title)s.%(ext)s"),
                    url
                ]

            self.log_status("Running yt-dlp...")
            
            # Run with Popen so we can track the process
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.current_process = proc
            
            # Wait for completion with periodic stop checks
            start_time = time.time()
            while proc.poll() is None:
                if self.check_should_stop():
                    kill_process_tree(proc.pid)
                    raise InterruptedError("Download stopped by user")
                
                # Check for timeout (15 minutes)
                if time.time() - start_time > 900:
                    kill_process_tree(proc.pid)
                    raise Exception("Download timeout after 15 minutes")
                
                time.sleep(1)
            
            stdout, stderr = proc.communicate()
            self.current_process = None
            
            # Log relevant lines
            if stdout:
                for line in stdout.splitlines():
                    if any(k in line for k in ("Destination:", "Downloading", "Merged", "has already been downloaded")):
                        self.log_status("  " + line.strip())
            if proc.returncode != 0:
                combined = (stderr or stdout or "")[:2000]
                # Check if it's a network error
                if any(err in combined.lower() for err in ["network", "connection", "timeout", "unable to download"]):
                    raise Exception(f"Network error during download: {combined}")
                raise Exception(f"yt-dlp failed: {combined}")

            # find downloaded file
            files = list(temp_dir.glob("*"))
            if not files:
                raise Exception("No files were downloaded by yt-dlp")

            # pick the largest file (likely our desired)
            chosen = sorted(files, key=lambda p: p.stat().st_size if p.exists() else 0, reverse=True)[0]
            self.log_status(f"✓ Downloaded: {chosen.name} ({chosen.stat().st_size} bytes)")
            
            # Sanitize filename to avoid issues with special characters
            safe_name = re.sub(r'[^\w\s\-_\.]', '_', chosen.stem) + chosen.suffix
            safe_name = re.sub(r'[\s]+', '_', safe_name)  # Replace spaces with underscores
            safe_path = chosen.parent / safe_name
            
            # Rename if needed
            if str(chosen) != str(safe_path):
                try:
                    chosen.rename(safe_path)
                    self.log_status(f"Renamed to: {safe_name}")
                    chosen = safe_path
                except Exception as e:
                    self.log_status(f"Warning: Could not rename file: {e}")
                    # Continue with original name

            # validate with ffmpeg probe
            ok, msg = ffmpeg_probe(chosen)
            if not ok:
                raise Exception(f"Downloaded file is invalid (ffmpeg): {msg}")

            return str(chosen)
        except Exception as e:
            raise

    # ----------------------------
    # Processing (Demucs) & outputs
    # ----------------------------
    def process_audio_with_demucs(self, input_path):
        """Run demucs in CPU mode and return tuple(paths): (vocals_path, instrumental_path) absolute paths to audio outputs"""
        try:
            # Ensure ffmpeg present
            install_ffmpeg_if_missing(gui_logger=self.log_status, persist=self.persist_ffmpeg.get())

            # Auto-install demucs if requested
            if self.auto_install_pip.get():
                pip_install_packages(PIP_PACKAGES, gui_logger=self.log_status)
            
            # Verify torch and torchaudio are available
            try:
                import torch
                import torchaudio
                self.log_status(f"✓ PyTorch {torch.__version__} available")
                self.log_status(f"✓ Torchaudio {torchaudio.__version__} available")
            except ImportError as e:
                raise Exception(f"Required dependency missing: {e}. Please enable 'Auto-install' or manually install: pip install torch torchaudio demucs")

            # Check demucs availability
            rc, out, err = run_subprocess(["demucs", "--help"], timeout=20, capture=True)
            if rc != 0 and "usage:" not in (out or err or "").lower():
                self.log_status("Warning: demucs check returned nonzero; will attempt to run demucs anyway")

            # Validate input file exists and is readable
            input_file = Path(input_path)
            if not input_file.exists():
                raise Exception(f"Input file not found: {input_path}")
            if input_file.stat().st_size == 0:
                raise Exception(f"Input file is empty: {input_path}")
            
            self.log_status(f"Input file size: {input_file.stat().st_size / (1024*1024):.2f} MB")
            
            # If filename has problematic characters, copy to a safe name
            safe_stem = re.sub(r'[^\w\s\-_]', '_', input_file.stem)
            safe_stem = re.sub(r'[\s]+', '_', safe_stem)
            safe_name = safe_stem + input_file.suffix
            
            if safe_name != input_file.name:
                self.log_status(f"Filename has special characters, creating safe copy...")
                safe_input_path = input_file.parent / safe_name
                try:
                    shutil.copy2(input_file, safe_input_path)
                    input_path = str(safe_input_path)
                    input_file = safe_input_path
                    self.log_status(f"Using safe filename: {safe_name}")
                except Exception as e:
                    self.log_status(f"Warning: Could not create safe copy: {e}")
                    self.log_status("Proceeding with original filename...")

            temp_output = Path(self.output_folder.get()) / "temp_demucs"
            if temp_output.exists():
                shutil.rmtree(temp_output, ignore_errors=True)
            temp_output.mkdir(parents=True, exist_ok=True)

            # Map model selection to demucs model names
            model_mapping = {
                "htdemucs_ft (Best Quality)": "htdemucs_ft",
                "htdemucs (Balanced)": "htdemucs",
                "htdemucs_6s (Fast)": "htdemucs_6s"
            }
            selected_model = model_mapping.get(self.demucs_model.get(), "htdemucs_ft")
            
            self.log_status(f"Using model: {selected_model}")
            
            # Use selected model with explicit specification
            # Fine-tuned models have much better vocal isolation with less bleed
            cmd = [
                "demucs",
                "--two-stems=vocals",
                "-n", selected_model,
                "--device", "cpu",
                "--float32",  # Use float32 precision (avoids some codec issues)
                "--mp3",  # Output as MP3 instead of WAV (better compatibility)
                "--mp3-bitrate", "320",  # Highest quality MP3
            ]
            
            # Add enhanced separation parameters if enabled
            if self.enhance_separation.get():
                self.log_status("Enhanced vocal removal enabled - using advanced parameters")
                cmd.extend([
                    "--clip-mode", "rescale",  # Better handling of clipping
                    "--shifts", "10",  # More random shifts for better quality (default is 1)
                ])
            
            cmd.extend([
                "-o", str(temp_output),
                str(input_path)  # Ensure string path
            ])
            
            self.log_status("Running Demucs (CPU mode, htdemucs model). This may take several minutes...")
            if self.enhance_separation.get():
                self.log_status("Note: Enhanced mode uses 10 random shifts - this takes longer but produces cleaner results")
            self.log_status(f"Command: {' '.join(cmd)}")
            self.log_status("\n⏳ AI Processing in progress... (This is the longest step)")
            self.log_status("💡 Progress updates every 30 seconds. Please be patient!\n")
            
            # Set UTF-8 encoding environment variables to prevent Unicode errors on Windows
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            
            # Capture both stdout and stderr separately for better error diagnosis
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True, 
                bufsize=1,
                env=env,
                encoding='utf-8',
                errors='replace',  # Replace problematic characters instead of crashing
                universal_newlines=True
            )
            
            stdout_lines = []
            stderr_lines = []
            
            # Read output in real-time with progress updates
            import select
            import sys
            last_update = time.time()
            
            # Helper to read from stderr in real-time
            def read_stderr_realtime():
                """Read stderr line by line and update progress"""
                nonlocal last_update
                for line in iter(process.stderr.readline, ''):
                    if not line:
                        break
                    line = line.strip()
                    if line:
                        stderr_lines.append(line)
                        self.log_status("  " + line)
                        
                        # Update progress label periodically
                        current_time = time.time()
                        if current_time - last_update > 30:  # Every 30 seconds
                            self.log_status("⏳ Still processing... (AI separation takes time)")
                            last_update = current_time
                            # Force UI update
                            self.root.update()
            
            # Read stderr in a separate thread
            import threading
            stderr_thread = threading.Thread(target=read_stderr_realtime, daemon=True)
            stderr_thread.start()
            
            # Wait for process to complete while periodically updating UI
            demucs_start_time = time.time()
            demucs_check_count = 0
            
            while process.poll() is None:
                time.sleep(2)  # Check every 2 seconds
                self.root.update()  # Keep UI responsive
                demucs_check_count += 1
                
                # Simulate sub-progress within the Demucs step (50% to 83%)
                # This gives visual feedback that processing is happening
                if demucs_check_count % 15 == 0:  # Every 30 seconds (15 checks * 2 seconds)
                    # Increment progress slightly to show activity
                    elapsed_demucs = time.time() - demucs_start_time
                    # Estimate we're moving through the demucs step
                    # Assume demucs takes 5-15 minutes, update proportionally
                    estimated_demucs_time = 600  # 10 minutes estimate
                    demucs_progress = min(elapsed_demucs / estimated_demucs_time, 0.95)  # Max 95% of step
                    
                    # Map to the 50-83% range (33% of total progress)
                    base_progress = 0.50  # 50%
                    demucs_range = 0.33   # 33% (from 50% to 83%)
                    new_progress = base_progress + (demucs_progress * demucs_range)
                    
                    # Update progress bar to show sub-progress
                    new_step = int(new_progress * self.total_steps)
                    if new_step > self.current_step and new_step < self.total_steps:
                        self.current_step = new_step
                        progress_pct = int((self.current_step / self.total_steps) * 100)
                        self.progress_bar.config(value=progress_pct)
                
                # Periodic status update
                current_time = time.time()
                if current_time - last_update > 30:
                    elapsed = int(current_time - self.start_time)
                    self.log_status(f"⏳ Still processing... ({elapsed}s elapsed)")
                    last_update = current_time
            
            # Wait for stderr thread to finish
            stderr_thread.join(timeout=5)
            
            # Read any remaining stdout
            stdout_data = process.stdout.read()
            if stdout_data:
                for line in stdout_data.splitlines():
                    if line.strip():
                        self.log_status("  " + line.strip())
                        stdout_lines.append(line)
            
            if process.returncode != 0:
                error_details = f"Demucs failed with code {process.returncode}\n"
                error_details += "\n\nLast stdout lines:\n" + "\n".join(stdout_lines[-10:]) if stdout_lines else ""
                error_details += "\n\nLast stderr lines:\n" + "\n".join(stderr_lines[-10:]) if stderr_lines else ""
                raise Exception(error_details)

            # find outputs (search recursively) - look for both wav and mp3
            vocals_candidates = list(temp_output.glob("**/*vocals.wav")) + list(temp_output.glob("**/*vocals.mp3"))
            no_vocals_candidates = list(temp_output.glob("**/*no_vocals.wav")) + list(temp_output.glob("**/*no_vocals.mp3"))
            
            # Best-effort: some demucs variants name "vocals.wav" and "no_vocals.wav"
            if not vocals_candidates and not no_vocals_candidates:
                # show directory contents
                self.log_status("Demucs output directory listing (for debugging):")
                for p in temp_output.rglob("*"):
                    self.log_status(f"  {p}")
                raise Exception("Demucs completed but expected output files were not found")

            # pick first matches
            vocals_path = vocals_candidates[0] if vocals_candidates else None
            instrumental_path = no_vocals_candidates[0] if no_vocals_candidates else None
            
            # Apply additional vocal suppression if enhanced mode is enabled
            if self.enhance_separation.get() and instrumental_path:
                self.log_status("Applying additional vocal suppression to instrumental...")
                instrumental_path = self.apply_vocal_suppression(instrumental_path)
            
            # Some installations produce 'vocals.wav' and 'no_vocals.wav'; sometimes inverted naming - attempt to detect by size (vocals usually smaller)
            if vocals_path and instrumental_path:
                return str(vocals_path), str(instrumental_path)
            else:
                # fallback: if only one file found, return it as instrumental and leave vocals None
                if instrumental_path:
                    return (None, str(instrumental_path))
                if vocals_path:
                    return (str(vocals_path), None)
                raise Exception("Unable to locate both vocals and instrumental outputs from Demucs")
        except Exception:
            raise

    def apply_vocal_suppression(self, audio_path):
        """Apply additional processing to reduce vocal bleed in instrumental track"""
        try:
            self.log_status("  Analyzing frequency spectrum...")
            
            # Create output path for enhanced version
            enhanced_path = Path(audio_path).parent / (Path(audio_path).stem + "_enhanced" + Path(audio_path).suffix)
            
            # Use FFmpeg high-pass filter to reduce vocal frequencies
            # Most vocals sit in 300Hz-3400Hz range, we'll use a gentle high-pass
            # and apply a vocal suppression filter
            cmd = [
                "ffmpeg", "-y", "-i", str(audio_path),
                "-af", "highpass=f=100,lowpass=f=15000,afftdn=nf=-25",  # Noise reduction + frequency filtering
                "-ar", "44100",  # Standard sample rate
                "-b:a", "320k",  # High quality
                str(enhanced_path)
            ]
            
            rc, out, err = run_subprocess(cmd, timeout=300, capture=True)
            
            if rc == 0 and enhanced_path.exists():
                self.log_status("  ✓ Vocal suppression applied")
                # Remove original, return enhanced
                try:
                    Path(audio_path).unlink()
                except Exception:
                    pass
                return str(enhanced_path)
            else:
                self.log_status("  Note: Additional processing skipped, using original")
                return str(audio_path)
                
        except Exception as e:
            self.log_status(f"  Note: Additional processing failed ({e}), using original")
            return str(audio_path)

    def convert_audio(self, src_audio, target_format_key, dest_path):
        """Convert an audio file to desired format using ffmpeg. Returns resulting path."""
        fmt = OUTPUT_FORMATS.get(target_format_key)
        if not fmt:
            raise Exception("Unknown output format selected")
        ext = fmt["ext"]
        ff_args = fmt["ffmpeg_args"]
        out_file = Path(dest_path).with_suffix(ext)
        # Build ffmpeg command: input is src_audio (WAV or MP3), output as ext
        cmd = ["ffmpeg", "-y", "-i", str(src_audio)] + ff_args + [str(out_file)]
        rc, out, err = run_subprocess(cmd, timeout=300, capture=True)
        if rc != 0:
            raise Exception(f"ffmpeg conversion failed: {err or out}")
        return str(out_file)

    def merge_audio_into_video(self, video_file, audio_file, out_video_path):
        """Replace the audio track of video_file with audio_file. Keeps video stream copy."""
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_file),
            "-i", str(audio_file),
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(out_video_path)
        ]
        rc, out, err = run_subprocess(cmd, timeout=300, capture=True)
        if rc != 0:
            raise Exception(f"ffmpeg merge failed: {err or out}")
        return str(out_video_path)

    # ----------------------------
    # Orchestration
    # ----------------------------
    def processing_thread(self):
        if self.debug_mode.get():
            print("DEBUG: processing_thread started")  # Debug output
        try:
            if self.debug_mode.get():
                print("DEBUG: Initializing progress tracking")  # Debug output
            # Initialize progress tracking
            self.start_time = time.time()
            self.current_step = 0
            
            # Calculate total steps based on options
            self.total_steps = 3  # Base steps: setup, demucs, conversion
            if self.youtube_url.get().strip():
                self.total_steps += 1  # YouTube download
            if self.create_video_output.get():
                self.total_steps += 2  # Video merging for vocals and instrumental
            
            if self.debug_mode.get():
                print(f"DEBUG: Total steps calculated: {self.total_steps}")  # Debug output
            self.root.after(0, lambda: self.progress_bar.config(value=0))
            
            input_path = None
            original_video = None

            # Determine source
            if self.debug_mode.get():
                print("DEBUG: Determining source...")  # Debug output
            if self.youtube_url.get().strip():
                if self.debug_mode.get():
                    print("DEBUG: YouTube URL detected, downloading...")  # Debug output
                self.update_progress("Downloading from YouTube", 1)
                downloaded = self.download_youtube(self.youtube_url.get().strip())
                
                # Check if stop was requested
                if self.check_should_stop():
                    raise InterruptedError("Download stopped by user")
                
                input_path = downloaded
                if self.debug_mode.get():
                    print(f"DEBUG: Downloaded to: {input_path}")  # Debug output
                # If user chose video download, the downloaded file will be a video file
                if self.create_video_output.get():
                    original_video = downloaded
            elif self.input_file.get().strip():
                if self.debug_mode.get():
                    print("DEBUG: Local file detected")  # Debug output
                self.update_progress("Validating input file", 1)
                input_path = self.input_file.get().strip()
                if not Path(input_path).exists():
                    raise Exception("Input path does not exist")
                # If local file is a video (by extension), treat original_video = input_path
                if Path(input_path).suffix.lower() in [".mp4", ".mkv", ".mov", ".webm", ".avi", ".flv"]:
                    original_video = input_path
            else:
                if self.debug_mode.get():
                    print("DEBUG: No input provided!")  # Debug output
                raise Exception("Please provide either a local file or a YouTube URL")

            if self.debug_mode.get():
                print(f"DEBUG: Input resolved: {input_path}")  # Debug output
            self.log_status(f"Input resolved: {input_path}")

            # Ensure ffmpeg installed before probing
            if self.debug_mode.get():
                print("DEBUG: Setting up dependencies...")  # Debug output
            self.update_progress("Setting up dependencies")
            install_ffmpeg_if_missing(gui_logger=self.log_status, persist=self.persist_ffmpeg.get())
            if self.debug_mode.get():
                print("DEBUG: FFmpeg setup complete")  # Debug output

            # Probe input
            ok, msg = ffmpeg_probe(input_path)
            if not ok:
                raise Exception(f"Input file is not readable by ffmpeg: {msg}")

            # Run Demucs with progress animation
            self.update_progress("AI vocal separation in progress")
            
            # Start progress animation
            self.demucs_animation_active = True
            self.start_demucs_animation()
            
            vocals_wav, instrumental_wav = self.process_audio_with_demucs(input_path)
            
            # Stop animation
            self.demucs_animation_active = False

            if not instrumental_wav and not vocals_wav:
                raise Exception("Demucs did not produce outputs")

            # Output folder
            out_dir = Path(self.output_folder.get())
            out_dir.mkdir(parents=True, exist_ok=True)

            input_name = Path(input_path).stem
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")

            created_files = []

            # Convert instrumentals (if present) to selected format
            target_fmt = self.selected_format.get()
            if instrumental_wav:
                self.update_progress("Converting instrumental audio")
                target_base = out_dir / f"{input_name}_instrumental_{ts}"
                self.log_status(f"Converting instrumental to {target_fmt}...")
                conv_path = self.convert_audio(instrumental_wav, target_fmt, str(target_base))
                created_files.append(conv_path)
                self.log_status(f"✓ Instrumental saved: {conv_path}")

                # If user wants MP4 video outputs and original video exists, merge
                if self.create_video_output.get() and original_video:
                    self.update_progress("Creating instrumental video")
                    video_out = out_dir / f"{input_name}_instrumental_video_{ts}.mp4"
                    self.log_status("Merging instrumental into original video (MP4)...")
                    merged = self.merge_audio_into_video(original_video, conv_path, video_out)
                    created_files.append(merged)
                    self.log_status(f"✓ Instrumental video saved: {merged}")

            # Convert vocals (if present)
            if vocals_wav:
                self.update_progress("Converting vocal audio")
                target_base = out_dir / f"{input_name}_vocals_{ts}"
                self.log_status(f"Converting vocals to {target_fmt}...")
                conv_path = self.convert_audio(vocals_wav, target_fmt, str(target_base))
                created_files.append(conv_path)
                self.log_status(f"✓ Vocals audio saved: {conv_path}")

                if self.create_video_output.get() and original_video:
                    self.update_progress("Creating vocals video")
                    video_out = out_dir / f"{input_name}_vocals_video_{ts}.mp4"
                    self.log_status("Merging vocals into original video (MP4)...")
                    merged = self.merge_audio_into_video(original_video, conv_path, video_out)
                    created_files.append(merged)
                    self.log_status(f"✓ Vocals video saved: {merged}")

            # Cleanup temp demucs and temp_download
            try:
                safe_remove(Path(self.output_folder.get()) / "temp_demucs")
                safe_remove(Path(self.output_folder.get()) / "temp_download")
            except Exception:
                pass

            # Mark as complete
            self.update_progress("Complete!", self.total_steps)
            
            self.log_status("\n" + "="*60)
            self.log_status("✓ SUCCESS! Created outputs:")
            for f in created_files:
                self.log_status(f"  {f}")
            self.log_status("="*60)

            # Calculate total time
            total_time = time.time() - self.start_time
            if total_time < 60:
                time_str = f"{int(total_time)}s"
            elif total_time < 3600:
                minutes = int(total_time / 60)
                seconds = int(total_time % 60)
                time_str = f"{minutes}m {seconds}s"
            else:
                hours = int(total_time / 3600)
                minutes = int((total_time % 3600) / 60)
                time_str = f"{hours}h {minutes}m"
            
            self.log_status(f"Total processing time: {time_str}")

            # Show completion popup with first few files
            first_files = "\n".join(created_files[:6])
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Outputs created in {time_str}:\n\n{first_files}\n\nSaved to:\n{out_dir}"))
        except InterruptedError as e:
            # User stopped the process
            self.log_status("\n" + "=" * 60)
            self.log_status("⏹ STOPPED: Processing cancelled by user")
            self.log_status("=" * 60)
            self.root.after(0, lambda: messagebox.showwarning("Stopped", "Processing was stopped by user."))
        except Exception as e:
            # Surface full exception message
            if self.debug_mode.get():
                print(f"DEBUG: Exception caught: {type(e).__name__}: {e}")  # Debug output
                import traceback
                traceback.print_exc()  # Print full traceback to console
            
            emsg = str(e) if str(e) else "Unknown error"
            self.log_status("\n❌ ERROR: " + emsg)
            
            # Provide context-specific error messages
            if "network" in emsg.lower() or "connection" in emsg.lower() or "internet" in emsg.lower():
                error_title = "Network Error"
                error_details = f"A network error occurred:\n\n{emsg}\n\nPlease check your internet connection and try again."
            elif "timeout" in emsg.lower():
                error_title = "Timeout Error"
                error_details = f"Operation timed out:\n\n{emsg}\n\nThe download or process took too long. Please try again."
            else:
                error_title = "Error"
                error_details = f"An error occurred:\n\n{emsg}\n\nCheck the debug console for more details."
            
            self.root.after(0, lambda: messagebox.showerror(error_title, error_details))
        finally:
            if self.debug_mode.get():
                print("DEBUG: Finally block - cleaning up")  # Debug output
            self.processing = False
            self.should_stop = False
            self.current_process = None
            self.root.after(0, lambda: self.progress_bar.config(value=0))
            self.root.after(0, lambda: self.progress_label_var.set("Ready"))
            self.root.after(0, lambda: self.process_btn.config(state='normal', text="⬇ Download"))
            self.root.after(0, lambda: self.stop_btn.config(state='disabled'))
            if self.debug_mode.get():
                print("DEBUG: Cleanup complete")  # Debug output

    # ----------------------------
    # UI control
    # ----------------------------
    def start_processing(self):
        try:
            if self.debug_mode.get():
                print("DEBUG: start_processing called")  # Debug output
            if self.processing:
                if self.debug_mode.get():
                    print("DEBUG: Already processing, returning")  # Debug output
                messagebox.showwarning("Already Processing", "Processing is already in progress. Please wait for it to complete.")
                return
            
            # Disable button immediately to show it was clicked
            self.process_btn.config(state='disabled', text="⏳ Preparing...")
            self.root.update()
            
            # Calculate estimated time based on settings
            estimated_minutes = 3  # Base time for setup and conversion
            
            if self.youtube_url.get().strip():
                estimated_minutes += 2  # YouTube download time
            
            # Demucs processing time estimation
            if self.enhance_separation.get():
                estimated_minutes += 8  # Enhanced mode takes longer (10 shifts)
            else:
                estimated_minutes += 4  # Standard mode
            
            if self.create_video_output.get():
                estimated_minutes += 2  # Video merging time
            
            # Show estimated time popup
            if estimated_minutes < 5:
                time_msg = f"approximately {estimated_minutes} minutes"
            elif estimated_minutes < 10:
                time_msg = f"{estimated_minutes}-{estimated_minutes + 2} minutes"
            else:
                time_msg = f"{estimated_minutes}-{estimated_minutes + 5} minutes"
            
            # Force window to front and show popup
            self.root.lift()
            self.root.attributes('-topmost', True)
            self.root.after(100, lambda: self.root.attributes('-topmost', False))
            
            response = messagebox.askokcancel(
                "Processing Time Estimate",
                f"⏱️ Estimated processing time: {time_msg}\n\n"
                f"{'🔥 Enhanced mode: Using 10x AI passes for best quality' if self.enhance_separation.get() else '⚡ Standard mode'}\n\n"
                f"The actual time may vary based on:\n"
                f"• File length and size\n"
                f"• CPU speed\n"
                f"• First-run downloads (~650MB AI models)\n\n"
                f"Ready to start?"
            )
            
            if not response:
                # User cancelled - re-enable button
                self.process_btn.config(state='normal', text="⬇ Download")
                return
            
            if self.debug_mode.get():
                print("DEBUG: Starting new process")  # Debug output
            self.status_text.delete('1.0', 'end')
            self.log_status("Starting processing...")  # Add initial log
            self.processing = True
            self.should_stop = False  # Reset stop flag
            self.process_btn.config(state='disabled', text="⏳ Processing...")
            self.stop_btn.config(state='normal')  # Enable stop button
            self.progress_bar.config(value=0)
            self.progress_label_var.set("Starting...")
            if self.debug_mode.get():
                print("DEBUG: About to start thread")  # Debug output
            thread = threading.Thread(target=self.processing_thread, daemon=True)
            thread.start()
            if self.debug_mode.get():
                print("DEBUG: Thread started")  # Debug output
        except Exception as e:
            if self.debug_mode.get():
                print(f"DEBUG: Exception in start_processing: {e}")  # Debug output
                import traceback
                traceback.print_exc()
            messagebox.showerror("Error", f"Failed to start processing:\n{e}")

def main():
    # Basic tkinter check
    try:
        import tkinter  # noqa: F401
    except Exception:
        print("tkinter missing. On Windows, install the python tkinter package or use a python distribution that includes tkinter.")
        sys.exit(1)
    root = tk.Tk()
    app = VocalRemoverApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()