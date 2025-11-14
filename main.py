# -*- coding: utf-8 -*-
import os
import sys
import shutil
import json
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
import tempfile
from threading import Lock
from datetime import datetime, timedelta

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QListWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QSpinBox, QCheckBox, QProgressBar, QLineEdit, QMessageBox,
    QGroupBox, QFormLayout, QTextEdit
)

import quality_presets as qp

try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

# ---------------------------
# Utilities
# ---------------------------

def check_ytdlp_update() -> tuple[bool, str, str]:
    """
    Verifica si hay una actualización de yt-dlp disponible.
    Returns: (needs_update, current_version, message)
    """
    if not YT_DLP_AVAILABLE:
        return False, "N/A", "yt-dlp no está instalado"
    
    # CRÍTICO: Deshabilitar auto-update en ejecutable compilado
    # sys.executable apunta al .exe, no a Python, causando bucle infinito
    if getattr(sys, 'frozen', False):
        # Estamos en ejecutable compilado por PyInstaller
        try:
            current_version = yt_dlp.version.__version__
            return False, current_version, f"Auto-actualización deshabilitada en ejecutable (versión actual: {current_version})"
        except:
            return False, "unknown", "Auto-actualización deshabilitada en ejecutable"
    
    try:
        # Obtener versión instalada
        current_version = yt_dlp.version.__version__
        
        # Verificar última actualización (archivo de timestamp)
        cache_dir = Path.home() / ".audio_converter_cache"
        cache_dir.mkdir(exist_ok=True)
        update_file = cache_dir / "ytdlp_last_update.txt"
        
        # Verificar si ya se actualizó hoy
        if update_file.exists():
            try:
                last_update = datetime.fromisoformat(update_file.read_text().strip())
                if datetime.now() - last_update < timedelta(days=1):
                    return False, current_version, f"yt-dlp {current_version} (actualizado hoy)"
            except:
                pass
        
        # Verificar si hay actualización disponible (sin instalar)
        # NOTA: Solo funciona en entorno Python normal, no en ejecutable
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "yt-dlp" in result.stdout.lower():
            return True, current_version, f"Actualización disponible para yt-dlp {current_version}"
        
        return False, current_version, f"yt-dlp {current_version} está actualizado"
        
    except Exception as e:
        return False, "unknown", f"Error verificando actualización: {str(e)}"


def update_ytdlp_silent() -> tuple[bool, str]:
    """
    Actualiza yt-dlp silenciosamente en segundo plano.
    Returns: (success, message)
    """
    # CRÍTICO: Deshabilitar auto-update en ejecutable compilado
    if getattr(sys, 'frozen', False):
        return False, "Actualización no disponible en ejecutable compilado"
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp", "--quiet"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Guardar timestamp de actualización
            cache_dir = Path.home() / ".audio_converter_cache"
            cache_dir.mkdir(exist_ok=True)
            update_file = cache_dir / "ytdlp_last_update.txt"
            update_file.write_text(datetime.now().isoformat())
            
            # Obtener nueva versión
            try:
                import importlib
                importlib.reload(yt_dlp.version)
                new_version = yt_dlp.version.__version__
                return True, f"yt-dlp actualizado a {new_version}"
            except:
                return True, "yt-dlp actualizado exitosamente"
        else:
            return False, f"Error al actualizar: {result.stderr[:200]}"
            
    except subprocess.TimeoutExpired:
        return False, "Timeout al actualizar (conexión lenta)"
    except Exception as e:
        return False, f"Error: {str(e)}"


def find_ffmpeg() -> Optional[str]:
    """
    Return path to ffmpeg executable.
    Priority: local ./bin/ffmpeg(.exe) then PATH.
    """
    # 1. Local bin dentro del ejecutable (PyInstaller _MEIPASS)
    local_bin = Path(getattr(sys, "_MEIPASS", Path.cwd())) / "bin"
    for candidate in ["ffmpeg.exe", "ffmpeg"]:
        p = local_bin / candidate
        if p.exists():
            print(f"✓ FFmpeg encontrado en _MEIPASS: {p}")
            return str(p)
    
    # 2. Carpeta bin junto al ejecutable (para distribución)
    if getattr(sys, 'frozen', False):
        # Estamos en ejecutable, buscar en carpeta del .exe
        exe_dir = Path(sys.executable).parent / "bin"
        for candidate in ["ffmpeg.exe", "ffmpeg"]:
            p = exe_dir / candidate
            if p.exists():
                print(f"✓ FFmpeg encontrado junto al ejecutable: {p}")
                return str(p)
    
    # 3. PATH del sistema
    exe = shutil.which("ffmpeg")
    if exe:
        print(f"✓ FFmpeg encontrado en PATH: {exe}")
        return exe

    # 4. Windows PATH try common installs
    if os.name == "nt":
        common = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        ]
        for c in common:
            if os.path.exists(c):
                print(f"✓ FFmpeg encontrado en ubicación común: {c}")
                return c
    
    print("❌ FFmpeg NO encontrado en ninguna ubicación")
    return None


