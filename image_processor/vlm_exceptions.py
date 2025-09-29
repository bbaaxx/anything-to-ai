"""VLM-specific exception types for image processing."""

from .exceptions import ImageProcessingError


class VLMConfigurationError(ImageProcessingError):
    """Exception raised for VLM configuration issues."""

    def __init__(self, message: str, config_field: str = None, suggested_fix: str = None):
        super().__init__(message)
        self.config_field = config_field
        self.suggested_fix = suggested_fix


class VLMModelLoadError(ImageProcessingError):
    """Exception raised when VLM model loading fails."""

    def __init__(self, message: str, model_name: str = None, error_reason: str = None):
        super().__init__(message)
        self.model_name = model_name
        self.error_reason = error_reason


class VLMProcessingError(ImageProcessingError):
    """Exception raised during VLM processing operations."""

    def __init__(self, message: str, image_path: str = None, model_name: str = None, error_details: str = None):
        super().__init__(message)
        self.image_path = image_path
        self.model_name = model_name
        self.error_details = error_details


class VLMTimeoutError(VLMProcessingError):
    """Exception raised when VLM processing exceeds timeout."""

    def __init__(self, message: str, timeout_seconds: int = None, actual_time: float = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_seconds = timeout_seconds
        self.actual_time = actual_time


class VLMModelNotFoundError(VLMConfigurationError):
    """Exception raised when specified VLM model is not available."""

    def __init__(self, message: str, model_name: str = None, available_models: list = None, **kwargs):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        self.available_models = available_models or []
