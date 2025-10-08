# Instrucciones para crear el repositorio en GitHub

## Estado actual
✅ Repositorio Git local inicializado
✅ Archivos añadidos y commit inicial creado
✅ Archivo .gitignore configurado

## Pasos para crear el repositorio en GitHub:

### 1. Crear el repositorio en GitHub.com

1. Ve a https://github.com/new
2. Completa los siguientes datos:
   - **Repository name**: `audio-converter-gui` (o el nombre que prefieras)
   - **Description**: "Audio converter GUI with focus on maximum quality. Supports WAV, FLAC, ALAC, MP3, AAC, Opus, and Ogg Vorbis formats."
   - **Visibility**: Public o Private (según prefieras)
   - **NO marques** "Initialize this repository with a README" (ya tienes uno)
   - **NO añadas** .gitignore ni license ahora (ya los tienes)
3. Haz clic en **Create repository**

### 2. Conectar tu repositorio local con GitHub

GitHub te mostrará instrucciones. Usa estas comandos en tu terminal (PowerShell):

```powershell
cd c:\Users\marti\Documents\!PROGRAMAS\Apps\audio_converter_gui

# Añadir el remote (reemplaza TU_USUARIO con tu nombre de usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/audio-converter-gui.git

# Renombrar la rama principal a 'main' (si es necesario)
git branch -M main

# Subir el código a GitHub
git push -u origin main
```

### 3. Verificar

Recarga la página de tu repositorio en GitHub y deberías ver todos tus archivos.

## Notas importantes:

### Sobre los binarios de FFmpeg
Los archivos `bin/ffmpeg.exe` y `bin/ffprobe.exe` son bastante grandes (~100-200 MB).
GitHub tiene un límite de 100 MB por archivo.

**Opciones:**
1. **Si los archivos son > 100 MB**: Deberás excluirlos del repositorio
   - Descomenta las líneas en `.gitignore`:
     ```
     bin/ffmpeg.exe
     bin/ffprobe.exe
     ```
   - Añade instrucciones en el README para que los usuarios descarguen FFmpeg
   
2. **Si son < 100 MB**: Puedes dejarlos (pero el repo será grande)

3. **Opción recomendada**: Usar Git LFS (Large File Storage) para archivos grandes
   ```powershell
   git lfs install
   git lfs track "bin/*.exe"
   git add .gitattributes
   git commit -m "Add Git LFS tracking for executables"
   ```

### Próximos pasos sugeridos:
- Añade una LICENSE (ej: MIT, GPL)
- Añade screenshots de la aplicación al README
- Configura GitHub Actions para CI/CD si lo necesitas
- Añade badges al README (build status, version, etc.)

## ¿Necesitas ayuda?
Si tienes problemas con algún paso, avísame y te ayudo a resolverlo.
