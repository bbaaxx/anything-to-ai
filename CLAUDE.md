# makeme-a-podcast-from-docs Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-09-28

## Active Technologies
- Python 3.8+ (for compatibility with standard library features) + PyPDF2 or pdfplumber for PDF parsing (minimal external dependencies per constitution) (001-a-simple-python)
- Python 3.13 (per project requirements) + mlx-vlm (VLM processing), PIL/Pillow (image handling) (002-implement-a-module)
- File system (image files), no persistent storage required (002-implement-a-module)
- Python 3.13 (per project requirements) + mlx-vlm (VLM processing), PIL/Pillow (image handling), existing image_processor module (003-real-vlm-insegration)

## Project Structure
```
src/
tests/
```

## Commands
uv run pytest
uv run ruff check .
uv run python check_file_lengths.py

# Image Processing CLI (MOCK)
uv run python -m image_processor <image_files> [--style brief|detailed|technical] [--format json|csv|plain]

## Code Style
Python 3.8+ (for compatibility with standard library features): Follow standard conventions

## Recent Changes
- 003-real-vlm-insegration: Added Python 3.13 (per project requirements) + mlx-vlm (VLM processing), PIL/Pillow (image handling), existing image_processor module
- 002-implement-a-module: Added Python 3.13 (per project requirements) + mlx-vlm (VLM processing), PIL/Pillow (image handling) - **MOCK IMPLEMENTATION** (returns placeholder text, not real AI analysis)
- 001-a-simple-python: Added Python 3.8+ (for compatibility with standard library features) + PyPDF2 or pdfplumber for PDF parsing (minimal external dependencies per constitution)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
