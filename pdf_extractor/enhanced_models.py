"""Enhanced data models for PDF extraction with image description support."""

from dataclasses import dataclass, field
from typing import List, Optional, Any
from .models import ExtractionConfig, PageResult, ExtractionResult


@dataclass
class EnhancedExtractionConfig(ExtractionConfig):
    """Configuration for PDF extraction with optional image description processing."""

    # Image processing settings
    include_images: bool = False
    image_processing_config: Optional[Any] = None

    # Error handling settings
    image_fallback_text: str = "[Image: processing failed]"
    max_images_per_page: Optional[int] = None

    # Performance settings
    image_batch_size: int = 4
    parallel_image_processing: bool = True

    def __post_init__(self):
        """Validate EnhancedExtractionConfig fields."""
        super().__post_init__()

        # Validate image_batch_size
        if not isinstance(self.image_batch_size, int) or self.image_batch_size < 1 or self.image_batch_size > 10:
            raise ValueError("image_batch_size must be between 1 and 10")

        # Validate max_images_per_page
        if self.max_images_per_page is not None and (not isinstance(self.max_images_per_page, int) or self.max_images_per_page < 1):
            raise ValueError("max_images_per_page must be a positive integer")

        # Validate include_images
        if not isinstance(self.include_images, bool):
            raise ValueError("include_images must be a boolean")

        # Validate fallback text
        if not isinstance(self.image_fallback_text, str):
            raise ValueError("image_fallback_text must be a string")

        # Validate parallel processing flag
        if not isinstance(self.parallel_image_processing, bool):
            raise ValueError("parallel_image_processing must be a boolean")


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
    pil_image: Optional[Any] = None  # PIL Image object
    description: Optional[str] = None
    processing_status: str = "pending"  # pending, success, failed
    error_message: Optional[str] = None

    def __post_init__(self):
        """Validate ImageContext fields."""
        if self.page_number <= 0:
            raise ValueError("page_number must be positive")
        if self.sequence_number <= 0:
            raise ValueError("sequence_number must be positive")
        if not isinstance(self.bounding_box, tuple) or len(self.bounding_box) != 4:
            raise ValueError("bounding_box must be a tuple of 4 coordinates")
        if self.width <= 0:
            raise ValueError("width must be positive")
        if self.height <= 0:
            raise ValueError("height must be positive")
        if not isinstance(self.format, str):
            raise ValueError("format must be a string")
        if self.processing_status not in ["pending", "success", "failed"]:
            raise ValueError("processing_status must be pending, success, or failed")


@dataclass
class EnhancedPageResult(PageResult):
    """Page extraction result with optional image descriptions."""

    # Image-specific additions
    images_found: int = 0
    images_processed: int = 0
    images_failed: int = 0
    image_contexts: List[ImageContext] = field(default_factory=list)
    enhanced_text: Optional[str] = None  # Text with inline image descriptions

    def __post_init__(self):
        """Validate EnhancedPageResult fields."""
        super().__post_init__()

        if self.images_found < 0:
            raise ValueError("images_found must be non-negative")
        if self.images_processed < 0:
            raise ValueError("images_processed must be non-negative")
        if self.images_failed < 0:
            raise ValueError("images_failed must be non-negative")
        if self.images_processed + self.images_failed > self.images_found:
            raise ValueError("processed + failed cannot exceed found images")
        if len(self.image_contexts) != self.images_found:
            raise ValueError("image_contexts length must match images_found")


@dataclass
class EnhancedExtractionResult(ExtractionResult):
    """Complete PDF extraction result with image processing summary."""

    # Image processing summary
    total_images_found: int = 0
    total_images_processed: int = 0
    total_images_failed: int = 0
    image_processing_time: float = 0.0
    vision_model_used: Optional[str] = None

    # Enhanced content
    enhanced_pages: List[EnhancedPageResult] = field(default_factory=list)
    combined_enhanced_text: Optional[str] = None

    def __post_init__(self):
        """Validate EnhancedExtractionResult fields."""
        super().__post_init__()

        if self.total_images_found < 0:
            raise ValueError("total_images_found must be non-negative")
        if self.total_images_processed < 0:
            raise ValueError("total_images_processed must be non-negative")
        if self.total_images_failed < 0:
            raise ValueError("total_images_failed must be non-negative")
        if self.total_images_processed + self.total_images_failed > self.total_images_found:
            raise ValueError("total processed + failed cannot exceed total found images")
        if self.image_processing_time < 0.0:
            raise ValueError("image_processing_time must be non-negative")
        if not isinstance(self.enhanced_pages, list):
            raise ValueError("enhanced_pages must be a list")


def validate_enhanced_extraction_config(config: EnhancedExtractionConfig) -> bool:
    """Validate enhanced extraction configuration."""
    try:
        return (
            isinstance(config.include_images, bool) and
            isinstance(config.image_fallback_text, str) and
            (config.max_images_per_page is None or (isinstance(config.max_images_per_page, int) and config.max_images_per_page > 0)) and
            isinstance(config.image_batch_size, int) and
            1 <= config.image_batch_size <= 10 and
            isinstance(config.parallel_image_processing, bool)
        )
    except (AttributeError, TypeError):
        return False


def validate_image_context(context: ImageContext) -> bool:
    """Validate image context."""
    try:
        return (
            isinstance(context.page_number, int) and context.page_number >= 1 and
            isinstance(context.sequence_number, int) and context.sequence_number >= 1 and
            isinstance(context.bounding_box, tuple) and len(context.bounding_box) == 4 and
            isinstance(context.width, int) and context.width > 0 and
            isinstance(context.height, int) and context.height > 0 and
            isinstance(context.format, str) and
            context.processing_status in ["pending", "success", "failed"]
        )
    except (AttributeError, TypeError):
        return False


def validate_enhanced_page_result(result: EnhancedPageResult) -> bool:
    """Validate enhanced page result."""
    try:
        return (
            isinstance(result.images_found, int) and result.images_found >= 0 and
            isinstance(result.images_processed, int) and result.images_processed >= 0 and
            isinstance(result.images_failed, int) and result.images_failed >= 0 and
            result.images_processed + result.images_failed <= result.images_found and
            isinstance(result.image_contexts, list) and
            len(result.image_contexts) == result.images_found
        )
    except (AttributeError, TypeError):
        return False


def validate_enhanced_extraction_result(result: EnhancedExtractionResult) -> bool:
    """Validate enhanced extraction result."""
    try:
        return (
            isinstance(result.total_images_found, int) and result.total_images_found >= 0 and
            isinstance(result.total_images_processed, int) and result.total_images_processed >= 0 and
            isinstance(result.total_images_failed, int) and result.total_images_failed >= 0 and
            result.total_images_processed + result.total_images_failed <= result.total_images_found and
            isinstance(result.image_processing_time, float) and result.image_processing_time >= 0.0 and
            isinstance(result.enhanced_pages, list)
        )
    except (AttributeError, TypeError):
        return False
