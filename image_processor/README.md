# Image VLM Text Description Module

A Python module for processing images with Vision Language Models (VLM) to generate descriptive text. Features real VLM integration using MLX framework for Apple Silicon optimization.

## Installation & Setup

### Prerequisites
- Python 3.13 or higher
- Apple Silicon Mac (for MLX optimization)
- UV package manager (recommended) or pip

### Dependencies Installation

Using UV (recommended):
```bash
uv add mlx-vlm>=0.3.3 pillow>=11.3.0 torch>=2.8.0
```

Using pip:
```bash
pip install mlx-vlm>=0.3.3 pillow>=11.3.0 torch>=2.8.0
```

### VLM Model Configuration

**Required**: Set the VISION_MODEL environment variable before using the module.

```bash
# Set the VLM model to use
export VISION_MODEL=google/gemma-3-4b

# Alternative models (examples)
export VISION_MODEL=mlx-community/gemma-3-4b-it-4bit
export VISION_MODEL=microsoft/DialoGPT-small
```

### Optional Environment Variables

```bash
# Timeout behavior when VLM processing fails
export VLM_TIMEOUT_BEHAVIOR=error  # options: error, fallback, continue

# Auto-download models if not available
export VLM_AUTO_DOWNLOAD=true  # options: true, false
```

### Verify Installation
```bash
python -m image_processor --help
```

## CLI Usage

### Basic Image Processing
```bash
# Process single image
python -m image_processor image.jpg

# Process multiple images
python -m image_processor *.jpg *.png

# Process with different description styles
python -m image_processor image.jpg --style brief
python -m image_processor image.jpg --style detailed
python -m image_processor image.jpg --style technical
```

### Output Formats
```bash
# JSON output
python -m image_processor image.jpg --format json

# CSV output
python -m image_processor *.jpg --format csv

# Plain text (default)
python -m image_processor image.jpg --format plain
```

### Advanced Options
```bash
# Batch processing with custom settings
python -m image_processor *.jpg --batch-size 2 --max-length 300

# Save output to file
python -m image_processor *.jpg --format json --output results.json

# Verbose progress tracking
python -m image_processor *.jpg --verbose

# Quiet mode (results only)
python -m image_processor image.jpg --quiet
```

### CLI Options
- `--style`: Description style (`detailed`, `brief`, `technical`)
- `--max-length`: Maximum description length (50-1000 chars)
- `--batch-size`: Images to process simultaneously (1-10)
- `--timeout`: Processing timeout per image in seconds
- `--format`: Output format (`plain`, `json`, `csv`)
- `--output`: Save results to file
- `--verbose`: Enable progress output
- `--quiet`: Suppress all output except results

## Python API Usage

### Basic Image Processing

```python
from image_processor import process_image, create_config

# Simple single image processing
result = process_image('image.jpg')
if result.success:
    print(f"Description: {result.description}")
    print(f"Confidence: {result.confidence_score}")
```

### Batch Processing
```python
from image_processor import process_images

# Process multiple images
image_paths = ['img1.jpg', 'img2.png', 'img3.jpeg']
results = process_images(image_paths)

print(f"Processed {results.successful_count}/{results.total_images} images")
for result in results.results:
    if result.success:
        print(f"{result.image_path}: {result.description}")
```

### Advanced Configuration

```python
from image_processor import process_images, create_config

# Custom configuration
config = create_config(
    description_style="technical",
    max_length=300,
    batch_size=2
)

results = process_images(image_paths, config)
```

### Streaming with Progress
```python
from image_processor import process_images_streaming, create_config

def progress_handler(current, total):
    print(f"Processing {current}/{total} images...")

config = create_config(
    description_style="detailed",
    progress_callback=progress_handler
)

# Stream processing with progress updates
for result in process_images_streaming(image_paths, config):
    print(f"Completed: {result.image_path}")
```

### Image Validation
```python
from image_processor import validate_image, get_supported_formats

# Validate image before processing
try:
    img_doc = validate_image('image.jpg')
    print(f"Valid image: {img_doc.format}, {img_doc.width}x{img_doc.height}")
except Exception as e:
    print(f"Invalid image: {e}")

# Check supported formats
formats = get_supported_formats()
print(f"Supported formats: {formats}")
```