def find_ffprobe() -> Optional[str]:
    """
    Return path to ffprobe executable.
    Mirror logic of find_ffmpeg.
    """
    # 1. Local bin dentro del ejecutable (PyInstaller _MEIPASS)
    local_bin = Path(getattr(sys, "_MEIPASS", Path.cwd())) / "bin"
    for candidate in ["ffprobe.exe", "ffprobe"]:
        p = local_bin / candidate
        if p.exists():
            print(f"✓ FFprobe encontrado en _MEIPASS: {p}")
            return str(p)
    
    # 2. Carpeta bin junto al ejecutable (para distribución)
    if getattr(sys, 'frozen', False):
        exe_dir = Path(sys.executable).parent / "bin"
        for candidate in ["ffprobe.exe", "ffprobe"]:
            p = exe_dir / candidate
            if p.exists():
                print(f"✓ FFprobe encontrado junto al ejecutable: {p}")
                return str(p)
    
    # 3. PATH del sistema
    exe = shutil.which("ffprobe")
    if exe:
        print(f"✓ FFprobe encontrado en PATH: {exe}")
        return exe

    # 4. Windows common locations
    if os.name == "nt":
        common = [
            r"C:\ffmpeg\bin\ffprobe.exe",
            r"C:\Program Files\ffmpeg\bin\ffprobe.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffprobe.exe",
        ]
        for c in common:
            if os.path.exists(c):
                print(f"✓ FFprobe encontrado en ubicación común: {c}")
                return c
    
    print("❌ FFprobe NO encontrado en ninguna ubicación")
    return None


def probe_audio_meta(ffprobe_path: str, fpath: str) -> dict:
    """
    Return metadata for the first audio stream via ffprobe json.
    """
    cmd = [
        ffprobe_path, "-v", "error", "-select_streams", "a:0",
        "-show_entries", "stream=codec_name,codec_type,channels,sample_rate,sample_fmt,bit_rate,duration",
        "-of", "json", fpath
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode != 0:
        return {}
    try:
        data = json.loads(p.stdout)
        if "streams" in data and data["streams"]:
            return data["streams"][0]
        return {}
    except json.JSONDecodeError:
        return {}


def duration_seconds(ffprobe_path: str, fpath: str) -> float:
    """
    Fetch format duration for progress computation.
    """
    cmd = [
        ffprobe_path, "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        fpath,
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode == 0:
        try:
            return float(p.stdout.strip())
        except:
            return 0.0
    return 0.0


# ---------------------------
# Download Worker Thread
# ---------------------------

class DownloadWorker(QThread):
    progress = Signal(str)  # status message
    progress_percent = Signal(int, float)  # index, percent
    finished = Signal(bool, str, list)  # success, message, list of downloaded files
    
    def __init__(self, urls: List[str], output_dir: str):
        super().__init__()
        self.urls = urls
        self.output_dir = output_dir
        self._stop = False
        self._stop_lock = Lock()
    
    def stop(self):
        with self._stop_lock:
            self._stop = True
    
    def is_stopped(self) -> bool:
        with self._stop_lock:
            return self._stop
    
    def run(self):
        if not YT_DLP_AVAILABLE:
            self.finished.emit(False, "yt-dlp no está instalado. Ejecuta: pip install yt-dlp", [])
            return
        
        downloaded_files = []
        
        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        for idx, url in enumerate(self.urls):
            if self.is_stopped():
                break
            
            try:
                self.progress.emit(f"Descargando de: {url}")
                self.progress_percent.emit(idx, 0.0)
                
                # Debug: Verificar si estamos en ejecutable
                if getattr(sys, 'frozen', False):
                    self.progress.emit(f"🔍 Modo: Ejecutable compilado (PyInstaller)")
                else:
                    self.progress.emit(f"🔍 Modo: Python directo")
                
                # Find FFmpeg for yt-dlp
                ffmpeg_path = find_ffmpeg()
                if not ffmpeg_path:
                    error_msg = ("❌ ERROR CRÍTICO: FFmpeg no encontrado\n\n"
                                "FFmpeg es necesario para procesar el audio descargado.\n\n"
                                "SOLUCIONES:\n"
                                "1. Instala FFmpeg: https://ffmpeg.org/download.html\n"
                                "2. Añade FFmpeg a la variable PATH del sistema\n"
                                "3. O coloca ffmpeg.exe en la carpeta 'bin' junto al ejecutable")
                    self.progress.emit(error_msg)
                    self.finished.emit(False, error_msg, [])
                    return  # ← Detener completamente, no continuar
                
                # Progress hook for yt-dlp
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        try:
                            if 'total_bytes' in d:
                                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                            elif 'total_bytes_estimate' in d:
                                percent = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
                            else:
                                percent = 0
                            self.progress_percent.emit(idx, min(percent, 99.0))
                        except:
                            pass
                    elif d['status'] == 'finished':
                        self.progress_percent.emit(idx, 100.0)
                
                # yt-dlp options for best audio quality
                # Configuración mejorada para evitar error 403 de YouTube
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': str(Path(self.output_dir) / '%(title)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'extract_flat': False,
                    'progress_hooks': [progress_hook],
                    'ffmpeg_location': str(Path(ffmpeg_path).parent),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'best',
                        'preferredquality': '0',
                    }],
                    'prefer_ffmpeg': True,
                    'keepvideo': False,
                    'writethumbnail': False,
                    'no_post_overwrites': False,
                    
                    # Soluciones para error 403 de YouTube
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web'],
                            'player_skip': ['webpage', 'configs'],
                        }
                    },
                    
                    # Headers para simular navegador real
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                        'Accept-Encoding': 'gzip, deflate',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    },
                    
                    # Opciones adicionales para estabilidad
                    'socket_timeout': 30,
                    'retries': 3,
                    'fragment_retries': 3,
                    'skip_unavailable_fragments': True,
                    'ignoreerrors': False,
                    'nocheckcertificate': False,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    # Get the downloaded file path - use yt-dlp's method
                    if 'entries' in info:
                        # Playlist
                        for entry in info['entries']:
                            if entry:
                                # Use yt-dlp's prepare_filename to get the actual output file
                                filename = ydl.prepare_filename(entry)
                                # Check if file exists as-is
                                if os.path.exists(filename):
                                    downloaded_files.append(filename)
                                    self.progress.emit(f"Descargado: {os.path.basename(filename)}")
                                else:
                                    # The postprocessor changes the extension
                                    base = os.path.splitext(filename)[0]
                                    # Try common audio extensions
                                    for ext in ['.opus', '.m4a', '.mp3', '.webm', '.ogg', '.wav', '.flac', '.aac']:
                                        potential_file = base + ext
                                        if os.path.exists(potential_file):
                                            downloaded_files.append(potential_file)
                                            self.progress.emit(f"Descargado: {os.path.basename(potential_file)}")
                                            break
                    else:
                        # Single video
                        filename = ydl.prepare_filename(info)
                        # Check if file exists as-is
                        if os.path.exists(filename):
                            downloaded_files.append(filename)
                            self.progress.emit(f"Descargado: {os.path.basename(filename)}")
                        else:
                            # The postprocessor changes the extension
                            base = os.path.splitext(filename)[0]
                            # Try common audio extensions
                            for ext in ['.opus', '.m4a', '.mp3', '.webm', '.ogg', '.wav', '.flac', '.aac']:
                                potential_file = base + ext
                                if os.path.exists(potential_file):
                                    downloaded_files.append(potential_file)
                                    self.progress.emit(f"Descargado: {os.path.basename(potential_file)}")
                                    break
                
            except Exception as e:
                error_msg = str(e)
                self.progress.emit(f"Error descargando {url}: {error_msg}")
                
                # Detectar errores específicos y dar soluciones
                if "403" in error_msg or "Forbidden" in error_msg:
                    self.progress.emit("⚠️ Error 403: YouTube bloqueó la descarga.")
                    self.progress.emit("💡 Solución: Actualiza yt-dlp con: pip install -U yt-dlp")
                elif "429" in error_msg or "Too Many Requests" in error_msg:
                    self.progress.emit("⚠️ Demasiadas peticiones. Espera unos minutos.")
                elif "Private video" in error_msg or "unavailable" in error_msg:
                    self.progress.emit("⚠️ El video es privado o no está disponible.")
        
        if downloaded_files:
            self.finished.emit(True, f"Descargados {len(downloaded_files)} archivo(s)", downloaded_files)
        else:
            # Mensaje más descriptivo si no se descargó nada
            if any("403" in str(e) for e in []):  # Simplificado
                error_detail = ("No se descargó ningún archivo.\n\n"
                               "Si obtuviste errores 403 de YouTube:\n"
                               "1. Actualiza yt-dlp: pip install -U yt-dlp\n"
                               "2. Reinicia la aplicación\n"
                               "3. Intenta de nuevo")
            else:
                error_detail = "No se descargó ningún archivo. Revisa los errores arriba."
            
            self.finished.emit(False, error_detail, [])


