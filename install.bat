@echo off
REM filepath: /d:/aiwaifu/AIMetadataExtractor/manage.bat

REM Create virtual environment and install dependencies
echo Creating virtual environment...
python -m venv .venv

echo Installing dependencies...
.venv\Scripts\pip install -r requirements.txt

REM Run the application
echo Starting the application...
.venv\Scripts\python src\main.py

REM Run tests
echo Running tests...
.venv\Scripts\python -m unittest discover -s tests -p "test_*.py"