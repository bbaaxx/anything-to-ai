"""Integration test for Audio language confidence workflow."""

import json
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest


class TestAudioMetadataIntegration:
    """End-to-end tests for audio processing with metadata."""

    def test_audio_processing_with_language_confidence(self, tmp_path):
        """Test audio processing captures language confidence."""
        from anyfile_to_ai.audio_processor.processor import process_audio
        from anyfile_to_ai.audio_processor.models import AudioDocument

        test_audio = tmp_path / "test.mp3"
        test_audio.write_bytes(b"fake mp3 data")

        mock_audio_doc = AudioDocument(
            file_path=str(test_audio),
            file_size=1024,
            duration=60.0,
            sample_rate=44100,
            channels=2,
            format="mp3",
        )

        with patch("anyfile_to_ai.audio_processor.processor.validate_audio") as mock_validate:
            mock_validate.return_value = mock_audio_doc

            with patch("anyfile_to_ai.audio_processor.processor.transcribe_audio") as mock_transcribe:
                mock_transcribe.return_value = MagicMock(text="Sample transcription", segments=[], language="en", language_probability=0.95)

                from anyfile_to_ai.audio_processor.models import TranscriptionConfig

                config = TranscriptionConfig(model="medium", language="en")
                result = process_audio(str(test_audio), config=config, include_metadata=True)

                assert result.success is True
                assert result.metadata is not None
                assert result.metadata["source"]["detected_language"] == "en"
                assert result.metadata["source"]["language_confidence"] == 0.95

    def test_audio_processing_without_metadata(self, tmp_path):
        """Test audio processing with metadata disabled."""
        from anyfile_to_ai.audio_processor.processor import process_audio
        from anyfile_to_ai.audio_processor.models import AudioDocument

        test_audio = tmp_path / "test.wav"
        test_audio.write_bytes(b"fake wav data")

        mock_audio_doc = AudioDocument(file_path=str(test_audio), file_size=2048, duration=30.0, sample_rate=16000, channels=1, format="wav")

        with patch("anyfile_to_ai.audio_processor.processor.validate_audio") as mock_validate:
            mock_validate.return_value = mock_audio_doc

            with patch("anyfile_to_ai.audio_processor.processor.transcribe_audio") as mock_transcribe:
                mock_transcribe.return_value = MagicMock(text="Transcription", segments=[], language=None, language_probability=None)

                result = process_audio(str(test_audio), include_metadata=False)

                assert result.success is True
                assert result.metadata is None

    def test_audio_metadata_unavailable_language(self, tmp_path):
        """Test audio metadata when language detection unavailable."""
        from anyfile_to_ai.audio_processor.processor import process_audio
        from anyfile_to_ai.audio_processor.models import AudioDocument

        test_audio = tmp_path / "test.m4a"
        test_audio.write_bytes(b"fake m4a data")

        mock_audio_doc = AudioDocument(file_path=str(test_audio), file_size=512, duration=15.0, sample_rate=44100, channels=2, format="m4a")

        with patch("anyfile_to_ai.audio_processor.processor.validate_audio") as mock_validate:
            mock_validate.return_value = mock_audio_doc

            with patch("anyfile_to_ai.audio_processor.processor.transcribe_audio") as mock_transcribe:
                mock_transcribe.return_value = MagicMock(text="Text", segments=[], language=None, language_probability=None)

                result = process_audio(str(test_audio), include_metadata=True)

                assert result.metadata is not None
                assert result.metadata["source"]["detected_language"] == "unavailable"
                assert result.metadata["source"]["language_confidence"] == "unavailable"
