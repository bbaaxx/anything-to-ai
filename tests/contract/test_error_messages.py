"""Contract tests for error message formatting."""

import pytest
from image_processor.exceptions import (
    ImageNotFoundError,
    UnsupportedFormatError,
    CorruptedImageError,
    ProcessingError,
    ValidationError
)


class TestErrorMessageFormattingContract:
    """Contract tests for consistent error message formatting."""

    def test_image_not_found_error_message_format(self):
        """Test ImageNotFoundError message format consistency."""
        error = ImageNotFoundError("/path/to/missing.jpg")
        message = str(error)
        assert "Image file not found" in message
        assert "/path/to/missing.jpg" in message

    def test_unsupported_format_error_message_format(self):
        """Test UnsupportedFormatError message format consistency."""
        error = UnsupportedFormatError("test.txt", "TXT")
        message = str(error)
        assert "Unsupported image format" in message
        assert "TXT" in message
        assert "test.txt" in message

    def test_unsupported_format_error_without_format(self):
        """Test UnsupportedFormatError message without format detection."""
        error = UnsupportedFormatError("test.unknown")
        message = str(error)
        assert "Unsupported image format" in message
        assert "test.unknown" in message

    def test_corrupted_image_error_message_format(self):
        """Test CorruptedImageError message format consistency."""
        error = CorruptedImageError("corrupted.jpg", "Invalid JPEG header")
        message = str(error)
        assert "Corrupted or unreadable image" in message
        assert "corrupted.jpg" in message
        assert "Invalid JPEG header" in message

    def test_corrupted_image_error_without_details(self):
        """Test CorruptedImageError message without details."""
        error = CorruptedImageError("corrupted.jpg")
        message = str(error)
        assert "Corrupted or unreadable image" in message
        assert "corrupted.jpg" in message

    def test_processing_error_message_format(self):
        """Test ProcessingError message format consistency."""
        error = ProcessingError("image.jpg", "VLM model failed")
        message = str(error)
        assert "VLM processing failed" in message
        assert "image.jpg" in message
        assert "VLM model failed" in message

    def test_processing_error_without_details(self):
        """Test ProcessingError message without details."""
        error = ProcessingError("image.jpg")
        message = str(error)
        assert "VLM processing failed" in message
        assert "image.jpg" in message

    def test_validation_error_message_format(self):
        """Test ValidationError message format consistency."""
        error = ValidationError("Must be between 1 and 10", "batch_size")
        message = str(error)
        assert "Validation error for 'batch_size'" in message
        assert "Must be between 1 and 10" in message

    def test_validation_error_without_parameter(self):
        """Test ValidationError message without parameter name."""
        error = ValidationError("Invalid configuration")
        message = str(error)
        assert "Invalid configuration" in message