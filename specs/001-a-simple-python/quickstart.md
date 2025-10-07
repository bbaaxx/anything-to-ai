# Quickstart Guide: PDF Text Extraction Module

## Installation

```bash
# Clone repository
git clone <repository-url>
cd anything-to-ai

# Install dependencies
pip install pdfplumber

# Verify installation
python -m pdf_extractor --version
```

## Basic Usage

### Command Line Interface

```bash
# Extract text from a small PDF
python -m pdf_extractor extract sample.pdf

# Extract with progress tracking
python -m pdf_extractor extract --progress large_document.pdf

# Stream processing for large files
python -m pdf_extractor extract --stream --progress report.pdf

# Get JSON output
python -m pdf_extractor extract --format json document.pdf

# Get PDF information
python -m pdf_extractor info document.pdf
```

### Programmatic API

```python
# Basic text extraction
from pdf_extractor import extract_text

result = extract_text("document.pdf")
if result.success:
    for page in result.pages:
        print(f"Page {page.page_number}: {page.text}")
else:
    print(f"Error: {result.error_message}")

# Streaming extraction with progress
from pdf_extractor import extract_text_streaming, ExtractionConfig

def progress_callback(current, total):
    print(f"Processing page {current}/{total}")

config = ExtractionConfig(
    streaming_enabled=True,
    progress_callback=progress_callback,
    output_format="plain"
)

for page_result in extract_text_streaming("large_file.pdf", config):
    print(f"Page {page_result.page_number}: {len(page_result.text)} chars")
```

## Test Scenarios

### Scenario 1: Small PDF Processing

```bash
# Test with a small PDF (≤ 20 pages)
python -m pdf_extractor extract test_files/small_document.pdf
# Expected: Fast processing without streaming
```

### Scenario 2: Large PDF with Streaming

```bash
# Test with a large PDF (> 20 pages)
python -m pdf_extractor extract --stream --progress test_files/large_report.pdf
# Expected: Page-by-page processing with progress updates
```

### Scenario 3: JSON Output Format

```bash
# Test JSON output format
python -m pdf_extractor extract --format json test_files/sample.pdf
# Expected: Structured JSON output with metadata
```

### Scenario 4: Error Handling

```bash
# Test with non-existent file
python -m pdf_extractor extract nonexistent.pdf
# Expected: Exit code 1, clear error message

# Test with corrupted PDF
python -m pdf_extractor extract test_files/corrupted.pdf
# Expected: Exit code 2, corruption error message

# Test with password-protected PDF
python -m pdf_extractor extract test_files/protected.pdf
# Expected: Exit code 3, password protection message
```

### Scenario 5: API Integration Test

```python
# Test programmatic integration
import pdf_extractor

# Basic extraction
result = pdf_extractor.extract_text("test_files/sample.pdf")
assert result.success == True
assert len(result.pages) > 0
assert result.total_chars > 0

# Configuration test
config = pdf_extractor.ExtractionConfig(output_format="json")
result = pdf_extractor.extract_text("test_files/sample.pdf", config)
assert result.success == True

# Error handling test
try:
    pdf_extractor.extract_text("nonexistent.pdf")
except pdf_extractor.PDFNotFoundError as e:
    print(f"Caught expected error: {e}")
```

## Performance Validation

### Memory Usage Test

```bash
# Monitor memory usage with large file
python -c "
import psutil
import pdf_extractor
import os

process = psutil.Process(os.getpid())
initial_memory = process.memory_info().rss

result = pdf_extractor.extract_text('large_file.pdf')
peak_memory = process.memory_info().rss

print(f'Memory usage: {(peak_memory - initial_memory) / 1024 / 1024:.2f} MB')
"
```

### Processing Speed Test

```bash
# Measure processing time
time python -m pdf_extractor extract large_document.pdf
```

## Success Criteria Validation

- [ ] Small files (≤ 20 pages) process without streaming automatically
- [ ] Large files (> 20 pages) can use streaming mode
- [ ] Progress tracking works for both callback and percentage modes
- [ ] CLI interface supports all required options (--stream, --format, --progress)
- [ ] JSON and plain text output formats work correctly
- [ ] Clear error messages for all error conditions
- [ ] Module can be imported and used programmatically
- [ ] Memory usage remains reasonable for large files with streaming
- [ ] Processing speed meets reasonable expectations

## Troubleshooting

### Common Issues

1. **"Module not found" error**

   - Ensure pdfplumber is installed: `pip install pdfplumber`
   - Check Python path includes current directory

2. **"Permission denied" error**

   - Verify file permissions on PDF file
   - Ensure file is not open in another application

3. **"No text found" error**

   - PDF may contain only images - this is expected behavior
   - Try with a different PDF that contains text

4. **Memory issues with large files**
   - Use streaming mode: `--stream` flag
   - Consider processing smaller files or increasing available memory
