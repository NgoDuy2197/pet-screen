@echo off
echo ========================================
echo    Building Pet Screen Demo...
echo ========================================

echo.
echo [1/3] Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del "*.spec"

echo.
echo [2/3] Building with PyInstaller...
pyinstaller --onefile --windowed --name "Pet_Screen" --add-data "assets;assets" --add-data "config.py;." --add-data "pet_python.py;." demo.py

echo.
echo [3/3] Build completed!
echo.
echo File location: dist\Pet_Screen.exe
echo File size: 
dir "dist\Pet_Screen.exe" | find "Pet_Screen.exe"
echo.
echo ========================================
echo    Build successful! 🎉
echo ========================================
pause
