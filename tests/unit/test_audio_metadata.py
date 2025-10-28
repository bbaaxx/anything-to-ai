"""Unit tests for Audio metadata extraction."""

from datetime import datetime, timezone, UTC
from unittest.mock import MagicMock

import pytest

from anyfile_to_ai.audio_processor.metadata import (
    _extract_audio_source_metadata,
    _extract_configuration_metadata,
    _extract_processing_metadata,
    extract_audio_metadata,
)
from anyfile_to_ai.audio_processor.models import AudioDocument


class TestProcessingMetadata:
    """Tests for processing metadata extraction."""

    def test_extract_processing_metadata_basic(self):
        """Test basic processing metadata extraction."""
        result = _extract_processing_metadata(3.2, "lightning-whisper-mlx-medium")

        assert "timestamp" in result
        assert result["model_version"] == "lightning-whisper-mlx-medium"
        assert result["processing_time_seconds"] == 3.2

    def test_timestamp_is_iso8601_with_timezone(self):
        """Test timestamp is ISO 8601 format with timezone."""
        result = _extract_processing_metadata(1.0, "test-model")
        timestamp = result["timestamp"]

        dt = datetime.fromisoformat(timestamp)
        assert dt.tzinfo == UTC


class TestConfigurationMetadata:
    """Tests for configuration metadata extraction."""

    def test_extract_configuration_metadata_basic(self):
        """Test basic configuration metadata extraction."""
        user_config = {"model": "medium", "language": "en"}
        effective_config = {"model": "medium", "language": "en", "quantization": "none"}

        result = _extract_configuration_metadata(user_config, effective_config)

        assert result["user_provided"] == user_config
        assert result["effective"] == effective_config


class TestAudioSourceMetadata:
    """Tests for audio source metadata extraction."""

    def test_extract_audio_source_metadata_complete(self):
        """Test complete audio source metadata extraction."""
        audio_doc = AudioDocument(
            file_path="/path/to/audio.mp3",
            file_size=5242880,
            duration=180.5,
            sample_rate=44100,
            channels=2,
            format="mp3",
        )

        result = _extract_audio_source_metadata(audio_doc, "en", 0.95)

        assert result["file_path"] == "/path/to/audio.mp3"
        assert result["file_size_bytes"] == 5242880
        assert result["duration_seconds"] == 180.5
        assert result["sample_rate_hz"] == 44100
        assert result["channels"] == 2
        assert result["format"] == "mp3"
        assert result["detected_language"] == "en"
        assert result["language_confidence"] == 0.95

    def test_extract_audio_source_metadata_no_language(self):
        """Test audio source metadata without language detection."""
        audio_doc = AudioDocument(
            file_path="/path/to/audio.wav",
            file_size=10485760,
            duration=60.0,
            sample_rate=48000,
            channels=1,
            format="wav",
        )

        result = _extract_audio_source_metadata(audio_doc, None, None)

        assert result["detected_language"] == "unavailable"
        assert result["language_confidence"] == "unavailable"

    def test_extract_audio_source_metadata_partial_language(self):
        """Test audio source metadata with language but no confidence."""
        audio_doc = AudioDocument(
            file_path="/path/to/audio.m4a",
            file_size=3145728,
            duration=120.0,
            sample_rate=44100,
            channels=2,
            format="m4a",
        )

        result = _extract_audio_source_metadata(audio_doc, "es", None)

        assert result["detected_language"] == "es"
        assert result["language_confidence"] == "unavailable"

    def test_extract_audio_source_metadata_mono(self):
        """Test audio source metadata for mono audio."""
        audio_doc = AudioDocument(
            file_path="/path/to/mono.wav",
            file_size=1048576,
            duration=30.0,
            sample_rate=16000,
            channels=1,
            format="wav",
        )

        result = _extract_audio_source_metadata(audio_doc, "en", 0.88)

        assert result["channels"] == 1


class TestFullMetadataExtraction:
    """Tests for complete metadata extraction."""

    def test_extract_audio_metadata_complete(self):
        """Test complete audio metadata extraction."""
        audio_doc = AudioDocument(
            file_path="/path/to/audio.mp3",
            file_size=5242880,
            duration=180.5,
            sample_rate=44100,
            channels=2,
            format="mp3",
        )

        user_config = {"model": "medium", "language": "en"}
        effective_config = {
            "model": "medium",
            "language": "en",
            "quantization": "none",
            "verbose": False,
        }

        result = extract_audio_metadata(audio_doc, 3.2, "lightning-whisper-mlx-medium", "en", 0.95, user_config, effective_config)

        assert "processing" in result
        assert "configuration" in result
        assert "source" in result

        assert result["processing"]["processing_time_seconds"] == 3.2
        assert result["processing"]["model_version"] == "lightning-whisper-mlx-medium"
        assert result["configuration"]["user_provided"] == user_config
        assert result["source"]["duration_seconds"] == 180.5
        assert result["source"]["detected_language"] == "en"

    def test_extract_audio_metadata_minimal(self):
        """Test audio metadata with minimal information."""
        audio_doc = AudioDocument(
            file_path="/audio.wav",
            file_size=1024,
            duration=10.0,
            sample_rate=16000,
            channels=1,
            format="wav",
        )

        result = extract_audio_metadata(audio_doc, 0.5, "tiny", None, None, {}, {})

        assert result["processing"]["model_version"] == "tiny"
        assert result["source"]["detected_language"] == "unavailable"
        assert result["source"]["language_confidence"] == "unavailable"

    def test_metadata_structure_consistency(self):
        """Test metadata structure is consistent."""
        audio_doc = AudioDocument(
            file_path="/test.mp3",
            file_size=1000,
            duration=5.0,
            sample_rate=44100,
            channels=2,
            format="mp3",
        )

        result = extract_audio_metadata(audio_doc, 1.0, "model", None, None, {}, {})

        required_sections = ["processing", "configuration", "source"]
        for section in required_sections:
            assert section in result
            assert isinstance(result[section], dict)

    def test_language_confidence_boundary_values(self):
        """Test language confidence with boundary values."""
        audio_doc = AudioDocument(
            file_path="/test.mp3",
            file_size=1000,
            duration=5.0,
            sample_rate=44100,
            channels=2,
            format="mp3",
        )

        result_min = extract_audio_metadata(audio_doc, 1.0, "model", "en", 0.0, {}, {})
        assert result_min["source"]["language_confidence"] == 0.0

        result_max = extract_audio_metadata(audio_doc, 1.0, "model", "en", 1.0, {}, {})
        assert result_max["source"]["language_confidence"] == 1.0
