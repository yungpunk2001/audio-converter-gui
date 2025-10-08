# -*- coding: utf-8 -*-
import os
import sys
import shutil
import json
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
import tempfile

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

def find_ffmpeg() -> Optional[str]:
    """
    Return path to ffmpeg executable.
    Priority: local ./bin/ffmpeg(.exe) then PATH.
    """
    # Local bin
    local_bin = Path(getattr(sys, "_MEIPASS", Path.cwd())) / "bin"
    for candidate in ["ffmpeg.exe", "ffmpeg"]:
        p = local_bin / candidate
        if p.exists():
            return str(p)

    # PATH
    exe = shutil.which("ffmpeg")
    if exe:
        return exe

    # Windows PATH try common installs
    if os.name == "nt":
        common = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        ]
        for c in common:
            if os.path.exists(c):
                return c
    return None


def find_ffprobe() -> Optional[str]:
    # Mirror logic of ffmpeg
    local_bin = Path(getattr(sys, "_MEIPASS", Path.cwd())) / "bin"
    for candidate in ["ffprobe.exe", "ffprobe"]:
        p = local_bin / candidate
        if p.exists():
            return str(p)

    exe = shutil.which("ffprobe")
    if exe:
        return exe

    if os.name == "nt":
        common = [
            r"C:\ffmpeg\bin\ffprobe.exe",
            r"C:\Program Files\ffmpeg\bin\ffprobe.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffprobe.exe",
        ]
        for c in common:
            if os.path.exists(c):
                return c
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
    finished = Signal(bool, str, list)  # success, message, list of downloaded files
    
    def __init__(self, urls: List[str], output_dir: str):
        super().__init__()
        self.urls = urls
        self.output_dir = output_dir
        self._stop = False
    
    def stop(self):
        self._stop = True
    
    def run(self):
        if not YT_DLP_AVAILABLE:
            self.finished.emit(False, "yt-dlp no está instalado. Ejecuta: pip install yt-dlp", [])
            return
        
        downloaded_files = []
        
        # Create output directory
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        for url in self.urls:
            if self._stop:
                break
            
            try:
                self.progress.emit(f"Descargando de: {url}")
                
                # yt-dlp options for best audio quality
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': str(Path(self.output_dir) / '%(title)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'extract_flat': False,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'best',  # Keep original codec
                        'preferredquality': '0',   # Best quality
                    }],
                    'prefer_ffmpeg': True,
                    'keepvideo': False,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    # Get the downloaded file path
                    if 'entries' in info:
                        # Playlist
                        for entry in info['entries']:
                            if entry:
                                filename = ydl.prepare_filename(entry)
                                # The postprocessor changes the extension
                                base = os.path.splitext(filename)[0]
                                # Try common audio extensions
                                for ext in ['.opus', '.m4a', '.mp3', '.webm', '.ogg', '.wav', '.flac']:
                                    potential_file = base + ext
                                    if os.path.exists(potential_file):
                                        downloaded_files.append(potential_file)
                                        self.progress.emit(f"Descargado: {os.path.basename(potential_file)}")
                                        break
                    else:
                        # Single video
                        filename = ydl.prepare_filename(info)
                        base = os.path.splitext(filename)[0]
                        for ext in ['.opus', '.m4a', '.mp3', '.webm', '.ogg', '.wav', '.flac']:
                            potential_file = base + ext
                            if os.path.exists(potential_file):
                                downloaded_files.append(potential_file)
                                self.progress.emit(f"Descargado: {os.path.basename(potential_file)}")
                                break
                
            except Exception as e:
                self.progress.emit(f"Error descargando {url}: {str(e)}")
        
        if downloaded_files:
            self.finished.emit(True, f"Descargados {len(downloaded_files)} archivo(s)", downloaded_files)
        else:
            self.finished.emit(False, "No se descargó ningún archivo", [])


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

    def stop(self):
        self._stop = True

    def run(self):
        for idx, task in enumerate(self.tasks):
            if self._stop:
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
                        if self._stop:
                            proc.kill()
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
                    # On failure, capture stderr once
                    stderr = proc.stderr.read().strip() if proc.stderr else ""
                    self.file_done.emit(idx, ok, "ok" if ok else stderr)
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
        self.chk_convert_downloaded.setChecked(True)
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

        # Progress
        self.progress_overall = QProgressBar()
        self.progress_overall.setRange(0, 100)
        self.progress_overall.setFormat("Progreso total: %p%")

        self.progress_current = QProgressBar()
        self.progress_current.setRange(0, 100)
        self.progress_current.setFormat("Archivo actual: %p%")

        # Convert controls
        btn_start = QPushButton("Convertir")
        btn_start.clicked.connect(self.start_convert)

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
        right.addWidget(self.progress_current)
        right.addWidget(self.progress_overall)
        right.addWidget(btn_start)

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
        if not self.ffmpeg or not self.ffprobe:
            QMessageBox.critical(self, "FFmpeg no encontrado",
                                 "No se encontró FFmpeg/FFprobe.\n"
                                 "Añade ffmpeg a PATH o coloca los binarios en ./bin junto al ejecutable.")
            return

        if self.list_files.count() == 0:
            QMessageBox.information(self, "Nada que hacer", "Añade al menos un archivo.")
            return

        tasks, out_root = self.build_tasks()
        self.progress_current.setValue(0)
        self.progress_overall.setValue(0)

        self.worker = ConvertWorker(tasks, self.ffmpeg, self.ffprobe)
        self.worker.progress_file.connect(self.on_file_progress)
        self.worker.file_done.connect(self.on_file_done)
        self.worker.all_done.connect(self.on_all_done)
        self._files_total = len(tasks)
        self._files_done = 0

        self.set_ui_enabled(False)
        self.worker.start()

    def on_file_progress(self, index: int, percent: float):
        self.progress_current.setValue(int(percent))
        # Update overall as average of completed + current
        pct = int((self._files_done * 100 + percent) / max(1, self._files_total))
        self.progress_overall.setValue(pct)

    def on_file_done(self, index: int, success: bool, message: str):
        self._files_done += 1
        self.progress_current.setValue(100)
        pct = int((self._files_done * 100) / max(1, self._files_total))
        self.progress_overall.setValue(pct)
        if not success:
            QMessageBox.warning(self, "Error en conversión", f"Archivo #{index+1}: {message}")

    def on_all_done(self):
        self.set_ui_enabled(True)
        QMessageBox.information(self, "Listo", "Conversión finalizada.")

    def set_ui_enabled(self, en: bool):
        self.findChild(QListWidget).setEnabled(en)
        for btn in self.findChildren(QPushButton):
            btn.setEnabled(en)
        for cb in self.findChildren(QComboBox):
            cb.setEnabled(en)
        for sp in self.findChildren(QSpinBox):
            sp.setEnabled(en)
        for le in self.findChildren(QLineEdit):
            le.setEnabled(en)
        for chk in self.findChildren(QCheckBox):
            chk.setEnabled(en)
    
    def start_download(self):
        if not YT_DLP_AVAILABLE:
            QMessageBox.critical(self, "yt-dlp no encontrado",
                               "yt-dlp no está instalado.\n"
                               "Instálalo con: pip install yt-dlp")
            return
        
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
        
        self.download_progress_label.setText("Iniciando descarga...")
        self.set_ui_enabled(False)
        
        self.download_worker = DownloadWorker(urls, out_dir)
        self.download_worker.progress.connect(self.on_download_progress)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.start()
    
    def on_download_progress(self, message: str):
        self.download_progress_label.setText(message)
    
    def on_download_finished(self, success: bool, message: str, files: List[str]):
        self.set_ui_enabled(True)
        self.download_progress_label.setText("")
        
        if success:
            if self.chk_convert_downloaded.isChecked():
                # Add downloaded files to conversion list
                for f in files:
                    self.list_files.addItem(f)
                QMessageBox.information(self, "Descarga completada", 
                                      f"{message}\n\nLos archivos se han añadido a la lista de conversión.")
            else:
                # Files saved directly
                QMessageBox.information(self, "Descarga completada",
                                      f"{message}\n\nLos archivos se han guardado en:\n{self.out_dir_line.text() or str(Path.cwd() / 'downloads')}")
            # Clear URL input
            self.url_input.clear()
        else:
            QMessageBox.warning(self, "Error en descarga", message)


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
