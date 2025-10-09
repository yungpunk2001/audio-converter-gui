# 📦 Instrucciones para Subir el Release v1.0.0

## ✅ Estado Actual
- ✅ Código actualizado y pusheado a GitHub
- ✅ Tag v1.0.0 creado y actualizado
- ✅ Ejecutable compilado: `dist\AudioConverter.exe` (167.65 MB)
- ✅ Incluye yt-dlp para descargas de YouTube

## 🚀 Pasos para Crear el Release

### 1. Ve a la página de Releases
Abre en tu navegador:
```
https://github.com/yungpunk2001/audio-converter-gui/releases/new
```

### 2. Configura el Release

**Choose a tag:** Selecciona `v1.0.0` (ya existe)

**Release title:** 
```
Audio Converter GUI v1.0.0
```

**Description:** Copia y pega el contenido de `RELEASE_NOTES.md` o usa esto:

```markdown
# 🎵 Audio Converter GUI v1.0.0

Primer lanzamiento oficial del conversor de audio con interfaz gráfica.

## ✨ Características Principales

### 🎯 Conversión de Audio
- **7 formatos soportados**: WAV, FLAC, ALAC, MP3, AAC, Opus, Ogg Vorbis
- **Calidades predefinidas**: Máxima calidad (sin pérdida) o personalizada
- **Procesamiento por lotes**: Convierte múltiples archivos simultáneamente
- **Drag & Drop**: Arrastra archivos directamente a la aplicación

### 🌐 Descarga desde Internet
- **YouTube**: Descarga audio de videos de YouTube
- **SoundCloud**: Descarga tracks de SoundCloud
- **Múltiples URLs**: Procesa varias URLs simultáneamente
- **Conversión opcional**: Elige si convertir el audio descargado o guardarlo en formato original
- **Por defecto NO convierte**: Los archivos descargados se guardan directamente sin conversión automática

### 🎚️ Control de Calidad
- **Bitrate personalizable**: 128-320 kbps para formatos con pérdida
- **Frecuencia de muestreo**: 44.1, 48, 96, 192 kHz
- **Modos VBR/CBR**: Variable o Constant Bitrate
- **Presets optimizados**: Configuraciones predefinidas por formato

### ⚡ Rendimiento
- **Procesamiento paralelo**: Usa todos los núcleos del CPU
- **FFmpeg integrado**: No requiere instalación adicional
- **Interfaz responsiva**: No se congela durante la conversión
- **Barra de progreso**: Seguimiento en tiempo real

## 📥 Instalación

1. Descarga `AudioConverter.exe` desde los assets
2. Ejecuta el archivo (no requiere instalación)
3. ¡Listo para usar!

**Nota:** Windows puede mostrar una advertencia de SmartScreen la primera vez. Haz clic en "Más información" → "Ejecutar de todas formas"

## 🔧 Requisitos del Sistema
- Windows 10/11 (64-bit)
- ~170 MB de espacio libre
- No requiere Python ni dependencias adicionales

## 📝 Incluye
- ✅ FFmpeg + FFprobe (procesamiento de audio)
- ✅ yt-dlp (descarga de YouTube/URLs)
- ✅ PySide6 (interfaz gráfica)

## 🐛 Problemas Conocidos
Ninguno reportado en esta versión.

## 📄 Licencia
MIT License - Ver [LICENSE](LICENSE) para más detalles
```

### 3. Sube el Ejecutable

En la sección **"Attach binaries"** al final de la página:
- Haz clic en "Attach binaries by dropping them here or selecting them"
- Selecciona el archivo: `dist\AudioConverter.exe`
- Espera a que se suba completamente (puede tardar 2-3 minutos por el tamaño)

### 4. Marca como Latest Release

✅ Asegúrate de marcar la casilla **"Set as the latest release"**

### 5. Publica

Haz clic en **"Publish release"**

## 🎉 Resultado

El release estará disponible en:
```
https://github.com/yungpunk2001/audio-converter-gui/releases
```

Los usuarios podrán descargar `AudioConverter.exe` directamente desde ahí.

---

## 🔄 Cambios en esta Versión

### Mejoras Recientes
- ✅ Casilla "Convertir archivos descargados" desactivada por defecto
- ✅ yt-dlp incluido en el ejecutable
- ✅ Script de compilación mejorado (COMPILAR.bat)
- ✅ Documentación completa actualizada

### Archivos Modificados
- `main.py`: Checkbox de conversión automática desactivada
- `COMPILAR.bat`: Mejorado script de compilación
- `RELEASE_NOTES.md`: Actualizado con nuevas características
