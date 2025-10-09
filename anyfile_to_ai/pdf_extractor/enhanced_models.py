"""Enhanced data models for PDF extraction with image description support."""

from dataclasses import dataclass, field
from typing import Any
from .models import ExtractionConfig, PageResult, ExtractionResult


@dataclass
class EnhancedExtractionConfig(ExtractionConfig):
    """Configuration for PDF extraction with optional image description processing."""

    # Image processing settings
    include_images: bool = False
    image_processing_config: Any | None = None

    # Error handling settings
    image_fallback_text: str = "[Image: processing failed]"
    max_images_per_page: int | None = None

    # Performance settings
    image_batch_size: int = 4
    parallel_image_processing: bool = True

    def __post_init__(self):
        """Validate EnhancedExtractionConfig fields."""
        super().__post_init__()

        # Validate image_batch_size
        if not isinstance(self.image_batch_size, int) or self.image_batch_size < 1 or self.image_batch_size > 10:
            msg = "image_batch_size must be between 1 and 10"
            raise ValueError(msg)

        # Validate max_images_per_page
        if self.max_images_per_page is not None and (not isinstance(self.max_images_per_page, int) or self.max_images_per_page < 1):
            msg = "max_images_per_page must be a positive integer"
            raise ValueError(msg)

        # Validate include_images
        if not isinstance(self.include_images, bool):
            msg = "include_images must be a boolean"
            raise ValueError(msg)

        # Validate fallback text
        if not isinstance(self.image_fallback_text, str):
            msg = "image_fallback_text must be a string"
            raise ValueError(msg)

        # Validate parallel processing flag
        if not isinstance(self.parallel_image_processing, bool):
            msg = "parallel_image_processing must be a boolean"
            raise ValueError(msg)


@dataclass
class ImageContext:
    """Context information for an image extracted from a PDF page."""

    # Position information
    page_number: int
    sequence_number: int  # Order within page
    bounding_box: tuple  # (x0, y0, x1, y1)

    # Image properties
    width: int
    height: int
    format: str  # e.g., "JPEG", "PNG"

    # Processing results
    pil_image: Any | None = None  # PIL Image object
    description: str | None = None
    processing_status: str = "pending"  # pending, success, failed
    error_message: str | None = None

    def __post_init__(self):
        """Validate ImageContext fields."""
        if self.page_number <= 0:
            msg = "page_number must be positive"
            raise ValueError(msg)
        if self.sequence_number <= 0:
            msg = "sequence_number must be positive"
            raise ValueError(msg)
        if not isinstance(self.bounding_box, tuple) or len(self.bounding_box) != 4:
            msg = "bounding_box must be a tuple of 4 coordinates"
            raise ValueError(msg)
        if self.width <= 0:
            msg = "width must be positive"
            raise ValueError(msg)
        if self.height <= 0:
            msg = "height must be positive"
            raise ValueError(msg)
        if not isinstance(self.format, str):
            msg = "format must be a string"
            raise ValueError(msg)
        if self.processing_status not in ["pending", "success", "failed"]:
            msg = "processing_status must be pending, success, or failed"
            raise ValueError(msg)


@dataclass
class EnhancedPageResult(PageResult):
    """Page extraction result with optional image descriptions."""

    # Image-specific additions
    images_found: int = 0
    images_processed: int = 0
    images_failed: int = 0
    image_contexts: list[ImageContext] = field(default_factory=list)
    enhanced_text: str | None = None  # Text with inline image descriptions

    def __post_init__(self):
        """Validate EnhancedPageResult fields."""
        super().__post_init__()

        if self.images_found < 0:
            msg = "images_found must be non-negative"
            raise ValueError(msg)
        if self.images_processed < 0:
            msg = "images_processed must be non-negative"
            raise ValueError(msg)
        if self.images_failed < 0:
            msg = "images_failed must be non-negative"
            raise ValueError(msg)
        if self.images_processed + self.images_failed > self.images_found:
            msg = "processed + failed cannot exceed found images"
            raise ValueError(msg)
        if len(self.image_contexts) != self.images_found:
            msg = "image_contexts length must match images_found"
            raise ValueError(msg)


