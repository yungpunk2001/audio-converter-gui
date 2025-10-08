@echo off
REM Audio Converter GUI - Build Script for Windows
REM Este script crea un ejecutable portable con PyInstaller

echo ========================================
echo Audio Converter GUI - Build Script
echo ========================================
echo.

REM Verificar que existen los binarios de FFmpeg
IF NOT EXIST "bin\ffmpeg.exe" (
    echo ERROR: No se encontro bin\ffmpeg.exe
    echo.
    echo Descarga FFmpeg desde: https://www.gyan.dev/ffmpeg/builds/
    echo Extrae ffmpeg.exe y ffprobe.exe en la carpeta bin\
    echo.
    pause
    exit /b 1
)

IF NOT EXIST "bin\ffprobe.exe" (
    echo ERROR: No se encontro bin\ffprobe.exe
    echo.
    echo Descarga FFmpeg desde: https://www.gyan.dev/ffmpeg/builds/
    echo Extrae ffmpeg.exe y ffprobe.exe en la carpeta bin\
    echo.
    pause
    exit /b 1
)

echo [1/4] Creando entorno virtual...
python -m venv .venv
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo [2/4] Instalando dependencias...
call .venv\Scripts\activate
pip install -q -r requirements.txt
pip install -q pyinstaller

echo [3/4] Compilando con PyInstaller...
pyinstaller --noconfirm --clean ^
  --name AudioConverter ^
  --windowed ^
  --add-binary "bin\ffmpeg.exe;bin" ^
  --add-binary "bin\ffprobe.exe;bin" ^
  main.py

IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo la compilacion
    pause
    exit /b 1
)

echo [4/4] Limpiando archivos temporales...
IF EXIST "build" rmdir /s /q build
IF EXIST "AudioConverter.spec" del AudioConverter.spec

echo.
echo ========================================
echo BUILD EXITOSO
echo ========================================
echo.
echo El ejecutable esta en: dist\AudioConverter\AudioConverter.exe
echo.
pause
