# anyfile-to-ai Project Overview

## Purpose

Universal file processor with AI-powered capabilities. Provides unified access to:
- **PDF text extraction** - Extract text from PDFs with streaming support
- **Image processing** - VLM-powered image description
- **Audio transcription** - MLX-optimized Whisper for Apple Silicon
- **Text summarization** - LLM-powered intelligent summarization
- **Document conversion** - Unified routing for various document types

## Tech Stack

- **Language**: Python 3.11+ (3.13 recommended)
- **Package Manager**: UV
- **Testing**: pytest, pytest-cov, pytest-rerunfailures
- **Linting/Formatting**: Ruff
- **Pre-commit**: Hooks for automated quality checks
- **Core Dependencies**:
  - pdfplumber (PDF extraction)
  - mlx-vlm, Pillow (image processing)
  - lightning-whisper-mlx (audio transcription)
  - httpx (LLM client)
  - pydantic (validation)
  - alive-progress (progress tracking)
  - markitdown (document conversion)

## Project Status

🚧 Work in progress - evolving experimental project

## Module Architecture

```
anyfile_to_ai/
├── pdf_extractor/      # PDF text extraction
├── image_processor/    # VLM image processing
├── audio_processor/    # Whisper transcription
├── text_summarizer/    # LLM summarization
├── document_converter/ # Unified document routing
├── output_formatter/   # Shared output formatting (plain/json/markdown)
├── llm_client/         # OpenAI-compatible LLM client
├── progress_tracker/   # Progress tracking and cancellation
├── task_manager/       # Persistent task state storage
└── routes/             # Document routing logic
```