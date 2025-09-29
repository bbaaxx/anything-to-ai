# PDF Text Extractor

A Python module for extracting text from PDF files with streaming support for large documents.

## Installation & Setup

### Prerequisites
- Python 3.13 or higher
- UV package manager (recommended) or pip

### Dependencies Installation

Using UV (recommended):
```bash
uv add pdfplumber>=0.11.7
```

Using pip:
```bash
pip install pdfplumber>=0.11.7
```

### Verify Installation
```bash
python -m pdf_extractor --version
```

## CLI Usage

### Basic Text Extraction
```bash
# Extract text in plain format
python -m pdf_extractor extract document.pdf

# Extract with JSON output
python -m pdf_extractor extract document.pdf --format json

# Extract with progress tracking
python -m pdf_extractor extract document.pdf --progress

# Extract large files with streaming
python -m pdf_extractor extract large_document.pdf --stream --progress
```

### Get PDF Information
```bash
# Get basic PDF metadata
python -m pdf_extractor info document.pdf
```

### CLI Options
- `extract`: Extract text from PDF file
  - `--stream`: Enable streaming mode for large files (>20 pages)
  - `--format`: Output format (`plain` or `json`)
  - `--progress`: Show extraction progress
- `info`: Display PDF metadata (pages, file size, etc.)

## Python API Usage

### Basic Text Extraction

```python
from pdf_extractor import extract_text, get_pdf_info

# Simple text extraction
result = extract_text('document.pdf')
if result.success:
    for page in result.pages:
        print(f"Page {page.page_number}: {page.text}")

# Get PDF information
info = get_pdf_info('document.pdf')
print(f"Pages: {info['page_count']}, Size: {info['file_size']} bytes")
```

### Streaming Extraction for Large Files

```python
from pdf_extractor import extract_text_streaming, ExtractionConfig

# Configure with progress tracking
def progress_handler(current, total):
    print(f"Processing page {current}/{total}")

config = ExtractionConfig(
    streaming_enabled=True,
    progress_callback=progress_handler,
    output_format="plain"
)

# Stream process pages one by one
for page_result in extract_text_streaming('large_document.pdf', config):
    print(f"Page {page_result.page_number}: {len(page_result.text)} characters")
```

### Advanced Configuration

```python
from pdf_extractor import extract_text, ExtractionConfig

# Custom configuration
config = ExtractionConfig(
    streaming_enabled=False,
    output_format="json"
)

result = extract_text('document.pdf', config)
print(f"Extracted {result.total_chars} characters in {result.processing_time:.2f}s")
```

## Configuration Options

### ExtractionConfig Parameters

- **streaming_enabled** (`bool`): Enable streaming mode (default: `True`)
  - `True`: Process pages one at a time (memory efficient)
  - `False`: Load entire document into memory
- **progress_callback** (`Callable[[int, int], None]`): Progress tracking function
  - Receives `(current_page, total_pages)` during extraction
- **output_format** (`str`): Output format (`"plain"` or `"json"`)

### Environment Recommendations

- **Small PDFs** (<20 pages): Use `streaming_enabled=False` for faster processing
- **Large PDFs** (≥20 pages): Use `streaming_enabled=True` to avoid memory issues
- **Progress Tracking**: Always use `progress_callback` for long-running extractions

## Error Handling

### Exception Types

```python
from pdf_extractor.exceptions import (
    PDFNotFoundError,
    PDFCorruptedError,
    PDFPasswordProtectedError,
    PDFNoTextError,
    ProcessingInterruptedError
)

try:
    result = extract_text('document.pdf')
except PDFNotFoundError:
    print("PDF file not found")
except PDFCorruptedError as e:
    print(f"PDF is corrupted: {e}")
except PDFPasswordProtectedError:
    print("PDF is password protected")
except PDFNoTextError:
    print("PDF contains no extractable text")
```

### Exit Codes (CLI)

- `0`: Success
- `1`: File not found
- `2`: Corrupted PDF
- `3`: Password protected
- `4`: No extractable text
- `5`: Processing interrupted
- `6`: Unexpected error

## Data Models

### Core Objects

```python
# PDF document metadata
PDFDocument(file_path, page_count, file_size, is_large_file)

# Individual page result
PageResult(page_number, text, char_count, extraction_time)

# Complete extraction result
ExtractionResult(success, pages, total_pages, total_chars, processing_time, error_message)
```

## Examples with Sample Data

```python
# Example with project sample files
sample_pdf = "sample-data/pdf/fpsyg-15-1353022 (1).pdf"

# Quick extraction
result = extract_text(sample_pdf)
print(f"Extracted {result.total_chars} characters from {result.total_pages} pages")

# Get info first
info = get_pdf_info(sample_pdf)
if info['is_large_file']:
    print("Using streaming mode for large file")
    # Use streaming for large files
```