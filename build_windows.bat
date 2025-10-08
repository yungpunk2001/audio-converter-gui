@echo off
REM Build helper for Windows
python -m venv .venv
call .venv\Scripts\activate
pip install -r requirements.txt
pip install pyinstaller

IF NOT EXIST bin mkdir bin
echo Coloca ffmpeg.exe y ffprobe.exe en bin\ antes de continuar.
pause

pyinstaller --noconfirm --clean ^
  --name AudioConverter ^
  --windowed ^
  --add-binary "bin\ffmpeg.exe;bin" ^
  --add-binary "bin\ffprobe.exe;bin" ^
  main.py
echo Listo. Revisa dist\AudioConverter\
pause
