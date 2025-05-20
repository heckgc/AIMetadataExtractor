@echo off
REM Set the PYTHONPATH to include the src directory
set PYTHONPATH=%CD%\src

REM Run unit tests
echo Running unit tests...
.venv\Scripts\python -m unittest discover -s tests -p "test_*.py"

REM Run UI test (Selenium)
echo Running UI test...
.venv\Scripts\python tests\test_ui_playright.py
