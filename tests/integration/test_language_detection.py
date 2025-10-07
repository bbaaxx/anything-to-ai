"""
Integration tests for language detection and hints.
Tests FR-022: Language detection and language hints.
"""

import pytest


class TestLanguageDetection:
    """Test language auto-detection and hint functionality."""

    def test_auto_detect_english(self):
        """Test auto-detection of English audio."""
        pytest.skip("Test audio file not available yet")

        config = audio_processor.create_config(language=None)  # Auto-detect
        result = audio_processor.process_audio("sample-data/audio/speech.mp3", config)

        assert result.success is True
        assert result.detected_language == "en"

    def test_auto_detect_spanish(self):
        """Test auto-detection of Spanish audio."""
        pytest.skip("Test audio file not available yet")

        config = audio_processor.create_config(language=None)  # Auto-detect
        result = audio_processor.process_audio("sample-data/audio/spanish.m4a", config)

        assert result.success is True
        assert result.detected_language == "es"

    def test_language_hint_english(self):
        """Test processing with English language hint."""
        pytest.skip("Test audio file not available yet")

        config = audio_processor.create_config(language="en")
        result = audio_processor.process_audio("sample-data/audio/speech.mp3", config)

        assert result.success is True
        assert result.detected_language == "en"

    def test_language_hint_spanish(self):
        """Test processing with Spanish language hint."""
        pytest.skip("Test audio file not available yet")

        config = audio_processor.create_config(language="es")
        result = audio_processor.process_audio("sample-data/audio/spanish.m4a", config)

        assert result.success is True
        assert result.detected_language == "es"

    def test_language_hint_improves_accuracy(self):
        """Test that language hint can improve transcription accuracy."""
        pytest.skip("Test audio file not available yet")

        # Process with and without hint
        config_no_hint = audio_processor.create_config(language=None)
        config_with_hint = audio_processor.create_config(language="es")

        result_no_hint = audio_processor.process_audio("sample-data/audio/spanish.m4a", config_no_hint)
        result_with_hint = audio_processor.process_audio("sample-data/audio/spanish.m4a", config_with_hint)

        # Both should succeed
        assert result_no_hint.success is True
        assert result_with_hint.success is True
        # Language should be detected correctly
        assert result_no_hint.detected_language == "es"
        assert result_with_hint.detected_language == "es"
