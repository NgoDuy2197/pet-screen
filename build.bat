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
pyinstaller --onefile --windowed --name "Pet_Screen_Demo" --add-data "assets;assets" --add-data "config.py;." --add-data "pet_python.py;." demo.py

echo.
echo [3/3] Build completed!
echo.
echo File location: dist\Pet_Screen_Demo.exe
echo File size: 
dir "dist\Pet_Screen_Demo.exe" | find "Pet_Screen_Demo.exe"
echo.
echo ========================================
echo    Build successful! 🎉
echo ========================================
pause
