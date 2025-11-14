# 📚 Documentación Completa - Audio Converter GUI

Guía completa de uso, configuración y funcionamiento de Audio Converter GUI.

---

## 📋 Índice

1. [Introducción](#introducción)
2. [Requisitos del Sistema](#requisitos-del-sistema)
3. [Instalación](#instalación)
4. [Guía de Uso](#guía-de-uso)
5. [Formatos Soportados](#formatos-soportados)
6. [Filosofía de Calidad](#filosofía-de-calidad)
7. [Características Avanzadas](#características-avanzadas)
8. [Descarga desde Internet](#descarga-desde-internet)
9. [Compilación del Ejecutable](#compilación-del-ejecutable)
10. [Solución de Problemas](#solución-de-problemas)
11. [Arquitectura Técnica](#arquitectura-técnica)
12. [Preguntas Frecuentes](#preguntas-frecuentes)

---

## Introducción

**Audio Converter GUI** es una aplicación de escritorio profesional para Windows diseñada para convertir archivos de audio entre diferentes formatos con **máxima calidad por defecto**.

### Características Principales

- 🎵 **Conversión entre 7 formatos**: WAV, FLAC, ALAC, MP3, AAC, Opus, Ogg Vorbis
- 📥 **Descarga desde YouTube**: Integración con yt-dlp para descargar audio de plataformas online
- 🖱️ **Drag & Drop**: Arrastra archivos o carpetas directamente
- ⚡ **Presets optimizados**: Configuraciones de máxima calidad para cada formato
- 🎛️ **Modo personalizado**: Control total sobre bitrate, sample rate y canales
- 🚀 **Smart Copy**: Evita recodificación innecesaria si el archivo ya está en el formato deseado
- 📊 **Progreso dual**: Barras de progreso por archivo y total
- 💾 **Ejecutable portable**: No requiere instalación, todo incluido

### Filosofía del Proyecto

> **Calidad primero, simplicidad siempre**

La aplicación está diseñada con dos principios:
1. **Configuración por defecto = máxima calidad** (transparencia auditiva)
2. **Interfaz simple** sin sacrificar potencia

---

## Requisitos del Sistema

### Ejecutable Portable (.exe)

- **Sistema Operativo**: Windows 10/11 (64-bit)
- **RAM**: 4 GB mínimo, 8 GB recomendado
- **Espacio en disco**: ~500 MB (incluye FFmpeg)
- **Permisos**: No requiere privilegios de administrador
- **Dependencias**: Ninguna (todo incluido en el ejecutable)

### Desde Código Fuente

- **Python**: 3.10 o superior
- **FFmpeg y FFprobe**: 
  - **Opción 1**: Instalados y accesibles en el PATH del sistema
  - **Opción 2**: Archivos `ffmpeg.exe` y `ffprobe.exe` en la carpeta `./bin/`
- **yt-dlp**: Incluido en `requirements.txt` (se instala automáticamente)
- **PySide6**: Framework de interfaz gráfica (incluido en requirements)

---

## Instalación

### Opción 1: Ejecutable Portable (Recomendado para Usuarios Finales)

1. **Descarga** la última versión desde [Releases](https://github.com/yungpunk2001/audio-converter-gui/releases/latest)
2. **Extrae** la carpeta completa (si es versión optimizada) o ejecuta directamente (si es versión onefile)
3. **Ejecuta** `AudioConverter.exe`
4. ¡Listo! No requiere instalación

> **Nota**: En Windows 10, puede aparecer SmartScreen. Click en "Más información" → "Ejecutar de todas formas"

### Opción 2: Desde Código Fuente (Para Desarrollo)

#### 1. Clonar el Repositorio
```bash
git clone https://github.com/yungpunk2001/audio-converter-gui.git
cd audio-converter-gui
```

#### 2. Crear Entorno Virtual
```bash
python -m venv .venv
```

#### 3. Activar Entorno Virtual
```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Windows CMD
.venv\Scripts\activate.bat
```

#### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### 5. Descargar FFmpeg

**Windows:**
- Descarga desde https://www.gyan.dev/ffmpeg/builds/ (elige "ffmpeg-release-essentials.zip")
- Extrae `ffmpeg.exe` y `ffprobe.exe` de la carpeta `bin`
- Colócalos en `./bin/` del proyecto

**O añade FFmpeg al PATH del sistema** (recomendado para desarrollo)

#### 6. Ejecutar la Aplicación
```bash
python main.py
```

---

## Guía de Uso

### Interfaz Principal

La ventana se divide en secciones lógicas:

```
┌─────────────────────────────────────────────────┐
│ Audio Converter                                 │
├─────────────────────────────────────────────────┤
│                                                 │
│ ┌─── Archivos a Convertir ───────────────────┐ │
│ │ [Lista de archivos]                        │ │
│ │                                            │ │
│ └────────────────────────────────────────────┘ │
│ [Añadir Archivos] [Añadir Carpeta] [Limpiar]  │
│                                                 │
│ ┌─── Configuración de Salida ───────────────┐  │
│ │ Formato: [MP3 ▼]    Carpeta: [...]       │  │
│ │ Calidad: [Máxima (recomendada) ▼]        │  │
│ └────────────────────────────────────────────┘  │
│                                                 │
│ ┌─── Descarga desde Internet ───────────────┐  │
│ │ URLs (una por línea):                     │  │
│ │ [Campo de texto]                          │  │
│ │ [✓] Convertir archivos descargados        │  │
│ │ [Descargar desde URL]                     │  │
│ └────────────────────────────────────────────┘  │
│                                                 │
│ ┌─── Progreso ───────────────────────────────┐  │
│ │ Archivo actual: [Nombre del archivo]      │  │
│ │ [████████░░░░░░░░] 67%                    │  │
│ │ Progreso total: Archivo 3 de 10           │  │
│ │ [███░░░░░░░░░░░░░] 27%                    │  │
│ └────────────────────────────────────────────┘  │
│                                                 │
│ [Convertir]  [Cancelar]                        │
└─────────────────────────────────────────────────┘
```

### Flujo de Trabajo Típico

#### Conversión de Archivos Locales

1. **Añadir archivos**:
   - **Opción A**: Click en "Añadir Archivos" y selecciona los archivos
   - **Opción B**: Click en "Añadir Carpeta" para procesar toda una carpeta
   - **Opción C**: Arrastra archivos o carpetas directamente a la ventana

2. **Seleccionar formato de salida**:
   - Elige el formato deseado en el desplegable "Formato destino"
   - Formatos disponibles: WAV, FLAC, ALAC, MP3, AAC, Opus, Ogg Vorbis

3. **Configurar calidad**:
   - **Máxima (recomendada)**: Usa presets optimizados para máxima calidad
   - **Personalizada**: Permite ajustar bitrate, VBR, sample rate y canales

4. **Seleccionar carpeta de salida** (opcional):
   - Por defecto usa `./downloads`
   - Click en "..." para elegir otra ubicación

5. **Convertir**:
   - Click en "Convertir"
   - Observa el progreso en tiempo real
   - Los archivos se guardarán en la carpeta de salida especificada

#### Descarga desde YouTube/Internet

1. **Obtener URLs**:
   - Copia las URLs de los videos/audios que quieras descargar
   - YouTube, SoundCloud y muchas otras plataformas soportadas

2. **Pegar en el campo**:
   - Pega una o más URLs en el campo de texto (una por línea)
   - Ejemplo:
     ```
     https://www.youtube.com/watch?v=dQw4w9WgXcQ
     https://soundcloud.com/artist/track
     https://www.youtube.com/watch?v=abc123
     ```

3. **Configurar conversión** (opcional):
   - **Marca** "Convertir archivos descargados" si quieres convertir después de descargar
   - Si NO marcas, los archivos se guardan en formato original

4. **Descargar**:
   - Click en "Descargar desde URL"
   - Los archivos se descargan en la carpeta de salida
   - Si marcaste conversión, se añaden automáticamente a la lista

5. **Convertir** (si marcaste la opción):
   - Selecciona formato y calidad
   - Click en "Convertir"

---

## Formatos Soportados

### Formatos de Entrada

La aplicación detecta automáticamente y puede convertir desde:

**Formatos Comunes**:
- MP3, WAV, FLAC, AAC, M4A, OGG, OPUS

**Formatos Adicionales**:
- WMA, MP2, AC3, AIFF, APE, WV, TTA, MKA, WEBM

**Básicamente**: Cualquier formato que FFmpeg pueda leer

### Formatos de Salida

| Formato | Extensión | Tipo | Calidad Máxima | Uso Recomendado |
|---------|-----------|------|----------------|-----------------|
| **WAV** | `.wav` | Sin pérdida | PCM 24-bit, 192 kHz | Producción, máster, archivo |
| **FLAC** | `.flac` | Sin pérdida | 24-bit, compresión | Archivo con ahorro de espacio |
| **ALAC** | `.m4a` | Sin pérdida | 24-bit, compatible Apple | Ecosistema Apple, iTunes |
| **MP3** | `.mp3` | Con pérdida | LAME V0 (~245 kbps VBR) | Compatibilidad universal |
| **AAC** | `.m4a` | Con pérdida | 256 kbps VBR | Moderno, excelente calidad/tamaño |
| **Opus** | `.opus` | Con pérdida | 192 kbps VBR | Mejor calidad/bitrate, streaming |
| **Vorbis** | `.ogg` | Con pérdida | Quality 7 (~224 kbps) | Código abierto, gaming |

---

## Filosofía de Calidad

### Presets "Máxima" por Formato

Cuando seleccionas "Máxima (recomendada)", la aplicación elige automáticamente los mejores parámetros para cada formato:

#### Formatos Sin Pérdida

##### WAV (PCM)
```
Codec: PCM signed 16-bit little-endian
Sample Rate: Original (o 44100 Hz si no especificado)
Canales: Original (o stereo si no especificado)
Bits: 16-bit (o 24-bit si el origen es de alta resolución)
```
**Características**:
- Sin compresión
- Máxima compatibilidad
- Tamaño de archivo grande

##### FLAC
```
Codec: FLAC (Free Lossless Audio Codec)
Sample Rate: Original (hasta 192 kHz)
Canales: Original (hasta 8 canales)
Bits: Original (hasta 24-bit)
Compresión: Nivel 5 (balance calidad/velocidad)
```
**Características**:
- Compresión sin pérdida (~50% del tamaño WAV)
- Soporta metadata extensiva
- Código abierto

##### ALAC (Apple Lossless)
```
Codec: ALAC (Apple Lossless Audio Codec)
Sample Rate: Original (hasta 192 kHz)
Canales: Original
Bits: Original (hasta 24-bit)
Container: M4A
```
**Características**:
- Compatible con iTunes/Apple Music
- Similar a FLAC en compresión
- Nativo en ecosistema Apple

#### Formatos Con Pérdida

##### MP3 (LAME)
```
Encoder: LAME MP3
Mode: VBR (Variable Bitrate)
Quality: V0 (equivalente a ~245 kbps promedio)
Comando: -q:a 0
Sample Rate: Original (o 44100 Hz)
Canales: Stereo
```
**Características**:
- Transparencia auditiva (indistinguible del original para la mayoría)
- Excelente compatibilidad
- Tamaño moderado (~1 MB/min stereo)

##### AAC (Advanced Audio Coding)
```
Encoder: FFmpeg AAC (nativo)
Mode: VBR (Variable Bitrate)
Bitrate: 256 kbps promedio
Sample Rate: Original
Canales: Original
```
**Características**:
- Superior a MP3 a mismo bitrate
- Formato moderno (post-MP3)
- Compatible con la mayoría de dispositivos

> **Nota**: Si compilas FFmpeg con `libfdk_aac`, la aplicación puede usar VBR 5 (calidad superior)

##### Opus
```
Encoder: libopus
Mode: VBR (Variable Bitrate)
Bitrate: 192 kbps
Complejidad: 10 (máxima calidad)
Sample Rate: 48 kHz (óptimo para Opus)
```
**Características**:
- Mejor calidad/bitrate de todos los códecs
- Excelente para voz y música
- Bajo delay (ideal para streaming)
- Relativamente nueva (menor compatibilidad)

##### Ogg Vorbis
```
Encoder: libvorbis
Mode: VBR (Variable Bitrate)
Quality: 7 (equivalente a ~224 kbps)
Comando: -q:a 7
Sample Rate: 44100 Hz o 48000 Hz
```
**Características**:
- Código abierto
- Calidad similar a MP3 V0
- Popular en gaming (Unreal Engine, Unity)

### Smart Copy: Evitar Recodificación

La aplicación detecta si un archivo ya está en el códec y contenedor objetivo. Si es así, ofrece **copiar sin recodificar**:

**Ejemplo**:
```
Archivo origen: musica.mp3 (MP3, 320 kbps CBR, 44.1 kHz)
Formato destino: MP3
Preset: Máxima (LAME V0)

→ La app detecta que ya es MP3
→ Ofrece copiar directamente sin pérdida adicional
→ Usuario puede forzar recodificación si desea VBR en lugar de CBR
```

**Beneficios**:
- Evita pérdida generacional (con pérdida → con pérdida)
- Procesamiento instantáneo
- Preserva calidad original

### Re-sampling de Alta Calidad

Cuando es necesario cambiar el sample rate, la aplicación usa **SOXR** (SoX Resampler):

```
Resampler: soxr
Quality: very high quality
Flags: VHQ
```

**Aplicación**:
- Conversión a Opus (prefiere 48 kHz)
- Downsampling desde archivos de alta resolución
- Upsampling si se especifica en modo personalizado

---

## Características Avanzadas

### Modo Personalizado

En el desplegable "Calidad", selecciona "Personalizada" para acceder a controles avanzados:

#### Parámetros Disponibles

1. **Bitrate (solo formatos con pérdida)**:
   - **CBR** (Constant Bitrate): Bitrate fijo
   - **VBR** (Variable Bitrate): Bitrate variable, mejor calidad
   - Rango: 64 kbps a 320 kbps (MP3, AAC)
   - Rango: 48 kbps a 256 kbps (Opus, Vorbis)

2. **Sample Rate**:
   - Original (mantener del archivo fuente)
   - 44100 Hz (CD quality)
   - 48000 Hz (audio profesional, óptimo para Opus)
   - 96000 Hz (high-resolution)
   - 192000 Hz (ultra high-resolution)

3. **Canales**:
   - Original (mantener del archivo fuente)
   - Mono (1 canal)
   - Stereo (2 canales)

#### Ejemplo: MP3 CBR 320 kbps
```
Formato: MP3
Calidad: Personalizada
  - Bitrate: 320 kbps
  - Modo: CBR
  - Sample Rate: 44100 Hz
  - Canales: Stereo
```

### Cancelación de Operaciones

Durante descargas o conversiones:

1. **Click en "Cancelar"**
2. Aparece confirmación: "¿Seguro que deseas cancelar la operación actual?"
3. **Sí** → Los workers se detienen limpiamente
4. **No** → Continúa la operación

**Detalles técnicos**:
- Usa flags thread-safe con `Lock()`
- Workers verifican flag periódicamente
- Limpieza automática de recursos
- UI se re-habilita correctamente

### Validación de Archivos

Antes de añadir archivos a la lista, la aplicación verifica:

1. **Existencia**: El archivo o carpeta existe
2. **Permisos**: Tienes permisos de lectura
3. **Formato**: FFmpeg puede leer el archivo (se verifica al convertir)

Antes de convertir:

4. **Carpeta de salida**: Existe y es accesible (se crea automáticamente si no existe)
5. **FFmpeg disponible**: Se encuentra en PATH o en `./bin/`

---

## Descarga desde Internet

### Plataformas Soportadas

Gracias a **yt-dlp**, la aplicación puede descargar audio de más de 1000 sitios, incluyendo:

**Populares**:
- YouTube (videos, playlists, live streams)
- SoundCloud
- Bandcamp
- Vimeo
- Dailymotion
- Mixcloud
- Twitch

**Y muchos más**: Ver [lista completa](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

### Cómo Funciona

1. **Usuario pega URL(s)**
2. **App llama a yt-dlp** con configuración optimizada:
   ```python
   ydl_opts = {
       'format': 'bestaudio/best',          # Mejor calidad de audio
       'outtmpl': '%(title)s.%(ext)s',     # Nombre basado en título
       'ffmpeg_location': './bin/',         # Usa FFmpeg incluido
       'postprocessors': [{
           'key': 'FFmpegExtractAudio',    # Extrae solo audio
       }],
       'writethumbnail': False,             # No descargar miniaturas
       'socket_timeout': 30,                # Timeout de 30s
       'retries': 3,                        # Reintentos automáticos
   }
   ```

3. **yt-dlp descarga y extrae** audio en mejor calidad disponible
4. **Formato de salida**: Generalmente Opus, M4A o WebM (según la fuente)
5. **Si "Convertir descargados" está marcado**: Añade archivos a lista de conversión

### Auto-Actualización de yt-dlp

**Problema**: YouTube y otras plataformas cambian frecuentemente, bloqueando versiones antiguas de yt-dlp.

**Solución**: Sistema de auto-actualización integrado:

#### Funcionamiento

1. **Al iniciar la app** (máximo 1 vez cada 24h):
   - Verifica si hay versión más nueva de yt-dlp
   - Usa caché en `~/.audio_converter_cache/ytdlp_check.json`

2. **Si hay actualización disponible**:
   - Muestra diálogo informativo explicando el motivo
   - Usuario puede elegir: "Actualizar ahora" o "Más tarde"

3. **Si usuario acepta**:
   - Ejecuta `pip install --upgrade yt-dlp` en segundo plano
   - Timeout de 30 segundos
   - Muestra resultado (éxito o error)

4. **Si falla**:
   - Mensaje con instrucciones manuales
   - App sigue funcionando normalmente

#### Archivo de Caché

Ubicación: `%USERPROFILE%\.audio_converter_cache\ytdlp_check.json`

Contenido:
```json
{
    "last_check": "2025-11-14T10:30:00",
    "last_update": "2025-11-14T10:31:00"
}
```

**Beneficio**: Evita verificaciones en cada inicio (solo 1 vez cada 24h)

### Solución de Problemas: HTTP 403 Forbidden

Si obtienes error 403 al descargar de YouTube:

#### Causa
- YouTube bloqueó la versión de yt-dlp que tienes instalada
- Cambios en la API de YouTube

#### Solución Automática
1. Reinicia la app
2. Si hay actualización, aparecerá diálogo automático
3. Click en "Actualizar ahora"
4. Espera ~30 segundos
5. Reinicia la app

#### Solución Manual
```bash
# Desde la consola del entorno virtual
pip install --upgrade yt-dlp

# O descarga ejecutable actualizado
```

#### Solución Adicional: Cookies
Para videos con restricción:

1. Inicia sesión en YouTube en tu navegador (Chrome o Firefox)
2. En `main.py`, añade en `ydl_opts`:
   ```python
   'cookiesfrombrowser': ('chrome',),  # o 'firefox'
   ```
3. Guarda y reinicia

---

## Compilación del Ejecutable

### Requisitos Previos

1. **Python 3.10+** instalado
2. **FFmpeg** descargado:
   - Descarga desde https://www.gyan.dev/ffmpeg/builds/
   - Extrae `ffmpeg.exe` y `ffprobe.exe`
   - Colócalos en `./bin/`

3. **PyInstaller** instalado:
   ```bash
   pip install pyinstaller
   ```

### Opción 1: Build Optimizado (Recomendado)

**Ventaja**: Inicio ultra-rápido (< 1 segundo)

**Script**: `build_release_optimized.bat`

```batch
@echo off
echo ======================================
echo   Audio Converter - Build Optimizado
echo ======================================
echo.

REM Verificar FFmpeg
if not exist "bin\ffmpeg.exe" (
    echo ERROR: No se encuentra bin\ffmpeg.exe
    pause
    exit /b 1
)

if not exist "bin\ffprobe.exe" (
    echo ERROR: No se encuentra bin\ffprobe.exe
    pause
    exit /b 1
)

echo [1/4] Limpiando builds anteriores...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec

echo [2/4] Activando entorno virtual...
call .venv\Scripts\activate.bat

echo [3/4] Compilando con PyInstaller (--onedir)...
pyinstaller --noconfirm --clean ^
  --name AudioConverter ^
  --windowed ^
  --add-binary "bin\ffmpeg.exe;bin" ^
  --add-binary "bin\ffprobe.exe;bin" ^
  main.py

echo [4/4] Build completado!
echo.
echo Ejecutable en: dist\AudioConverter\AudioConverter.exe
echo.
echo NOTA: Distribuye toda la carpeta dist\AudioConverter
pause
```

**Ejecutar**:
```bash
build_release_optimized.bat
```

**Salida**: `dist\AudioConverter\` (distribuir carpeta completa o crear instalador)

### Opción 2: Build Onefile (Archivo Único)

**Ventaja**: Un solo archivo ejecutable

**Desventaja**: Inicio lento (10-30 segundos)

**Script**: `build_windows.bat` (ya existe)

```bash
build_windows.bat
```

**Salida**: `dist\AudioConverter.exe` (~290 MB)

### Crear Instalador con Inno Setup (Opcional)

1. **Descarga Inno Setup**: https://jrsoftware.org/isdl.php

2. **Crea script** `installer.iss`:
   ```iss
   [Setup]
   AppName=Audio Converter
   AppVersion=1.1.0
   DefaultDirName={autopf}\AudioConverter
   DefaultGroupName=Audio Converter
   OutputDir=installer
   OutputBaseFilename=AudioConverter_Setup
   
   [Files]
   Source: "dist\AudioConverter\*"; DestDir: "{app}"; Flags: recursesubdirs
   
   [Icons]
   Name: "{group}\Audio Converter"; Filename: "{app}\AudioConverter.exe"
   Name: "{autodesktop}\Audio Converter"; Filename: "{app}\AudioConverter.exe"
   ```

3. **Compila** con Inno Setup Compiler

4. **Salida**: `installer\AudioConverter_Setup.exe`

---

## Solución de Problemas

### La aplicación no inicia

#### Síntoma
- Doble click en el ejecutable, nada pasa
- O ventana aparece y desaparece inmediatamente

#### Causa
- FFmpeg no encontrado
- Archivo corrupto
- Antivirus bloqueando

#### Solución
1. **Ejecuta desde CMD** para ver errores:
   ```cmd
   cd ruta\donde\esta\AudioConverter.exe
   AudioConverter.exe
   ```

2. **Verifica FFmpeg**:
   - Si es ejecutable portable, verifica que `bin\ffmpeg.exe` exista
   - Si no, descárgalo y colócalo en la carpeta `bin`

3. **Añade excepción en antivirus**:
   - Windows Defender → Protección contra virus y amenazas → Exclusiones
   - Añade la carpeta completa

### Error: "FFmpeg no encontrado"

#### Síntoma
- Mensaje al iniciar conversión: "FFmpeg no encontrado en el sistema"

#### Solución

**Opción A**: Añadir al PATH
1. Descarga FFmpeg desde https://www.gyan.dev/ffmpeg/builds/
2. Extrae a `C:\ffmpeg\`
3. Añade `C:\ffmpeg\bin\` al PATH del sistema:
   - Panel de Control → Sistema → Configuración avanzada
   - Variables de entorno → Path → Editar → Nuevo
   - Añade `C:\ffmpeg\bin`
   - Reinicia la app

**Opción B**: Usar carpeta bin local
1. Descarga FFmpeg
2. Extrae `ffmpeg.exe` y `ffprobe.exe`
3. Colócalos en la carpeta `bin\` junto al ejecutable (o del proyecto si ejecutas desde código)

### Error 403 al descargar de YouTube

Ver sección [Descarga desde Internet](#descarga-desde-internet) → Solución de Problemas

### Conversión muy lenta

#### Causa
- Archivos muy grandes (>500 MB)
- Sample rate muy alto (192 kHz)
- Procesador lento

#### Solución
1. **Usa SSD** en lugar de HDD para carpeta de salida
2. **Cierra otras aplicaciones** pesadas
3. **Modo personalizado**: Reduce sample rate si no necesitas alta resolución
   - 96 kHz → 48 kHz puede ser 2x más rápido sin pérdida audible

### Archivos descargados tienen nombres extraños

#### Síntoma
- Nombres como `video-dQw4w9WgXcQ.opus`

#### Causa
- Plantilla de nombre por defecto de yt-dlp

#### Solución (Para Desarrolladores)
En `main.py`, modifica `ydl_opts`:
```python
'outtmpl': '%(artist)s - %(title)s.%(ext)s',  # Mejor formato
```

O:
```python
'outtmpl': '%(title)s.%(ext)s',  # Solo título (actual)
```

### Aplicación se congela al cerrar

#### Síntoma
- Click en X, la ventana se queda en blanco

#### Causa
- Workers no terminaron a tiempo

#### Solución Automática
- Ya implementado: `closeEvent()` con timeout de 5 segundos
- Si persiste, usa "Cancelar" antes de cerrar

#### Solución Forzada
- Ctrl+Alt+Supr → Administrador de Tareas → Finalizar tarea

---

## Arquitectura Técnica

### Estructura del Código

```
audio_converter_gui/
├── main.py                 # Aplicación principal (1242 líneas)
│   ├── find_ffmpeg()       # Localiza FFmpeg en sistema
│   ├── check_ytdlp_update() # Verifica actualizaciones yt-dlp
│   ├── update_ytdlp_silent() # Actualiza yt-dlp
│   ├── DownloadWorker      # QThread para descargas
│   ├── ConvertWorker       # QThread para conversiones
│   └── MainWindow          # Interfaz principal PySide6
│
├── quality_presets.py      # Presets de calidad (317 líneas)
│   ├── MetadataCache       # Caché de metadatos FFprobe
│   ├── QUALITY_PRESETS     # Diccionario de presets
│   └── get_convert_command() # Genera comandos FFmpeg
│
├── requirements.txt        # Dependencias Python
├── build_windows.bat       # Script build onefile
├── build_release_optimized.bat  # Script build onedir
└── bin/                    # Binarios FFmpeg
    ├── ffmpeg.exe
    └── ffprobe.exe
```

### Tecnologías Utilizadas

| Componente | Tecnología | Propósito |
|------------|------------|-----------|
| **Interfaz Gráfica** | PySide6 (Qt) | Widgets, señales, threading |
| **Conversión Audio** | FFmpeg | Transcodificación, metadatos |
| **Descarga** | yt-dlp | Extracción de audio desde Internet |
| **Empaquetado** | PyInstaller | Creación de ejecutable Windows |
| **Threading** | QThread + Lock | Operaciones asíncronas thread-safe |

### Flujo de Datos: Conversión

```
┌─────────────┐
│   Usuario   │
│  Añade arch │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   MainWindow        │
│ - Valida archivos   │
│ - Añade a QListWidget│
└──────┬──────────────┘
       │ Click "Convertir"
       ▼
┌─────────────────────────┐
│  get_convert_command()  │ ← quality_presets.py
│ - Lee metadata (cache)  │
│ - Genera comando FFmpeg │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────┐
│  ConvertWorker      │ ← QThread
│ - Ejecuta FFmpeg    │
│ - Parsea progreso   │
│ - Emite señales     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   MainWindow        │
│ - Actualiza barras  │
│ - Muestra progreso  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Archivo convertido  │
│ en carpeta salida   │
└─────────────────────┘
```

### Flujo de Datos: Descarga

```
┌─────────────┐
│   Usuario   │
│  Pega URLs  │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   MainWindow        │
│ - Parsea URLs       │
│ - Verifica yt-dlp   │
└──────┬──────────────┘
       │ Click "Descargar"
       ▼
┌─────────────────────┐
│  DownloadWorker     │ ← QThread
│ - Configura yt-dlp  │
│ - Descarga c/ progreso│
│ - Emite señales     │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   MainWindow        │
│ - Actualiza progreso│
│ - Si convertir:     │
│   añade a lista     │
└─────────────────────┘
```

### Thread Safety

**Problema**: Workers (QThread) comparten flag `_stop` con thread principal

**Solución**: `threading.Lock()`

```python
from threading import Lock

class ConvertWorker(QThread):
    def __init__(self):
        super().__init__()
        self._stop = False
        self._stop_lock = Lock()  # ← Protege _stop
    
    def stop(self):
        """Llamado desde thread principal"""
        with self._stop_lock:
            self._stop = True
    
    def is_stopped(self) -> bool:
        """Llamado desde worker thread"""
        with self._stop_lock:
            return self._stop
    
    def run(self):
        for file in self.files:
            if self.is_stopped():  # ← Verificación thread-safe
                break
            # ... procesar archivo
```

**Beneficio**: Eliminados race conditions y crashes aleatorios

### Caché de Metadatos

**Problema**: Llamadas múltiples a `ffprobe` para el mismo archivo (ineficiente)

**Solución**: Clase `MetadataCache` en `quality_presets.py`

```python
class MetadataCache:
    _cache = {}  # Diccionario compartido
    
    @staticmethod
    def get_metadata(file_path: str, ffprobe_path: str):
        if file_path in MetadataCache._cache:
            return MetadataCache._cache[file_path]  # ← Hit
        
        # Miss: ejecuta ffprobe y cachea
        metadata = probe_file(file_path, ffprobe_path)
        MetadataCache._cache[file_path] = metadata
        return metadata
```

**Impacto**: Reducción del 66% en llamadas a ffprobe (3 → 1 por archivo)

---

## Preguntas Frecuentes

### ¿Puedo convertir múltiples archivos a la vez?

Sí, pero se procesan secuencialmente (uno después de otro). Esto evita saturar la CPU y asegura estabilidad.

### ¿Se pierden los metadatos (tags) al convertir?

FFmpeg preserva la mayoría de metadatos por defecto (título, artista, álbum, etc.). Algunos formatos tienen limitaciones específicas.

### ¿Puedo convertir videos a solo audio?

Sí, pero requiere modificación en el código (actualmente solo soporta archivos de audio). Feature planeada para futuro.

### ¿Funciona offline?

**Conversión**: Sí, completamente offline una vez instalado.

**Descarga**: No, requiere conexión a Internet.

### ¿Es gratis?

Sí, 100% gratuito y de código abierto bajo licencia MIT.

### ¿Funciona en Mac/Linux?

El código fuente es compatible, pero el ejecutable es solo para Windows. Puedes compilar para Mac/Linux siguiendo los pasos de instalación desde código.

### ¿Puedo usar esto comercialmente?

Sí, la licencia MIT lo permite. Ver `LICENSE` para detalles.

### ¿Dónde se guardan los archivos convertidos?

Por defecto en `./downloads` (carpeta junto al ejecutable). Puedes cambiar la ubicación en "Carpeta de Salida".

### ¿Qué tan seguros son mis archivos?

- La app no envía datos a ningún servidor (excepto yt-dlp al descargar)
- Los archivos se procesan localmente
- No se recopila telemetría ni analytics
- Código fuente abierto y auditable

---

## Soporte y Contribuciones

### Reportar Problemas

¿Encontraste un bug? [Abre un issue](https://github.com/yungpunk2001/audio-converter-gui/issues/new?labels=bug)

Incluye:
- Versión de la app
- Sistema operativo
- Pasos para reproducir
- Mensaje de error (si aplica)

### Solicitar Funcionalidades

¿Tienes una idea? [Abre un issue](https://github.com/yungpunk2001/audio-converter-gui/issues/new?labels=enhancement)

### Contribuir al Código

Ver `CONTRIBUTING.md` para guías de estilo y proceso de Pull Requests.

### Contacto

- GitHub: [@yungpunk2001](https://github.com/yungpunk2001)
- Issues: https://github.com/yungpunk2001/audio-converter-gui/issues

---

## Licencia

Este proyecto está bajo la licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## Créditos

Desarrollado con ❤️ usando:

- **FFmpeg** - https://ffmpeg.org/
- **yt-dlp** - https://github.com/yt-dlp/yt-dlp
- **PySide6** - https://www.qt.io/qt-for-python
- **PyInstaller** - https://www.pyinstaller.org/

---

**Última actualización**: 2025-11-14  
**Versión de la documentación**: 2.0
