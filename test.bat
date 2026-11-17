@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" call setup.bat
if errorlevel 1 exit /b 1

".venv\Scripts\python.exe" -m unittest discover -s tests -v
if errorlevel 1 exit /b 1

echo.
echo All automated tests passed.
echo For a large-file test: .venv\Scripts\python scripts\stress_test.py --size-mb 512
endlocal
