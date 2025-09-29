# Quickstart Guide: Image VLM Text Description Module

## Installation Requirements

```bash
# Install project dependencies
uv add mlx-vlm pillow

# Verify MLX framework is available (macOS required)
python -c "import mlx.core; print('MLX available')"
```

## Basic Usage

### Single Image Processing

```python
from image_processor import process_image, ProcessingConfig

# Basic processing with defaults
result = process_image("sample.jpg")
print(f"Description: {result.description}")

# Custom configuration
config = ProcessingConfig(
    description_style="brief",
    max_description_length=200
)
result = process_image("sample.jpg", config)
```

### Batch Processing

```python
from image_processor import process_images

# Process multiple images
image_paths = ["image1.jpg", "image2.png", "image3.gif"]
results = process_images(image_paths)

print(f"Processed {results.successful_count}/{results.total_images} images")
for result in results.results:
    if result.success:
        print(f"{result.image_path}: {result.description}")
```

### Progress Tracking

```python
from image_processor import process_images_streaming, ProcessingConfig

def progress_handler(current, total):
    print(f"Processing {current}/{total} images...")

config = ProcessingConfig(progress_callback=progress_handler)
for result in process_images_streaming(image_paths, config):
    print(f"Completed: {result.image_path}")
```

## Command Line Usage

### Basic Commands

```bash
# Process single image
python -m image_processor photo.jpg

# Process multiple images with custom style
python -m image_processor *.png --style brief --max-length 200

# Batch processing with progress
python -m image_processor images/ --verbose --batch-size 2
```

### Output Formats

```bash
# JSON output to file
python -m image_processor images/ --format json --output results.json

# CSV format for spreadsheet import
python -m image_processor *.jpg --format csv --output descriptions.csv

# Plain text to stdout
python -m image_processor image.jpg --format plain
```

## Configuration Options

### Description Styles

- **detailed**: Comprehensive descriptions with context and details
- **brief**: Concise descriptions focusing on key elements
- **technical**: Technical descriptions suitable for accessibility

### Model Sizes

- **small**: Fast processing, good quality (2B parameters)
- **medium**: Balanced performance (7B parameters)
- **large**: Highest quality, slower processing (72B parameters)

### Batch Processing

```python
config = ProcessingConfig(
    batch_size=4,        # Images per batch
    timeout_seconds=120, # Per-image timeout
    model_name="mlx-community/Qwen2-VL-7B-Instruct-4bit"
)
```

## Error Handling

### Common Errors

```python
from image_processor.exceptions import (
    ImageNotFoundError,
    UnsupportedFormatError,
    ProcessingError
)

try:
    result = process_image("missing.jpg")
except ImageNotFoundError as e:
    print(f"File not found: {e.image_path}")
except UnsupportedFormatError as e:
    print(f"Format not supported: {e}")
except ProcessingError as e:
    print(f"Processing failed: {e}")
```

### Graceful Batch Processing

```python
results = process_images(image_paths)
for result in results.results:
    if result.success:
        print(f"✓ {result.image_path}: {result.description}")
    else:
        print(f"✗ {result.image_path}: Processing failed")
```

## Integration Examples

### With PDF Processor

```python
from pdf_extractor import extract_text
from image_processor import process_image

def process_document_assets(pdf_path, image_paths):
    """Process both PDF and image content."""

    # Extract PDF text
    pdf_result = extract_text(pdf_path)
    pdf_content = "\n".join(page.text for page in pdf_result.pages)

    # Process associated images
    image_descriptions = []
    for image_path in image_paths:
        result = process_image(image_path)
        if result.success:
            image_descriptions.append(result.description)

    return {
        "pdf_content": pdf_content,
        "image_descriptions": image_descriptions
    }
```

### Progress Integration

```python
from image_processor import ProcessingConfig, process_images_streaming

def process_with_unified_progress(image_paths):
    """Unified progress tracking across processing."""

    def progress_handler(current, total):
        percentage = (current / total) * 100
        print(f"Progress: {percentage:.1f}% ({current}/{total})")

    config = ProcessingConfig(progress_callback=progress_handler)

    results = []
    for result in process_images_streaming(image_paths, config):
        results.append(result)

    return results
```

## Performance Guidelines

### Memory Management

- Keep batch sizes small for large images (2-4 images)
- Use larger batches for small images (4-8 images)
- Monitor system memory usage during processing

### Optimization Tips

```python
# Optimize for speed
fast_config = ProcessingConfig(
    model_name="mlx-community/Qwen2-VL-2B-Instruct-4bit",
    description_style="brief",
    max_description_length=200,
    batch_size=6
)

# Optimize for quality
quality_config = ProcessingConfig(
    model_name="mlx-community/Qwen2.5-VL-72B-Instruct-4bit",
    description_style="detailed",
    max_description_length=800,
    batch_size=2
)
```

## Troubleshooting

### Common Issues

1. **Model loading fails**
   - Ensure MLX framework is properly installed
   - Check available system memory
   - Verify internet connection for model download

2. **Image processing slow**
   - Reduce batch size for large images
   - Use smaller model for faster processing
   - Check image file sizes and optimize if needed

3. **Memory errors**
   - Reduce batch size
   - Process images sequentially
   - Use image preprocessing to reduce size

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all processing will show debug information
result = process_image("debug.jpg")
```