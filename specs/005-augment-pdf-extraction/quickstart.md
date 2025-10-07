# Quickstart: Enhanced PDF Extraction with Image Description

**Date**: 2025-09-29
**Feature**: 005-augment-pdf-extraction

## Prerequisites

1. **Environment Setup**:
   ```bash
   export VISION_MODEL=google/gemma-3-4b
   ```

2. **Test Data**:
   - Sample PDF with text and images: `sample-data/pdfs/document-with-images.pdf`
   - Sample PDF with text only: `sample-data/pdfs/text-only.pdf`

3. **Dependencies**:
   - Existing `pdf_extractor` module working
   - Existing `image_processor` module working with VLM

## Basic Usage

### 1. Text-Only Extraction (Existing Functionality)
```bash
# Should work exactly as before
uv run python -m pdf_extractor sample-data/pdfs/text-only.pdf

# Expected output: Text content only, no image processing
```

### 2. Enhanced Extraction with Image Descriptions
```bash
# Enable image processing
uv run python -m pdf_extractor sample-data/pdfs/document-with-images.pdf --include-images

# Expected output: Text content with inline image descriptions
# Example: "The document discusses... [Image 1: A chart showing sales data] ...the quarterly results"
```

### 3. Customized Image Processing
```bash
# Custom image style and fallback text
uv run python -m pdf_extractor sample-data/pdfs/document-with-images.pdf \
    --include-images \
    --image-style brief \
    --image-fallback "[Figure: description unavailable]"

# Limit images per page
uv run python -m pdf_extractor sample-data/pdfs/document-with-images.pdf \
    --include-images \
    --max-images 3
```

## Output Formats

### 1. JSON Output with Image Data
```bash
uv run python -m pdf_extractor sample-data/pdfs/document-with-images.pdf \
    --include-images \
    --format json

# Expected JSON structure:
{
  "text": "Combined text with image descriptions",
  "enhanced_text": "Text with [Image N: description] annotations",
  "pages": [...],
  "total_pages": 5,
  "total_images_found": 3,
  "total_images_processed": 3,
  "total_images_failed": 0,
  "vision_model_used": "google/gemma-3-4b",
  "processing_time": 2.5,
  "image_processing_time": 1.8
}
```

### 2. CSV Output with Image Summary
```bash
uv run python -m pdf_extractor sample-data/pdfs/document-with-images.pdf \
    --include-images \
    --format csv

# Expected CSV columns:
# page_number,text,images_found,images_processed,processing_time
```

## Streaming Processing

### 1. Progress Monitoring
```bash
uv run python -m pdf_extractor sample-data/pdfs/large-document.pdf \
    --include-images \
    --progress

# Expected progress output:
# Processing page 1/10... (2 images found)
# Processing image 1/2... success
# Processing image 2/2... success
# Page 1 complete (2.3s)
```

### 2. Batch Processing Configuration
```bash
# Process images in smaller batches (memory constrained environments)
uv run python -m pdf_extractor sample-data/pdfs/document-with-images.pdf \
    --include-images \
    --batch-size 2

# Process with maximum time limits
export VLM_TIMEOUT_BEHAVIOR=fallback
uv run python -m pdf_extractor sample-data/pdfs/document-with-images.pdf \
    --include-images
```

## Error Scenarios

### 1. Missing Vision Model Configuration
```bash
# Unset VISION_MODEL
unset VISION_MODEL
uv run python -m pdf_extractor sample-data/pdfs/document-with-images.pdf --include-images

# Expected error:
# Error: VISION_MODEL environment variable required for image processing
# Exit code: 1
```

### 2. Corrupted PDF with Images
```bash
uv run python -m pdf_extractor sample-data/pdfs/corrupted-with-images.pdf --include-images

# Expected behavior:
# - PDF extraction fails with clear error message
# - No partial results returned
# - Exit code: 2
```

### 3. PDF with Unprocessable Images
```bash
uv run python -m pdf_extractor sample-data/pdfs/unsupported-images.pdf --include-images

# Expected behavior:
# - Text extraction succeeds
# - Failed images show fallback text: "[Image: processing failed]"
# - Processing completes successfully
# - Exit code: 0
```

## Validation Scenarios

### 1. Backward Compatibility Check
```bash
# Test that existing functionality works unchanged
uv run python -m pdf_extractor sample-data/pdfs/text-only.pdf > before.txt
# Install enhanced version
uv run python -m pdf_extractor sample-data/pdfs/text-only.pdf > after.txt
diff before.txt after.txt

# Expected: No differences (identical output)
```

### 2. Performance Baseline
```bash
# Measure text-only extraction time
time uv run python -m pdf_extractor sample-data/pdfs/large-document.pdf

# Measure enhanced extraction time
time uv run python -m pdf_extractor sample-data/pdfs/large-document.pdf --include-images

# Expected: Enhanced processing takes longer but remains reasonable
# Text-only: <5s, Enhanced: <30s for 10-page document with 20 images
```

### 3. Memory Usage Validation
```bash
# Monitor memory usage during processing
uv run python -m pdf_extractor sample-data/pdfs/large-document.pdf \
    --include-images \
    --batch-size 1  # Minimal memory usage

# Expected: Memory usage stays under 1GB throughout processing
```

## Integration Testing

### 1. Module Interface Validation
```bash
# Test programmatic API
python -c "
from pdf_extractor import extract_text
from pdf_extractor.enhanced_models import EnhancedExtractionConfig

config = EnhancedExtractionConfig(include_images=True)
result = extract_text('sample-data/pdfs/document-with-images.pdf', config)
print(f'Processed {result.total_images_processed} images')
"
```

### 2. Streaming Interface Validation
```bash
# Test streaming API
python -c "
from pdf_extractor import extract_text_streaming
from pdf_extractor.enhanced_models import EnhancedExtractionConfig

config = EnhancedExtractionConfig(include_images=True)
for page_result in extract_text_streaming('sample-data/pdfs/document-with-images.pdf', config):
    print(f'Page {page_result.page_number}: {page_result.images_found} images')
"
```

## Expected Test Results

### Success Criteria
1. **Functionality**: All commands execute without errors
2. **Output Quality**: Image descriptions are coherent and relevant
3. **Performance**: Processing completes within reasonable time limits
4. **Compatibility**: Existing functionality unchanged when `--include-images` not used
5. **Error Handling**: Clear error messages for all failure scenarios
6. **Memory Usage**: No memory leaks during long-running processes

### Failure Indicators
1. **Silent Failures**: Commands succeed but produce no image descriptions
2. **Memory Leaks**: Memory usage continuously increases during processing
3. **Broken Compatibility**: Existing commands produce different outputs
4. **Poor Error Messages**: Cryptic or missing error information
5. **Performance Regression**: Text-only extraction becomes slower

## Troubleshooting

### Common Issues
1. **"VISION_MODEL not set"**: Export the environment variable
2. **"VLM model not found"**: Check model name and availability
3. **Out of memory**: Reduce batch size or process fewer images
4. **Slow processing**: Check VLM model size and system resources
5. **No images found**: Verify PDF contains embedded images

### Debug Commands
```bash
# Check VLM configuration
uv run python -c "from image_processor import validate_model_availability; print(validate_model_availability())"

# Test image processing isolation
uv run python -m image_processor sample-data/images/test.jpg --format json

# Validate PDF structure
uv run python -c "import pdfplumber; pdf = pdfplumber.open('test.pdf'); print([len(p.images) for p in pdf.pages])"
```

This quickstart guide validates that the enhanced PDF extraction feature works correctly across all intended use cases while maintaining backward compatibility and providing clear error handling.
