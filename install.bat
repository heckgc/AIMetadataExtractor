@echo off
REM Create virtual environment and install dependencies
echo Creating virtual environment...
python -m venv .venv

echo Installing dependencies...
.venv\Scripts\pip install -r requirements.txt
