"""
Integration tests for output formatting.
Tests FR-004, FR-015: Plain and JSON output formats.
"""

import pytest
import json


class TestOutputFormats:
    """Test output format options (plain text and JSON)."""

    def test_plain_text_output_format(self):
        """Test that plain text output format works."""
        pytest.skip("Test audio file not available yet")
        import audio_processor

        config = audio_processor.create_config(output_format="plain")
        result = audio_processor.process_audio("sample-data/audio/speech.mp3", config)

        assert result.success is True
        assert result.text is not None
        assert isinstance(result.text, str)

    def test_json_output_format(self):
        """Test that JSON output format works."""
        pytest.skip("Test audio file not available yet")
        import audio_processor

        config = audio_processor.create_config(output_format="json")
        result = audio_processor.process_audio("sample-data/audio/speech.mp3", config)

        assert result.success is True
        # Verify result can be converted to JSON
        result_dict = {
            "audio_path": result.audio_path,
            "text": result.text,
            "confidence_score": result.confidence_score,
            "processing_time": result.processing_time,
            "model_used": result.model_used,
            "quantization": result.quantization,
            "detected_language": result.detected_language,
            "success": result.success,
            "error_message": result.error_message
        }
        json_str = json.dumps(result_dict)
        assert json_str is not None

    def test_batch_results_json_serializable(self):
        """Test that batch results are JSON serializable."""
        pytest.skip("Test audio files not available yet")
        import audio_processor

        files = [
            "sample-data/audio/speech.mp3",
            "sample-data/audio/spanish.m4a"
        ]

        config = audio_processor.create_config(output_format="json")
        result = audio_processor.process_audio_batch(files, config)

        # Verify result can be converted to JSON
        result_dict = {
            "success": result.success,
            "total_files": result.total_files,
            "successful_count": result.successful_count,
            "failed_count": result.failed_count,
            "total_processing_time": result.total_processing_time,
            "average_processing_time": result.average_processing_time,
            "results": [
                {
                    "audio_path": r.audio_path,
                    "text": r.text,
                    "confidence_score": r.confidence_score,
                    "processing_time": r.processing_time,
                    "model_used": r.model_used,
                    "quantization": r.quantization,
                    "detected_language": r.detected_language,
                    "success": r.success,
                    "error_message": r.error_message
                }
                for r in result.results
            ],
            "error_summary": result.error_summary
        }
        json_str = json.dumps(result_dict)
        assert json_str is not None

    def test_output_format_validation(self):
        """Test that invalid output format raises error."""
        import audio_processor
        from audio_processor import ValidationError

        with pytest.raises(ValidationError):
            audio_processor.create_config(output_format="invalid")
