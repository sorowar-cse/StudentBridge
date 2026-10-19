@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3.12 -m venv .venv
  if errorlevel 1 (
    echo Install Python 3.12, including the Python launcher, then retry.
    pause
    exit /b 1
  )
)
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 (
  echo Dependency installation failed. Check your internet connection.
  pause
  exit /b 1
)
.venv\Scripts\python.exe scripts\setup_local.py
if errorlevel 1 (
  echo Setup was not completed. See DEVELOPER_GUIDE_BN.md.
  pause
  exit /b 1
)
echo Setup files created. Finish the Supabase SQL and account steps before signing in.
pause
