# AIMetadataExtractor
Allows you to extract embedded metadata information from images generated from AI sources

# Live preview
It is available at https://heckgc.pythonanywhere.com/ for live preview.

## UI
![page1](/docs/page1.png)
![page2](/docs/page2.png)

## Features
This runs entirely locally, is fast and reliable, and work with any kind of image (that contains any kind of embedded information).
It makes use of [Flask](https://flask.palletsprojects.com/en/stable/) and [Python](https://www.python.org/) to run a microserver, allowing you easy access to image information.
This can be used to extract prompts, information and workflows, proving both JSON and copy function.

### Testing

This project includes both unit tests and UI automation tests.

#### Unit Tests

Unit tests are written using Python’s built-in `unittest` framework.  
They cover the core logic and can be run with:

```bash
make test
```
or, if you prefer to run only unit tests:
```bash
make test  # (unit tests run first, then UI tests)
```

#### UI Tests (Playwright)

UI tests use [Playwright for Python](https://playwright.dev/python/), which automates browser interactions to verify the web interface works as expected.

To run the UI test alone:

```bash
make uitest
```

**Requirements:**  
- Playwright and its Python bindings must be installed in your virtual environment.  
  You can install them with:
  ```bash
  pip install playwright
  python -m playwright install
  ```

**How it works:**  
- The UI test uploads a sample image and checks that the expected UI elements (such as "prompt" and "workflow" boxes) appear.

#### Notes

- Make sure your Flask app is running before executing UI tests.
- You can find the test scripts in the `tests/` directory.
- The `Makefile` automates the test process for convenience.

## Installation and Running

You can use the provided `Makefile` (Linux/macOS) or `run.bat` (Windows) to set up and run the application easily.

### Installation

**On Linux/macOS:**
1. Create the virtual environment and install dependencies:
    ```bash
    make install
    ```
2. Run the service:
    ```bash
    make run
    ```

**On Windows:**
1. Create the virtual environment and install dependencies:
    ```bat
    run.bat
    ```

### Access the App

Once running, open your browser and go to:
```
http://0.0.0.0:50001
```
or
```
http://127.0.0.1:50001
```

---

You can still use `make test` or `test.bat` to run all tests as described above.

## Versions
This is should be version 1.0, but there could be improvements in the future.

## Thank you
Thank you for taking a look.
