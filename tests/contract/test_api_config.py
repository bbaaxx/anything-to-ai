"""Contract tests for create_config() API function."""

import pytest
from image_processor import create_config, ProcessingConfig
from image_processor.exceptions import ValidationError


class TestCreateConfigContract:
    """Contract tests for configuration creation."""

    def test_create_config_basic_call(self):
        """Test basic create_config call returns ProcessingConfig."""
        result = create_config()
        assert isinstance(result, ProcessingConfig)
        assert result.description_style == "detailed"
        assert result.max_description_length == 500
        assert result.batch_size == 4

    def test_create_config_with_parameters(self):
        """Test create_config with custom parameters."""
        result = create_config(
            description_style="brief",
            max_length=200,
            batch_size=2
        )
        assert isinstance(result, ProcessingConfig)
        assert result.description_style == "brief"
        assert result.max_description_length == 200
        assert result.batch_size == 2

    def test_create_config_invalid_style(self):
        """Test create_config raises ValidationError for invalid style."""
        with pytest.raises(ValidationError) as exc_info:
            create_config(description_style="invalid")
        assert "style" in str(exc_info.value).lower()

    def test_create_config_invalid_max_length(self):
        """Test create_config validates max_length range."""
        with pytest.raises(ValidationError) as exc_info:
            create_config(max_length=0)
        assert "length" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            create_config(max_length=2000)
        assert "length" in str(exc_info.value).lower()

    def test_create_config_invalid_batch_size(self):
        """Test create_config validates batch_size range."""
        with pytest.raises(ValidationError) as exc_info:
            create_config(batch_size=0)
        assert "batch" in str(exc_info.value).lower()

        with pytest.raises(ValidationError) as exc_info:
            create_config(batch_size=20)
        assert "batch" in str(exc_info.value).lower()

    def test_create_config_with_progress_callback(self):
        """Test create_config accepts progress callback."""
        def callback(current, total):
            pass

        result = create_config(progress_callback=callback)
        assert result.progress_callback is callback