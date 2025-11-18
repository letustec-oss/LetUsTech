#!/usr/bin/env python3
"""
LetUsTech Vocal Remover - Full featured
- Auto-installs FFmpeg (FULL build) to C:\ffmpeg (user-chosen Full build)
- Auto-installs demucs and yt-dlp via pip if missing
- Validates downloads
- Runs demucs in CPU mode
- Export options: WAV, MP3, FLAC, M4A (audio in mp4 container), OGG
- Optional MP4 video outputs (merge isolated audio into original video)
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

# ----------------------------
# Configuration (adjust if desired)
# ----------------------------
FFMPEG_INSTALL_DIR = Path("C:/ffmpeg")
FFMPEG_BIN = FFMPEG_INSTALL_DIR / "bin"
FFMPEG_DOWNLOAD_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.zip"
FFMPEG_ZIP_NAME = "ffmpeg-full.zip"

PIP_PACKAGES = ["demucs", "yt-dlp"]

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
        # Build pip install command
        cmd = [sys.executable, "-m", "pip", "install", "--break-system-packages"] + packages
        if gui_logger:
            gui_logger(f"Installing Python packages: {', '.join(packages)} (this may take a while)...")
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            if gui_logger:
                gui_logger("pip install failed. Output:")
                for line in (proc.stdout + proc.stderr).splitlines()[:20]:
                    gui_logger("  " + line)
            return False
        if gui_logger:
            gui_logger("✓ Python packages installed")
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
        self.root.title("LetUsTech Vocal Remover - Wired For Your World")
        self.root.geometry("860x760")
        self.root.configure(bg='#001f3f')

        # Variables
        self.input_file = tk.StringVar()
        self.youtube_url = tk.StringVar()
        self.output_folder = tk.StringVar(value=str(Path.home() / "Music" / "Instrumentals"))
        self.processing = False
        self.selected_format = tk.StringVar(value="WAV (.wav)")
        self.create_video_output = tk.BooleanVar(value=True)
        self.auto_install_pip = tk.BooleanVar(value=True)
        self.persist_ffmpeg = tk.BooleanVar(value=True)

        Path(self.output_folder.get()).mkdir(parents=True, exist_ok=True)
        self.create_widgets()

    def create_widgets(self):
        header_frame = tk.Frame(self.root, bg='#001f3f')
        header_frame.pack(pady=12)
        title_label = tk.Label(header_frame, text="🎵 LetUsTech Vocal Remover", font=('Arial', 24, 'bold'), bg='#001f3f', fg='#00ff00')
        title_label.pack()
        subtitle_label = tk.Label(header_frame, text="Wired For Your World", font=('Arial', 11, 'italic'), bg='#001f3f', fg='#00ff00')
        subtitle_label.pack()

        main_frame = tk.Frame(self.root, bg='#001f3f')
        main_frame.pack(padx=12, pady=6, fill='both', expand=True)

        method_frame = tk.LabelFrame(main_frame, text="Input Method", font=('Arial', 12, 'bold'), bg='#003366', fg='#00ff00', padx=12, pady=12)
        method_frame.pack(fill='x', pady=6)

        file_frame = tk.Frame(method_frame, bg='#003366')
        file_frame.pack(fill='x', pady=4)
        tk.Label(file_frame, text="Local File (MP3, MP4, WAV, M4A, FLAC):", font=('Arial', 11), bg='#003366', fg='white').pack(anchor='w', pady=4)
        file_input_frame = tk.Frame(file_frame, bg='#003366')
        file_input_frame.pack(fill='x')
        tk.Entry(file_input_frame, textvariable=self.input_file, font=('Arial', 10), width=68).pack(side='left', padx=(0,10))
        tk.Button(file_input_frame, text="Browse", command=self.browse_file, bg='#00ff00', fg='#001f3f', font=('Arial', 10, 'bold'), cursor='hand2').pack(side='left')

        tk.Label(method_frame, text="─── OR ───", font=('Arial', 10, 'bold'), bg='#003366', fg='#00ff00').pack(pady=8)
        url_frame = tk.Frame(method_frame, bg='#003366')
        url_frame.pack(fill='x', pady=4)
        tk.Label(url_frame, text="YouTube URL:", font=('Arial', 11), bg='#003366', fg='white').pack(anchor='w', pady=4)
        tk.Entry(url_frame, textvariable=self.youtube_url, font=('Arial', 10), width=86).pack(fill='x')

        output_frame = tk.LabelFrame(main_frame, text="Output Settings", font=('Arial', 12, 'bold'), bg='#003366', fg='#00ff00', padx=12, pady=12)
        output_frame.pack(fill='x', pady=6)
        tk.Label(output_frame, text="Save Instrumentals To:", font=('Arial', 11), bg='#003366', fg='white').pack(anchor='w', pady=4)
        output_input_frame = tk.Frame(output_frame, bg='#003366')
        output_input_frame.pack(fill='x')
        tk.Entry(output_input_frame, textvariable=self.output_folder, font=('Arial', 10), width=68).pack(side='left', padx=(0,10))
        tk.Button(output_input_frame, text="Browse", command=self.browse_output_folder, bg='#00ff00', fg='#001f3f', font=('Arial', 10, 'bold'), cursor='hand2').pack(side='left')

        options_frame = tk.Frame(output_frame, bg='#003366')
        options_frame.pack(fill='x', pady=8)
        tk.Label(options_frame, text="Export Format:", font=('Arial', 10), bg='#003366', fg='white').pack(side='left', padx=(0,8))
        format_menu = ttk.Combobox(options_frame, textvariable=self.selected_format, values=list(OUTPUT_FORMATS.keys()), width=30, state='readonly')
        format_menu.pack(side='left')

        tk.Checkbutton(options_frame, text="Also create MP4 video outputs (if source has video)", variable=self.create_video_output, bg='#003366', fg='white', selectcolor='#003366').pack(side='left', padx=12)
        tk.Checkbutton(options_frame, text="Auto-install demucs & yt-dlp", variable=self.auto_install_pip, bg='#003366', fg='white', selectcolor='#003366').pack(side='left', padx=8)
        tk.Checkbutton(options_frame, text="Persist FFmpeg to PATH (setx)", variable=self.persist_ffmpeg, bg='#003366', fg='white', selectcolor='#003366').pack(side='left', padx=8)

        self.process_btn = tk.Button(main_frame, text="🎵 Remove Vocals & Create Outputs", command=self.start_processing, bg='#00ff00', fg='#001f3f', font=('Arial', 14, 'bold'), cursor='hand2', pady=12)
        self.process_btn.pack(pady=12, fill='x')

        progress_frame = tk.LabelFrame(main_frame, text="Progress & Logs", font=('Arial', 12, 'bold'), bg='#003366', fg='#00ff00', padx=12, pady=12)
        progress_frame.pack(fill='both', expand=True, pady=6)

        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=520)
        self.progress_bar.pack(pady=8, fill='x')

        self.status_text = tk.Text(progress_frame, height=14, font=('Courier', 9), bg='#001a33', fg='#00ff00', wrap='word')
        self.status_text.pack(fill='both', expand=True, pady=4)
        scrollbar = tk.Scrollbar(self.status_text)
        scrollbar.pack(side='right', fill='y')
        self.status_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.status_text.yview)

        info_label = tk.Label(main_frame, text="Tip: First run may download FFmpeg (~180MB) and Demucs models (~250MB). Be patient.", font=('Arial', 9), bg='#001f3f', fg='#00cc00')
        info_label.pack(pady=6)

    def log_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert('end', f"[{timestamp}] {message}\n")
        self.status_text.see('end')
        self.root.update()

    def browse_file(self):
        filename = filedialog.askopenfilename(title="Select Audio/Video File", filetypes=[("Media Files", "*.mp3 *.mp4 *.wav *.m4a *.flac *.ogg *.webm *.mov"), ("All Files", "*.*")])
        if filename:
            self.input_file.set(filename)
            self.youtube_url.set("")

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)

    # ----------------------------
    # Download & validation
    # ----------------------------
    def download_youtube(self, url):
        """Downloads audio or full video depending on 'create_video_output' flag."""
        try:
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
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=900)
            # Log relevant lines
            if proc.stdout:
                for line in proc.stdout.splitlines():
                    if any(k in line for k in ("Destination:", "Downloading", "Merged", "has already been downloaded")):
                        self.log_status("  " + line.strip())
            if proc.returncode != 0:
                combined = (proc.stderr or proc.stdout or "")[:2000]
                raise Exception(f"yt-dlp failed: {combined}")

            # find downloaded file
            files = list(temp_dir.glob("*"))
            if not files:
                raise Exception("No files were downloaded by yt-dlp")

            # pick the largest file (likely our desired)
            chosen = sorted(files, key=lambda p: p.stat().st_size if p.exists() else 0, reverse=True)[0]
            self.log_status(f"✓ Downloaded: {chosen.name} ({chosen.stat().st_size} bytes)")

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
        """Run demucs in CPU mode and return tuple(paths): (vocals_path, instrumental_path) absolute paths to WAV outputs"""
        try:
            # Ensure ffmpeg present
            install_ffmpeg_if_missing(gui_logger=self.log_status, persist=self.persist_ffmpeg.get())

            # Auto-install demucs if requested
            if self.auto_install_pip.get():
                pip_install_packages(PIP_PACKAGES, gui_logger=self.log_status)

            # Check demucs availability
            rc, out, err = run_subprocess(["demucs", "--help"], timeout=20, capture=True)
            if rc != 0 and rc != 0 and "usage:" not in (out or err or ""):
                self.log_status("Warning: demucs check returned nonzero; will attempt to run demucs anyway")

            temp_output = Path(self.output_folder.get()) / "temp_demucs"
            if temp_output.exists():
                shutil.rmtree(temp_output, ignore_errors=True)
            temp_output.mkdir(parents=True, exist_ok=True)

            cmd = [
                "demucs",
                "--two-stems=vocals",
                "--device", "cpu",
                "-o", str(temp_output),
                input_path
            ]
            self.log_status("Running Demucs (CPU mode). This may take a while...")
            # spawn and stream output
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in process.stdout:
                if line.strip():
                    self.log_status("  " + line.strip())
            process.wait()
            if process.returncode != 0:
                raise Exception(f"Demucs failed with code {process.returncode}")

            # find outputs (search recursively)
            vocals_candidates = list(temp_output.glob("**/*vocals.wav"))
            no_vocals_candidates = list(temp_output.glob("**/*no_vocals.wav"))
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

    def convert_audio(self, src_wav, target_format_key, dest_path):
        """Convert a WAV file to desired format using ffmpeg. Returns resulting path."""
        fmt = OUTPUT_FORMATS.get(target_format_key)
        if not fmt:
            raise Exception("Unknown output format selected")
        ext = fmt["ext"]
        ff_args = fmt["ffmpeg_args"]
        out_file = Path(dest_path).with_suffix(ext)
        # Build ffmpeg command: input is src_wav (WAV), output as ext
        cmd = ["ffmpeg", "-y", "-i", str(src_wav)] + ff_args + [str(out_file)]
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
        try:
            input_path = None
            original_video = None

            # Determine source
            if self.youtube_url.get().strip():
                downloaded = self.download_youtube(self.youtube_url.get().strip())
                input_path = downloaded
                # If user chose video download, the downloaded file will be a video file
                if self.create_video_output.get():
                    original_video = downloaded
            elif self.input_file.get().strip():
                input_path = self.input_file.get().strip()
                if not Path(input_path).exists():
                    raise Exception("Input path does not exist")
                # If local file is a video (by extension), treat original_video = input_path
                if Path(input_path).suffix.lower() in [".mp4", ".mkv", ".mov", ".webm", ".avi", ".flv"]:
                    original_video = input_path
            else:
                raise Exception("Please provide either a local file or a YouTube URL")

            self.log_status(f"Input resolved: {input_path}")

            # Ensure ffmpeg installed before probing
            install_ffmpeg_if_missing(gui_logger=self.log_status, persist=self.persist_ffmpeg.get())

            # Probe input
            ok, msg = ffmpeg_probe(input_path)
            if not ok:
                raise Exception(f"Input file is not readable by ffmpeg: {msg}")

            # Run Demucs
            vocals_wav, instrumental_wav = self.process_audio_with_demucs(input_path)

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
                target_base = out_dir / f"{input_name}_instrumental_{ts}"
                self.log_status(f"Converting instrumental to {target_fmt}...")
                conv_path = self.convert_audio(instrumental_wav, target_fmt, str(target_base))
                created_files.append(conv_path)
                self.log_status(f"✓ Instrumental saved: {conv_path}")

                # If user wants MP4 video outputs and original video exists, merge
                if self.create_video_output.get() and original_video:
                    video_out = out_dir / f"{input_name}_instrumental_video_{ts}.mp4"
                    self.log_status("Merging instrumental into original video (MP4)...")
                    merged = self.merge_audio_into_video(original_video, conv_path, video_out)
                    created_files.append(merged)
                    self.log_status(f"✓ Instrumental video saved: {merged}")

            # Convert vocals (if present)
            if vocals_wav:
                target_base = out_dir / f"{input_name}_vocals_{ts}"
                self.log_status(f"Converting vocals to {target_fmt}...")
                conv_path = self.convert_audio(vocals_wav, target_fmt, str(target_base))
                created_files.append(conv_path)
                self.log_status(f"✓ Vocals audio saved: {conv_path}")

                if self.create_video_output.get() and original_video:
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

            self.log_status("\n" + "="*60)
            self.log_status("✓ SUCCESS! Created outputs:")
            for f in created_files:
                self.log_status(f"  {f}")
            self.log_status("="*60)

            # Show completion popup with first few files
            first_files = "\n".join(created_files[:6])
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Outputs created:\n\n{first_files}\n\nSaved to:\n{out_dir}"))
        except Exception as e:
            # Surface full exception message
            emsg = str(e) if str(e) else "Unknown error"
            self.log_status("\n❌ ERROR: " + emsg)
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n\n{emsg}"))
        finally:
            self.processing = False
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, lambda: self.process_btn.config(state='normal'))

    # ----------------------------
    # UI control
    # ----------------------------
    def start_processing(self):
        if self.processing:
            return
        self.status_text.delete('1.0', 'end')
        self.processing = True
        self.process_btn.config(state='disabled')
        self.progress_bar.start()
        thread = threading.Thread(target=self.processing_thread, daemon=True)
        thread.start()

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
