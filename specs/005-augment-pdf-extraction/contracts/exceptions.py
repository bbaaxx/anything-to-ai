"""Exception Contract: Enhanced PDF Extraction Error Handling

This contract defines the exception hierarchy for enhanced PDF extraction.
Contract tests must validate these exception behaviors before implementation.
"""

from abc import ABC
from typing import Optional, Any, Dict


class ImageExtractionError(Exception):
    """Base exception for image extraction errors."""

    def __init__(self, message: str, file_path: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.file_path = file_path
        self.details = details or {}

    def __str__(self) -> str:
        if self.file_path:
            return f"{super().__str__()} (file: {self.file_path})"
        return super().__str__()


class ImageNotFoundInPDFError(ImageExtractionError):
    """Raised when expected image cannot be found in PDF."""

    def __init__(self, page_number: int, image_index: int, file_path: Optional[str] = None):
        message = f"Image {image_index} not found on page {page_number}"
        super().__init__(message, file_path)
        self.page_number = page_number
        self.image_index = image_index


class ImageCroppingError(ImageExtractionError):
    """Raised when image cannot be cropped from PDF page."""

    def __init__(self, page_number: int, bounding_box: tuple, file_path: Optional[str] = None, reason: Optional[str] = None):
        message = f"Cannot crop image from page {page_number} at {bounding_box}"
        if reason:
            message += f": {reason}"
        super().__init__(message, file_path)
        self.page_number = page_number
        self.bounding_box = bounding_box
        self.reason = reason


class VLMConfigurationError(Exception):
    """Raised when VLM configuration is invalid or missing."""

    def __init__(self, message: str, config_key: Optional[str] = None, expected_value: Optional[str] = None):
        super().__init__(message)
        self.config_key = config_key
        self.expected_value = expected_value

    def __str__(self) -> str:
        if self.config_key:
            msg = f"VLM Configuration Error - {self.config_key}: {super().__str__()}"
            if self.expected_value:
                msg += f" (expected: {self.expected_value})"
            return msg
        return f"VLM Configuration Error: {super().__str__()}"


class VLMServiceError(Exception):
    """Base exception for VLM service errors."""

    def __init__(self, message: str, model_name: Optional[str] = None, retry_count: int = 0):
        super().__init__(message)
        self.model_name = model_name
        self.retry_count = retry_count

    def __str__(self) -> str:
        msg = super().__str__()
        if self.model_name:
            msg += f" (model: {self.model_name})"
        if self.retry_count > 0:
            msg += f" (retries: {self.retry_count})"
        return msg


class VLMTimeoutError(VLMServiceError):
    """Raised when VLM processing times out."""

    def __init__(self, timeout_seconds: float, model_name: Optional[str] = None):
        message = f"VLM processing timed out after {timeout_seconds} seconds"
        super().__init__(message, model_name)
        self.timeout_seconds = timeout_seconds


class VLMMemoryError(VLMServiceError):
    """Raised when VLM runs out of memory."""

    def __init__(self, required_memory: Optional[str] = None, available_memory: Optional[str] = None, model_name: Optional[str] = None):
        message = "VLM processing failed due to insufficient memory"
        if required_memory and available_memory:
            message += f" (required: {required_memory}, available: {available_memory})"
        super().__init__(message, model_name)
        self.required_memory = required_memory
        self.available_memory = available_memory


class VLMCircuitBreakerError(VLMServiceError):
    """Raised when VLM circuit breaker is open."""

    def __init__(self, failure_count: int, threshold: int, model_name: Optional[str] = None):
        message = f"VLM circuit breaker open: {failure_count} failures (threshold: {threshold})"
        super().__init__(message, model_name)
        self.failure_count = failure_count
        self.threshold = threshold


class EnhancedExtractionError(Exception):
    """Base exception for enhanced extraction process errors."""

    def __init__(self, message: str, file_path: Optional[str] = None, partial_result: Optional[Any] = None):
        super().__init__(message)
        self.file_path = file_path
        self.partial_result = partial_result

    def __str__(self) -> str:
        msg = super().__str__()
        if self.file_path:
            msg += f" (file: {self.file_path})"
        return msg


class PartialExtractionError(EnhancedExtractionError):
    """Raised when extraction partially succeeds but has significant failures."""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        partial_result: Optional[Any] = None,
        failed_pages: Optional[list] = None,
        failed_images: Optional[list] = None
    ):
        super().__init__(message, file_path, partial_result)
        self.failed_pages = failed_pages or []
        self.failed_images = failed_images or []

    def __str__(self) -> str:
        msg = super().__str__()
        if self.failed_pages:
            msg += f" (failed pages: {len(self.failed_pages)})"
        if self.failed_images:
            msg += f" (failed images: {len(self.failed_images)})"
        return msg


class ConfigurationValidationError(Exception):
    """Raised when enhanced extraction configuration is invalid."""

    def __init__(self, field_name: str, field_value: Any, validation_error: str):
        message = f"Invalid configuration for '{field_name}': {validation_error}"
        super().__init__(message)
        self.field_name = field_name
        self.field_value = field_value
        self.validation_error = validation_error

    def __str__(self) -> str:
        return f"Configuration Validation Error - {self.field_name}: {self.validation_error} (value: {self.field_value})"


