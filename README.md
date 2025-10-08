# Audio Converter GUI (Windows)
Programa sencillo para convertir audio con foco en **calidad máxima por defecto**.

## Características
- Interfaz gráfica simple.
- Arrastra y suelta archivos o carpetas.
- Selecciona formato destino: WAV, FLAC, ALAC (sin pérdida), MP3 (LAME), AAC, Opus, Ogg Vorbis.
- Preset **Máxima (recomendada)** que elige parámetros de transparencia por formato.
- Modo **Personalizada** para ajustar bitrate, VBR, sample rate y canales.
- Opción de **copiar sin recodificar** si el archivo ya cumple el objetivo.
- Progreso por archivo y total. Usa `ffmpeg -progress`.

## Filosofía de calidad
- Si eliges un formato **sin pérdida**: no se añade compresión destructiva. FLAC/ALAC guardan hasta 24-bit. WAV usa PCM de alta calidad.
- Si eliges **con pérdida**:
  - **MP3**: LAME `-q:a 0` (V0) por defecto. Transparencia típica para música.
  - **AAC**: 256 kbps por defecto con el encoder nativo de FFmpeg. Si usas `libfdk_aac`, ajusta el comando a VBR 5.
  - **Opus**: 192 kbps VBR, complejidad 10.
  - **Vorbis**: `-q:a 7`.
- Re-muestreo con **SOXR** de alta calidad cuando procede.

## Requisitos
- **Python 3.10+**
- **FFmpeg** y **FFprobe** accesibles:
  - Añade a `PATH`, o
  - Coloca los binarios en `./bin/ffmpeg.exe` y `./bin/ffprobe.exe` junto al `.exe` final.

## Ejecutar en desarrollo
```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Empaquetar a .exe (PyInstaller)
Instala PyInstaller y genera un ejecutable portátil:
```bash
.venv\Scripts\pip install pyinstaller
.venv\Scripts\pyinstaller --noconfirm --clean ^
  --name AudioConverter ^
  --windowed ^
  --add-binary "bin\ffmpeg.exe;bin" ^
  --add-binary "bin\ffprobe.exe;bin" ^
  main.py
```
Coloca `ffmpeg.exe` y `ffprobe.exe` en `.\bin` antes de empaquetar. El `.exe` quedará en `dist\AudioConverter\`.

## Consejos de uso
- Para conservar **máxima calidad**, elige un destino **sin pérdida** si no necesitas compresión destructiva.
- Evita **re-encode** de con pérdida → con pérdida cuando sea posible. La opción “Copiar sin recodificar” se activará si el archivo ya está en el códec y contenedor objetivo sin cambios.

## Mapeo rápido de presets
- WAV: PCM 24-bit o float, sample rate y canales originales.
- FLAC/ALAC: hasta 24-bit, compresión sin pérdida.
- MP3: LAME V0 (`-q:a 0`) por defecto.
- AAC: 256 kbps por defecto (nativo). Con `libfdk_aac`, usa VBR 5.
- Opus: 192 kbps VBR, `-application audio`, complejidad 10.
- Vorbis: `-q:a 7`.

## Licencias
- Este proyecto usa **FFmpeg**, que tiene sus propias licencias (LGPL/GPL según build y códecs).
- Verifica la redistribución de binarios al empaquetar.
