"""Contract tests for get_image_info() API function."""

import pytest
from anyfile_to_ai.image_processor import get_image_info
from anyfile_to_ai.image_processor.exceptions import ImageNotFoundError, CorruptedImageError


class TestGetImageInfoContract:
    """Contract tests for image information retrieval."""

    def test_get_image_info_basic_call(self):
        """Test basic get_image_info call returns dictionary."""
        result = get_image_info("sample.jpg")
        assert isinstance(result, dict)
        assert len(result) > 0

    def test_get_image_info_required_fields(self):
        """Test get_image_info returns required metadata fields."""
        result = get_image_info("sample.jpg")
        required_fields = ["file_path", "format", "width", "height", "file_size", "is_large_image"]
        for field in required_fields:
            assert field in result

    def test_get_image_info_data_types(self):
        """Test get_image_info returns correct data types."""
        result = get_image_info("sample.jpg")
        assert isinstance(result["file_path"], str)
        assert isinstance(result["format"], str)
        assert isinstance(result["width"], int)
        assert isinstance(result["height"], int)
        assert isinstance(result["file_size"], int)
        assert isinstance(result["is_large_image"], bool)

    def test_get_image_info_positive_values(self):
        """Test get_image_info returns positive values for dimensions."""
        result = get_image_info("sample.jpg")
        assert result["width"] > 0
        assert result["height"] > 0
        assert result["file_size"] > 0

    def test_get_image_info_missing_file(self):
        """Test get_image_info raises ImageNotFoundError for missing files."""
        with pytest.raises(ImageNotFoundError) as exc_info:
            get_image_info("nonexistent.jpg")
        assert "nonexistent.jpg" in str(exc_info.value)

    def test_get_image_info_corrupted_file(self):
        """Test get_image_info raises CorruptedImageError for corrupted files."""
        with pytest.raises(CorruptedImageError) as exc_info:
            get_image_info("corrupted.jpg")
        assert "corrupted.jpg" in str(exc_info.value)

    def test_get_image_info_large_image_detection(self):
        """Test get_image_info correctly identifies large images."""
        # This test requires actual implementation logic
        result = get_image_info("large_image.jpg")
        if result["file_size"] > 10 * 1024 * 1024 or result["width"] > 2048 or result["height"] > 2048:
            assert result["is_large_image"] is True
        else:
            assert result["is_large_image"] is False
