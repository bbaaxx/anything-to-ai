"""
Configuration factory for audio transcription.
"""

from collections.abc import Callable
from anyfile_to_ai.audio_processor.models import TranscriptionConfig
from anyfile_to_ai.audio_processor.exceptions import ValidationError


# Valid model choices
VALID_MODELS = [
    "tiny",
    "small",
    "distil-small.en",
    "base",
    "medium",
    "distil-medium.en",
    "large",
    "large-v2",
    "distil-large-v2",
    "large-v3",
    "distil-large-v3",
]

# Valid quantization choices
VALID_QUANTIZATIONS = ["none", "4bit", "8bit"]

# Valid output formats
VALID_OUTPUT_FORMATS = ["plain", "json"]


def create_config(
    model: str = "medium",
    quantization: str = "none",  # Changed from "4bit" due to MLX compatibility
    batch_size: int = 12,
    language: str | None = None,
    output_format: str = "plain",
    timeout_seconds: int = 600,
    progress_callback: Callable[[int, int], None] | None = None,
    verbose: bool = False,
    max_duration_seconds: int = 7200,
) -> TranscriptionConfig:
    """
    Create transcription configuration with parameter validation.

    Args:
        model: Whisper model selection (default: "medium")
        quantization: Quantization level (default: "none")
        batch_size: Whisper decoder batch size (default: 12)
        language: ISO 639-1 language code, None for auto-detect (default: None)
        output_format: Output format "plain" or "json" (default: "plain")
        timeout_seconds: Processing timeout per file (default: 600)
        progress_callback: Progress callback function (default: None)
        verbose: Enable verbose output (default: False)
        max_duration_seconds: Maximum audio duration (default: 7200)

    Returns:
        TranscriptionConfig: Validated configuration object

    Raises:
        ValidationError: If any parameter value is invalid
    """
    # Validate model
    if model not in VALID_MODELS:
        raise ValidationError(
            f"Invalid model '{model}'. Valid models: {', '.join(VALID_MODELS)}",
            parameter_name="model",
        )

    # Validate quantization
    if quantization not in VALID_QUANTIZATIONS:
        raise ValidationError(
            f"Invalid quantization '{quantization}'. Valid values: {', '.join(VALID_QUANTIZATIONS)}",
            parameter_name="quantization",
        )

    # Validate batch_size
    if not (1 <= batch_size <= 128):
        raise ValidationError(
            f"batch_size must be between 1 and 128, got {batch_size}",
            parameter_name="batch_size",
        )

    # Validate language (if provided)
    if language is not None:
        if not isinstance(language, str) or len(language) != 2:
            raise ValidationError(
                f"language must be a 2-letter ISO 639-1 code, got '{language}'",
                parameter_name="language",
            )

    # Validate output_format
    if output_format not in VALID_OUTPUT_FORMATS:
        raise ValidationError(
            f"Invalid output_format '{output_format}'. Valid formats: {', '.join(VALID_OUTPUT_FORMATS)}",
            parameter_name="output_format",
        )

    # Validate timeout_seconds
    if timeout_seconds <= 0:
        raise ValidationError(
            f"timeout_seconds must be > 0, got {timeout_seconds}",
            parameter_name="timeout_seconds",
        )

    # Validate max_duration_seconds
    if not (0 < max_duration_seconds <= 7200):
        raise ValidationError(
            f"max_duration_seconds must be between 0 and 7200 (2 hours), got {max_duration_seconds}",
            parameter_name="max_duration_seconds",
        )

    # Create and return config
    return TranscriptionConfig(
        model=model,
        quantization=quantization,
        batch_size=batch_size,
        language=language,
        output_format=output_format,
        timeout_seconds=timeout_seconds,
        progress_callback=progress_callback,
        verbose=verbose,
        max_duration_seconds=max_duration_seconds,
    )
