@echo off
rem ## Windows icin PdSqliteLib.exe olusturma ##
rem Kullanim: proje klasorunde  scripts\build_windows.bat
rem Cikti:    dist\PdSqliteLib\PdSqliteLib.exe  (klasoruyle birlikte kullanilir/tasinir)
rem Not: data\DBL_Kayit.db o anki haliyle pakete eklenir ve uygulamanin ilk acilisinda
rem      %APPDATA%\PdSqliteLib\ altina kopyalanir. Sonraki paketler mevcut verinin uzerine yazmaz.

setlocal
cd /d "%~dp0\.."

if not exist "data\DBL_Kayit.db" (
    echo HATA: data\DBL_Kayit.db bulunamadi. Once veritabanini data klasorune koyun.
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv || goto hata
)
".venv\Scripts\python.exe" -m pip install -q -r requirements.txt pyinstaller || goto hata

".venv\Scripts\pyinstaller.exe" main.py ^
    --name PdSqliteLib ^
    --windowed ^
    --noconfirm ^
    --clean ^
    --icon "%CD%\media\family.ico" ^
    --exclude-module matplotlib ^
    --exclude-module PIL ^
    --exclude-module tkinter ^
    --exclude-module pandas ^
    --exclude-module numpy ^
    --add-data "%CD%\data\DBL_Kayit.db;data" ^
    --add-data "%CD%\media\fonts;media\fonts" ^
    --workpath build\pyinstaller ^
    --specpath build\pyinstaller ^
    --distpath dist || goto hata

echo.
echo Hazir: dist\PdSqliteLib\PdSqliteLib.exe
exit /b 0

:hata
echo.
echo HATA: paket olusturulamadi. Yukaridaki mesajlara bakin.
exit /b 1
