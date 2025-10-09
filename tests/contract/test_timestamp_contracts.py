"""
Contract tests for timestamp support feature.

Tests the API contracts for TranscriptionSegment, timestamp extraction,
CLI parsing, and formatting functions.
"""

import pytest
from dataclasses import is_dataclass, fields
from anyfile_to_ai.audio_processor.models import TranscriptionResult
from anyfile_to_ai.audio_processor.config import create_config


class TestTranscriptionSegmentModel:
    """Contract test for TranscriptionSegment dataclass."""

    def test_transcription_segment_model(self):
        """Test that TranscriptionSegment exists and has required fields."""
        # Import should work (will fail until implemented)
        from anyfile_to_ai.audio_processor.models import TranscriptionSegment

        # Must be a dataclass
        assert is_dataclass(TranscriptionSegment)

        # Must have exactly these fields with correct types
        field_dict = {f.name: f.type for f in fields(TranscriptionSegment)}
        assert "start" in field_dict
        assert "end" in field_dict
        assert "text" in field_dict

        # Validate types
        assert field_dict["start"] == float
        assert field_dict["end"] == float
        assert field_dict["text"] == str

        # Test instantiation
        segment = TranscriptionSegment(start=0.0, end=5.23, text="Test segment")
        assert segment.start == 0.0
        assert segment.end == 5.23
        assert segment.text == "Test segment"

        # Test validation: end > start
        assert segment.end > segment.start


class TestTranscriptionResultSegments:
    """Contract test for TranscriptionResult.segments field."""

    def test_transcription_result_segments(self):
        """Test that TranscriptionResult has segments field."""
        from anyfile_to_ai.audio_processor.models import TranscriptionSegment

        # segments field must exist and be optional
        field_dict = {f.name: f for f in fields(TranscriptionResult)}
        assert "segments" in field_dict

        # Must be list[TranscriptionSegment] | None
        segments_field = field_dict["segments"]
        # Check that default is None (optional field)
        assert segments_field.default is None or segments_field.default_factory is not None

        # Test instantiation with segments
        segments = [
            TranscriptionSegment(start=0.0, end=5.0, text="First"),
            TranscriptionSegment(start=5.0, end=10.0, text="Second"),
        ]

        result = TranscriptionResult(
            audio_path="/test/audio.mp3",
            text="First Second",
            confidence_score=0.95,
            processing_time=1.0,
            model_used="medium",
            quantization="none",
            detected_language="en",
            success=True,
            error_message=None,
            segments=segments,
        )

        assert result.segments is not None
        assert len(result.segments) == 2
        assert result.segments[0].start == 0.0
        assert result.segments[1].end == 10.0

        # Test instantiation without segments (backward compatibility)
        result_no_segments = TranscriptionResult(
            audio_path="/test/audio.mp3",
            text="Test",
            confidence_score=0.95,
            processing_time=1.0,
            model_used="medium",
            quantization="none",
            detected_language="en",
            success=True,
            error_message=None,
        )

        assert result_no_segments.segments is None


class TestProcessAudioWithTimestamps:
    """Contract test for process_audio() with timestamps."""

    def test_process_audio_with_timestamps(self):
        """Test that process_audio returns segments when timestamps enabled."""
        from anyfile_to_ai.audio_processor.processor import process_audio
        from anyfile_to_ai.audio_processor.models import TranscriptionSegment

        # Create config with timestamps enabled
        config = create_config(
            model="tiny",  # Use tiny model for faster tests
            timestamps=True,
        )

        # Process a real audio file
        result = process_audio("sample-data/audio/podcast.mp3", config)

        # Must succeed
        assert result.success is True
        assert result.error_message is None

        # Must have segments (if audio has speech)
        if result.text.strip():  # Only check if there's actual transcription
            assert result.segments is not None
            assert isinstance(result.segments, list)

            # Each segment must be TranscriptionSegment
            for segment in result.segments:
                assert isinstance(segment, TranscriptionSegment)
                assert segment.start >= 0.0
                assert segment.end > segment.start
                assert isinstance(segment.text, str)
                assert len(segment.text) > 0

            # Segments must be in chronological order
            for i in range(len(result.segments) - 1):
                assert result.segments[i].end <= result.segments[i + 1].start

    def test_process_audio_without_timestamps(self):
        """Test that process_audio doesn't include segments when timestamps disabled."""
        from anyfile_to_ai.audio_processor.processor import process_audio

        # Create config with timestamps disabled (default)
        config = create_config(model="tiny")

        # Process audio file
        result = process_audio("sample-data/audio/podcast.mp3", config)

        # Must succeed
        assert result.success is True

        # Must NOT have segments
        assert result.segments is None


class TestCLITimestampsFlag:
    """Contract test for CLI --timestamps flag."""

    def test_cli_timestamps_flag(self):
        """Test that CLI parser accepts --timestamps flag."""
        from anyfile_to_ai.audio_processor.cli import create_cli_parser

        parser = create_cli_parser()

        # Parse with --timestamps flag
        args = parser.parse_args(
            ["sample-data/audio/podcast.mp3", "--timestamps", "--format", "json"],
        )

        # Must have timestamps attribute
        assert hasattr(args, "timestamps")
        assert args.timestamps is True

        # Parse without --timestamps flag
        args_no_ts = parser.parse_args(["sample-data/audio/podcast.mp3"])

        assert hasattr(args_no_ts, "timestamps")
        assert args_no_ts.timestamps is False


class TestFormatTimestampContract:
    """Contract test for format_timestamp() function."""

    def test_format_timestamp_contract(self):
        """Test that format_timestamp exists and returns HH:MM:SS.CC format."""
        from anyfile_to_ai.audio_processor.markdown_formatter import format_timestamp

        # Test basic functionality
        result = format_timestamp(0.0)
        assert result == "00:00:00.00"

        result = format_timestamp(5.23)
        assert result == "00:00:05.23"

        result = format_timestamp(65.45)
        assert result == "00:01:05.45"

        result = format_timestamp(3661.12)
        assert result == "01:01:01.12"

        # Test format structure
        import re

        pattern = r"^\d{2}:\d{2}:\d{2}\.\d{2}$"
        assert re.match(pattern, format_timestamp(123.45))

        # Test rounding to centiseconds
        result = format_timestamp(5.234)  # Should round to 5.23
        assert result in ["00:00:05.23", "00:00:05.24"]  # Allow for rounding

        # Test error handling
        with pytest.raises(ValueError):
            format_timestamp(-1.0)  # Negative time

        with pytest.raises(ValueError):
            format_timestamp(7201.0)  # Exceeds max duration
