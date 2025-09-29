# Quickstart: Real VLM Integration

## Prerequisites

1. **Environment Setup**
   ```bash
   # Set VLM model (required)
   export VISION_MODEL=google/gemma-3-4b

   # Optional VLM configuration
   export VLM_TIMEOUT_BEHAVIOR=error  # error, fallback, continue
   export VLM_AUTO_DOWNLOAD=true
   ```

2. **Dependencies**
   ```bash
   # Install VLM dependencies
   uv add mlx-vlm

   # Existing dependencies (preserved)
   uv add pillow
   ```

## Basic Usage (Unchanged Interface)

### CLI Usage
```bash
# Single image (same as before, now with real VLM)
python -m image_processor image.jpg

# Multiple images with JSON output
python -m image_processor *.png --format json --output results.json

# Batch processing with style preference
python -m image_processor folder/ --style brief --batch-size 2
```

### Module Usage (Enhanced but Compatible)
```python
from image_processor import create_config, process_images

# Create configuration (same interface)
config = create_config(
    description_style="detailed",
    batch_size=4,
    timeout_seconds=60
)

# Process images (same interface, enhanced results)
results = process_images(["image1.jpg", "image2.png"], config)

# Results now include real VLM descriptions + technical metadata
for result in results.results:
    print(f"Image: {result.image_path}")
    print(f"VLM Description: {result.description}")  # Real AI description
    print(f"Technical: {result.technical_metadata}")  # Format, size, dimensions
    print(f"Model: {result.model_used} v{result.model_version}")
```

## New VLM Features

### Model Configuration
```python
# Check available models
from image_processor import get_available_models
print(get_available_models())

# Validate model before use
from image_processor import validate_model_availability
if validate_model_availability("google/gemma-3-4b"):
    # Proceed with processing
    pass
```

### Enhanced Results
```python
# VLM-enhanced results structure
result = {
    "image_path": "image.jpg",
    "description": "A real AI-generated description",  # No longer mock
    "confidence_score": 0.95,
    "processing_time": 2.3,
    "model_used": "google/gemma-3-4b",
    "model_version": "v1.0",
    "success": True,
    "technical_metadata": {
        "format": "JPEG",
        "dimensions": [1920, 1080],
        "file_size": 245760
    },
    "vlm_processing_time": 1.8
}
```

## Testing Scenarios

### 1. Basic VLM Processing
```bash
# Test: VLM model loads and processes image
export VISION_MODEL=google/gemma-3-4b
python -m image_processor sample-data/test-image.jpg --format json

# Expected: Real AI description in JSON output
# Verify: description field contains actual AI analysis, not mock text
```

### 2. Model Configuration Validation
```bash
# Test: Error when no model configured
unset VISION_MODEL
python -m image_processor image.jpg

# Expected: Clear error message about VISION_MODEL requirement
# Verify: Exit code 1 with helpful error message
```

### 3. Invalid Model Handling
```bash
# Test: Error for unavailable model
export VISION_MODEL=nonexistent/model
python -m image_processor image.jpg

# Expected: Model not found error with available models list
# Verify: Clear error message and graceful failure
```

### 4. Timeout Behavior
```bash
# Test: Configurable timeout behavior
export VISION_MODEL=google/gemma-3-4b
export VLM_TIMEOUT_BEHAVIOR=error
python -m image_processor large-image.jpg --timeout 5

# Expected: Timeout error after 5 seconds
# Verify: Processing stops and reports timeout
```

### 5. Batch Processing with Cleanup
```bash
# Test: Memory cleanup after batch
export VISION_MODEL=google/gemma-3-4b
python -m image_processor *.jpg --batch-size 4 --verbose

# Expected: Processes all images, cleans up model memory
# Verify: No memory leaks, successful batch completion
```

### 6. Backward Compatibility
```bash
# Test: All existing CLI arguments work
python -m image_processor folder/ \
    --style technical \
    --max-length 200 \
    --batch-size 2 \
    --timeout 30 \
    --output results.csv \
    --format csv \
    --verbose

# Expected: Same behavior as before, with real VLM descriptions
# Verify: CSV output format unchanged, descriptions enhanced
```

### 7. Module API Compatibility
```python
# Test: Existing code continues to work
from image_processor import create_config, process_images

# Old configuration code (unchanged)
config = create_config(description_style="brief")
results = process_images(["test.jpg"], config)

# Verify: Same interface, enhanced results
assert hasattr(results.results[0], 'description')
assert hasattr(results.results[0], 'technical_metadata')
```

## Error Handling Test Cases

### VLM Configuration Errors
- Missing VISION_MODEL environment variable
- Invalid model name specification
- Model validation failure

### VLM Processing Errors
- Model loading failure
- Image processing timeout
- VLM inference errors

### Backward Compatibility
- All existing error scenarios preserved
- New VLM errors provide clear guidance
- No breaking changes to error handling patterns

## Performance Validation

### Expected Performance
- **Model Loading**: One-time cost per batch (amortized)
- **VLM Processing**: 1-5 seconds per image (model-dependent)
- **Memory Usage**: Monitored and cleaned up automatically
- **Batch Efficiency**: Model reuse within batches

### Performance Tests
```bash
# Time single image processing
time python -m image_processor image.jpg

# Monitor memory during batch processing
python -m image_processor *.jpg --batch-size 8 --verbose
```

## Success Criteria

1. ✅ **VLM Integration**: Real AI descriptions replace mock text
2. ✅ **API Compatibility**: All existing interfaces preserved
3. ✅ **Configuration**: Environment-based model selection works
4. ✅ **Error Handling**: Clear errors for VLM configuration/processing issues
5. ✅ **Performance**: Reasonable processing times with automatic cleanup
6. ✅ **Output Enhancement**: Technical metadata preserved alongside VLM descriptions
7. ✅ **Model Management**: Automatic download, validation, and resource cleanup

## Rollback Plan

If issues arise:
1. VLM processing can be disabled via environment variable
2. System falls back to existing implementation patterns
3. No data loss or interface breaking changes
4. Clear error messages guide troubleshooting