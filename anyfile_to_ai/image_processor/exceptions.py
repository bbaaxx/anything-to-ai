"""Exception hierarchy for image processing module."""


class ImageProcessingError(Exception):
    """Base exception for all image processing errors."""

    def __init__(self, message: str, image_path: str | None = None):
        self.message = message
        self.image_path = image_path
        super().__init__(message)


class ImageNotFoundError(ImageProcessingError):
    """Raised when image file cannot be found or accessed."""

    def __init__(self, image_path: str):
        message = f"Image file not found: {image_path}"
        super().__init__(message, image_path)


class UnsupportedFormatError(ImageProcessingError):
    """Raised when image format is not supported."""

    def __init__(self, image_path: str, format_detected: str | None = None):
        message = f"Unsupported image format '{format_detected}': {image_path}" if format_detected else f"Unsupported image format: {image_path}"
        super().__init__(message, image_path)


class CorruptedImageError(ImageProcessingError):
    """Raised when image file is corrupted or unreadable."""

    def __init__(self, image_path: str, details: str | None = None):
        message = f"Corrupted or unreadable image: {image_path}"
        if details:
            message += f" ({details})"
        super().__init__(message, image_path)


class ProcessingError(ImageProcessingError):
    """Raised when VLM processing fails."""

    def __init__(self, image_path: str, details: str | None = None):
        message = f"VLM processing failed: {image_path}"
        if details:
            message += f" ({details})"
        super().__init__(message, image_path)


class ImageTooLargeError(ImageProcessingError):
    """Raised when image is too large for processing."""

    def __init__(self, image_path: str, size_mb: float, max_size_mb: float = 50):
        message = f"Image too large: {size_mb:.1f}MB > {max_size_mb}MB limit: {image_path}"
        super().__init__(message, image_path)


class ProcessingTimeoutError(ImageProcessingError):
    """Raised when processing exceeds timeout limit."""

    def __init__(self, image_path: str, timeout_seconds: int):
        message = f"Processing timeout after {timeout_seconds}s: {image_path}"
        super().__init__(message, image_path)


class InsufficientMemoryError(ImageProcessingError):
    """Raised when system memory is exhausted during processing."""

    def __init__(self, image_path: str | None = None):
        message = f"Insufficient memory for processing: {image_path}" if image_path else "Insufficient memory for batch processing"
        super().__init__(message, image_path)


class ModelLoadError(ImageProcessingError):
    """Raised when MLX-VLM model fails to load."""

    def __init__(self, model_name: str, details: str | None = None):
        message = f"Failed to load model '{model_name}'"
        if details:
            message += f": {details}"
        super().__init__(message)


class ProcessingInterruptedError(ImageProcessingError):
    """Raised when processing is interrupted by user or system."""

    def __init__(self, images_processed: int, total_images: int):
        message = f"Processing interrupted: {images_processed}/{total_images} completed"
        super().__init__(message)


class ValidationError(ImageProcessingError):
    """Raised when input validation fails."""

    def __init__(self, message: str, parameter_name: str | None = None):
        if parameter_name:
            message = f"Validation error for '{parameter_name}': {message}"
        super().__init__(message)


# VLM-specific exceptions
class VLMConfigurationError(ImageProcessingError):
    """Exception raised for VLM configuration issues."""

    def __init__(self, message: str, config_field: str | None = None, suggested_fix: str | None = None):
        super().__init__(message)
        self.config_field = config_field
        self.suggested_fix = suggested_fix


class VLMModelLoadError(ImageProcessingError):
    """Exception raised when VLM model loading fails."""

    def __init__(self, message: str, model_name: str | None = None, error_reason: str | None = None):
        super().__init__(message)
        self.model_name = model_name
        self.error_reason = error_reason


class VLMProcessingError(ImageProcessingError):
    """Exception raised during VLM processing operations."""

    def __init__(self, message: str, image_path: str | None = None, model_name: str | None = None, error_details: str | None = None):
        super().__init__(message, image_path)
        self.model_name = model_name
        self.error_details = error_details


class VLMTimeoutError(VLMProcessingError):
    """Exception raised when VLM processing exceeds timeout."""

    def __init__(self, message: str, timeout_seconds: int | None = None, actual_time: float | None = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.actual_time = actual_time


class VLMModelNotFoundError(VLMConfigurationError):
    """Exception raised when specified VLM model is not available."""

    def __init__(self, message: str, model_name: str | None = None, available_models: list | None = None, **kwargs):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        self.available_models = available_models or []
