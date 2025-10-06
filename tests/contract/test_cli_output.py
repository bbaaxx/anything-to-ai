"""Contract tests for CLI output formatting functions."""

import json
from anyfile_to_ai.image_processor.cli import format_output, format_single_result
from anyfile_to_ai.image_processor import ProcessingResult, DescriptionResult


class TestCliOutputFormattingContract:
    """Contract tests for CLI output formatting."""

    def test_format_output_function_exists(self):
        """Test format_output function exists and is callable."""
        assert callable(format_output)

    def test_format_single_result_function_exists(self):
        """Test format_single_result function exists and is callable."""
        assert callable(format_single_result)

    def test_format_output_plain_format(self):
        """Test format_output with plain format."""
        result = ProcessingResult(
            success=True,
            results=[],
            total_images=1,
            successful_count=1,
            failed_count=0,
            total_processing_time=1.5
        )
        output = format_output(result, "plain")
        assert isinstance(output, str)
        assert len(output) > 0

    def test_format_output_json_format(self):
        """Test format_output with JSON format."""
        result = ProcessingResult(
            success=True,
            results=[],
            total_images=1,
            successful_count=1,
            failed_count=0,
            total_processing_time=1.5
        )
        output = format_output(result, "json")
        assert isinstance(output, str)
        # Should be valid JSON
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_format_output_csv_format(self):
        """Test format_output with CSV format."""
        result = ProcessingResult(
            success=True,
            results=[],
            total_images=1,
            successful_count=1,
            failed_count=0,
            total_processing_time=1.5
        )
        output = format_output(result, "csv")
        assert isinstance(output, str)
        assert len(output) > 0

    def test_format_single_result_plain_format(self):
        """Test format_single_result with plain format."""
        result = DescriptionResult(
            image_path="test.jpg",
            description="A test image",
            confidence_score=0.95,
            processing_time=1.2,
            model_used="test-model",
            prompt_used="test prompt",
            success=True
        )
        output = format_single_result(result, "plain")
        assert isinstance(output, str)
        assert "test.jpg" in output
        assert "A test image" in output

    def test_format_single_result_json_format(self):
        """Test format_single_result with JSON format."""
        result = DescriptionResult(
            image_path="test.jpg",
            description="A test image",
            confidence_score=0.95,
            processing_time=1.2,
            model_used="test-model",
            prompt_used="test prompt",
            success=True
        )
        output = format_single_result(result, "json")
        assert isinstance(output, str)
        # Should be valid JSON
        parsed = json.loads(output)
        assert parsed["image_path"] == "test.jpg"
        assert parsed["description"] == "A test image"

    def test_format_single_result_csv_format(self):
        """Test format_single_result with CSV format."""
        result = DescriptionResult(
            image_path="test.jpg",
            description="A test image",
            confidence_score=0.95,
            processing_time=1.2,
            model_used="test-model",
            prompt_used="test prompt",
            success=True
        )
        output = format_single_result(result, "csv")
        assert isinstance(output, str)
        # Should contain CSV-appropriate format
        assert "," in output  # CSV delimiter present
