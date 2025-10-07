"""Batch processing and streaming functionality."""

import time
from collections.abc import Generator
from .models import DescriptionResult, ProcessingResult, ProcessingConfig
from .progress import ProgressTracker
from .exceptions import ValidationError
from .vlm_processor import get_global_vlm_processor


class StreamingProcessor:
    """Handles batch processing with streaming progress updates."""

    def __init__(self, processor):
        self.processor = processor
        self.vlm_processor = get_global_vlm_processor()

    def process_batch(self, file_paths: list[str], config: ProcessingConfig) -> ProcessingResult:
        """Process multiple images in batch."""
        if not file_paths:
            raise ValidationError("Cannot process empty list of images")

        start_time = time.time()
        results = []
        successful_count = 0
        failed_count = 0

        # Create progress tracker
        progress = ProgressTracker(len(file_paths), config.progress_callback)

        for i, file_path in enumerate(file_paths):
            try:
                # Validate and process each image
                image_doc = self.processor.validate_image(file_path)
                result = self.processor.process_single_image(image_doc, config)
                results.append(result)

                if result.success:
                    successful_count += 1
                else:
                    failed_count += 1

            except Exception as e:
                # Create failed result
                failed_result = DescriptionResult(image_path=file_path, description=f"Error: {e!s}", confidence_score=None, processing_time=0.0, model_used="", prompt_used="", success=False)
                results.append(failed_result)
                failed_count += 1

            # Update progress
            progress.update()

        total_time = time.time() - start_time

        # Clean up VLM resources after batch processing
        try:
            self.vlm_processor.cleanup()
        except Exception:
            # Don't let cleanup errors affect the result
            pass

        return ProcessingResult(
            success=successful_count > 0,
            results=results,
            total_images=len(file_paths),
            successful_count=successful_count,
            failed_count=failed_count,
            total_processing_time=total_time,
            error_message=None if successful_count > 0 else "All images failed to process",
        )

    def process_streaming(self, file_paths: list[str], config: ProcessingConfig) -> Generator[DescriptionResult, None, None]:
        """Process images with streaming progress updates."""
        if not file_paths:
            raise ValidationError("Cannot process empty list of images")

        # Create progress tracker
        progress = ProgressTracker(len(file_paths), config.progress_callback)

        try:
            for file_path in file_paths:
                try:
                    # Validate and process each image
                    image_doc = self.processor.validate_image(file_path)
                    result = self.processor.process_single_image(image_doc, config)
                    yield result

                except Exception:
                    # Yield failed result
                    failed_result = DescriptionResult(image_path=file_path, description="", confidence_score=None, processing_time=0.0, model_used="", prompt_used="", success=False)
                    yield failed_result

                # Update progress
                progress.update()

        finally:
            # Clean up VLM resources after streaming completes
            try:
                self.vlm_processor.cleanup()
            except Exception:
                # Don't let cleanup errors affect the streaming
                pass

    def calculate_batch_size(self, file_paths: list[str], config: ProcessingConfig) -> int:
        """Calculate optimal batch size based on image sizes."""
        # Simple implementation - could be enhanced with actual file size analysis
        base_batch_size = config.batch_size

        # For now, return the configured batch size
        # In a real implementation, this would analyze image file sizes
        # and adjust batch size accordingly
        return min(base_batch_size, len(file_paths))
