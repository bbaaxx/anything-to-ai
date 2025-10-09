"""Custom exception classes for PDF extraction."""


class PDFExtractionError(Exception):
    """Base exception for PDF extraction errors."""

    def __init__(self, message: str, file_path: str | None = None):
        self.message = message
        self.file_path = file_path
        super().__init__(self.format_message())

    def format_message(self) -> str:
        if self.file_path:
            return f"{self.message}: {self.file_path}"
        return self.message


class PDFNotFoundError(PDFExtractionError):
    """Raised when PDF file does not exist or is not accessible."""

    def __init__(self, file_path: str):
        super().__init__("PDF file not found or not accessible", file_path)


class PDFCorruptedError(PDFExtractionError):
    """Raised when PDF file is corrupted or invalid."""

    def __init__(self, file_path: str, details: str | None = None):
        message = "PDF file is corrupted or invalid"
        if details:
            message += f": {details}"
        super().__init__(message, file_path)


class PDFPasswordProtectedError(PDFExtractionError):
    """Raised when PDF requires password for access."""

    def __init__(self, file_path: str):
        super().__init__("PDF file is password protected", file_path)


class PDFNoTextError(PDFExtractionError):
    """Raised when PDF contains no extractable text (images only)."""

    def __init__(self, file_path: str):
        super().__init__("PDF contains no extractable text (images only)", file_path)


class ProcessingInterruptedError(PDFExtractionError):
    """Raised when PDF processing is interrupted mid-stream."""

    def __init__(self, file_path: str, page_number: int):
        message = f"PDF processing interrupted at page {page_number}"
        super().__init__(message, file_path)


# Enhanced extraction exceptions
class ImageExtractionError(Exception):
    """Base exception for image extraction errors."""

    def __init__(self, message: str, file_path: str | None = None, details: dict | None = None):
        super().__init__(message)
        self.file_path = file_path
        self.details = details or {}

    def __str__(self) -> str:
        if self.file_path:
            return f"{super().__str__()} (file: {self.file_path})"
        return super().__str__()


class ImageNotFoundInPDFError(ImageExtractionError):
    """Raised when expected image cannot be found in PDF."""

    def __init__(self, page_number: int, image_index: int, file_path: str | None = None):
        message = f"Image {image_index} not found on page {page_number}"
        super().__init__(message, file_path)
        self.page_number = page_number
        self.image_index = image_index


class ImageCroppingError(ImageExtractionError):
    """Raised when image cannot be cropped from PDF page."""

    def __init__(self, page_number: int, bounding_box: tuple, file_path: str | None = None, reason: str | None = None):
        message = f"Cannot crop image from page {page_number} at {bounding_box}"
        if reason:
            message += f": {reason}"
        super().__init__(message, file_path)
        self.page_number = page_number
        self.bounding_box = bounding_box
        self.reason = reason


class VLMConfigurationError(Exception):
    """Raised when VLM configuration is invalid or missing."""

    def __init__(self, message: str, config_key: str | None = None, expected_value: str | None = None):
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

    def __init__(self, message: str, model_name: str | None = None, retry_count: int = 0):
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

    def __init__(self, timeout_seconds: float, model_name: str | None = None):
        message = f"VLM processing timed out after {timeout_seconds} seconds"
        super().__init__(message, model_name)
        self.timeout_seconds = timeout_seconds


class VLMMemoryError(VLMServiceError):
    """Raised when VLM runs out of memory."""

    def __init__(self, required_memory: str | None = None, available_memory: str | None = None, model_name: str | None = None):
        message = "VLM processing failed due to insufficient memory"
        if required_memory and available_memory:
            message += f" (required: {required_memory}, available: {available_memory})"
        super().__init__(message, model_name)
        self.required_memory = required_memory
        self.available_memory = available_memory


class VLMCircuitBreakerError(VLMServiceError):
    """Raised when VLM circuit breaker is open."""

    def __init__(self, failure_count: int, threshold: int, model_name: str | None = None):
        message = f"VLM circuit breaker open: {failure_count} failures (threshold: {threshold})"
        super().__init__(message, model_name)
        self.failure_count = failure_count
        self.threshold = threshold


class EnhancedExtractionError(Exception):
    """Base exception for enhanced extraction process errors."""

    def __init__(self, message: str, file_path: str | None = None, partial_result: dict | None = None):
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

    def __init__(self, message: str, file_path: str | None = None, partial_result: dict | None = None, failed_pages: list | None = None, failed_images: list | None = None):
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

    def __init__(self, field_name: str, field_value, validation_error: str):
        message = f"Invalid configuration for '{field_name}': {validation_error}"
        super().__init__(message)
        self.field_name = field_name
        self.field_value = field_value
        self.validation_error = validation_error

    def __str__(self) -> str:
        return f"Configuration Validation Error - {self.field_name}: {self.validation_error} (value: {self.field_value})"
