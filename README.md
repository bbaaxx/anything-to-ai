# anyfile_to_ai

> **Universal File Processor with AI-Powered Capabilities**

A Python package that provides unified access to PDF text extraction, image processing, audio transcription, and text summarization using AI models. Install as a package with optional dependencies for modular usage.

## What's Inside

### 📄 PDF Text Extractor

Extract text from PDF documents with streaming support for large files.

- **Documentation**: [`anyfile_to_ai/pdf_extractor/README.md`](anyfile_to_ai/pdf_extractor/README.md)
- **Usage**: CLI and Python API for text extraction

### 🖼️ Image VLM Processor

Process images with Vision Language Models to generate descriptive text.

- **Documentation**: [`anyfile_to_ai/image_processor/README.md`](anyfile_to_ai/image_processor/README.md)
- **Usage**: CLI and Python API for AI-powered image description

### 🎙️ Audio Transcription Module

Transcribe audio files using MLX-optimized Whisper models for Apple Silicon.

- **Documentation**: [`anyfile_to_ai/audio_processor/README.md`](anyfile_to_ai/audio_processor/README.md)
- **Usage**: CLI and Python API for audio-to-text transcription with multilingual support

### 📝 Text Summarizer Module

Summarize text using LLM models with automatic language detection and intelligent chunking.

- **Documentation**: [`anyfile_to_ai/text_summarizer/README.md`](anyfile_to_ai/text_summarizer/README.md)
- **Usage**: CLI and Python API for AI-powered text summarization with pipeline support

### 🔀 Document Converter Bridge

Convert a local file path or HTTP/HTTPS URL with deterministic backend routing across PDF, image, audio, and MarkItDown-backed document formats.

- **Usage**: CLI and Python API with stable `source`/`route`/`content` output contract

## Installation

### Install Core Package

```bash
pip install anyfile_to_ai
```

### Install with Specific Modules

```bash
# PDF processing only
pip install anyfile_to_ai[pdf]

# Image processing only
pip install anyfile_to_ai[image]

# Audio transcription only
pip install anyfile_to_ai[audio]

# Text summarization only
pip install anyfile_to_ai[text]

# All modules
pip install anyfile_to_ai[all]
```

### Install for Development

```bash
pip install anyfile_to_ai[dev]
```

## Quick Usage Examples

### PDF Text Extraction

```bash
# Extract text from PDF
pdf-extractor extract document.pdf --format json

# Extract with streaming for large files
pdf-extractor extract large-document.pdf --stream --progress
```

### Image Processing

```bash
# Process images with AI description
image-processor photo.jpg --style detailed

# Batch process multiple images
image-processor *.jpg --style brief --format json
```

### Audio Transcription

```bash
# Transcribe audio file
audio-processor podcast.mp3 --format json --verbose

# Transcribe with specific model
audio-processor interview.wav --model base --language en
```

### Text Summarization

```bash
# Summarize text file
text-summarizer article.txt --format markdown

# Summarize from stdin
cat document.txt | text-summarizer --stdin --format json
```

### Document Conversion

```bash
# Convert a local Office file via MarkItDown route
document-converter /tmp/report.docx

# Convert with metadata enabled for specialized routes
document-converter /tmp/file.pdf --include-metadata
```

### Pipeline Examples

```bash
# Audio to Summary Pipeline
audio-processor podcast.mp3 --format plain | \
text-summarizer --stdin --format markdown > summary.md

# PDF to Summary Pipeline
pdf-extractor extract document.pdf --format plain | \
text-summarizer --stdin --format json > summary.json

# PDF with image descriptions (provider-aware vision backend)
pdf-extractor extract document.pdf --include-images \
  --provider lmstudio \
  --base-url http://127.0.0.1:1234/v1 \
  --vision-model qwen/qwen3-vl-8b
```

## Python API Usage

### Import Modules

```python
from anyfile_to_ai.pdf_extractor import extract_text
from anyfile_to_ai.image_processor import process_image
from anyfile_to_ai.audio_processor import transcribe_audio
from anyfile_to_ai.text_summarizer import summarize_text
from anyfile_to_ai.document_converter import convert_document
```

### PDF Processing Example

```python
result = extract_text("document.pdf", format="json")
print(result.text)
```

### Image Processing Example

```python
result = process_image("image.jpg", style="detailed")
print(result.description)
```

### Audio Transcription Example

```python
result = transcribe_audio("audio.mp3", format="json")
print(result.text)
```

### Text Summarization Example

```python
result = summarize_text("long_text.txt", format="markdown")
print(result.summary)
```

### Document Converter Example

```python
result = convert_document("/tmp/report.docx")
print(result.route, result.content)
```

## Model Setup

### ML Model Installation

Since ML models are not included in the package, install them separately:

```bash
# For image processing (VLM models)
pip install mlx-vlm

# For audio transcription (Whisper models)
pip install lightning-whisper-mlx

# For text summarization (LLM client)
pip install httpx
```

### Model Configuration

```bash
# Unified provider configuration
export PROVIDER=ollama
export BASE_URL=http://127.0.0.1:11434

# Text and vision model selection
export TEXT_MODEL=qwen/qwen3-14b
export VISION_MODEL=qwen/qwen3-vl-8b
```

```bash
# Per-command overrides (highest priority)
text-summarizer article.txt --provider lmstudio --base-url http://127.0.0.1:1234/v1 --text-model qwen/qwen3-14b
image-processor photo.jpg --provider lmstudio --base-url http://127.0.0.1:1234/v1 --vision-model qwen/qwen3-vl-8b
pdf-extractor extract paper.pdf --include-images --provider lmstudio --base-url http://127.0.0.1:1234/v1 --vision-model qwen/qwen3-vl-8b
```

## Development

### Prerequisites

- Python 3.11+
- UV package manager (recommended)
- Apple Silicon Mac (for MLX-optimized features)

### Development Setup

```bash
# Clone and enter directory
git clone <repo-url>
cd anyfile-to-ai

# Install development dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install
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
## Shared Output Formatter (Spec 017)

The repository now includes `anyfile_to_ai/output_formatter/` as the canonical formatter package for `plain`, `markdown`, and `json` output assembly.

- Use profile values: `pdf`, `image`, `audio`, `text`, `document_converter`.
- JSON serialization is deterministic and can include normalized metadata when requested.
- Module-local formatter paths remain available with rollback toggles (`ANYFILE_OUTPUT_FORMATTER_*_SHARED=0`) during migration.
