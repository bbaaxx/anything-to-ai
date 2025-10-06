"""
Integration tests for error handling workflows.
Tests FR-010, FR-023: Error detection and handling.
"""

import pytest


class TestAudioErrorWorkflows:
    """Test error handling in various scenarios."""

    def test_file_not_found_error(self):
        """Test handling of non-existent audio file."""
        import anyfile_to_ai.audio_processor
        from anyfile_to_ai.audio_processor import AudioNotFoundError

        config = audio_processor.create_config()

        with pytest.raises(AudioNotFoundError) as exc_info:
            audio_processor.process_audio("nonexistent.mp3", config)

        assert "nonexistent.mp3" in str(exc_info.value)

    def test_unsupported_format_error(self):
        """Test handling of unsupported audio format."""
        pytest.skip("Test file not available yet")
        import anyfile_to_ai.audio_processor
        from anyfile_to_ai.audio_processor import UnsupportedFormatError

        config = audio_processor.create_config()

        with pytest.raises(UnsupportedFormatError):
            audio_processor.process_audio("sample-data/audio/test.ogg", config)

    def test_no_speech_detected_error(self):
        """Test handling of audio file with no speech."""
        pytest.skip("Test audio file not available yet")
        import anyfile_to_ai.audio_processor
        from anyfile_to_ai.audio_processor import NoSpeechDetectedError

        config = audio_processor.create_config()

        with pytest.raises(NoSpeechDetectedError) as exc_info:
            audio_processor.process_audio("sample-data/audio/silence.wav", config)

        assert "no speech" in str(exc_info.value).lower()

    def test_duration_exceeded_error(self):
        """Test handling of audio file exceeding 2-hour limit."""
        pytest.skip("Test audio file not available yet")
        import anyfile_to_ai.audio_processor
        from anyfile_to_ai.audio_processor import DurationExceededError

        config = audio_processor.create_config()

        with pytest.raises(DurationExceededError) as exc_info:
            audio_processor.process_audio("sample-data/audio/long-audio.mp3", config)

        assert "2-hour" in str(exc_info.value) or "7200" in str(exc_info.value)

    def test_validate_audio_file_not_found(self):
        """Test validation with non-existent file."""
        import anyfile_to_ai.audio_processor
        from anyfile_to_ai.audio_processor import AudioNotFoundError

        with pytest.raises(AudioNotFoundError):
            audio_processor.validate_audio("nonexistent.mp3")

    def test_batch_process_continues_after_error(self):
        """Test that batch processing continues after individual file error."""
        pytest.skip("Test audio files not available yet")
        import anyfile_to_ai.audio_processor

        # Mix valid and invalid files
        files = [
            "sample-data/audio/speech.mp3",
            "nonexistent.mp3",
            "sample-data/audio/spanish.m4a"
        ]

        config = audio_processor.create_config()
        result = audio_processor.process_audio_batch(files, config)

        # Should process all files despite errors
        assert result.total_files == 3
        assert result.successful_count == 2
        assert result.failed_count == 1

        # Failed file should have error in result
        failed_results = [r for r in result.results if not r.success]
        assert len(failed_results) == 1
        assert failed_results[0].error_message is not None
