@echo off
rem ## PdSqliteLib'i Windows'ta paketlemeden calistirma ##
rem Ilk calistirmada sanal ortami kurar; sonra konsol penceresi acmadan programi baslatir.
rem Masaustune kisayol icin bu dosyaya sag tik > Kisayol olustur.

setlocal
cd /d "%~dp0\.."

if not exist ".venv\Scripts\pythonw.exe" (
    echo Ilk kurulum yapiliyor, bu birkac dakika surebilir...
    python -m venv .venv || goto hata
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto hata
)
start "" ".venv\Scripts\pythonw.exe" main.py
exit /b 0

:hata
echo.
echo HATA: Python bulunamadi veya kurulum basarisiz oldu.
echo python.org adresinden Python 3.9+ kurun ("Add python.exe to PATH" isaretli olsun).
pause
exit /b 1
