"""Contract tests for exception hierarchy."""

from anyfile_to_ai.image_processor.exceptions import (
    ImageProcessingError,
    ImageNotFoundError,
    UnsupportedFormatError,
    CorruptedImageError,
    ProcessingError,
    ValidationError
)


class TestExceptionHierarchyContract:
    """Contract tests for exception hierarchy and behavior."""

    def test_base_exception_inheritance(self):
        """Test all custom exceptions inherit from ImageProcessingError."""
        exceptions = [
            ImageNotFoundError,
            UnsupportedFormatError,
            CorruptedImageError,
            ProcessingError,
            ValidationError
        ]
        for exc_class in exceptions:
            assert issubclass(exc_class, ImageProcessingError)
            assert issubclass(exc_class, Exception)

    def test_image_not_found_error_creation(self):
        """Test ImageNotFoundError creation and attributes."""
        error = ImageNotFoundError("test.jpg")
        assert isinstance(error, ImageProcessingError)
        assert error.image_path == "test.jpg"
        assert "test.jpg" in str(error)

    def test_unsupported_format_error_creation(self):
        """Test UnsupportedFormatError creation and attributes."""
        error = UnsupportedFormatError("test.txt", "TXT")
        assert isinstance(error, ImageProcessingError)
        assert error.image_path == "test.txt"
        assert "test.txt" in str(error)
        assert "TXT" in str(error)

    def test_corrupted_image_error_creation(self):
        """Test CorruptedImageError creation and attributes."""
        error = CorruptedImageError("test.jpg", "Invalid header")
        assert isinstance(error, ImageProcessingError)
        assert error.image_path == "test.jpg"
        assert "test.jpg" in str(error)
        assert "Invalid header" in str(error)

    def test_processing_error_creation(self):
        """Test ProcessingError creation and attributes."""
        error = ProcessingError("test.jpg", "Model timeout")
        assert isinstance(error, ImageProcessingError)
        assert error.image_path == "test.jpg"
        assert "test.jpg" in str(error)
        assert "Model timeout" in str(error)

    def test_validation_error_creation(self):
        """Test ValidationError creation and attributes."""
        error = ValidationError("Invalid value", "batch_size")
        assert isinstance(error, ImageProcessingError)
        assert "batch_size" in str(error)
        assert "Invalid value" in str(error)

    def test_base_exception_attributes(self):
        """Test base ImageProcessingError attributes."""
        error = ImageProcessingError("Test message", "test.jpg")
        assert error.message == "Test message"
        assert error.image_path == "test.jpg"
        assert str(error) == "Test message"
