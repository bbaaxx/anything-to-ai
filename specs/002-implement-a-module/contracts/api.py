"""API contracts for image VLM processing module.

This module defines the expected function signatures and return types
that match the functional requirements from the specification.
"""

from typing import Any
from collections.abc import Callable
from dataclasses import dataclass

# Progress callback signature
ProgressCallback = Callable[[int, int], None]  # (current_image, total_images)


@dataclass
class ImageDocument:
    """Contract for image document representation."""

    file_path: str
    format: str
    width: int
    height: int
    file_size: int
    is_large_image: bool


@dataclass
class DescriptionResult:
    """Contract for individual image processing result."""

    image_path: str
    description: str
    confidence_score: float | None
    processing_time: float
    model_used: str
    prompt_used: str
    success: bool


@dataclass
class ProcessingResult:
    """Contract for complete processing operation result."""

    success: bool
    results: list[DescriptionResult]
    total_images: int
    successful_count: int
    failed_count: int
    total_processing_time: float
    error_message: str | None = None


@dataclass
class ProcessingConfig:
    """Contract for processing configuration."""

    model_name: str = "mlx-community/Qwen2-VL-2B-Instruct-4bit"
    description_style: str = "detailed"
    max_description_length: int = 500
    batch_size: int = 4
    progress_callback: ProgressCallback | None = None
    prompt_template: str = "Describe this image in a {style} manner."
    timeout_seconds: int = 60


# Core Processing Functions (FR-003, FR-004)
def process_image(file_path: str, config: ProcessingConfig | None = None) -> DescriptionResult:
    """Process single image and generate descriptive text.

    Args:
        file_path: Path to image file
        config: Optional processing configuration

    Returns:
        DescriptionResult with generated description and metadata

    Raises:
        ImageNotFoundError: Image file doesn't exist
        UnsupportedFormatError: Image format not supported
        ProcessingError: VLM processing failed
    """


def process_images(file_paths: list[str], config: ProcessingConfig | None = None) -> ProcessingResult:
    """Process multiple images in batch (FR-007).

    Args:
        file_paths: List of image file paths
        config: Optional processing configuration

    Returns:
        ProcessingResult with all individual results and batch metadata

    Raises:
        ValidationError: Invalid input parameters
        ProcessingError: Batch processing failed
    """


# Validation Functions (FR-001, FR-002)
def validate_image(file_path: str) -> ImageDocument:
    """Validate image file and extract metadata.

    Args:
        file_path: Path to image file

    Returns:
        ImageDocument with validated metadata

    Raises:
        ImageNotFoundError: File doesn't exist
        UnsupportedFormatError: Format not supported
        CorruptedImageError: File corrupted or unreadable
    """


def get_supported_formats() -> list[str]:
    """Get list of supported image formats (FR-001).

    Returns:
        List of supported file extensions
    """


# Progress and Streaming Functions (FR-005)
def process_images_streaming(file_paths: list[str], config: ProcessingConfig | None = None) -> list[DescriptionResult]:
    """Process images with streaming progress updates.

    Args:
        file_paths: List of image file paths
        config: Configuration including progress callback

    Yields:
        DescriptionResult for each processed image

    Raises:
        ValidationError: Invalid configuration
        ProcessingError: Streaming processing failed
    """


# Configuration Functions (FR-009, FR-010)
def create_config(description_style: str = "detailed", max_length: int = 500, batch_size: int = 4, progress_callback: ProgressCallback | None = None) -> ProcessingConfig:
    """Create processing configuration with validation.

    Args:
        description_style: Style preference (detailed, brief, technical)
        max_length: Maximum description length
        batch_size: Batch processing size
        progress_callback: Optional progress callback

    Returns:
        Validated ProcessingConfig instance

    Raises:
        ValidationError: Invalid configuration parameters
    """


def get_image_info(file_path: str) -> dict[str, Any]:
    """Get image information without processing (similar to PDF get_info).

    Args:
        file_path: Path to image file

    Returns:
        Dictionary with image metadata

    Raises:
        ImageNotFoundError: File doesn't exist
        CorruptedImageError: File unreadable
    """
