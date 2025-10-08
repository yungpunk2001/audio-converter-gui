@echo off
setlocal enabledelayedexpansion
echo ========================================
echo   COMPILAR AUDIO CONVERTER GUI v1.0.0
echo ========================================
echo.
echo Este proceso tardara entre 5-10 minutos
echo NO cierres esta ventana hasta que termine
echo.
echo Incluye:
echo  - PySide6 (Interfaz grafica)
echo  - yt-dlp (Descarga de YouTube)
echo  - FFmpeg y FFprobe (142 MB cada uno)
echo.
pause
echo.
echo [1/3] Verificando dependencias...
echo.

cd /d "%~dp0"

REM Verificar que yt-dlp está instalado
.\.venv\Scripts\python.exe -c "import yt_dlp" 2>nul
if errorlevel 1 (
    echo Instalando yt-dlp...
    .\.venv\Scripts\python.exe -m pip install -q yt-dlp
)

echo [2/3] Compilando con PyInstaller...
echo Este es el paso mas lento, por favor espera...
echo.

.\.venv\Scripts\pyinstaller.exe --noconfirm --clean --name "AudioConverter" --windowed --onefile --add-binary "bin\ffmpeg.exe;bin" --add-binary "bin\ffprobe.exe;bin" main.py

echo.
echo [3/3] Verificando resultado...
echo.
echo ========================================
if exist "dist\AudioConverter.exe" (
    echo   COMPILACION EXITOSA!
    echo ========================================
    echo.
    echo El ejecutable esta en: dist\AudioConverter.exe
    echo.
    for %%F in (dist\AudioConverter.exe) do (
        set size=%%~zF
        set /a sizeMB=!size! / 1048576
    )
    echo Tamano: !sizeMB! MB
    echo.
    echo Incluye:
    echo  - FFmpeg + FFprobe (procesamiento de audio)
    echo  - yt-dlp (descarga de YouTube/URLs)
    echo  - PySide6 (interfaz grafica)
    echo.
    echo Listo para distribuir!
    echo.
) else (
    echo   ERROR EN LA COMPILACION
    echo ========================================
    echo.
    echo Revisa los errores arriba
    echo.
)

pause
