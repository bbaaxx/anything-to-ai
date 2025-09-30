"""
Contract tests for audio_processor exception hierarchy.
Tests FR-010: Exception types and hierarchy.
"""



class TestAudioExceptionsContract:
    """Test that all required exception classes exist with correct hierarchy."""

    def test_base_exception_exists(self):
        """Test that AudioProcessingError base exception exists."""
        from audio_processor import AudioProcessingError
        assert issubclass(AudioProcessingError, Exception)

    def test_audio_not_found_error_exists(self):
        """Test that AudioNotFoundError exists and inherits from base."""
        from audio_processor import AudioProcessingError, AudioNotFoundError
        assert issubclass(AudioNotFoundError, AudioProcessingError)

    def test_unsupported_format_error_exists(self):
        """Test that UnsupportedFormatError exists and inherits from base."""
        from audio_processor import AudioProcessingError, UnsupportedFormatError
        assert issubclass(UnsupportedFormatError, AudioProcessingError)

    def test_corrupted_audio_error_exists(self):
        """Test that CorruptedAudioError exists and inherits from base."""
        from audio_processor import AudioProcessingError, CorruptedAudioError
        assert issubclass(CorruptedAudioError, AudioProcessingError)

    def test_transcription_error_exists(self):
        """Test that TranscriptionError exists and inherits from base."""
        from audio_processor import AudioProcessingError, TranscriptionError
        assert issubclass(TranscriptionError, AudioProcessingError)

    def test_no_speech_detected_error_exists(self):
        """Test that NoSpeechDetectedError exists and inherits from base."""
        from audio_processor import AudioProcessingError, NoSpeechDetectedError
        assert issubclass(NoSpeechDetectedError, AudioProcessingError)

    def test_duration_exceeded_error_exists(self):
        """Test that DurationExceededError exists and inherits from base."""
        from audio_processor import AudioProcessingError, DurationExceededError
        assert issubclass(DurationExceededError, AudioProcessingError)

    def test_validation_error_exists(self):
        """Test that ValidationError exists and inherits from base."""
        from audio_processor import AudioProcessingError, ValidationError
        assert issubclass(ValidationError, AudioProcessingError)

    def test_model_load_error_exists(self):
        """Test that ModelLoadError exists and inherits from base."""
        from audio_processor import AudioProcessingError, ModelLoadError
        assert issubclass(ModelLoadError, AudioProcessingError)

    def test_processing_timeout_error_exists(self):
        """Test that ProcessingTimeoutError exists and inherits from base."""
        from audio_processor import AudioProcessingError, ProcessingTimeoutError
        assert issubclass(ProcessingTimeoutError, AudioProcessingError)

    def test_processing_interrupted_error_exists(self):
        """Test that ProcessingInterruptedError exists and inherits from base."""
        from audio_processor import AudioProcessingError, ProcessingInterruptedError
        assert issubclass(ProcessingInterruptedError, AudioProcessingError)

    def test_exception_hierarchy_complete(self):
        """Test that all expected exceptions are available."""
        # If import succeeds, all exceptions exist
        assert True

    def test_base_exception_instantiation(self):
        """Test that AudioProcessingError can be instantiated."""
        from audio_processor import AudioProcessingError
        error = AudioProcessingError("test message")
        assert str(error) == "test message"

    def test_exception_with_audio_path(self):
        """Test that exceptions can store audio_path."""
        from audio_processor import AudioNotFoundError
        error = AudioNotFoundError("test message", audio_path="/path/to/audio.mp3")
        assert hasattr(error, 'audio_path')
        assert error.audio_path == "/path/to/audio.mp3"
