@echo off
setlocal enabledelayedexpansion
echo ========================================
echo    Building Pet Screen Demo...
echo ========================================

echo.
echo [1/5] Checking free disk space on TEMP drive...
for /f "tokens=3" %%a in ('dir /-c "%TEMP%" ^| find "bytes free"') do set FREEBYTES=%%a
echo Free bytes on TEMP drive: %FREEBYTES%
rem Canh bao neu duoi ~1.5GB (1500000000). Onefile can du cho de nen archive khi build.
if %FREEBYTES% LSS 1500000000 (
    echo.
    echo [CANH BAO] O dia chua TEMP con rat it dung luong trong!
    echo Build --onefile co the bi cat cut/hong, dan den loi luc chay:
    echo   "Failed to extract ... decompression resulted in return code -1"
    echo Hay don bot dung luong dia roi build lai.
    echo.
)

echo.
echo [2/5] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

echo.
echo [3/5] Cleaning stale PyInstaller temp folders (_MEI*)...
for /d %%d in ("%TEMP%\_MEI*") do rmdir /s /q "%%d" 2>nul

echo.
echo [4/5] Building with PyInstaller...
rem --clean: xoa cache PyInstaller; --noconfirm: khong hoi de ghi de;
rem --noupx: tat nen UPX (tranh loi giai nen / bi antivirus chan).
pyinstaller --onefile --windowed --clean --noconfirm --noupx ^
    --name "Pet_Screen" ^
    --add-data "assets;assets" ^
    --add-data "config.py;." ^
    --add-data "pet_python.py;." ^
    demo.py

if not exist "dist\Pet_Screen.exe" (
    echo.
    echo [LOI] Build that bai - khong tao duoc dist\Pet_Screen.exe
    echo Kiem tra log o tren va dung luong dia.
    pause
    exit /b 1
)

echo.
echo [5/5] Build completed!
echo.
echo File location: dist\Pet_Screen.exe
echo File size:
dir "dist\Pet_Screen.exe" | find "Pet_Screen.exe"
echo.
echo ========================================
echo    Build successful!
echo ========================================
echo.
echo Meo: neu chay exe van loi giai nen, nguyen nhan thuong gap:
echo   1) O dia chua %%TEMP%% gan day - don bot dung luong.
echo   2) Antivirus chan/khoa file khi giai nen - them ngoai le cho exe.
echo   3) Can build --onedir (thu muc) thay vi --onefile de bo buoc giai nen.
pause
