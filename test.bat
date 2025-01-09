@echo off
REM filepath: /d:/aiwaifu/AIMetadataExtractor/test.bat

REM Set the PYTHONPATH to include the src directory
set PYTHONPATH=%CD%\src

REM Run tests
echo Running tests...
.venv\Scripts\python -m unittest discover -s tests -p "test_*.py"