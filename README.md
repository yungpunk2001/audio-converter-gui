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
  - **Opción 1**: Añade FFmpeg a tu `PATH` del sistema
  - **Opción 2**: Descarga FFmpeg desde [ffmpeg.org](https://ffmpeg.org/download.html) o [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) y coloca `ffmpeg.exe` y `ffprobe.exe` en la carpeta `./bin/` del proyecto

## Ejecutar en desarrollo
```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python main.py
```

## Empaquetar a .exe (PyInstaller)

**Antes de empaquetar**: Descarga FFmpeg y coloca `ffmpeg.exe` y `ffprobe.exe` en la carpeta `.\bin\`

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

El `.exe` quedará en `dist\AudioConverter\`.

### Descarga de FFmpeg
- Windows: https://www.gyan.dev/ffmpeg/builds/ (elige "ffmpeg-release-essentials.zip")
- Extrae `ffmpeg.exe` y `ffprobe.exe` de la carpeta `bin` del archivo descargado

## Consejos de uso
- Para conservar **máxima calidad**, elige un destino **sin pérdida** si no necesitas compresión destructiva.
- Evita **re-encode** de con pérdida → con pérdida cuando sea posible. La opción “Copiar sin recodificar” se activará si el archivo ya está en el códec y contenedor objetivo sin cambios.

## Mapeo rápido de presets
- **WAV**: PCM 24-bit o float, sample rate y canales originales.
- **FLAC/ALAC**: hasta 24-bit, compresión sin pérdida.
- **MP3**: LAME V0 (`-q:a 0`) por defecto, transparencia auditiva.
- **AAC**: 256 kbps VBR con encoder nativo de FFmpeg.
- **Opus**: 192 kbps VBR, complejidad 10, ideal para todo tipo de audio.
- **Vorbis**: Quality 7 (~224 kbps), excelente relación calidad/tamaño.

## Estructura del proyecto
```
audio-converter-gui/
├── main.py              # Interfaz gráfica y lógica principal
├── quality_presets.py   # Presets de calidad y parámetros de FFmpeg
├── requirements.txt     # Dependencias Python
├── build_windows.bat    # Script para compilar a .exe
├── README.md           # Esta documentación
├── LICENSE             # Licencia MIT
└── bin/                # Binarios de FFmpeg (no incluidos, ver bin/README.md)
    └── README.md       # Instrucciones para descargar FFmpeg
```

## Contribuciones
¡Las contribuciones son bienvenidas! Si encuentras un bug o tienes una sugerencia:
1. Abre un [Issue](https://github.com/yungpunk2001/audio-converter-gui/issues)
2. Haz un Fork del proyecto
3. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
4. Haz commit de tus cambios (`git commit -am 'Añade nueva funcionalidad'`)
5. Push a la rama (`git push origin feature/nueva-funcionalidad`)
6. Abre un Pull Request

## Licencia
Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Créditos
- **FFmpeg**: [ffmpeg.org](https://ffmpeg.org/) - Herramienta de procesamiento multimedia
- **PySide6**: Framework Qt para Python
- **PyInstaller**: Empaquetador de aplicaciones Python
- AAC: 256 kbps por defecto (nativo). Con `libfdk_aac`, usa VBR 5.
- Opus: 192 kbps VBR, `-application audio`, complejidad 10.
- Vorbis: `-q:a 7`.

## Licencias
- Este proyecto usa **FFmpeg**, que tiene sus propias licencias (LGPL/GPL según build y códecs).
- Verifica la redistribución de binarios al empaquetar.