# ---------------------------
# Worker Thread
# ---------------------------

class ConvertWorker(QThread):
    progress_file = Signal(int, float)  # index, percent
    file_done = Signal(int, bool, str)  # index, success, message
    all_done = Signal()

    def __init__(self, tasks: List[dict], ffmpeg_path: str, ffprobe_path: str):
        super().__init__()
        self.tasks = tasks
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
        self._stop = False
        self._stop_lock = Lock()

    def stop(self):
        with self._stop_lock:
            self._stop = True
    
    def is_stopped(self) -> bool:
        with self._stop_lock:
            return self._stop

    def run(self):
        for idx, task in enumerate(self.tasks):
            if self.is_stopped():
                break

            in_f = task["input"]
            out_f = task["output"]
            codec = task["codec"]
            params = task["params"]  # dict
            smart_copy = task.get("smart_copy", True)

            # Ensure output folder exists
            Path(out_f).parent.mkdir(parents=True, exist_ok=True)

            # Probe duration for progress
            dur = duration_seconds(self.ffprobe_path, in_f)
            dur = max(dur, 0.001)

            # Optional smart-copy: if container+codec already match and no resample requested, do stream copy
            if smart_copy and qp.can_stream_copy(in_f, out_f, self.ffprobe_path, codec, params):
                cmd = [
                    self.ffmpeg_path, "-y", "-hide_banner", "-nostdin",
                    "-i", in_f, "-map", "0:a:0", "-c:a", "copy",
                ]
                if task["params"].get("copy_meta", True):
                    cmd += ["-map_metadata", "0", "-map_chapters", "0", "-map", "0:v:0?"]
                    if codec == "mp3":
                        cmd += ["-c:v", "mjpeg", "-id3v2_version", "3", "-write_id3v1", "1", "-disposition:v", "attached_pic"]
                    else:
                        cmd += ["-c:v", "copy", "-disposition:v", "attached_pic"]

                cmd += [out_f]
                # Run without progress since copy is instant
                p = subprocess.run(cmd, capture_output=True, text=True)
                ok = (p.returncode == 0)
                self.file_done.emit(idx, ok, "copiado sin recodificar" if ok else p.stderr.strip())
                continue

            # Build filterchain and codec options
            codec_args, container_ext = qp.build_codec_args(codec, params, ffprobe=self.ffprobe_path, in_file=in_f)

            # Prepare progress via -progress pipe:1
            # Base mapping
            cmd_base = [self.ffmpeg_path, "-y", "-hide_banner", "-nostdin", "-i", in_f, "-map", "0:a:0"]

            # Copiar metadatos
            if params.get("copy_meta", True):
                cmd_base += ["-map_metadata", "0", "-map_chapters", "0"]

            # Portada sólo si el contenedor lo soporta
            if params.get("copy_meta", True) and qp.supports_cover(codec):
                cmd_base += ["-map", "0:v:0?"]
                if codec == "mp3":
                    cmd_base += ["-c:v", "mjpeg", "-id3v2_version", "3", "-write_id3v1", "1", "-disposition:v", "attached_pic"]
                else:
                    cmd_base += ["-c:v", "copy", "-disposition:v", "attached_pic"]

            cmd         = cmd_base + codec_args + [out_f]
            cmd_progress= cmd_base + ["-progress", "pipe:1"] + codec_args + [out_f]

            try:
                with subprocess.Popen(cmd_progress, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1) as proc:
                    last_time = 0.0
                    for line in proc.stdout:
                        if self.is_stopped():
                            proc.terminate()
                            try:
                                proc.wait(timeout=2)
                            except subprocess.TimeoutExpired:
                                proc.kill()
                                proc.wait()
                            break
                        line = line.strip()
                        if line.startswith("out_time_ms"):
                            try:
                                micro = float(line.split("=")[1])
                                secs = micro / 1_000_000.0
                                last_time = secs
                                pct = min(100, max(0, (secs / dur) * 100.0))
                                self.progress_file.emit(idx, pct)
                            except:
                                pass
                        elif line == "progress=end":
                            self.progress_file.emit(idx, 100.0)
                    proc.wait()
                    ok = (proc.returncode == 0)
                    # On failure, capture stderr (limited to avoid memory issues)
                    stderr = ""
                    if proc.stderr:
                        stderr_lines = proc.stderr.read().strip().split('\n')
                        # Keep only last 20 lines to avoid memory issues with large outputs
                        stderr = '\n'.join(stderr_lines[-20:])
                    self.file_done.emit(idx, ok, "ok" if ok else stderr)
            except subprocess.TimeoutExpired:
                if proc.poll() is None:
                    proc.kill()
                    proc.wait()
                self.file_done.emit(idx, False, "Proceso cancelado o timeout")
            except Exception as e:
                self.file_done.emit(idx, False, str(e))

        self.all_done.emit()


