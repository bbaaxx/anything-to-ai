"""
Batch processing with progress updates.
"""

import time
from collections import defaultdict
from anyfile_to_ai.audio_processor.models import (
    TranscriptionResult,
    TranscriptionConfig,
    ProcessingResult,
)
from anyfile_to_ai.audio_processor.exceptions import ValidationError
from anyfile_to_ai.audio_processor.processor import process_audio
from anyfile_to_ai.audio_processor.progress import ProgressTracker


def process_audio_batch(file_paths: list[str], config: TranscriptionConfig | None = None, include_metadata: bool = False) -> ProcessingResult:
    """
    Process multiple audio files in batch.

    Args:
        file_paths: List of audio file paths
        config: Processing configuration (uses defaults if not provided)
        include_metadata: Include source file and processing metadata in output

    Returns:
        ProcessingResult: Aggregate results with statistics

    Raises:
        ValidationError: If file_paths is empty
    """
    # Validate input
    if not file_paths:
        msg = "file_paths list cannot be empty"
        raise ValidationError(msg, parameter_name="file_paths")

    # Use default config if not provided
    if config is None:
        from anyfile_to_ai.audio_processor.config import create_config

        config = create_config()

    # Initialize results
    results: list[TranscriptionResult] = []
    error_counts: defaultdict = defaultdict(int)
    start_time = time.time()

    # Create progress tracker
    progress = ProgressTracker(len(file_paths), config.progress_callback)

    # Process each file
    for file_path in file_paths:
        try:
            # Process audio file
            result = process_audio(file_path, config, include_metadata)
            results.append(result)

            # Track errors
            if not result.success and result.error_message:
                error_type = _categorize_error(result.error_message)
                error_counts[error_type] += 1

        except Exception as e:
            # Create failed result for unhandled exceptions
            failed_result = TranscriptionResult(
                audio_path=file_path,
                text="",
                confidence_score=None,
                processing_time=0.0,
                model_used=config.model,
                quantization=config.quantization,
                detected_language=None,
                success=False,
                error_message=str(e),
            )
            results.append(failed_result)

            error_type = _categorize_error(str(e))
            error_counts[error_type] += 1

        # Update progress
        progress.increment()

    # Calculate statistics
    total_processing_time = time.time() - start_time
    successful_count = sum(1 for r in results if r.success)
    failed_count = len(results) - successful_count
    average_processing_time = sum(r.processing_time for r in results) / len(results) if results else 0.0

    # Create error summary
    error_summary = dict(error_counts) if error_counts else None

    return ProcessingResult(
        success=successful_count > 0,
        results=results,
        total_files=len(file_paths),
        successful_count=successful_count,
        failed_count=failed_count,
        total_processing_time=total_processing_time,
        average_processing_time=average_processing_time,
        error_summary=error_summary,
    )


def _categorize_error(error_message: str) -> str:
    """
    Categorize error message into error type.

    Args:
        error_message: Error message string

    Returns:
        str: Error category
    """
    error_lower = error_message.lower()

    if "not found" in error_lower or "no such file" in error_lower:
        return "file_not_found"
    if "unsupported format" in error_lower:
        return "unsupported_format"
    if "no speech" in error_lower:
        return "no_speech_detected"
    if "duration exceeded" in error_lower or "2-hour" in error_lower:
        return "duration_exceeded"
    if "corrupted" in error_lower:
        return "corrupted_audio"
    if "model" in error_lower and "load" in error_lower:
        return "model_load_error"
    if "timeout" in error_lower:
        return "processing_timeout"
    return "other_error"
