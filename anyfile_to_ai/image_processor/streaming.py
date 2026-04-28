"""Batch processing and streaming functionality."""

import time
from collections.abc import Generator
from .models import DescriptionResult, ProcessingResult, ProcessingConfig
from .progress import ProgressTracker
from .exceptions import ValidationError
from .vlm_processor import get_global_vlm_processor
from anyfile_to_ai.progress_tracker import CancellationToken, OperationCancelledError


class StreamingProcessor:
    """Handles batch processing with streaming progress updates."""

    def __init__(self, processor):
        self.processor = processor
        self.vlm_processor = get_global_vlm_processor()

    def process_batch(self, file_paths: list[str], config: ProcessingConfig, include_metadata: bool = False, cancel_token: CancellationToken | None = None) -> ProcessingResult:
        """Process multiple images in batch.

        Args:
            file_paths: List of image file paths to process
            config: Processing configuration
            include_metadata: Whether to include metadata in results
            cancel_token: Optional cancellation token for graceful termination

        Returns:
            ProcessingResult with all results

        Raises:
            ValidationError: If file_paths is empty
            OperationCancelledError: If cancellation is requested during processing
        """
        if not file_paths:
            msg = "Cannot process empty list of images"
            raise ValidationError(msg)

        start_time = time.time()
        results = []
        successful_count = 0
        failed_count = 0

        # Create progress tracker
        progress = ProgressTracker(len(file_paths), config.progress_callback)

        for _i, file_path in enumerate(file_paths):
            # Check for cancellation at iteration boundary
            if cancel_token and cancel_token.is_cancelled:
                # Clean up VLM resources before raising
                self._cleanup_vlm()
                msg = f"Image batch processing cancelled at image {_i + 1}"
                raise OperationCancelledError(msg)

            try:
                # Validate and process each image
                image_doc = self.processor.validate_image(file_path)
                result = self.processor.process_single_image(image_doc, config, include_metadata)
                results.append(result)

                if result.success:
                    successful_count += 1
                else:
                    failed_count += 1

            except OperationCancelledError:
                # Re-raise cancellation without wrapping
                self._cleanup_vlm()
                raise
            except Exception as e:
                # Create failed result
                failed_result = DescriptionResult(image_path=file_path, description=f"Error: {e!s}", confidence_score=None, processing_time=0.0, model_used="", prompt_used="", success=False)
                results.append(failed_result)
                failed_count += 1

            # Update progress
            progress.update()

        total_time = time.time() - start_time

        # Clean up VLM resources after batch processing
        self._cleanup_vlm()

        return ProcessingResult(
            success=successful_count > 0,
            results=results,
            total_images=len(file_paths),
            successful_count=successful_count,
            failed_count=failed_count,
            total_processing_time=total_time,
            error_message=None if successful_count > 0 else "All images failed to process",
        )

    def process_streaming(self, file_paths: list[str], config: ProcessingConfig, include_metadata: bool = False, cancel_token: CancellationToken | None = None) -> Generator[DescriptionResult, None, None]:
        """Process images with streaming progress updates.

        Args:
            file_paths: List of image file paths to process
            config: Processing configuration
            include_metadata: Whether to include metadata in results
            cancel_token: Optional cancellation token for graceful termination

        Yields:
            DescriptionResult for each processed image

        Raises:
            ValidationError: If file_paths is empty
            OperationCancelledError: If cancellation is requested during processing
        """
        if not file_paths:
            msg = "Cannot process empty list of images"
            raise ValidationError(msg)

        # Create progress tracker
        progress = ProgressTracker(len(file_paths), config.progress_callback)

        try:
            for idx, file_path in enumerate(file_paths):
                # Check for cancellation at iteration boundary
                if cancel_token and cancel_token.is_cancelled:
                    msg = f"Image streaming processing cancelled at image {idx + 1}"
                    raise OperationCancelledError(msg)

                try:
                    # Validate and process each image
                    image_doc = self.processor.validate_image(file_path)
                    result = self.processor.process_single_image(image_doc, config, include_metadata)
                    yield result

                except OperationCancelledError:
                    # Re-raise cancellation without wrapping
                    raise
                except Exception:
                    # Yield failed result
                    failed_result = DescriptionResult(image_path=file_path, description="", confidence_score=None, processing_time=0.0, model_used="", prompt_used="", success=False)
                    yield failed_result

                # Update progress
                progress.update()

        finally:
            # Clean up VLM resources after streaming completes
            self._cleanup_vlm()

    def _cleanup_vlm(self) -> None:
        """Clean up VLM resources safely."""
        try:
            self.vlm_processor.cleanup()
        except Exception:
            # Don't let cleanup errors affect the result
            pass

    def calculate_batch_size(self, file_paths: list[str], config: ProcessingConfig) -> int:
        """Calculate optimal batch size based on image sizes."""
        # Simple implementation - could be enhanced with actual file size analysis
        base_batch_size = config.batch_size

        # For now, return the configured batch size
        # In a real implementation, this would analyze image file sizes
        # and adjust batch size accordingly
        return min(base_batch_size, len(file_paths))
