"""Unit tests for utility functions."""

import tempfile
import os
from PIL import Image
from anything_to_ai.image_processor import get_supported_formats
from anything_to_ai.image_processor.cli import expand_image_paths, format_output
from anything_to_ai.image_processor.models import ProcessingResult, DescriptionResult


class TestUtilityFunctions:
    """Unit tests for utility function logic."""

    def test_supported_formats_constant(self):
        """Test get_supported_formats function."""
        expected_formats = {"JPEG", "JPG", "PNG", "GIF", "BMP", "WEBP"}
        assert set(get_supported_formats()) == expected_formats

    def test_expand_image_paths_single_file(self):
        """Test expand_image_paths with single file."""
        # Create temporary image file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            img = Image.new("RGB", (10, 10), color="red")
            img.save(f.name, "JPEG")
            temp_path = f.name

        try:
            result = expand_image_paths([temp_path])
            assert result == [temp_path]
        finally:
            os.unlink(temp_path)

    def test_expand_image_paths_directory(self):
        """Test expand_image_paths with directory."""
        # Create temporary directory with images
        temp_dir = tempfile.mkdtemp()
        image_paths = []

        try:
            for i, ext in enumerate(["jpg", "png"]):
                img_path = os.path.join(temp_dir, f"image{i}.{ext}")
                img = Image.new("RGB", (10, 10), color="red")
                img.save(img_path)
                image_paths.append(img_path)

            result = expand_image_paths([temp_dir])
            assert len(result) == 2
            assert all(path in result for path in image_paths)

        finally:
            for path in image_paths:
                if os.path.exists(path):
                    os.unlink(path)
            os.rmdir(temp_dir)

    def test_format_output_plain(self):
        """Test format_output with plain format."""
        result = ProcessingResult(
            success=True,
            results=[
                DescriptionResult(
                    image_path="test.jpg",
                    description="Test description",
                    confidence_score=0.9,
                    processing_time=1.0,
                    model_used="test-model",
                    prompt_used="test prompt",
                    success=True,
                ),
            ],
            total_images=1,
            successful_count=1,
            failed_count=0,
            total_processing_time=1.0,
        )

        output = format_output(result, "plain")
        assert "Processed 1 images" in output
        assert "Successful: 1, Failed: 0" in output
        assert "test.jpg" in output
        assert "Test description" in output

    def test_format_output_json(self):
        """Test format_output with JSON format."""
        import json

        result = ProcessingResult(
            success=True,
            results=[
                DescriptionResult(
                    image_path="test.jpg",
                    description="Test description",
                    confidence_score=0.9,
                    processing_time=1.0,
                    model_used="test-model",
                    prompt_used="test prompt",
                    success=True,
                ),
            ],
            total_images=1,
            successful_count=1,
            failed_count=0,
            total_processing_time=1.0,
        )

        output = format_output(result, "json")
        data = json.loads(output)

        assert data["success"] is True
        assert data["total_images"] == 1
        assert len(data["results"]) == 1
        assert data["results"][0]["image_path"] == "test.jpg"

    def test_format_output_csv(self):
        """Test format_output with CSV format."""
        result = ProcessingResult(
            success=True,
            results=[
                DescriptionResult(
                    image_path="test.jpg",
                    description="Test description",
                    confidence_score=0.9,
                    processing_time=1.0,
                    model_used="test-model",
                    prompt_used="test prompt",
                    success=True,
                ),
            ],
            total_images=1,
            successful_count=1,
            failed_count=0,
            total_processing_time=1.0,
        )

        output = format_output(result, "csv")
        lines = output.strip().split("\n")

        assert len(lines) >= 2  # Header + data
        assert "image_path" in lines[0]  # Header row
        assert "test.jpg" in lines[1]  # Data row
