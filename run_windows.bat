@echo off
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo First install: python -m venv .venv
  echo Then: .venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
pause
