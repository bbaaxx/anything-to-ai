"""API Contract: Enhanced PDF Extraction with Image Description

This contract defines the interface for PDF extraction with optional image processing.
Contract tests must validate these interfaces before implementation.
"""

from abc import ABC, abstractmethod
from typing import Iterator, Optional, List
from dataclasses import dataclass
from pdf_extractor.models import ExtractionConfig, ExtractionResult, PageResult


@dataclass
class EnhancedExtractionConfig(ExtractionConfig):
    """Configuration for PDF extraction with optional image processing."""
    include_images: bool = False
    image_processing_config: Optional[object] = None
    image_fallback_text: str = "[Image: processing failed]"
    max_images_per_page: Optional[int] = None
    image_batch_size: int = 4
    parallel_image_processing: bool = True


@dataclass
class ImageContext:
    """Context information for an image extracted from a PDF page."""
    page_number: int
    sequence_number: int
    bounding_box: tuple  # (x0, y0, x1, y1)
    width: int
    height: int
    format: str
    pil_image: Optional[object] = None
    description: Optional[str] = None
    processing_status: str = "pending"
    error_message: Optional[str] = None


@dataclass
class EnhancedPageResult(PageResult):
    """Page extraction result with optional image descriptions."""
    images_found: int = 0
    images_processed: int = 0
    images_failed: int = 0
    image_contexts: List[ImageContext] = None
    enhanced_text: Optional[str] = None

    def __post_init__(self):
        if self.image_contexts is None:
            self.image_contexts = []


@dataclass
class EnhancedExtractionResult(ExtractionResult):
    """Complete PDF extraction result with image processing summary."""
    total_images_found: int = 0
    total_images_processed: int = 0
    total_images_failed: int = 0
    image_processing_time: float = 0.0
    vision_model_used: Optional[str] = None
    enhanced_pages: List[EnhancedPageResult] = None
    combined_enhanced_text: Optional[str] = None

    def __post_init__(self):
        if self.enhanced_pages is None:
            self.enhanced_pages = []


class PDFImageProcessorInterface(ABC):
    """Interface for PDF extraction with image processing capabilities."""

    @abstractmethod
    def extract_with_images(
        self,
        file_path: str,
        config: EnhancedExtractionConfig
    ) -> EnhancedExtractionResult:
        """Extract PDF text with optional image descriptions.

        Args:
            file_path: Path to PDF file
            config: Enhanced extraction configuration

        Returns:
            Enhanced extraction result with image processing data

        Raises:
            PDFNotFoundError: When PDF file not found
            PDFCorruptedError: When PDF cannot be read
            VLMConfigurationError: When vision model not configured
        """
        pass

    @abstractmethod
    def extract_with_images_streaming(
        self,
        file_path: str,
        config: EnhancedExtractionConfig
    ) -> Iterator[EnhancedPageResult]:
        """Stream PDF extraction with image processing.

        Args:
            file_path: Path to PDF file
            config: Enhanced extraction configuration

        Yields:
            Enhanced page results as they are processed

        Raises:
            PDFNotFoundError: When PDF file not found
            PDFCorruptedError: When PDF cannot be read
            VLMConfigurationError: When vision model not configured
        """
        pass

    @abstractmethod
    def validate_config(self, config: EnhancedExtractionConfig) -> None:
        """Validate enhanced extraction configuration.

        Args:
            config: Configuration to validate

        Raises:
            ValidationError: When configuration is invalid
            VLMConfigurationError: When image processing config invalid
        """
        pass


class ImageExtractionInterface(ABC):
    """Interface for extracting images from PDF pages."""

    @abstractmethod
    def extract_page_images(
        self,
        page_number: int,
        file_path: str
    ) -> List[ImageContext]:
        """Extract images from a specific PDF page.

        Args:
            page_number: Page number (1-indexed)
            file_path: Path to PDF file

        Returns:
            List of image contexts with position and metadata

        Raises:
            PDFNotFoundError: When PDF file not found
            PDFCorruptedError: When PDF page cannot be read
        """
        pass

    @abstractmethod
    def crop_image_from_page(
        self,
        page_number: int,
        file_path: str,
        bounding_box: tuple
    ) -> object:
        """Crop image from PDF page using bounding box.

        Args:
            page_number: Page number (1-indexed)
            file_path: Path to PDF file
            bounding_box: (x0, y0, x1, y1) coordinates

        Returns:
            PIL Image object

        Raises:
            PDFNotFoundError: When PDF file not found
            ImageExtractionError: When image cannot be cropped
        """
        pass


class VLMCircuitBreakerInterface(ABC):
    """Interface for VLM service circuit breaker."""

    @abstractmethod
    def can_process(self) -> bool:
        """Check if VLM processing is allowed."""
        pass

    @abstractmethod
    def record_success(self) -> None:
        """Record successful VLM operation."""
        pass

    @abstractmethod
    def record_failure(self) -> None:
        """Record VLM operation failure."""
        pass

    @abstractmethod
    def get_state(self) -> str:
        """Get current circuit breaker state."""
        pass


# Contract validation functions
def validate_enhanced_extraction_config(config: EnhancedExtractionConfig) -> bool:
    """Validate enhanced extraction configuration contract."""
    return (
        isinstance(config.include_images, bool) and
        isinstance(config.image_fallback_text, str) and
        (config.max_images_per_page is None or isinstance(config.max_images_per_page, int)) and
        isinstance(config.image_batch_size, int) and
        config.image_batch_size >= 1 and
        config.image_batch_size <= 10 and
        isinstance(config.parallel_image_processing, bool)
    )


def validate_image_context(context: ImageContext) -> bool:
    """Validate image context contract."""
    return (
        isinstance(context.page_number, int) and
        context.page_number >= 1 and
        isinstance(context.sequence_number, int) and
        context.sequence_number >= 1 and
        isinstance(context.bounding_box, tuple) and
        len(context.bounding_box) == 4 and
        isinstance(context.width, int) and
        context.width > 0 and
        isinstance(context.height, int) and
        context.height > 0 and
        isinstance(context.format, str) and
        context.processing_status in ["pending", "success", "failed"]
    )


def validate_enhanced_page_result(result: EnhancedPageResult) -> bool:
    """Validate enhanced page result contract."""
    return (
        isinstance(result.images_found, int) and
        result.images_found >= 0 and
        isinstance(result.images_processed, int) and
        result.images_processed >= 0 and
        isinstance(result.images_failed, int) and
        result.images_failed >= 0 and
        result.images_processed + result.images_failed <= result.images_found and
        isinstance(result.image_contexts, list) and
        len(result.image_contexts) == result.images_found
    )


def validate_enhanced_extraction_result(result: EnhancedExtractionResult) -> bool:
    """Validate enhanced extraction result contract."""
    return (
        isinstance(result.total_images_found, int) and
        result.total_images_found >= 0 and
        isinstance(result.total_images_processed, int) and
        result.total_images_processed >= 0 and
        isinstance(result.total_images_failed, int) and
        result.total_images_failed >= 0 and
        result.total_images_processed + result.total_images_failed <= result.total_images_found and
        isinstance(result.image_processing_time, float) and
        result.image_processing_time >= 0.0 and
        isinstance(result.enhanced_pages, list)
    )
