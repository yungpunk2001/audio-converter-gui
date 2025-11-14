# Audio Converter GUI

![Release](https://img.shields.io/github/v/release/yungpunk2001/audio-converter-gui?style=flat-square)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg?style=flat-square)

**[⬇️ Descargar la última versión](https://github.com/yungpunk2001/audio-converter-gui/releases/latest)** | **[📋 Ver todas las versiones](https://github.com/yungpunk2001/audio-converter-gui/releases)** | **[📚 Documentación Completa](DOCUMENTATION.md)** | **[📝 Changelog](CHANGELOG.md)**

Programa sencillo para convertir audio con foco en **calidad máxima por defecto**.

---

## 📚 Documentación

- **[📖 DOCUMENTATION.md](DOCUMENTATION.md)** - Guía completa de uso, configuración y funcionamiento
- **[📝 CHANGELOG.md](CHANGELOG.md)** - Historial de cambios y actualizaciones
- **[🤝 CONTRIBUTING.md](CONTRIBUTING.md)** - Guía para contribuidores
- **[📋 RELEASE_NOTES.md](RELEASE_NOTES.md)** - Notas de la última versión

---

## 🚀 Inicio Rápido

### Opción 1: Ejecutable Portable (Recomendado)
1. **[Descarga AudioConverter.exe](https://github.com/yungpunk2001/audio-converter-gui/releases/latest)** (~290 MB)
2. Ejecuta el archivo (no requiere instalación)
3. ¡Listo! Comienza a convertir audio

> **💡 Versión Optimizada**: Usa `build_release_optimized.bat` para inicio ultra-rápido (< 1 segundo)

### Opción 2: Desde el Código Fuente
```bash
# 1. Clonar repositorio
git clone https://github.com/yungpunk2001/audio-converter-gui.git
cd audio-converter-gui

# 2. Crear entorno virtual
python -m venv .venv

# 3. Instalar dependencias
.venv\Scripts\pip install -r requirements.txt

# 4. Ejecutar
.venv\Scripts\python main.py
```

**Ver [DOCUMENTATION.md](DOCUMENTATION.md) para instrucciones detalladas de instalación y compilación.**

---

## ✨ Características Principales

- 🎵 **7 formatos de salida**: WAV, FLAC, ALAC, MP3, AAC, Opus, Ogg Vorbis
- 📥 **Descarga desde YouTube**: Integración con yt-dlp (YouTube, SoundCloud, etc.)
- 🖱️ **Drag & Drop**: Arrastra archivos o carpetas directamente
- ⚡ **Presets optimizados**: Máxima calidad por defecto para cada formato
- 🎛️ **Modo personalizado**: Control total sobre bitrate, sample rate y canales
- 🚀 **Smart Copy**: Evita recodificación innecesaria
- 📊 **Progreso dual**: Barras de progreso por archivo y total en tiempo real
- 🔄 **Auto-actualización**: Sistema automático de actualización de yt-dlp (previene errores HTTP 403)

---

## 🎵 Formatos Soportados

| Formato | Calidad por Defecto | Tipo | Tamaño Relativo |
|---------|---------------------|------|-----------------|
| **WAV** | PCM 16/24-bit | Sin pérdida | ⭐⭐⭐⭐⭐ (Grande) |
| **FLAC** | Hasta 24-bit | Sin pérdida | ⭐⭐⭐ (Medio) |
| **ALAC** | Hasta 24-bit | Sin pérdida | ⭐⭐⭐ (Medio) |
| **MP3** | LAME V0 (~245 kbps VBR) | Con pérdida | ⭐⭐ (Pequeño) |
| **AAC** | 256 kbps VBR | Con pérdida | ⭐⭐ (Pequeño) |
| **Opus** | 192 kbps VBR | Con pérdida | ⭐ (Muy pequeño) |
| **Vorbis** | Quality 7 (~224 kbps) | Con pérdida | ⭐⭐ (Pequeño) |

**Ver [DOCUMENTATION.md](DOCUMENTATION.md#formatos-soportados) para detalles técnicos completos.**

---

## 🎯 Filosofía de Calidad

> **"Calidad primero, simplicidad siempre"**

### Presets por Defecto = Máxima Calidad

- **Formatos sin pérdida (WAV/FLAC/ALAC)**: Sin compresión destructiva, hasta 24-bit
- **MP3**: LAME V0 (`-q:a 0`) - Transparencia auditiva
- **AAC**: 256 kbps VBR - Calidad profesional
- **Opus**: 192 kbps VBR, complejidad 10 - Mejor relación calidad/tamaño
- **Vorbis**: Quality 7 (~224 kbps) - Excelente para gaming/streaming

### Características Avanzadas

- **Re-muestreo SOXR**: Máxima calidad cuando se cambia sample rate
- **Smart Copy**: Detecta si el archivo ya está en el formato objetivo y evita recodificación innecesaria
- **Modo Personalizado**: Control granular sobre todos los parámetros

**Ver [DOCUMENTATION.md](DOCUMENTATION.md#filosofía-de-calidad) para especificaciones técnicas detalladas.**

---

## Requisitos
- **Python 3.10+**
- **FFmpeg** y **FFprobe** accesibles:
  - **Opción 1**: Añade FFmpeg a tu `PATH` del sistema
  - **Opción 2**: Descarga FFmpeg desde [ffmpeg.org](https://ffmpeg.org/download.html) o [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) y coloca `ffmpeg.exe` y `ffprobe.exe` en la carpeta `./bin/` del proyecto
- **yt-dlp**: Para la funcionalidad de descarga de audio desde Internet (se instala automáticamente con `pip install -r requirements.txt`)

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

## Descarga desde Internet
La aplicación ahora incluye funcionalidad para descargar audio directamente desde URLs de plataformas como:
- **YouTube**: Usa yt-dlp para descargar audio en la mejor calidad disponible
- **SoundCloud**: Descarga en formato original
- **Muchas otras plataformas**: Cualquier sitio soportado por yt-dlp

### Cómo usar la descarga:
1. Introduce una o más URLs en el campo de texto (una por línea)
2. Selecciona si quieres convertir los archivos descargados o guardarlos directamente
3. Haz clic en "Descargar desde URL"
4. Los archivos se descargarán en la carpeta de salida especificada (o en `./downloads` por defecto)

Si marcas "Convertir archivos descargados", los archivos se añadirán automáticamente a la lista de conversión.

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