# ---------------------------
# Main Window
# ---------------------------

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Converter • Calidad Máxima por Defecto")
        self.resize(900, 600)

        self.ffmpeg = find_ffmpeg()
        self.ffprobe = find_ffprobe()

        if not self.ffmpeg or not self.ffprobe:
            QMessageBox.critical(self, "FFmpeg no encontrado",
                                 "No se encontró FFmpeg/FFprobe.\n"
                                 "Añade ffmpeg a PATH o coloca los binarios en ./bin junto al ejecutable.")
        self.worker: Optional[ConvertWorker] = None
        self.download_worker: Optional[DownloadWorker] = None
        
        # Verificar actualización de yt-dlp al inicio (solo una vez al día)
        if YT_DLP_AVAILABLE:
            self.check_and_update_ytdlp()

        # Widgets
        self.list_files = QListWidget()

        btn_add = QPushButton("Añadir archivos")
        btn_add.clicked.connect(self.add_files)
        btn_add_dir = QPushButton("Añadir carpeta")
        btn_add_dir.clicked.connect(self.add_folder)
        btn_rm = QPushButton("Quitar seleccionados")
        btn_rm.clicked.connect(self.remove_selected)
        btn_clear = QPushButton("Limpiar lista")
        btn_clear.clicked.connect(self.list_files.clear)
        
        # Download from URL section
        self.url_input = QTextEdit()
        self.url_input.setPlaceholderText("Introduce URL(s) para descargar (una por línea)\nEjemplo: https://www.youtube.com/watch?v=...")
        self.url_input.setMaximumHeight(80)
        
        self.chk_convert_downloaded = QCheckBox("Convertir archivos descargados")
        self.chk_convert_downloaded.setChecked(False)
        self.chk_convert_downloaded.setToolTip("Si está marcado, los archivos descargados se añadirán a la lista para convertir.\nSi no, se guardarán directamente en su formato original.")
        
        btn_download = QPushButton("Descargar desde URL")
        btn_download.clicked.connect(self.start_download)
        
        self.download_progress_label = QLabel("")
        self.download_progress_label.setWordWrap(True)

        # Output path
        self.out_dir_line = QLineEdit()
        self.out_dir_line.setPlaceholderText("Carpeta de salida…")
        btn_out = QPushButton("Elegir…")
        btn_out.clicked.connect(self.choose_out_dir)

        # Format and quality
        self.format_combo = QComboBox()
        self.format_combo.addItems(qp.SUPPORTED_FORMATS_DISPLAY)

        self.quality_mode = QComboBox()
        self.quality_mode.addItems(["Máxima (recomendada)", "Personalizada"])

        # Advanced parameters group
        adv_group = QGroupBox("Parámetros avanzados (solo si eliges Personalizada)")
        form = QFormLayout()

        self.spin_bitrate = QSpinBox()
        self.spin_bitrate.setRange(32, 1024)
        self.spin_bitrate.setValue(320)  # kbps
        form.addRow("Bitrate (kbps):", self.spin_bitrate)

        self.spin_vbr_q = QSpinBox()
        self.spin_vbr_q.setRange(0, 10)
        self.spin_vbr_q.setValue(0)  # e.g., LAME V0
        form.addRow("Calidad VBR (0=mejor):", self.spin_vbr_q)

        self.spin_samplerate = QSpinBox()
        self.spin_samplerate.setRange(0, 384000)           # <- mínimo 0
        self.spin_samplerate.setSpecialValueText("0 = mantener")
        self.spin_samplerate.setSuffix(" Hz")
        self.spin_samplerate.setSingleStep(1000)
        self.spin_samplerate.setValue(0)                   # por defecto 0
        form.addRow("Sample rate (Hz, 0=mantener):", self.spin_samplerate)

        self.spin_channels = QSpinBox()
        self.spin_channels.setRange(0, 8)
        self.spin_channels.setValue(0)  # 0 = mantener
        form.addRow("Canales (0=mantener):", self.spin_channels)

        self.chk_soxr = QCheckBox("Resampling SOXR de alta calidad")
        self.chk_soxr.setChecked(True)
        form.addRow("", self.chk_soxr)

        self.chk_smart_copy = QCheckBox("Copiar sin recodificar cuando sea posible")
        self.chk_smart_copy.setChecked(True)
        form.addRow("", self.chk_smart_copy)

        self.chk_copy_meta = QCheckBox("Conservar metadatos y carátula")
        self.chk_copy_meta.setChecked(True)
        form.addRow("", self.chk_copy_meta)


        adv_group.setLayout(form)

        # Progress labels and bars
        self.lbl_current_file = QLabel("")
        self.lbl_current_file.setWordWrap(True)
        self.lbl_current_file.setStyleSheet("font-weight: bold; color: #0066cc;")
        
        self.progress_current = QProgressBar()
        self.progress_current.setRange(0, 100)
        self.progress_current.setFormat("Progreso individual: %p%")
        self.progress_current.setTextVisible(True)
        
        self.lbl_total_status = QLabel("")
        self.lbl_total_status.setWordWrap(True)
        
        self.progress_overall = QProgressBar()
        self.progress_overall.setRange(0, 100)
        self.progress_overall.setFormat("Progreso total: %p%")
        self.progress_overall.setTextVisible(True)

        # Convert controls
        btn_start = QPushButton("Convertir")
        btn_start.clicked.connect(self.start_convert)
        
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.cancel_operation)
        self.btn_cancel.setEnabled(False)
        # self.btn_cancel.setStyleSheet("background-color: #cc0000; color: white; font-weight: bold;")

        # Layouts
        left = QVBoxLayout()
        
        # Download section
        download_group = QGroupBox("Descargar desde Internet")
        download_layout = QVBoxLayout()
        download_layout.addWidget(QLabel("URL(s) para descargar:"))
        download_layout.addWidget(self.url_input)
        download_layout.addWidget(self.chk_convert_downloaded)
        download_layout.addWidget(btn_download)
        download_layout.addWidget(self.download_progress_label)
        download_group.setLayout(download_layout)
        left.addWidget(download_group)
        
        left.addWidget(QLabel("Archivos a convertir"))
        left.addWidget(self.list_files)
        hbtns = QHBoxLayout()
        for b in (btn_add, btn_add_dir, btn_rm, btn_clear):
            hbtns.addWidget(b)
        left.addLayout(hbtns)

        right = QVBoxLayout()
        # Output dir
        out_h = QHBoxLayout()
        out_h.addWidget(QLabel("Salida:"))
        out_h.addWidget(self.out_dir_line, 1)
        out_h.addWidget(btn_out)
        right.addLayout(out_h)

        # Format + quality
        fmt_h = QHBoxLayout()
        fmt_h.addWidget(QLabel("Formato destino:"))
        fmt_h.addWidget(self.format_combo)
        fmt_h.addWidget(QLabel("Modo de calidad:"))
        fmt_h.addWidget(self.quality_mode)
        right.addLayout(fmt_h)

        right.addWidget(adv_group)
        
        # Progress section with labels
        progress_group = QGroupBox("Progreso")
        progress_layout = QVBoxLayout()
        progress_layout.addWidget(QLabel("Archivo actual:"))
        progress_layout.addWidget(self.lbl_current_file)
        progress_layout.addWidget(self.progress_current)
        progress_layout.addWidget(QLabel("Progreso total:"))
        progress_layout.addWidget(self.lbl_total_status)
        progress_layout.addWidget(self.progress_overall)
        progress_group.setLayout(progress_layout)
        
        right.addWidget(progress_group)
        
        # Buttons layout
        buttons_h = QHBoxLayout()
        buttons_h.addWidget(btn_start)
        buttons_h.addWidget(self.btn_cancel)
        right.addLayout(buttons_h)

        root = QHBoxLayout()
        w = QWidget()
        root.addLayout(left, 1)
        root.addLayout(right, 1)
        w.setLayout(root)
        self.setCentralWidget(w)

        self.quality_mode.currentIndexChanged.connect(self.on_quality_mode_changed)
        self.on_quality_mode_changed()

    def on_quality_mode_changed(self):
        is_custom = (self.quality_mode.currentText().startswith("Personalizada"))
        # Enable/disable advanced fields
        for wid in [self.spin_bitrate, self.spin_vbr_q, self.spin_samplerate, self.spin_channels, self.chk_soxr]:
            wid.setEnabled(is_custom)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Selecciona archivos de audio")
        for f in files:
            # Validar existencia y permisos
            if not os.path.exists(f):
                QMessageBox.warning(self, "Archivo no encontrado", 
                                  f"No se puede acceder a:\n{f}")
                continue
            
            if not os.access(f, os.R_OK):
                QMessageBox.warning(self, "Sin permisos", 
                                  f"No se puede leer:\n{f}")
                continue
            
            # Evitar duplicados
            items = [self.list_files.item(i).text() 
                    for i in range(self.list_files.count())]
            if f not in items:
                self.list_files.addItem(f)

    def add_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecciona carpeta")
        if folder:
            exts = {".wav",".aiff",".aif",".flac",".mp3",".m4a",".aac",".ogg",".opus",".wma",".mka",".mkv",".mp4",".mov"}
            for root, _, files in os.walk(folder):
                for name in files:
                    if os.path.splitext(name)[1].lower() in exts:
                        self.list_files.addItem(os.path.join(root, name))

    def remove_selected(self):
        for item in self.list_files.selectedItems():
            self.list_files.takeItem(self.list_files.row(item))

    def choose_out_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Selecciona carpeta de salida")
        if d:
            self.out_dir_line.setText(d)

    def build_tasks(self) -> Tuple[List[dict], str]:
        fmt_display = self.format_combo.currentText()
        fmt_key = qp.DISPLAY_TO_KEY[fmt_display]

        out_root = self.out_dir_line.text().strip()
        if not out_root:
            out_root = str(Path.cwd() / "output")
        Path(out_root).mkdir(parents=True, exist_ok=True)

        is_custom = (self.quality_mode.currentText().startswith("Personalizada"))
        params = {}
        if is_custom:
            params = {
                "bitrate_k": int(self.spin_bitrate.value()),
                "vbr_q": int(self.spin_vbr_q.value()),
                "samplerate": int(self.spin_samplerate.value()),
                "channels": int(self.spin_channels.value()),
                "use_soxr": bool(self.chk_soxr.isChecked()),
                "mode": "custom",
                "copy_meta": bool(self.chk_copy_meta.isChecked())
            }
        else:
            params = {"mode": "max", "copy_meta": bool(self.chk_copy_meta.isChecked())}

        smart_copy = bool(self.chk_smart_copy.isChecked())

        tasks = []
        for i in range(self.list_files.count()):
            in_f = self.list_files.item(i).text()
            ext = qp.EXT_FOR_FORMAT[fmt_key]
            rel = Path(in_f).name
            rel = os.path.splitext(rel)[0] + ext
            out_f = str(Path(out_root) / rel)
            tasks.append({
                "input": in_f,
                "output": out_f,
                "codec": fmt_key,
                "params": params,
                "smart_copy": smart_copy
            })
        return tasks, out_root

    def start_convert(self):
        """Inicia conversión con validaciones y mensajes al usuario"""
        if not self.ffmpeg or not self.ffprobe:
            QMessageBox.critical(self, "FFmpeg no encontrado",
                                 "No se encontró FFmpeg/FFprobe.\n"
                                 "Añade ffmpeg a PATH o coloca los binarios en ./bin junto al ejecutable.")
            return

        if self.list_files.count() == 0:
            QMessageBox.information(self, "Nada que hacer", "Añade al menos un archivo.")
            return

        # Validar carpeta de salida
        out_dir = self.out_dir_line.text().strip()
        if out_dir:
            try:
                Path(out_dir).mkdir(parents=True, exist_ok=True)
                # Test write permissions
                test_file = Path(out_dir) / ".write_test"
                test_file.touch()
                test_file.unlink()
            except PermissionError:
                QMessageBox.critical(self, "Sin permisos",
                                   f"No se puede escribir en:\n{out_dir}")
                return
            except Exception as e:
                QMessageBox.critical(self, "Error de acceso", 
                                   f"Error al acceder a carpeta de salida:\n{str(e)}")
                return

        self.start_convert_internal()
    
    def start_convert_internal(self):
        """Inicia conversión sin validaciones (para uso interno/automático)"""
        if not self.ffmpeg or not self.ffprobe or self.list_files.count() == 0:
            return

        tasks, out_root = self.build_tasks()
        self.progress_current.setValue(0)
        self.progress_overall.setValue(0)
        self.lbl_current_file.setText("")
        self.lbl_total_status.setText("")

        # Store input files for potential cleanup after automatic conversion
        self._conversion_input_files = []
        for task in tasks:
            self._conversion_input_files.append(task["input"])

        self.worker = ConvertWorker(tasks, self.ffmpeg, self.ffprobe)
        self.worker.progress_file.connect(self.on_file_progress)
        self.worker.file_done.connect(self.on_file_done)
        self.worker.all_done.connect(self.on_all_done)
        self._files_total = len(tasks)
        self._files_done = 0
        self._conversion_success_count = 0

        self.set_ui_enabled(False)
        self.worker.start()

    def on_file_progress(self, index: int, percent: float):
        # Update current file info
        if index < self.list_files.count():
            filename = os.path.basename(self.list_files.item(index).text())
            self.lbl_current_file.setText(f"Convirtiendo: {filename}")
        
        self.progress_current.setValue(int(percent))
        
        # Update overall as average of completed + current
        pct = int((self._files_done * 100 + percent) / max(1, self._files_total))
        self.progress_overall.setValue(pct)
        self.lbl_total_status.setText(f"Archivo {self._files_done + 1} de {self._files_total}")

    def on_file_done(self, index: int, success: bool, message: str):
        self._files_done += 1
        self.progress_current.setValue(100)
        pct = int((self._files_done * 100) / max(1, self._files_total))
        self.progress_overall.setValue(pct)
        self.lbl_total_status.setText(f"Completados: {self._files_done} de {self._files_total}")
        
        # Track successful conversions for automatic cleanup
        if success:
            if not hasattr(self, '_conversion_success_count'):
                self._conversion_success_count = 0
            self._conversion_success_count += 1
        else:
            QMessageBox.warning(self, "Error en conversión", f"Archivo #{index+1}: {message}")

    def on_all_done(self):
        self.set_ui_enabled(True)
        self.lbl_current_file.setText("✓ Conversión completada")
        self.lbl_total_status.setText(f"✓ Completados: {self._files_total} de {self._files_total}")
        
        # Check if this was an automatic conversion after download
        if hasattr(self, '_will_convert') and self._will_convert:
            # Delete original downloaded files after successful conversion
            deleted_count = 0
            if hasattr(self, '_conversion_input_files'):
                for input_file in self._conversion_input_files:
                    try:
                        if os.path.exists(input_file):
                            os.remove(input_file)
                            deleted_count += 1
                    except Exception as e:
                        # Si no se puede eliminar, continuar sin error crítico
                        print(f"No se pudo eliminar {input_file}: {e}")
            
            # Clear the list after automatic conversion
            self.list_files.clear()
            
            success_count = getattr(self, '_conversion_success_count', 0)
            message = f"Descarga y conversión finalizadas.\n\n"
            message += f"✓ Convertidos: {success_count} archivo(s)\n"
            if deleted_count > 0:
                message += f"✓ Archivos temporales eliminados: {deleted_count}"
            
            QMessageBox.information(self, "Proceso completado", message)
            self._will_convert = False  # Reset flag
            self._conversion_input_files = []  # Clear list
        else:
            QMessageBox.information(self, "Listo", "Conversión finalizada.")

    def set_ui_enabled(self, en: bool):
        self.findChild(QListWidget).setEnabled(en)
        for btn in self.findChildren(QPushButton):
            # No deshabilitar el botón cancelar, solo habilitarlo/deshabilitarlo inversamente
            if btn != self.btn_cancel:
                btn.setEnabled(en)
        for cb in self.findChildren(QComboBox):
            cb.setEnabled(en)
        for sp in self.findChildren(QSpinBox):
            sp.setEnabled(en)
        for le in self.findChildren(QLineEdit):
            le.setEnabled(en)
        for chk in self.findChildren(QCheckBox):
            chk.setEnabled(en)
        
        # Habilitar botón cancelar solo durante operaciones
        self.btn_cancel.setEnabled(not en)
    
    def cancel_operation(self):
        """Cancela la operación en curso (descarga o conversión)"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self, "Cancelar conversión",
                "¿Deseas cancelar la conversión en curso?\n\nLos archivos ya convertidos se mantendrán.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.worker.stop()
                self.lbl_current_file.setText("✗ Conversión cancelada por el usuario")
                self.btn_cancel.setEnabled(False)
        
        if self.download_worker and self.download_worker.isRunning():
            reply = QMessageBox.question(
                self, "Cancelar descarga",
                "¿Deseas cancelar la descarga en curso?\n\nLos archivos ya descargados se mantendrán.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.download_worker.stop()
                self.lbl_current_file.setText("✗ Descarga cancelada por el usuario")
                self.btn_cancel.setEnabled(False)
    
    def check_and_update_ytdlp(self):
        """Verifica y actualiza yt-dlp si es necesario (solo una vez al día)"""
        try:
            needs_update, current_ver, message = check_ytdlp_update()
            
            if needs_update:
                # Mostrar diálogo con información de actualización
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Actualización de yt-dlp disponible")
                msg.setText(f"Se ha detectado una nueva versión de yt-dlp.\n\n{message}")
                msg.setInformativeText(
                    "Se recomienda actualizar para evitar errores al descargar de YouTube.\n\n"
                    "¿Deseas actualizar ahora? (tardará unos segundos)"
                )
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                msg.setDefaultButton(QMessageBox.Yes)
                
                if msg.exec() == QMessageBox.Yes:
                    # Mostrar mensaje de progreso
                    progress_msg = QMessageBox(self)
                    progress_msg.setIcon(QMessageBox.Information)
                    progress_msg.setWindowTitle("Actualizando yt-dlp")
                    progress_msg.setText("Actualizando yt-dlp, por favor espera...")
                    progress_msg.setStandardButtons(QMessageBox.NoButton)
                    progress_msg.setModal(True)
                    progress_msg.show()
                    QApplication.processEvents()
                    
                    # Realizar actualización
                    success, update_msg = update_ytdlp_silent()
                    progress_msg.close()
                    
                    if success:
                        QMessageBox.information(
                            self, "Actualización completada",
                            f"✓ {update_msg}\n\n"
                            "yt-dlp se ha actualizado correctamente."
                        )
                    else:
                        QMessageBox.warning(
                            self, "Error de actualización",
                            f"No se pudo actualizar yt-dlp:\n\n{update_msg}\n\n"
                            "Puedes intentar actualizar manualmente con:\n"
                            "pip install --upgrade yt-dlp"
                        )
            elif message:  # Hay mensaje pero no necesita actualización (ya está actualizado)
                # Solo mostrar en caso de primera comprobación del día
                pass  # No molestar al usuario si ya está actualizado
                
        except Exception as e:
            # Fallo silencioso: no interrumpir el inicio de la app por errores de actualización
            print(f"Error al verificar actualización de yt-dlp: {e}")
    
    def closeEvent(self, event):
        """Limpieza al cerrar la aplicación"""
        # Verificar si hay operaciones en curso
        worker_running = self.worker and self.worker.isRunning()
        download_running = self.download_worker and self.download_worker.isRunning()
        
        if worker_running or download_running:
            reply = QMessageBox.question(
                self, "Operación en curso",
                "Hay una operación en progreso.\n¿Deseas cancelarla y salir?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
            
            # Detener hilos activos
            if worker_running:
                self.worker.stop()
                self.worker.wait(5000)  # Esperar máx 5 segundos
                if self.worker.isRunning():
                    self.worker.terminate()
            
            if download_running:
                self.download_worker.stop()
                self.download_worker.wait(5000)
                if self.download_worker.isRunning():
                    self.download_worker.terminate()
        
        event.accept()
    
    def start_download(self):
        if not YT_DLP_AVAILABLE:
            QMessageBox.critical(self, "yt-dlp no encontrado",
                               "yt-dlp no está instalado.\n\n"
                               "Instálalo con: pip install yt-dlp")
            return
        
        # Verificar versión de yt-dlp (opcional pero recomendado)
        try:
            import yt_dlp
            yt_dlp_version = yt_dlp.version.__version__
        except:
            yt_dlp_version = "desconocida"
        
        url_text = self.url_input.toPlainText().strip()
        if not url_text:
            QMessageBox.information(self, "Sin URLs", "Introduce al menos una URL para descargar.")
            return
        
        # Parse URLs (one per line)
        urls = [line.strip() for line in url_text.split('\n') if line.strip()]
        
        # Determine output directory
        out_dir = self.out_dir_line.text().strip()
        if not out_dir:
            out_dir = str(Path.cwd() / "downloads")
        
        # Reset progress bars
        self.progress_current.setValue(0)
        self.progress_overall.setValue(0)
        self.lbl_current_file.setText("Iniciando descarga...")
        self.lbl_total_status.setText(f"0 de {len(urls)} URLs descargadas")
        self.download_progress_label.setText("Preparando descarga...")
        
        self._download_total = len(urls)
        self._download_done = 0
        self._will_convert = self.chk_convert_downloaded.isChecked()
        
        self.set_ui_enabled(False)
        
        self.download_worker = DownloadWorker(urls, out_dir)
        self.download_worker.progress.connect(self.on_download_progress)
        self.download_worker.progress_percent.connect(self.on_download_percent)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.start()
    
    def on_download_progress(self, message: str):
        self.download_progress_label.setText(message)
        self.lbl_current_file.setText(message)
    
    def on_download_percent(self, index: int, percent: float):
        # Update individual progress
        self.progress_current.setValue(int(percent))
        
        # If download is complete for this file, increment counter
        if percent >= 100.0 and index >= self._download_done:
            self._download_done = index + 1
        
        # Update overall progress
        overall_pct = int((self._download_done * 100 + percent) / max(1, self._download_total))
        self.progress_overall.setValue(overall_pct)
        self.lbl_total_status.setText(f"Descargadas: {self._download_done} de {self._download_total}")
    
    def on_download_finished(self, success: bool, message: str, files: List[str]):
        self.download_progress_label.setText("")
        
        if success:
            # Update progress indicators
            self.progress_overall.setValue(100)
            self.lbl_total_status.setText(f"✓ Descargadas: {len(files)} de {self._download_total}")
            
            if self.chk_convert_downloaded.isChecked():
                # Add downloaded files to conversion list
                for f in files:
                    self.list_files.addItem(f)
                
                self.lbl_current_file.setText("✓ Descarga completada. Iniciando conversión automática...")
                
                # Clear URL input
                self.url_input.clear()
                
                # Start conversion automatically (without re-enabling UI)
                # The UI will be enabled when conversion finishes
                self.start_convert_internal()
            else:
                # Solo descargar, sin convertir
                self.set_ui_enabled(True)
                self.lbl_current_file.setText("✓ Descarga completada")
                
                # Mostrar archivos descargados
                files_list = "\n".join([os.path.basename(f) for f in files[:5]])
                if len(files) > 5:
                    files_list += f"\n... y {len(files) - 5} más"
                
                QMessageBox.information(
                    self, "Descarga completada", 
                    f"Se descargaron {len(files)} archivo(s):\n\n{files_list}\n\n"
                    f"Guardados en: {self.out_dir_line.text() or './downloads'}"
                )
                self.url_input.clear()
        else:
            # ERROR en descarga
            self.set_ui_enabled(True)
            self.lbl_current_file.setText("✗ Error en descarga")
            self.progress_overall.setValue(0)
            self.progress_current.setValue(0)
            QMessageBox.warning(self, "Error en descarga", message)


def main():
    # CRÍTICO: Protección para evitar múltiples instancias en Windows
    # Esto es necesario cuando se usa multiprocessing o subprocess en ejecutables
    if sys.platform.startswith('win'):
        import multiprocessing
        multiprocessing.freeze_support()
    
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