## Configuration Options

### ProcessingConfig Parameters

- **description_style** (`str`): Style of description
  - `"detailed"`: Comprehensive descriptions (default)
  - `"brief"`: Short, concise descriptions
  - `"technical"`: Technical/analytical descriptions
- **max_description_length** (`int`): Max characters (50-1000, default: 500)
- **batch_size** (`int`): Concurrent processing (1-10, default: 4)
- **timeout_seconds** (`int`): Per-image timeout (default: 60)
- **progress_callback** (`Callable[[int, int], None]`): Progress tracking function

### VLM-Specific Options

- **vlm_timeout_behavior** (`str`): How to handle timeouts
  - `"error"`: Raise exception (default)
  - `"fallback"`: Use fallback description
  - `"continue"`: Skip and continue processing
- **auto_download_models** (`bool`): Auto-download models (default: `True`)
- **validate_model_before_load** (`bool`): Validate model availability (default: `True`)

## Environment Setup

### Model Configuration
```python
import os
from image_processor import validate_model_availability

# Check if model is available
model_name = "google/gemma-3-4b"
os.environ['VISION_MODEL'] = model_name

is_available = validate_model_availability(model_name)
if not is_available:
    print("Model will be downloaded on first use")
```

### Performance Optimization
```bash
# For faster processing on Apple Silicon
export VISION_MODEL=mlx-community/gemma-3-4b-it-4bit

# For memory-constrained environments
export VLM_AUTO_DOWNLOAD=false
```

## Error Handling

### Exception Types

```python
from image_processor.exceptions import (
    ImageProcessingError,
    ImageNotFoundError,
    UnsupportedFormatError,
    CorruptedImageError
)
from image_processor.vlm_exceptions import (
    VLMConfigurationError,
    VLMModelLoadError,
    VLMProcessingError,
    VLMTimeoutError
)

try:
    result = process_image('image.jpg')
except ImageNotFoundError:
    print("Image file not found")
except UnsupportedFormatError:
    print("Unsupported image format")
except VLMConfigurationError as e:
    print(f"VLM config error: {e}")
    if e.suggested_fix:
        print(f"Fix: {e.suggested_fix}")
except VLMModelLoadError as e:
    print(f"Model loading failed: {e}")
except VLMTimeoutError:
    print("VLM processing timed out")
```

### Common Issues & Solutions

**VLM Configuration Error**:
```bash
# Error: VISION_MODEL not set
export VISION_MODEL=google/gemma-3-4b
```

**Model Loading Issues**:
```python
# Check available models
from image_processor import get_available_models
print(get_available_models())
```

**Memory Issues**:
```python
# Use smaller batch size
config = create_config(batch_size=1)
```

## Data Models

### Core Objects

```python
# Image metadata
ImageDocument(file_path, format, width, height, file_size, is_large_image)

# Processing result for single image
DescriptionResult(
    image_path, description, confidence_score, processing_time,
    model_used, success, technical_metadata, vlm_processing_time, model_version
)

# Batch processing result
ProcessingResult(
    success, results, total_images, successful_count,
    failed_count, total_processing_time, error_message
)
```

## Examples with Sample Data

```python
# Example with project sample images
sample_image = "sample-data/images/DJI_20250817104854_0118_D.JPG"

# Quick processing
result = process_image(sample_image)
print(f"Description: {result.description}")

# Batch process all samples
import glob
sample_images = glob.glob("sample-data/images/*.jpg")
results = process_images(sample_images)

# Technical analysis
config = create_config(description_style="technical")
tech_result = process_image(sample_image, config)
print(f"Technical analysis: {tech_result.description}")
```

## Supported Image Formats

- **JPEG** (.jpg, .jpeg)
- **PNG** (.png)
- **GIF** (.gif)
- **BMP** (.bmp)
- **WebP** (.webp)

Check programmatically:
```python
from image_processor import get_supported_formats
print(get_supported_formats())  # ['bmp', 'gif', 'jpeg', 'png', 'webp']
```