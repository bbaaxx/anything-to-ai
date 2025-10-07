"""Contract tests for get_supported_formats() API function."""

from anything_to_ai.image_processor import get_supported_formats


class TestSupportedFormatsContract:
    """Contract tests for supported formats API."""

    def test_get_supported_formats_basic_call(self):
        """Test basic get_supported_formats call returns list."""
        result = get_supported_formats()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_supported_formats_common_formats(self):
        """Test get_supported_formats includes common image formats."""
        result = get_supported_formats()
        expected_formats = ["JPG", "JPEG", "PNG", "GIF", "BMP", "WEBP"]
        for fmt in expected_formats:
            assert fmt in result or fmt.lower() in result

    def test_get_supported_formats_no_duplicates(self):
        """Test get_supported_formats returns unique formats."""
        result = get_supported_formats()
        assert len(result) == len(set(result))

    def test_get_supported_formats_string_elements(self):
        """Test get_supported_formats returns list of strings."""
        result = get_supported_formats()
        for fmt in result:
            assert isinstance(fmt, str)
            assert len(fmt) > 0

    def test_get_supported_formats_uppercase_consistency(self):
        """Test get_supported_formats returns consistent case."""
        result = get_supported_formats()
        # Expect either all uppercase or all lowercase, but consistent
        if result:
            first_case = result[0].isupper()
            for fmt in result:
                assert fmt.isupper() == first_case
