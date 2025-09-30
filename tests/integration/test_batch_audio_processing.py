"""
Integration tests for batch audio processing.
Tests FR-008, FR-009: Batch processing with progress callbacks.
"""

import pytest
from pathlib import Path


class TestBatchAudioProcessing:
    """Test batch processing multiple audio files."""

    @pytest.fixture
    def sample_audio_files(self):
        """List of sample audio files."""
        return [
            "sample-data/audio/speech.mp3",
            "sample-data/audio/spanish.m4a",
            "sample-data/audio/long.mp3"
        ]

    def test_batch_process_multiple_files(self, sample_audio_files):
        """Test batch processing multiple audio files."""
        pytest.skip("Test audio files not available yet")
        import audio_processor

        config = audio_processor.create_config()
        result = audio_processor.process_audio_batch(sample_audio_files, config)

        assert result.success is True
        assert result.total_files == 3
        assert result.successful_count >= 0
        assert result.failed_count >= 0
        assert result.successful_count + result.failed_count == result.total_files
        assert len(result.results) == 3
        assert result.total_processing_time > 0
        assert result.average_processing_time > 0

    def test_batch_process_with_progress_callback(self, sample_audio_files):
        """Test batch processing with progress callback."""
        pytest.skip("Test audio files not available yet")
        import audio_processor

        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        config = audio_processor.create_config(progress_callback=progress_callback)
        result = audio_processor.process_audio_batch(sample_audio_files, config)

        # Verify progress callback was called
        assert len(progress_calls) > 0
        # Verify final progress shows completion
        final_call = progress_calls[-1]
        assert final_call[0] == final_call[1]  # current == total

    def test_batch_process_empty_list(self):
        """Test batch processing with empty file list."""
        import audio_processor
        from audio_processor import ValidationError

        config = audio_processor.create_config()

        with pytest.raises(ValidationError):
            audio_processor.process_audio_batch([], config)

    def test_batch_process_handles_mixed_success_failure(self):
        """Test batch processing with mix of successful and failed files."""
        pytest.skip("Test audio files not available yet")
        import audio_processor

        # Include non-existent file
        files = [
            "sample-data/audio/speech.mp3",
            "sample-data/audio/nonexistent.mp3",
            "sample-data/audio/spanish.m4a"
        ]

        config = audio_processor.create_config()
        result = audio_processor.process_audio_batch(files, config)

        # Should have some successes and some failures
        assert result.total_files == 3
        assert result.successful_count > 0
        assert result.failed_count > 0
        assert result.error_summary is not None