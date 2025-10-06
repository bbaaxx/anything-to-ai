# Make Me a Podcast from Docs

> **Experimental Project**: An evolving experiment exploring complexity in document processing and content generation.

This repository contains modular tools for processing documents, images, and audio with AI models. Currently implemented as independent modules that can be used separately or together.

## What's Inside

### 📄 PDF Text Extractor

Extract text from PDF documents with streaming support for large files.

- **Documentation**: [`pdf_extractor/README.md`](pdf_extractor/README.md)
- **Usage**: CLI and Python API for text extraction

### 🖼️ Image VLM Processor

Process images with Vision Language Models to generate descriptive text.

- **Documentation**: [`image_processor/README.md`](image_processor/README.md)
- **Usage**: CLI and Python API for AI-powered image description

### 🎙️ Audio Transcription Module

Transcribe audio files using MLX-optimized Whisper models for Apple Silicon.

- **Documentation**: [`audio_processor/README.md`](audio_processor/README.md)
- **Usage**: CLI and Python API for audio-to-text transcription with multilingual support

### 📝 Text Summarizer Module

Summarize text using LLM models with automatic language detection and intelligent chunking.

- **Documentation**: [`text_summarizer/README.md`](text_summarizer/README.md)
- **Usage**: CLI and Python API for AI-powered text summarization with pipeline support

## Quick Start

### Prerequisites

- Python 3.13+
- UV package manager (recommended)
- Apple Silicon Mac (for MLX-optimized features)

### Setup

```bash
# Clone and enter directory
git clone <repo-url>
cd makeme-a-podcast-from-docs

# Install dependencies
uv sync

# For image processing, configure VLM model
export VISION_MODEL=google/gemma-3-4b
```

### Try It Out

```bash
# Extract text from a PDF
python -m pdf_extractor extract sample-data/pdf/*.pdf --format json

# Process images with VLM
python -m image_processor sample-data/images/*.jpg --style brief

# Transcribe audio files
python -m audio_processor sample-data/audio/*.mp3 --format json --verbose

# Summarize text
echo "Artificial intelligence is transforming industries..." | python -m text_summarizer --stdin --format plain

# Pipeline: Audio → Transcription → Summary
python -m audio_processor sample-data/audio/podcast.mp3 --format plain | python -m text_summarizer --stdin
```

## Project Structure

```
makeme-a-podcast-from-docs/
├── pdf_extractor/          # PDF text extraction module
├── image_processor/        # VLM image processing module
├── audio_processor/        # Audio transcription module
├── text_summarizer/        # Text summarization module
├── llm_client/            # Unified LLM client for AI services
├── sample-data/           # Sample PDFs, images, and audio for testing
├── tests/                 # Test suites
└── specs/                 # Feature specifications and development docs
```

## Development Commands

```bash
# Run tests
uv run pytest

# Run comprehensive human review test suite (quick integration test)
./tests/human_review_quick_test

# Code formatting and linting
uv run ruff check .
uv run ruff format .

# Pre-commit hooks (auto-run on git commit)
uv run pre-commit install        # Install hooks (one-time setup)
uv run pre-commit run --all-files # Run manually on all files

# Check file length compliance
uv run python check_file_lengths.py
```

### Development Workflow

Pre-commit hooks automatically run linting and formatting checks when you commit. These hooks:

- Fix simple issues automatically (imports, whitespace, formatting)
- Report complex issues that require manual fixes (complexity, undefined names)

**When to bypass hooks** (use `git commit --no-verify`):

- Emergency hotfixes that need immediate deployment
- Pre-commit tool malfunction or configuration issues
- Work-in-progress commits during local experimentation
- Dependency updates that may temporarily break checks

**When NOT to bypass hooks**:

- To avoid fixing legitimate linting errors
- To skip required code quality checks
- To save time during normal development

Note: CI will enforce all checks regardless of local bypass, making this a safe escape hatch for edge cases.

## Module Features

### PDF Extractor

- Streaming support for large files
- Progress tracking
- Multiple output formats (plain, JSON, CSV)
- Error handling for corrupted/protected PDFs

### Image Processor

- Vision Language Model integration
- Multiple description styles (brief, detailed, technical)
- Batch processing with progress
- MLX optimization for Apple Silicon

### Audio Transcription

- MLX-optimized Whisper models
- Multilingual support with auto-detection
- Multiple model sizes (tiny to large-v3)
- Batch processing with progress tracking
- Support for mp3, wav, and m4a formats

### Text Summarizer

- LLM-powered intelligent summarization
- Automatic language detection (outputs in English)
- Hierarchical chunking for large documents (>10k words)
- Minimum 3 categorization tags per summary
- Pipeline integration with other modules
- JSON and plain text output formats

## Status

🚧 **Work in Progress** - This is an evolving experiment. Modules are functional but the overall vision continues to develop.

Each module is documented independently. Check their individual READMEs for detailed usage instructions.

## Contributing

This is an experimental project exploring modular design patterns. Feel free to explore the code and documentation in the `specs/` directory to understand the development process.
