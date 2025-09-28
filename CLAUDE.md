# makeme-a-podcast-from-docs Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-09-28

## Active Technologies
- Python 3.8+ (for compatibility with standard library features) + PyPDF2 or pdfplumber for PDF parsing (minimal external dependencies per constitution) (001-a-simple-python)

## Project Structure
```
src/
tests/
```

## Commands
uv run pytest
uv run ruff check .
uv run python check_file_lengths.py

## Code Style
Python 3.8+ (for compatibility with standard library features): Follow standard conventions

## Recent Changes
- 001-a-simple-python: Added Python 3.8+ (for compatibility with standard library features) + PyPDF2 or pdfplumber for PDF parsing (minimal external dependencies per constitution)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
- use uv venv with python 3.13 on this project and never the os python version
- use python version 3.13