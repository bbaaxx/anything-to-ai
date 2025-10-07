"""Unit tests for model validation."""

from anything_to_ai.image_processor.models import (
    ImageDocument,
    DescriptionResult,
    ProcessingResult,
    ProcessingConfig,
)


class TestModelValidation:
    """Unit tests for data model validation logic."""

    def test_image_document_creation(self):
        """Test ImageDocument creation and attributes."""
        doc = ImageDocument(
            file_path="/test/image.jpg",
            format="JPEG",
            width=1024,
            height=768,
            file_size=102400,
            is_large_image=False,
        )

        assert doc.file_path == "/test/image.jpg"
        assert doc.format == "JPEG"
        assert doc.width == 1024
        assert doc.height == 768
        assert doc.file_size == 102400
        assert doc.is_large_image is False

    def test_description_result_creation(self):
        """Test DescriptionResult creation and attributes."""
        result = DescriptionResult(
            image_path="/test/image.jpg",
            description="A test image",
            confidence_score=0.95,
            processing_time=1.5,
            model_used="test-model",
            prompt_used="test prompt",
            success=True,
        )

        assert result.image_path == "/test/image.jpg"
        assert result.description == "A test image"
        assert result.confidence_score == 0.95
        assert result.processing_time == 1.5
        assert result.model_used == "test-model"
        assert result.prompt_used == "test prompt"
        assert result.success is True

    def test_processing_result_creation(self):
        """Test ProcessingResult creation and attributes."""
        individual_result = DescriptionResult(
            image_path="/test/image.jpg",
            description="A test image",
            confidence_score=0.95,
            processing_time=1.5,
            model_used="test-model",
            prompt_used="test prompt",
            success=True,
        )

        result = ProcessingResult(
            success=True,
            results=[individual_result],
            total_images=1,
            successful_count=1,
            failed_count=0,
            total_processing_time=1.5,
            error_message=None,
        )

        assert result.success is True
        assert len(result.results) == 1
        assert result.total_images == 1
        assert result.successful_count == 1
        assert result.failed_count == 0
        assert result.total_processing_time == 1.5
        assert result.error_message is None

    def test_processing_config_defaults(self):
        """Test ProcessingConfig default values."""
        import os

        # Set VISION_MODEL for this test
        original_vision_model = os.environ.get("VISION_MODEL")
        os.environ["VISION_MODEL"] = "mlx-community/Qwen2-VL-2B-Instruct-4bit"

        try:
            config = ProcessingConfig()
            assert config.model_name == "mlx-community/Qwen2-VL-2B-Instruct-4bit"
        finally:
            # Restore original value
            if original_vision_model is not None:
                os.environ["VISION_MODEL"] = original_vision_model
            else:
                del os.environ["VISION_MODEL"]
        assert config.description_style == "detailed"
        assert config.max_description_length == 500
        assert config.batch_size == 4
        assert config.progress_callback is None
        assert config.prompt_template == "Describe this image in a {style} manner."
        assert config.timeout_seconds == 60

    def test_processing_config_custom_values(self):
        """Test ProcessingConfig with custom values."""

        def dummy_callback(current, total):
            pass

        config = ProcessingConfig(
            model_name="custom-model",
            description_style="brief",
            max_description_length=200,
            batch_size=2,
            progress_callback=dummy_callback,
            prompt_template="Custom prompt: {style}",
            timeout_seconds=30,
        )

        assert config.model_name == "custom-model"
        assert config.description_style == "brief"
        assert config.max_description_length == 200
        assert config.batch_size == 2
        assert config.progress_callback is dummy_callback
        assert config.prompt_template == "Custom prompt: {style}"
        assert config.timeout_seconds == 30
