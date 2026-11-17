@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title W-Rookie Launcher

if not exist ".venv\Scripts\python.exe" (
  echo [W-Rookie] First-time setup is required.
  echo.
  call setup.bat
  if errorlevel 1 goto :setup_error
)

if not exist ".venv\Scripts\pythonw.exe" goto :environment_error
if not exist "run_gui.pyw" goto :environment_error

".venv\Scripts\python.exe" -c "import docpicalign, defusedxml, olefile, tkinter" >nul 2>nul
if errorlevel 1 goto :environment_error

echo Starting the W-Rookie GUI...
start "" ".venv\Scripts\pythonw.exe" "%~dp0run_gui.pyw"
if errorlevel 1 goto :launch_error
exit /b 0

:setup_error
echo.
echo [ERROR] Setup did not complete.
echo Read setup-error.log or run setup.bat again.
echo.
pause
exit /b 1

:environment_error
echo.
echo [ERROR] The installation is incomplete or damaged.
echo Run setup.bat again. If it still fails, rename the .venv folder first.
echo.
pause
exit /b 1

:launch_error
echo.
echo [ERROR] The GUI could not be started.
echo Check w-rookie-error.log in this folder.
echo.
pause
exit /b 1
