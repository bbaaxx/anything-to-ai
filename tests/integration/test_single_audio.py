"""
Integration tests for single audio file transcription.
Tests FR-003, FR-012: Single audio processing with default settings.
"""

import pytest
import os
from pathlib import Path


class TestSingleAudioIntegration:
    """Test single audio file transcription with defaults."""

    @pytest.fixture
    def sample_audio_path(self):
        """Path to sample audio file."""
        return "sample-data/audio/speech.mp3"

    def test_process_single_audio_with_defaults(self, sample_audio_path):
        """Test processing single audio file with default configuration."""
        pytest.skip("Test audio file not available yet")
        import audio_processor

        # Create default config
        config = audio_processor.create_config()

        # Process audio
        result = audio_processor.process_audio(sample_audio_path, config)

        # Verify result
        assert result.success is True
        assert result.text is not None
        assert len(result.text) > 0
        assert result.model_used == "medium"
        assert result.quantization == "4bit"
        assert result.processing_time > 0
        assert result.detected_language is not None
        assert result.error_message is None

    def test_process_single_audio_returns_confidence_score(self, sample_audio_path):
        """Test that transcription returns confidence score."""
        pytest.skip("Test audio file not available yet")
        import audio_processor

        config = audio_processor.create_config()
        result = audio_processor.process_audio(sample_audio_path, config)

        assert result.confidence_score is not None
        assert 0.0 <= result.confidence_score <= 1.0

    def test_process_with_tiny_model(self, sample_audio_path):
        """Test processing with tiny model for speed."""
        pytest.skip("Test audio file not available yet")
        import audio_processor

        config = audio_processor.create_config(model="tiny", quantization="4bit")
        result = audio_processor.process_audio(sample_audio_path, config)

        assert result.success is True
        assert result.model_used == "tiny"

    def test_process_with_language_auto_detect(self, sample_audio_path):
        """Test language auto-detection."""
        pytest.skip("Test audio file not available yet")
        import audio_processor

        config = audio_processor.create_config(language=None)  # Auto-detect
        result = audio_processor.process_audio(sample_audio_path, config)

        assert result.success is True
        assert result.detected_language is not None
        assert len(result.detected_language) == 2  # ISO 639-1 code