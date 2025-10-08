@echo off
REM Audio Converter GUI - Build Script usando py launcher
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

echo [1/5] Verificando Python...
py --version
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python no esta instalado
    pause
    exit /b 1
)

echo.
echo [2/5] Creando entorno virtual...
py -m venv .venv
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo crear el entorno virtual
    pause
    exit /b 1
)

echo [3/5] Instalando dependencias...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -q -r requirements.txt
pip install -q pyinstaller

echo.
echo [4/5] Compilando con PyInstaller...
echo Esto puede tardar varios minutos...
echo.
pyinstaller --noconfirm --clean ^
  --name "AudioConverter" ^
  --windowed ^
  --onefile ^
  --add-binary "bin\ffmpeg.exe;bin" ^
  --add-binary "bin\ffprobe.exe;bin" ^
  main.py

IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo la compilacion
    pause
    exit /b 1
)

echo.
echo [5/5] Limpiando archivos temporales...
IF EXIST "build" rmdir /s /q build
IF EXIST "AudioConverter.spec" del AudioConverter.spec

echo.
echo ========================================
echo BUILD EXITOSO
echo ========================================
echo.
echo El ejecutable esta en: dist\AudioConverter.exe
echo Tamano aproximado: ~290 MB (incluye FFmpeg)
echo.
pause
