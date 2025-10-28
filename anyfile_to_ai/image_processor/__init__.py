"""Image VLM Text Description Module.

A module for processing images with Vision Language Models (VLM) to generate
descriptive text. Features real VLM integration using MLX framework for Apple
Silicon optimization.

This implementation provides:
- Real VLM processing with configurable models via VISION_MODEL environment variable
- Enhanced results combining AI descriptions with technical metadata
- Backward-compatible API preserving existing interfaces
- Comprehensive error handling with VLM-specific exception types
- Batch processing with automatic memory cleanup

Environment Configuration:
    VISION_MODEL: Required - VLM model identifier (e.g., google/gemma-3-4b)
    VLM_TIMEOUT_BEHAVIOR: Optional - Timeout behavior (error/fallback/continue)
    VLM_AUTO_DOWNLOAD: Optional - Auto-download models (true/false)

Example:
    export VISION_MODEL=google/gemma-3-4b
    python -m image_processor image.jpg --format json
"""

from .models import ImageDocument, DescriptionResult, ProcessingResult, ProcessingConfig
from .exceptions import (
    ImageProcessingError,
    ImageNotFoundError,
    UnsupportedFormatError,
    CorruptedImageError,
    ProcessingError,
    ValidationError,
    # VLM-specific exceptions
    VLMConfigurationError,
    VLMModelLoadError,
    VLMProcessingError,
    VLMTimeoutError,
    VLMModelNotFoundError,
)

# Import VLM model validation functions
from .model_loader import validate_model_availability, get_available_models

# Global processor instances
_processor = None
_streaming_processor = None


def _get_processor():
    """Get or create processor instance."""
    global _processor
    if _processor is None:
        from .processor import VLMProcessor

        _processor = VLMProcessor()
    return _processor


def _get_streaming_processor():
    """Get or create streaming processor instance."""
    global _streaming_processor
    if _streaming_processor is None:
        from .streaming import StreamingProcessor

        _streaming_processor = StreamingProcessor(_get_processor())
    return _streaming_processor


# Core API functions
def process_image(file_path: str, config: "ProcessingConfig" = None, include_metadata: bool = False) -> "DescriptionResult":
    """Process single image and generate descriptive text."""
    if config is None:
        config = ProcessingConfig()

    processor = _get_processor()
    image_doc = processor.validate_image(file_path)
    return processor.process_single_image(image_doc, config, include_metadata)


def process_images(file_paths: list, config: "ProcessingConfig" = None, include_metadata: bool = False) -> "ProcessingResult":
    """Process multiple images in batch."""
    if config is None:
        config = ProcessingConfig()

    streaming_processor = _get_streaming_processor()
    return streaming_processor.process_batch(file_paths, config, include_metadata)


def validate_image(file_path: str) -> "ImageDocument":
    """Validate image file and extract metadata."""
    processor = _get_processor()
    return processor.validate_image(file_path)


def get_supported_formats() -> list:
    """Get list of supported image formats."""
    from .processor import SUPPORTED_FORMATS

    return sorted(SUPPORTED_FORMATS)


def process_images_streaming(file_paths: list, config: "ProcessingConfig" = None, include_metadata: bool = False):
    """Process images with streaming progress updates."""
    if config is None:
        config = ProcessingConfig()

    streaming_processor = _get_streaming_processor()
    return streaming_processor.process_streaming(file_paths, config, include_metadata)


def create_config(description_style: str = "detailed", max_length: int = 500, batch_size: int = 4, progress_callback=None, **kwargs) -> "ProcessingConfig":
    """Create processing configuration with validation."""
    # Validate parameters
    valid_styles = ["detailed", "brief", "technical"]
    if description_style not in valid_styles:
        from .exceptions import ValidationError

        msg = f"Must be one of {valid_styles}"
        raise ValidationError(msg, "description_style")

    if not (50 <= max_length <= 1000):
        from .exceptions import ValidationError

        msg = "Must be between 50 and 1000"
        raise ValidationError(msg, "max_length")

    if not (1 <= batch_size <= 10):
        from .exceptions import ValidationError

        msg = "Must be between 1 and 10"
        raise ValidationError(msg, "batch_size")

    return ProcessingConfig(description_style=description_style, max_description_length=max_length, batch_size=batch_size, progress_callback=progress_callback, **kwargs)


def get_image_info(file_path: str) -> dict:
    """Get image information without processing."""
    image_doc = validate_image(file_path)
    return {"file_path": image_doc.file_path, "format": image_doc.format, "width": image_doc.width, "height": image_doc.height, "file_size": image_doc.file_size, "is_large_image": image_doc.is_large_image}


__version__ = "0.1.0"
__all__ = [
    "CorruptedImageError",
    "DescriptionResult",
    # Core models and data structures
    "ImageDocument",
    "ImageNotFoundError",
    # Exception hierarchy
    "ImageProcessingError",
    "ProcessingConfig",
    "ProcessingError",
    "ProcessingResult",
    "UnsupportedFormatError",
    # VLM-specific exceptions
    "VLMConfigurationError",
    "VLMModelLoadError",
    "VLMModelNotFoundError",
    "VLMProcessingError",
    "VLMTimeoutError",
    "ValidationError",
    "create_config",
    "get_available_models",
    "get_image_info",
    "get_supported_formats",
    # Core processing functions
    "process_image",
    "process_images",
    "process_images_streaming",
    "validate_image",
    # VLM-specific functions
    "validate_model_availability",
]