# Exception hierarchy validation interface
class ExceptionHierarchyInterface(ABC):
    """Interface for validating exception hierarchy contracts."""

    @staticmethod
    def validate_base_exception_structure(exception: Exception) -> bool:
        """Validate that exception follows base structure contract."""
        return (
            hasattr(exception, '__str__') and
            hasattr(exception, 'args') and
            isinstance(exception.args, tuple)
        )

    @staticmethod
    def validate_image_extraction_error(exception: ImageExtractionError) -> bool:
        """Validate ImageExtractionError contract."""
        return (
            isinstance(exception, Exception) and
            hasattr(exception, 'file_path') and
            hasattr(exception, 'details') and
            isinstance(exception.details, dict)
        )

    @staticmethod
    def validate_vlm_configuration_error(exception: VLMConfigurationError) -> bool:
        """Validate VLMConfigurationError contract."""
        return (
            isinstance(exception, Exception) and
            hasattr(exception, 'config_key') and
            hasattr(exception, 'expected_value')
        )

    @staticmethod
    def validate_vlm_service_error(exception: VLMServiceError) -> bool:
        """Validate VLMServiceError contract."""
        return (
            isinstance(exception, Exception) and
            hasattr(exception, 'model_name') and
            hasattr(exception, 'retry_count') and
            isinstance(exception.retry_count, int) and
            exception.retry_count >= 0
        )


# Error recovery strategies
class ErrorRecoveryStrategy:
    """Defines error recovery strategies for different exception types."""

    STRATEGIES = {
        ImageNotFoundInPDFError: "skip_image",
        ImageCroppingError: "use_fallback_text",
        VLMTimeoutError: "use_fallback_text",
        VLMMemoryError: "reduce_batch_size",
        VLMCircuitBreakerError: "disable_image_processing",
        VLMConfigurationError: "fail_fast",
        PartialExtractionError: "return_partial_result",
        ConfigurationValidationError: "fail_fast"
    }

    @classmethod
    def get_strategy(cls, exception_type: type) -> str:
        """Get recovery strategy for exception type."""
        return cls.STRATEGIES.get(exception_type, "fail_fast")

    @classmethod
    def is_recoverable(cls, exception_type: type) -> bool:
        """Check if exception type is recoverable."""
        strategy = cls.get_strategy(exception_type)
        return strategy != "fail_fast"


# Contract validation functions
def validate_exception_inheritance() -> bool:
    """Validate exception inheritance hierarchy."""
    # Image extraction errors
    assert issubclass(ImageNotFoundInPDFError, ImageExtractionError)
    assert issubclass(ImageCroppingError, ImageExtractionError)
    assert issubclass(ImageExtractionError, Exception)

    # VLM service errors
    assert issubclass(VLMTimeoutError, VLMServiceError)
    assert issubclass(VLMMemoryError, VLMServiceError)
    assert issubclass(VLMCircuitBreakerError, VLMServiceError)
    assert issubclass(VLMServiceError, Exception)

    # Enhanced extraction errors
    assert issubclass(PartialExtractionError, EnhancedExtractionError)
    assert issubclass(EnhancedExtractionError, Exception)

    # Configuration errors
    assert issubclass(ConfigurationValidationError, Exception)
    assert issubclass(VLMConfigurationError, Exception)

    return True


def validate_exception_attributes(exception: Exception) -> bool:
    """Validate exception has required attributes for its type."""
    if isinstance(exception, ImageExtractionError):
        return hasattr(exception, 'file_path') and hasattr(exception, 'details')
    elif isinstance(exception, VLMServiceError):
        return hasattr(exception, 'model_name') and hasattr(exception, 'retry_count')
    elif isinstance(exception, VLMConfigurationError):
        return hasattr(exception, 'config_key') and hasattr(exception, 'expected_value')
    elif isinstance(exception, ConfigurationValidationError):
        return (hasattr(exception, 'field_name') and
                hasattr(exception, 'field_value') and
                hasattr(exception, 'validation_error'))
    else:
        return True


def validate_error_messages() -> bool:
    """Validate that all exceptions provide meaningful error messages."""
    test_exceptions = [
        ImageNotFoundInPDFError(1, 0, "test.pdf"),
        ImageCroppingError(1, (0, 0, 100, 100), "test.pdf"),
        VLMConfigurationError("Model not found", "VISION_MODEL"),
        VLMTimeoutError(30.0, "test-model"),
        VLMMemoryError("2GB", "1GB", "test-model"),
        VLMCircuitBreakerError(5, 3, "test-model"),
        PartialExtractionError("Some pages failed", "test.pdf"),
        ConfigurationValidationError("batch_size", 15, "must be between 1 and 10")
    ]

    for exception in test_exceptions:
        message = str(exception)
        if not message or len(message) < 10:
            return False

    return True
