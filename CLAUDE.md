# makeme-a-podcast-from-docs Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-09-28

## Active Technologies
- Python 3.8+ (for compatibility with standard library features) + PyPDF2 or pdfplumber for PDF parsing (minimal external dependencies per constitution) (001-a-simple-python)
- Python 3.13 (per project requirements) + mlx-vlm (VLM processing), PIL/Pillow (image handling) (002-implement-a-module)
- File system (image files), no persistent storage required (002-implement-a-module)
- Python 3.13 (per project requirements) + mlx-vlm (VLM processing), PIL/Pillow (image handling), existing image_processor module (003-real-vlm-insegration)
- Python 3.13 (per project requirements) + pdfplumber (PDF parsing), mlx-vlm (VLM processing), PIL/Pillow (image handling), existing pdf_extractor and image_processor modules (005-augment-pdf-extraction)
- File system (PDF and image files), no persistent storage required (005-augment-pdf-extraction)
- Python 3.13 (per project requirements) + lightning-whisper-mlx (MLX-optimized Whisper for audio transcription) (006-audio-to-text)
- File system (audio files: mp3, wav, m4a), no persistent storage required (006-audio-to-text)
- Python 3.13 + pre-commit (hook framework), ruff (linting/formatting), pytest (testing), pytest-cov (coverage measurement) (007-add-linting-and)
- N/A (configuration files only) (007-add-linting-and)

## Project Structure
```
src/
tests/
```

## Commands
uv run pytest
uv run ruff check .
uv run python check_file_lengths.py

# Pre-commit hooks
uv run pre-commit install
uv run pre-commit run --all-files
git commit --no-verify

# Image Processing CLI
uv run python -m image_processor <image_files> [--style brief|detailed|technical] [--format json|csv|plain]

# Audio Transcription CLI
uv run python -m audio_processor <audio_files> [--format plain|json] [--model tiny|small|base|medium|large|large-v3] [--quantization none|4bit|8bit] [--language LANG] [--output FILE] [--verbose]

# Note: Default quantization is 'none' due to MLX compatibility. Use --quantization 4bit/8bit only if your MLX version supports it.

## Code Style
Python 3.8+ (for compatibility with standard library features): Follow standard conventions

## Recent Changes
- 007-add-linting-and: Added Python 3.13 + pre-commit (hook framework), ruff (linting/formatting), pytest (testing), pytest-cov (coverage measurement)
- 006-audio-to-text: Added Python 3.13 + lightning-whisper-mlx (MLX-optimized Whisper for Apple Silicon), audio transcription module with support for mp3/wav/m4a formats, multilingual support, batch processing with progress callbacks
- 005-augment-pdf-extraction: Added Python 3.13 (per project requirements) + pdfplumber (PDF parsing), mlx-vlm (VLM processing), PIL/Pillow (image handling), existing pdf_extractor and image_processor modules

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
