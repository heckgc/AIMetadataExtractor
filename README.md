# AIMetadataExtractor
Allows you to extract embedded metadata information from images generated from AI sourcers

## Features
This runs entirely locally, is fast and reliable, and work with any kind of image (that contains any kind of embedded information).
It makes use of [Flask]() and [Python]() to run a microserver, allowing you easy access to image information.
This can be used to extract prompts, information and workflows, proving both JSON and copy function.

## Installation and Running
Make sure you have the required dependencies. Python and Flask.
Also make sure to run this in a contained environment for better handling of pip packages.

### Installation
1. Install the dependencies:
```bash
python3 -m venv .venv
pip install -r requirements.txt
```
2. Run the service:
```bash
python3 main.py
```
3. Access it via any browser:
```bash
0.0.0.0:50001
```

## Versions
This is should be version 1.0, but there could be improvements in the future.

## Thank you
Thank you for taking a look.