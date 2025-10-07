# Quick Start: anything_to_ai Package

**Date**: 2025-10-06
**Feature**: Prepare Repository for Python Packaging
**Status**: Complete

## Installation

### Install Core Package

```bash
pip install anything_to_ai
```

### Install with Specific Modules

```bash
# PDF processing only
pip install anything_to_ai[pdf]

# Image processing only
pip install anything_to_ai[image]

# Audio transcription only
pip install anything_to_ai[audio]

# Text summarization only
pip install anything_to_ai[text]

# All modules
pip install anything_to_ai[all]
```

### Install for Development

```bash
pip install anything_to_ai[dev]
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

## Python API Usage

### Import Modules

```python
from anything_to_ai.pdf_extractor import PDFExtractor
from anything_to_ai.image_processor import ImageProcessor
from anything_to_ai.audio_processor import AudioProcessor
from anything_to_ai.text_summarizer import TextSummarizer
```

### PDF Processing Example

```python
extractor = PDFExtractor()
result = extractor.extract("document.pdf", format="json")
print(result.text)
```

### Image Processing Example

```python
processor = ImageProcessor()
result = processor.process("image.jpg", style="detailed")
print(result.description)
```

### Audio Transcription Example

```python
transcriber = AudioProcessor()
result = transcriber.transcribe("audio.mp3", format="json")
print(result.text)
```

### Text Summarization Example

```python
summarizer = TextSummarizer()
result = summarizer.summarize("long_text.txt", format="markdown")
print(result.summary)
```

## Pipeline Examples

### Audio to Summary Pipeline

```bash
audio-processor podcast.mp3 --format plain | \
text-summarizer --stdin --format markdown > summary.md
```

### PDF to Summary Pipeline

```bash
pdf-extractor extract document.pdf --format plain | \
text-summarizer --stdin --format json > summary.json
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
# Set vision model for image processing
export VISION_MODEL=google/gemma-3-4b

# Configure LLM provider for text summarization
export LLM_PROVIDER=ollama
export LLM_MODEL=mistral
```

## Validation Steps

### Verify Installation

```bash
# Check package installation
python -c "import anything_to_ai; print('Package installed successfully')"

# Test CLI commands
pdf-extractor --help
image-processor --help
audio-processor --help
text-summarizer --help
```

### Test Module Functionality

```bash
# Test with sample files
pdf-extractor extract test.pdf --format plain
image-processor test.jpg --style brief
audio-processor test.mp3 --format json
text-summarizer test.txt --format markdown
```

## Troubleshooting

### Common Issues

1. **Module not found error**

   - Ensure correct optional dependencies are installed
   - Check Python version compatibility (>=3.11)

2. **ML model errors**

   - Install required ML models separately
   - Check model configuration environment variables

3. **CLI command not found**
   - Verify package installation with correct extras
   - Check Python scripts directory in PATH

### Getting Help

```bash
# Check package version
pip show anything_to_ai

# Get help for specific commands
pdf-extractor --help
image-processor --help
audio-processor --help
text-summarizer --help
```

## Next Steps

1. Install required ML models for your use case
2. Configure environment variables for model settings
3. Test with your own files
4. Explore Python API for integration projects
5. Check documentation for advanced features

## Support

- Documentation: Available in each module's README
- Issues: Report via project repository
- Examples: Check test files for usage patterns
