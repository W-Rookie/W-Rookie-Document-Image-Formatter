@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" call setup.bat
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m pip install -e ".[hwp,dev]"
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m unittest discover -s tests -v
if errorlevel 1 exit /b 1

".venv\Scripts\pyinstaller.exe" --noconfirm --clean --windowed --name W-Rookie --paths src --collect-data docpicalign launcher.py
if errorlevel 1 exit /b 1

echo.
echo Build complete: dist\W-Rookie\W-Rookie.exe
endlocal
