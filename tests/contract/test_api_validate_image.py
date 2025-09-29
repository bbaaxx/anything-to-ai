"""Contract tests for validate_image() API function."""

import pytest
from image_processor import validate_image, ImageDocument
from image_processor.exceptions import ImageNotFoundError, UnsupportedFormatError, CorruptedImageError


class TestValidateImageContract:
    """Contract tests for image validation."""

    def test_validate_image_basic_call(self):
        """Test basic validate_image call returns ImageDocument."""
        result = validate_image("sample.jpg")
        assert isinstance(result, ImageDocument)
        assert result.file_path == "sample.jpg"
        assert result.format in ["JPG", "JPEG"]
        assert result.width > 0
        assert result.height > 0
        assert result.file_size > 0

    def test_validate_image_large_file_detection(self):
        """Test validate_image detects large images correctly."""
        result = validate_image("large_image.jpg")
        assert isinstance(result, ImageDocument)
        assert isinstance(result.is_large_image, bool)

    def test_validate_image_missing_file(self):
        """Test validate_image raises ImageNotFoundError for missing files."""
        with pytest.raises(ImageNotFoundError) as exc_info:
            validate_image("nonexistent.jpg")
        assert "nonexistent.jpg" in str(exc_info.value)

    def test_validate_image_unsupported_format(self):
        """Test validate_image raises UnsupportedFormatError for unsupported formats."""
        with pytest.raises(UnsupportedFormatError) as exc_info:
            validate_image("document.txt")
        assert "document.txt" in str(exc_info.value)

    def test_validate_image_corrupted_file(self):
        """Test validate_image raises CorruptedImageError for corrupted files."""
        with pytest.raises(CorruptedImageError) as exc_info:
            validate_image("corrupted.jpg")
        assert "corrupted.jpg" in str(exc_info.value)

    def test_validate_image_metadata_fields(self):
        """Test validate_image returns all required metadata fields."""
        result = validate_image("sample.jpg")
        assert hasattr(result, 'file_path')
        assert hasattr(result, 'format')
        assert hasattr(result, 'width')
        assert hasattr(result, 'height')
        assert hasattr(result, 'file_size')
        assert hasattr(result, 'is_large_image')
