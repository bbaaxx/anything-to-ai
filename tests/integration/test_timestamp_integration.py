"""
Integration tests for timestamp support feature.

Tests end-to-end workflows including single file processing,
batch processing, and graceful degradation.
"""

from anyfile_to_ai.audio_processor.config import create_config
from anyfile_to_ai.audio_processor.processor import process_audio
from anyfile_to_ai.audio_processor.streaming import process_audio_batch
from anyfile_to_ai.audio_processor.models import TranscriptionSegment


class TestSingleAudioWithTimestamps:
    """Integration test for single audio file with timestamps."""

    def test_single_audio_with_timestamps(self):
        """Test processing single audio file with timestamps enabled."""
        # Create config with timestamps
        config = create_config(
            model="tiny",  # Fast model for testing
            timestamps=True,
            output_format="json",
        )

        # Process audio
        result = process_audio("sample-data/audio/podcast.mp3", config)

        # Validate result
        assert result.success is True
        assert result.segments is not None

        # Validate segments structure
        if len(result.segments) > 0:
            for segment in result.segments:
                assert isinstance(segment, TranscriptionSegment)
                assert segment.start >= 0.0
                assert segment.end > segment.start
                assert segment.end <= 7200.0  # Max audio duration (2 hours)

            # Validate chronological order
            for i in range(len(result.segments) - 1):
                assert result.segments[i].end <= result.segments[i + 1].start

            # Validate text consistency
            full_text = " ".join(seg.text for seg in result.segments)
            # Segments should contribute to the full text
            assert len(full_text) > 0

    def test_single_audio_markdown_format(self):
        """Test that markdown format includes timestamps."""
        config = create_config(
            model="tiny",
            timestamps=True,
            output_format="markdown",
        )

        result = process_audio("sample-data/audio/podcast.mp3", config)

        assert result.success is True
        assert result.segments is not None

        # Segments should be present for markdown formatting
        if result.segments and len(result.segments) > 0:
            # First segment should have valid timestamps
            first_seg = result.segments[0]
            assert first_seg.start >= 0.0
            assert first_seg.end > first_seg.start


class TestBatchWithTimestamps:
    """Integration test for batch processing with timestamps."""

    def test_batch_with_timestamps(self):
        """Test batch processing with timestamps enabled."""
        config = create_config(
            model="tiny",
            timestamps=True,
            batch_size=12,
        )

        # Process multiple files
        audio_files = [
            "sample-data/audio/podcast.mp3",
            "sample-data/audio/silence.mp3",
        ]

        result = process_audio_batch(audio_files, config)

        # Validate batch result
        assert result.success is True
        assert result.total_files == 2
        assert len(result.results) == 2

        # Check that successful results have segments
        for transcription in result.results:
            if transcription.success and transcription.text.strip():
                # Should have segments if there was speech
                assert hasattr(transcription, "segments")

    def test_batch_preserves_segment_ordering(self):
        """Test that batch processing preserves segment order per file."""
        config = create_config(model="tiny", timestamps=True)

        audio_files = ["sample-data/audio/podcast.mp3"]
        result = process_audio_batch(audio_files, config)

        assert result.success is True

        for transcription in result.results:
            if transcription.segments and len(transcription.segments) > 1:
                # Verify ordering
                for i in range(len(transcription.segments) - 1):
                    curr_seg = transcription.segments[i]
                    next_seg = transcription.segments[i + 1]
                    assert curr_seg.end <= next_seg.start


class TestGracefulDegradation:
    """Integration test for graceful degradation when timestamps unavailable."""

    def test_graceful_degradation(self):
        """Test that processing continues when timestamps are unavailable."""
        # Even with timestamps enabled, if they're unavailable, should continue
        config = create_config(
            model="tiny",
            timestamps=True,
        )

        # Process a file (even if segments are unavailable, should not fail)
        result = process_audio("sample-data/audio/silence.mp3", config)

        # Must succeed even if no segments
        assert result.success is True
        assert result.text is not None

        # segments can be None or empty list if no speech detected
        if result.segments is None:
            # This is acceptable - graceful degradation
            assert result.text is not None
        elif len(result.segments) == 0:
            # Empty list is also acceptable for silence
            assert result.text is not None or result.text == ""

    def test_timestamps_disabled_no_segments(self):
        """Test that disabling timestamps results in no segments."""
        config = create_config(
            model="tiny",
            timestamps=False,  # Explicitly disabled
        )

        result = process_audio("sample-data/audio/podcast.mp3", config)

        assert result.success is True
        assert result.segments is None  # Must be None when disabled

    def test_backward_compatibility(self):
        """Test that existing code without timestamps continues to work."""
        # Config without timestamps parameter (uses default)
        config = create_config(model="tiny", output_format="plain")

        result = process_audio("sample-data/audio/podcast.mp3", config)

        # Should work as before
        assert result.success is True
        assert result.text is not None
        assert result.segments is None  # Default is no timestamps
