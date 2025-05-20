# Makefile for AIMetadataExtractor

# Variables
VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

# Targets
.PHONY: all install run test uitest clean

all: install run

install:
    @echo "Creating virtual environment..."
    python3 -m venv $(VENV_DIR)
    @echo "Installing dependencies..."
    $(PIP) install -r requirements.txt

run:
    @echo "Starting the application..."
    $(PYTHON) src/main.py

test:
    @echo "Running unit tests..."
    $(PYTHON) -m unittest discover -s tests -p "test_*.py"
    @$(MAKE) uitest

uitest:
    @echo "Running Playwright UI test..."
    $(PYTHON) tests/test_ui_playright.py

clean:
    @echo "Cleaning up..."
    rm -rf $(VENV_DIR)
    find . -type f -name '*.pyc' -delete
    find . -type d -name '__pycache__' -delete
