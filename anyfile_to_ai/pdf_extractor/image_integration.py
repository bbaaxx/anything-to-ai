"""Main PDF image processing orchestration."""

import os
import time
from collections.abc import Iterator

import pdfplumber

from .enhanced_models import EnhancedExtractionConfig, ImageContext, EnhancedPageResult, EnhancedExtractionResult
from .exceptions import PDFNotFoundError, PDFCorruptedError, VLMConfigurationError, ConfigurationValidationError
from .models import PageResult
from .circuit_breaker import VLMCircuitBreaker
from .image_extractor import ImageExtractor
from .image_adapter import ImageProcessorAdapter


class PDFImageProcessor:
    """Orchestrates PDF text extraction with optional image description processing."""

    def __init__(self, image_processor=None):
        """Initialize with optional image processor."""
        if image_processor is None:
            try:
                self.image_processor = ImageProcessorAdapter()
            except Exception:
                self.image_processor = None
        else:
            self.image_processor = image_processor
        self.circuit_breaker = VLMCircuitBreaker()
        self.image_extractor = ImageExtractor()

    def validate_config(self, config: EnhancedExtractionConfig) -> None:
        """Validate enhanced extraction configuration."""
        if config.include_images:
            vision_model = os.getenv("VISION_MODEL")
            if not vision_model:
                raise VLMConfigurationError("VISION_MODEL environment variable required for image processing", config_key="VISION_MODEL")

        # Validate batch size
        if not (1 <= config.image_batch_size <= 10):
            raise ConfigurationValidationError("image_batch_size", config.image_batch_size, "must be between 1 and 10")

        # Validate max images per page
        if config.max_images_per_page is not None and config.max_images_per_page < 1:
            raise ConfigurationValidationError("max_images_per_page", config.max_images_per_page, "must be positive")

    def extract_with_images(self, file_path: str, config: EnhancedExtractionConfig) -> EnhancedExtractionResult:
        """Extract PDF text with optional image descriptions."""
        self.validate_config(config)

        if not os.path.exists(file_path):
            raise PDFNotFoundError(file_path)

        start_time = time.time()
        image_processing_start = time.time()

        try:
            with pdfplumber.open(file_path) as pdf:
                enhanced_pages = []
                total_images_found = 0
                total_images_processed = 0
                total_images_failed = 0

                for page_num, page in enumerate(pdf.pages, 1):
                    enhanced_page = self._process_page(page, page_num, file_path, config)
                    enhanced_pages.append(enhanced_page)

                    total_images_found += enhanced_page.images_found
                    total_images_processed += enhanced_page.images_processed
                    total_images_failed += enhanced_page.images_failed

                processing_time = time.time() - start_time
                image_processing_time = time.time() - image_processing_start

                # Convert enhanced pages to regular pages for base class compatibility
                regular_pages = [PageResult(page_number=ep.page_number, text=ep.text, char_count=ep.char_count, extraction_time=ep.extraction_time) for ep in enhanced_pages]

                return EnhancedExtractionResult(
                    success=True,
                    pages=regular_pages,
                    total_pages=len(enhanced_pages),
                    total_chars=sum(p.char_count for p in enhanced_pages),
                    processing_time=processing_time,
                    total_images_found=total_images_found,
                    total_images_processed=total_images_processed,
                    total_images_failed=total_images_failed,
                    image_processing_time=image_processing_time,
                    vision_model_used=os.getenv("VISION_MODEL") if config.include_images else None,
                    enhanced_pages=enhanced_pages,
                    combined_enhanced_text="\n\n".join(p.enhanced_text or p.text for p in enhanced_pages),
                )

        except Exception as e:
            raise PDFCorruptedError(file_path, str(e))

    def extract_with_images_streaming(self, file_path: str, config: EnhancedExtractionConfig) -> Iterator[EnhancedPageResult]:
        """Stream PDF extraction with image processing."""
        self.validate_config(config)

        if not os.path.exists(file_path):
            raise PDFNotFoundError(file_path)

        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    enhanced_page = self._process_page(page, page_num, file_path, config)
                    yield enhanced_page

        except Exception as e:
            raise PDFCorruptedError(file_path, str(e))

    def _process_page(self, page, page_num: int, file_path: str, config: EnhancedExtractionConfig) -> EnhancedPageResult:
        """Process a single PDF page with optional image processing."""
        text = page.extract_text() or ""
        char_count = len(text)

        enhanced_page = EnhancedPageResult(page_number=page_num, text=text, char_count=char_count, extraction_time=0.1)

        if config.include_images:
            # Extract images
            image_contexts = self.image_extractor.extract_page_images(page_num, file_path)

            if config.max_images_per_page:
                image_contexts = image_contexts[: config.max_images_per_page]

            enhanced_page.images_found = len(image_contexts)
            enhanced_page.image_contexts = image_contexts

            # Process images if circuit breaker allows
            if self.circuit_breaker.can_process() and self.image_processor and image_contexts:
                processed_count, failed_count = self._process_images(image_contexts, page_num, file_path, config)
                enhanced_page.images_processed = processed_count
                enhanced_page.images_failed = failed_count

            # Generate enhanced text
            enhanced_page.enhanced_text = self._insert_image_descriptions(text, image_contexts)

        return enhanced_page

    def _process_images(self, image_contexts: list[ImageContext], page_num: int, file_path: str, config: EnhancedExtractionConfig):
        """Process images with VLM."""
        processed_count = 0
        failed_count = 0

        for context in image_contexts:
            try:
                # Try to crop the image from PDF
                pil_image = self.image_extractor.crop_image_from_page(page_num, file_path, context.bounding_box)

                # Verify the image is valid
                if pil_image is None:
                    raise Exception("Image cropping returned None")

                context.pil_image = pil_image

                # Process with VLM if available
                if hasattr(self.image_processor, "process_image"):
                    result = self.image_processor.process_image(pil_image, config.image_processing_config)
                    context.description = getattr(result, "description", str(result))
                    context.processing_status = "success"
                    processed_count += 1
                    self.circuit_breaker.record_success()

            except Exception as e:
                # Handle various image processing errors gracefully
                context.processing_status = "failed"
                error_msg = str(e)

                # Provide specific error context for common PDF image issues
                if "invalid float value" in error_msg or "Cannot set gray" in error_msg:
                    context.error_message = "PDF image metadata is corrupted or invalid"
                elif "crop" in error_msg.lower():
                    context.error_message = f"Image cropping failed: {error_msg}"
                else:
                    context.error_message = error_msg

                context.description = config.image_fallback_text
                failed_count += 1
                self.circuit_breaker.record_failure()

        return processed_count, failed_count

    def _insert_image_descriptions(self, text: str, image_contexts: list[ImageContext]) -> str:
        """Insert image descriptions into text."""
        if not image_contexts:
            return text

        enhanced_text = text
        for i, context in enumerate(image_contexts, 1):
            if context.description and context.description != "[Image: processing failed]":
                image_marker = f"[Image {i}: {context.description}]"
            else:
                image_marker = f"[Image {i}: processing failed]"

            enhanced_text += f"\n\n{image_marker}"

        return enhanced_text
