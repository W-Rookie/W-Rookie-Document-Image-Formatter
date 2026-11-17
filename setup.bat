@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title W-Rookie Setup

set "PYTHON_CMD="
set "SETUP_STEP=Python detection"
set "ERROR_LOG=%~dp0setup-error.log"

echo ============================================================
echo  W-Rookie - First-time setup
echo ============================================================
echo.

where py >nul 2>nul
if not errorlevel 1 (
  py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
  if not errorlevel 1 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
  where python >nul 2>nul
  if not errorlevel 1 (
    python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
  )
)

if not defined PYTHON_CMD goto :no_python

echo [1/4] Python 3.10 or newer found.
%PYTHON_CMD% --version
echo.

set "SETUP_STEP=Virtual environment creation"
if not exist ".venv\Scripts\python.exe" (
  echo [2/4] Creating a private Python environment...
  call %PYTHON_CMD% -m venv ".venv"
  if errorlevel 1 goto :setup_failed
) else (
  echo [2/4] Existing private Python environment found.
)

".venv\Scripts\python.exe" -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if errorlevel 1 (
  set "SETUP_STEP=Virtual environment validation"
  goto :broken_venv
)

set "SETUP_STEP=pip upgrade"
echo [3/4] Updating the installer...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :setup_failed

set "SETUP_STEP=W-Rookie dependency installation"
echo.
echo [4/4] Installing W-Rookie and security components...
".venv\Scripts\python.exe" -m pip install -e ".[hwp]"
if errorlevel 1 goto :setup_failed

".venv\Scripts\python.exe" -c "import docpicalign, defusedxml, olefile, tkinter" >nul 2>nul
if errorlevel 1 (
  set "SETUP_STEP=Final import validation"
  goto :setup_failed
)

if exist "%ERROR_LOG%" del /q "%ERROR_LOG%" >nul 2>nul
echo.
echo ============================================================
echo  Setup completed successfully.
echo  Next: double-click run.bat to open the GUI.
echo ============================================================
echo.
echo Press any key to close this setup window.
pause >nul
exit /b 0

:no_python
>"%ERROR_LOG%" echo [%date% %time%] Python 3.10 or newer was not found.
echo.
echo [ERROR] Python 3.10 or newer was not found.
echo.
echo Install Python from:
echo https://www.python.org/downloads/windows/
echo.
echo During installation, enable these options if shown:
echo   - Add python.exe to PATH
echo   - Install launcher for all users
echo.
echo After installation, restart Windows and run setup.bat again.
echo Error details: %ERROR_LOG%
echo.
pause
exit /b 1

:broken_venv
>"%ERROR_LOG%" echo [%date% %time%] Existing .venv is invalid or uses an old Python version.
echo.
echo [ERROR] The existing .venv folder is invalid or too old.
echo Rename or delete the .venv folder, then run setup.bat again.
echo Error details: %ERROR_LOG%
echo.
pause
exit /b 1

:setup_failed
set "SETUP_CODE=%errorlevel%"
>"%ERROR_LOG%" echo [%date% %time%] Setup failed.
>>"%ERROR_LOG%" echo Step: %SETUP_STEP%
>>"%ERROR_LOG%" echo Exit code: %SETUP_CODE%
echo.
echo [ERROR] Setup failed during: %SETUP_STEP%
echo Exit code: %SETUP_CODE%
echo Error details: %ERROR_LOG%
echo.
echo Read the messages above. This window will stay open until you press a key.
pause
exit /b %SETUP_CODE%