@dataclass
class EnhancedExtractionResult(ExtractionResult):
    """Complete PDF extraction result with image processing summary."""

    # Image processing summary
    total_images_found: int = 0
    total_images_processed: int = 0
    total_images_failed: int = 0
    image_processing_time: float = 0.0
    vision_model_used: str | None = None

    # Enhanced content
    enhanced_pages: list[EnhancedPageResult] = field(default_factory=list)
    combined_enhanced_text: str | None = None

    def __post_init__(self):
        """Validate EnhancedExtractionResult fields."""
        super().__post_init__()

        if self.total_images_found < 0:
            msg = "total_images_found must be non-negative"
            raise ValueError(msg)
        if self.total_images_processed < 0:
            msg = "total_images_processed must be non-negative"
            raise ValueError(msg)
        if self.total_images_failed < 0:
            msg = "total_images_failed must be non-negative"
            raise ValueError(msg)
        if self.total_images_processed + self.total_images_failed > self.total_images_found:
            msg = "total processed + failed cannot exceed total found images"
            raise ValueError(msg)
        if self.image_processing_time < 0.0:
            msg = "image_processing_time must be non-negative"
            raise ValueError(msg)
        if not isinstance(self.enhanced_pages, list):
            msg = "enhanced_pages must be a list"
            raise ValueError(msg)


def validate_enhanced_extraction_config(config: EnhancedExtractionConfig) -> bool:
    """Validate enhanced extraction configuration."""
    try:
        return (
            isinstance(config.include_images, bool)
            and isinstance(config.image_fallback_text, str)
            and (config.max_images_per_page is None or (isinstance(config.max_images_per_page, int) and config.max_images_per_page > 0))
            and isinstance(config.image_batch_size, int)
            and 1 <= config.image_batch_size <= 10
            and isinstance(config.parallel_image_processing, bool)
        )
    except (AttributeError, TypeError):
        return False


def validate_image_context(context: ImageContext) -> bool:
    """Validate image context."""
    try:
        return (
            isinstance(context.page_number, int)
            and context.page_number >= 1
            and isinstance(context.sequence_number, int)
            and context.sequence_number >= 1
            and isinstance(context.bounding_box, tuple)
            and len(context.bounding_box) == 4
            and isinstance(context.width, int)
            and context.width > 0
            and isinstance(context.height, int)
            and context.height > 0
            and isinstance(context.format, str)
            and context.processing_status in ["pending", "success", "failed"]
        )
    except (AttributeError, TypeError):
        return False


def validate_enhanced_page_result(result: EnhancedPageResult) -> bool:
    """Validate enhanced page result."""
    try:
        return (
            isinstance(result.images_found, int)
            and result.images_found >= 0
            and isinstance(result.images_processed, int)
            and result.images_processed >= 0
            and isinstance(result.images_failed, int)
            and result.images_failed >= 0
            and result.images_processed + result.images_failed <= result.images_found
            and isinstance(result.image_contexts, list)
            and len(result.image_contexts) == result.images_found
        )
    except (AttributeError, TypeError):
        return False


def validate_enhanced_extraction_result(result: EnhancedExtractionResult) -> bool:
    """Validate enhanced extraction result."""
    try:
        return (
            isinstance(result.total_images_found, int)
            and result.total_images_found >= 0
            and isinstance(result.total_images_processed, int)
            and result.total_images_processed >= 0
            and isinstance(result.total_images_failed, int)
            and result.total_images_failed >= 0
            and result.total_images_processed + result.total_images_failed <= result.total_images_found
            and isinstance(result.image_processing_time, float)
            and result.image_processing_time >= 0.0
            and isinstance(result.enhanced_pages, list)
        )
    except (AttributeError, TypeError):
        return False
