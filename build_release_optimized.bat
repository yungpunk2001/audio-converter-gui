@echo off
REM Audio Converter GUI - Build Script OPTIMIZADO
REM Genera ejecutable con inicio rápido usando --onedir

echo ========================================
echo Audio Converter GUI - Build Optimizado
echo ========================================
echo.
echo NOTA: Este script genera una carpeta con
echo       el ejecutable (inicio mas rapido)
echo       en lugar de un solo .exe
echo.

REM Verificar binarios de FFmpeg
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

echo [1/6] Verificando Python...
py --version
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python no esta instalado
    pause
    exit /b 1
)

echo.
echo [2/6] Creando entorno virtual...
IF EXIST ".venv" (
    echo Entorno virtual ya existe, saltando...
) ELSE (
    py -m venv .venv
    IF %ERRORLEVEL% NEQ 0 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
)

echo [3/6] Instalando dependencias...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -q -r requirements.txt
pip install -q pyinstaller

echo.
echo [4/6] Limpiando builds anteriores...
IF EXIST "dist" rmdir /s /q dist
IF EXIST "build" rmdir /s /q build
IF EXIST "AudioConverter.spec" del AudioConverter.spec

echo.
echo [5/6] Compilando con PyInstaller (modo --onedir)...
echo VENTAJA: Inicio INSTANTANEO (sin descompresion)
echo Esto puede tardar 2-3 minutos...
echo.

pyinstaller --noconfirm --clean ^
  --name "AudioConverter" ^
  --windowed ^
  --onedir ^
  --add-binary "bin\ffmpeg.exe;bin" ^
  --add-binary "bin\ffprobe.exe;bin" ^
  --icon=NONE ^
  --optimize=2 ^
  main.py

IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo la compilacion
    pause
    exit /b 1
)

echo.
echo [6/6] Limpiando archivos temporales...
IF EXIST "build" rmdir /s /q build
IF EXIST "AudioConverter.spec" del AudioConverter.spec

echo.
echo ========================================
echo BUILD OPTIMIZADO EXITOSO
echo ========================================
echo.
echo Ejecutable en: dist\AudioConverter\AudioConverter.exe
echo Distribuye toda la carpeta: dist\AudioConverter\
echo.
echo INICIO: 10x MAS RAPIDO que con --onefile
echo Tamano en disco: Similar (~300 MB)
echo.
echo TIP: Puedes crear un instalador con Inno Setup
echo      o comprimir la carpeta en .zip para distribuir
echo.
pause
