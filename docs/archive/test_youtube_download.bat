@echo off
REM Script de prueba para verificar descargas de YouTube
REM Uso: test_youtube_download.bat

echo ========================================
echo Test de Descarga de YouTube con yt-dlp
echo ========================================
echo.

echo [1/4] Activando entorno virtual...
call .venv\Scripts\activate.bat
IF %ERRORLEVEL% NEQ 0 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

echo [2/4] Verificando version de yt-dlp...
yt-dlp --version
echo.

echo [3/4] Probando con video simple (Me at the zoo)...
echo URL: https://www.youtube.com/watch?v=jNQXAC9IVRw
echo.
yt-dlp -F "https://www.youtube.com/watch?v=jNQXAC9IVRw"
IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: No se pudo obtener formatos del video
    echo.
    echo Posibles causas:
    echo - Sin conexion a internet
    echo - YouTube bloqueando tu IP
    echo - Necesitas usar cookies de navegador
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo TEST EXITOSO
echo ========================================
echo.
echo yt-dlp puede acceder a YouTube correctamente.
echo Ahora prueba la aplicacion principal.
echo.

echo [4/4] ¿Descargar audio de prueba? (S/N)
set /p DOWNLOAD="Respuesta: "
IF /I "%DOWNLOAD%"=="S" (
    echo.
    echo Descargando audio de prueba...
    mkdir test_downloads 2>nul
    yt-dlp -f bestaudio -o "test_downloads\%%(title)s.%%(ext)s" ^
        --extract-audio ^
        --audio-format best ^
        "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    echo.
    echo Archivo descargado en: test_downloads\
)

echo.
pause
