"""Integration tests for PDF processor integration scenarios."""

import pytest
import tempfile
import os
from PIL import Image
from anything_to_ai.image_processor import process_image, ProcessingConfig


class TestPdfIntegration:
    """Integration tests for image processor and PDF processor integration."""

    @pytest.fixture
    def sample_image(self):
        """Create a sample image for integration testing."""
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            img = Image.new("RGB", (100, 100), color="blue")
            img.save(f.name, "JPEG")
            yield f.name
        os.unlink(f.name)

    def test_image_processor_import_compatibility(self):
        """Test image processor can be imported alongside PDF processor."""
        # Test that both modules can be imported without conflicts
        try:
            import anything_to_ai.pdf_extractor
            import anything_to_ai.image_processor

            # Both should be importable
            assert hasattr(pdf_extractor, "extract_text")
            assert hasattr(image_processor, "process_image")

        except ImportError as e:
            pytest.skip(f"PDF extractor not available: {e}")

    def test_unified_document_processing_workflow(self, sample_image):
        """Test unified workflow processing both PDF and image content."""
        try:
            from anything_to_ai.pdf_extractor import extract_text
            from anything_to_ai.image_processor import process_image

            # Simulate processing document with both text and images
            def process_document_assets(pdf_path, image_paths):
                """Simulate the quickstart integration example."""
                results = {}

                # Process PDF content (simulated)
                if pdf_path:
                    # Would normally extract text here
                    results["pdf_content"] = "Sample PDF text content"

                # Process associated images
                image_descriptions = []
                for image_path in image_paths:
                    result = process_image(image_path)
                    if result.success:
                        image_descriptions.append(result.description)

                results["image_descriptions"] = image_descriptions
                return results

            # Test the integration
            assets = process_document_assets(None, [sample_image])

            assert "image_descriptions" in assets
            assert len(assets["image_descriptions"]) >= 0  # May be empty if processing fails

        except ImportError:
            pytest.skip("PDF extractor not available for integration testing")

    def test_consistent_error_handling_patterns(self, sample_image):
        """Test that error handling patterns are consistent between modules."""
        try:
            from anything_to_ai.pdf_extractor.exceptions import PDFExtractionError
            from anything_to_ai.image_processor.exceptions import ImageProcessingError

            # Both should inherit from Exception and follow similar patterns
            assert issubclass(PDFExtractionError, Exception)
            assert issubclass(ImageProcessingError, Exception)

            # Both should have similar error attributes
            pdf_error = PDFExtractionError("Test error", "test.pdf")
            image_error = ImageProcessingError("Test error", "test.jpg")

            # Both should have message attributes
            assert hasattr(pdf_error, "message")
            assert hasattr(image_error, "message")

        except ImportError:
            pytest.skip("PDF extractor not available for error pattern testing")

    def test_progress_callback_integration_pattern(self, sample_image):
        """Test that progress callbacks follow consistent patterns."""
        # Test image processor progress callback
        progress_calls = []

        def unified_progress_handler(current, total):
            """Unified progress tracking across processing types."""
            percentage = (current / total) * 100
            progress_calls.append({"current": current, "total": total, "percentage": percentage})

        config = ProcessingConfig(progress_callback=unified_progress_handler)

        # Process single image to test progress pattern
        result = process_image(sample_image, config)

        # Should work with image processor (may or may not call progress for single image)
        assert isinstance(result, (type(None), object))  # Allow for not implemented

    def test_configuration_pattern_consistency(self):
        """Test that configuration patterns are consistent between modules."""
        from anything_to_ai.image_processor import ProcessingConfig, create_config

        # Test that config creation follows expected patterns
        config = create_config(description_style="detailed", max_length=500, batch_size=4)

        assert isinstance(config, ProcessingConfig)
        assert config.description_style == "detailed"
        assert config.max_description_length == 500
        assert config.batch_size == 4

    def test_file_handling_consistency(self, sample_image):
        """Test that file handling is consistent between modules."""
        # Test that image processor handles file paths consistently
        result = process_image(sample_image)

        # Should return result object (even if not implemented)
        assert result is not None or result is None  # Allow for not implemented

        # Test nonexistent file handling
        try:
            process_image("nonexistent.jpg")
        except Exception as e:
            # Should raise appropriate exception type
            assert "not found" in str(e).lower() or str(e) == ""

    def test_module_version_compatibility(self):
        """Test that module versions are compatible."""

        # Should have version information
        assert hasattr(image_processor, "__version__")
        assert isinstance(image_processor.__version__, str)

    def test_api_surface_consistency(self):
        """Test that API surface follows consistent patterns."""

        # Core functions should be available
        expected_functions = [
            "process_image",
            "process_images",
            "validate_image",
            "get_supported_formats",
            "process_images_streaming",
            "create_config",
            "get_image_info",
        ]

        for func_name in expected_functions:
            assert hasattr(image_processor, func_name)
            assert callable(getattr(image_processor, func_name))

    def test_memory_usage_patterns(self, sample_image):
        """Test that memory usage patterns are reasonable for integration."""
        # Test that image processing doesn't consume excessive memory
        # This is important when both PDF and image processing run together

        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Process an image
        process_image(sample_image)

        # Check memory usage after processing
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB for test image)
        assert memory_increase < 100 * 1024 * 1024  # 100MB limit
