"""Contract tests for Audio processor metadata structure."""

import pytest


class TestTranscriptionResultMetadata:
    """Test TranscriptionResult metadata field contract."""

    def test_transcription_result_has_metadata_field(self):
        from anyfile_to_ai.audio_processor.models import TranscriptionResult

        result = TranscriptionResult(
            audio_path="test.mp3",
            text="test transcription",
            confidence_score=0.95,
            processing_time=15.0,
            model_used="medium",
            quantization="none",
            detected_language="en",
            success=True,
            error_message=None,
        )
        assert hasattr(result, "metadata"), "TranscriptionResult must have metadata field"

    def test_metadata_is_optional_dict_or_none(self):
        from anyfile_to_ai.audio_processor.models import TranscriptionResult

        result_without = TranscriptionResult(
            audio_path="test.mp3",
            text="test",
            confidence_score=None,
            processing_time=1.0,
            model_used="medium",
            quantization="none",
            detected_language=None,
            success=True,
            error_message=None,
        )
        assert result_without.metadata is None

        metadata = {
            "processing": {
                "timestamp": "2025-10-25T14:40:00+00:00",
                "model_version": "lightning-whisper-mlx-medium",
                "processing_time_seconds": 15.3,
            },
            "configuration": {
                "user_provided": {"model": "medium", "language": "en"},
                "effective": {
                    "model": "medium",
                    "language": "en",
                    "quantization": "none",
                    "batch_size": 12,
                },
            },
            "source": {
                "file_path": "podcast.mp3",
                "file_size_bytes": 5242880,
                "duration_seconds": 180.5,
                "sample_rate_hz": 44100,
                "channels": 2,
                "format": "mp3",
                "detected_language": "en",
                "language_confidence": 0.95,
            },
        }
        result_with = TranscriptionResult(
            audio_path="podcast.mp3",
            text="test",
            confidence_score=0.95,
            processing_time=15.3,
            model_used="medium",
            quantization="none",
            detected_language="en",
            success=True,
            error_message=None,
            metadata=metadata,
        )
        assert result_with.metadata == metadata

    def test_metadata_includes_language_confidence(self):
        from anyfile_to_ai.audio_processor.models import TranscriptionResult

        metadata = {
            "processing": {
                "timestamp": "2025-10-25T14:40:00+00:00",
                "model_version": "lightning-whisper-mlx-medium",
                "processing_time_seconds": 15.3,
            },
            "configuration": {"user_provided": {}, "effective": {}},
            "source": {
                "file_path": "audio.mp3",
                "file_size_bytes": 5242880,
                "duration_seconds": 180.5,
                "sample_rate_hz": 44100,
                "channels": 2,
                "format": "mp3",
                "detected_language": "en",
                "language_confidence": 0.95,
            },
        }

        result = TranscriptionResult(
            audio_path="audio.mp3",
            text="Transcribed text",
            confidence_score=0.95,
            processing_time=15.3,
            model_used="medium",
            quantization="none",
            detected_language="en",
            success=True,
            error_message=None,
            metadata=metadata,
        )

        assert result.metadata["source"]["detected_language"] == "en"
        assert result.metadata["source"]["language_confidence"] == 0.95
        assert result.metadata["source"]["duration_seconds"] == 180.5

    def test_metadata_language_confidence_unavailable_when_user_specified(self):
        from anyfile_to_ai.audio_processor.models import TranscriptionResult

        metadata = {
            "processing": {
                "timestamp": "2025-10-25T14:40:00+00:00",
                "model_version": "lightning-whisper-mlx-medium",
                "processing_time_seconds": 10.0,
            },
            "configuration": {"user_provided": {"language": "es"}, "effective": {}},
            "source": {
                "file_path": "audio.mp3",
                "file_size_bytes": 5242880,
                "duration_seconds": 120.0,
                "sample_rate_hz": 44100,
                "channels": 2,
                "format": "mp3",
                "detected_language": "es",
                "language_confidence": "unavailable",
            },
        }

        result = TranscriptionResult(
            audio_path="audio.mp3",
            text="Texto transcrito",
            confidence_score=None,
            processing_time=10.0,
            model_used="medium",
            quantization="none",
            detected_language="es",
            success=True,
            error_message=None,
            metadata=metadata,
        )

        assert result.metadata["source"]["language_confidence"] == "unavailable"
