"""
API Contract: Image Processor Module Interface
Defines the public API that must be maintained for backward compatibility.
"""

from typing import Any
from dataclasses import dataclass


@dataclass
class DescriptionResult:
    """Enhanced result with both VLM description and technical metadata."""

    image_path: str
    description: str  # Real VLM description (no longer mock)
    confidence_score: float | None
    processing_time: float
    model_used: str  # Environment-configured VLM model
    prompt_used: str
    success: bool
    # New fields for VLM integration
    technical_metadata: dict[str, Any]  # Format, dimensions, file size
    vlm_processing_time: float  # Separate VLM processing time
    model_version: str  # VLM model version information


@dataclass
class ProcessingConfig:
    """Enhanced configuration with VLM model settings."""

    # Existing fields (backward compatibility)
    model_name: str  # Now reads from VISION_MODEL environment variable
    description_style: str = "detailed"
    max_description_length: int = 500
    batch_size: int = 4
    progress_callback: Any | None = None
    prompt_template: str = "Describe this image in a {style} manner."
    timeout_seconds: int = 60
    # New VLM-specific fields
    vlm_timeout_behavior: str = "error"  # "error", "fallback", "continue"
    auto_download_models: bool = True
    validate_model_before_load: bool = True


@dataclass
class ProcessingResult:
    """Enhanced batch processing result with VLM metadata."""

    total_images: int
    successful_count: int
    failed_count: int
    total_processing_time: float
    results: list[DescriptionResult]
    errors: list[dict[str, Any]]


def create_config(**kwargs) -> ProcessingConfig:
    """
    Create processing configuration.

    BACKWARD COMPATIBILITY: Existing signature preserved.
    NEW: Reads model from VISION_MODEL environment variable if not provided.

    Returns:
        ProcessingConfig: Enhanced configuration with VLM settings

    Raises:
        VLMConfigurationError: If VISION_MODEL not set and no model provided
        VLMModelNotFoundError: If specified model not available
    """


def process_images(image_paths: list[str], config: ProcessingConfig) -> "ProcessingResult":
    """
    Process images with real VLM integration.

    BACKWARD COMPATIBILITY: Exact same signature as existing implementation.
    NEW: Uses real VLM models instead of mock descriptions.

    Args:
        image_paths: List of image file paths
        config: Processing configuration with VLM settings

    Returns:
        ProcessingResult: Enhanced results with VLM descriptions and metadata

    Raises:
        VLMModelLoadError: If VLM model fails to load
        VLMProcessingError: If VLM processing fails
        VLMTimeoutError: If processing exceeds timeout
        ImageProcessingError: Existing errors preserved
    """


def validate_model_availability(model_name: str) -> bool:
    """
    Validate that specified VLM model is available.

    NEW API: Added for VLM model validation.

    Args:
        model_name: VLM model identifier

    Returns:
        bool: True if model available, False otherwise
    """


def get_available_models() -> list[str]:
    """
    Get list of available VLM models.

    NEW API: Added for VLM model discovery.

    Returns:
        List[str]: Available VLM model identifiers
    """


# Environment Variable Contract
ENV_VISION_MODEL = "VISION_MODEL"  # Required for VLM model selection

# Output Format Contract (Enhanced but Backward Compatible)
JSON_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "total_images": {"type": "integer"},
        "successful_count": {"type": "integer"},
        "failed_count": {"type": "integer"},
        "total_processing_time": {"type": "number"},
        "results": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string"},
                    "description": {"type": "string"},  # Real VLM description
                    "confidence_score": {"type": ["number", "null"]},
                    "processing_time": {"type": "number"},
                    "model_used": {"type": "string"},  # VLM model name
                    "success": {"type": "boolean"},
                    # Enhanced fields
                    "technical_metadata": {"type": "object", "properties": {"format": {"type": "string"}, "dimensions": {"type": "array", "items": {"type": "integer"}}, "file_size": {"type": "integer"}}},
                    "vlm_processing_time": {"type": "number"},
                    "model_version": {"type": "string"},
                },
                "required": ["image_path", "description", "processing_time", "model_used", "success", "technical_metadata"],
            },
        },
    },
    "required": ["success", "total_images", "successful_count", "failed_count", "total_processing_time", "results"],
}

# CLI Contract (Exact Backward Compatibility)
CLI_ARGUMENTS = [
    "images",  # Positional: image file paths
    "--style",  # choices=['detailed', 'brief', 'technical']
    "--max-length",  # int: maximum description length
    "--batch-size",  # int: batch processing size
    "--timeout",  # int: processing timeout
    "--output",  # str: output file path
    "--format",  # choices=['plain', 'json', 'csv']
    "--verbose",  # bool: verbose output
    "--quiet",  # bool: quiet mode
]

# Error Hierarchy Contract (Extended)
EXCEPTION_HIERARCHY = {
    "ImageProcessingError": "Base exception (existing)",
    "VLMConfigurationError": "VLM configuration issues (new)",
    "VLMModelLoadError": "VLM model loading failures (new)",
    "VLMProcessingError": "VLM processing failures (new)",
    "VLMTimeoutError": "VLM processing timeout (new)",
    "VLMModelNotFoundError": "Specified model unavailable (new)",
}
