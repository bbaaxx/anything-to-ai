# Data Model: Image VLM Text Description Module

## Core Entities

### ImageDocument
**Purpose**: Represents an image file being processed with metadata for validation and processing decisions.

**Fields**:
- `file_path: str` - Absolute path to the image file
- `format: str` - Image format (JPG, PNG, GIF, BMP, WEBP)
- `width: int` - Image width in pixels
- `height: int` - Image height in pixels
- `file_size: int` - File size in bytes
- `is_large_image: bool` - Flag for images requiring special handling

**Validation Rules**:
- `file_path` must exist and be readable
- `format` must be in supported formats list
- `width` and `height` must be positive integers
- `file_size` must be non-negative
- `is_large_image` determined by file size > 10MB or dimensions > 2048px

**State Transitions**: None (immutable data structure)

### DescriptionResult
**Purpose**: Contains generated text description with processing metadata and confidence metrics.

**Fields**:
- `image_path: str` - Path to processed image
- `description: str` - Generated descriptive text
- `confidence_score: Optional[float]` - Model confidence if available (0.0-1.0)
- `processing_time: float` - Time taken for VLM processing
- `model_used: str` - Name of VLM model used for generation
- `prompt_used: str` - Prompt template used for generation
- `success: bool` - Processing success status

**Validation Rules**:
- `image_path` must match original input path
- `description` must be non-empty string when success=True
- `confidence_score` must be between 0.0 and 1.0 if provided
- `processing_time` must be positive float
- `success` must be True for valid descriptions

**State Transitions**: None (immutable result structure)

### ProcessingResult
**Purpose**: Complete result of image processing operation including batch metadata and overall status.

**Fields**:
- `success: bool` - Overall processing success
- `results: List[DescriptionResult]` - Individual image processing results
- `total_images: int` - Number of images processed
- `successful_count: int` - Number of successfully processed images
- `failed_count: int` - Number of failed processing attempts
- `total_processing_time: float` - Total time for entire operation
- `error_message: Optional[str]` - Error message if success=False

**Validation Rules**:
- `total_images` must equal length of results list
- `successful_count + failed_count` must equal `total_images`
- `total_processing_time` must be positive
- `error_message` must be None when success=True
- `success` must be False when failed_count > 0 and successful_count == 0

**Relationships**:
- Contains multiple `DescriptionResult` entities
- Aggregates success/failure statistics from individual results

### ProcessingConfig
**Purpose**: Configuration settings for VLM processing including style preferences and callback options.

**Fields**:
- `model_name: str` - MLX-VLM model identifier
- `description_style: str` - Style preference (detailed, brief, technical)
- `max_description_length: int` - Maximum characters in description
- `batch_size: int` - Number of images to process simultaneously
- `progress_callback: Optional[ProgressCallback]` - Callback for progress updates
- `prompt_template: str` - Template for VLM prompts
- `timeout_seconds: int` - Maximum processing time per image

**Validation Rules**:
- `model_name` must be valid MLX-VLM model identifier
- `description_style` must be in ["detailed", "brief", "technical"]
- `max_description_length` must be positive integer (50-1000)
- `batch_size` must be positive integer (1-10)
- `timeout_seconds` must be positive integer (10-300)
- `prompt_template` must contain "{style}" placeholder

**Default Values**:
- `model_name`: "mlx-community/Qwen2-VL-2B-Instruct-4bit"
- `description_style`: "detailed"
- `max_description_length`: 500
- `batch_size`: 4
- `timeout_seconds`: 60
- `prompt_template`: "Describe this image in a {style} manner."

## Data Relationships

### Processing Flow
```
ImageDocument → ProcessingConfig → VLM Processing → DescriptionResult → ProcessingResult
```

### Aggregation Hierarchy
```
ProcessingResult
├── Multiple DescriptionResult instances
└── Aggregated statistics and metadata
```

### Configuration Dependencies
```
ProcessingConfig
├── Influences DescriptionResult.model_used
├── Determines DescriptionResult.prompt_used
└── Controls batch processing behavior
```

## Validation Patterns

### Input Validation
- All file paths validated for existence and readability
- Image formats checked against supported types
- Configuration parameters within acceptable ranges

### Processing Validation
- Results must match input image count
- Success flags must be consistent with content
- Timing metrics must be realistic (positive values)

### Output Validation
- Descriptions must be non-empty for successful processing
- Error messages required for failed processing
- Statistics must sum correctly across results

## Error Handling Integration

### Validation Errors
- `ValidationError`: Invalid input parameters or configuration
- `UnsupportedFormatError`: Unsupported image format detected
- `FileSizeError`: Image file too large for processing

### Processing Errors
- `ModelLoadError`: MLX-VLM model loading failure
- `ProcessingTimeoutError`: Processing exceeded timeout limit
- `InsufficientMemoryError`: System memory exhausted during processing

### Result Errors
- All processing errors captured in DescriptionResult.success = False
- Error details preserved in ProcessingResult.error_message
- Partial results supported for batch processing failures
