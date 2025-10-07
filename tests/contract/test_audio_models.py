"""
Contract tests for audio_processor data models.
Tests FR-001, FR-003, FR-012: Data model classes.
"""

from dataclasses import fields


class TestAudioModelsContract:
    """Test that all required data model classes exist with correct fields."""

    def test_audio_document_class_exists(self):
        """Test that AudioDocument class exists."""
        from anyfile_to_ai.audio_processor import AudioDocument

        assert AudioDocument is not None

    def test_audio_document_fields(self):
        """Test that AudioDocument has required fields."""
        from anyfile_to_ai.audio_processor import AudioDocument

        field_names = [f.name for f in fields(AudioDocument)]
        expected_fields = [
            "file_path",
            "format",
            "duration",
            "sample_rate",
            "file_size",
            "channels",
        ]
        for field in expected_fields:
            assert field in field_names, f"Missing field: {field}"

    def test_transcription_result_class_exists(self):
        """Test that TranscriptionResult class exists."""
        from anyfile_to_ai.audio_processor import TranscriptionResult

        assert TranscriptionResult is not None

    def test_transcription_result_fields(self):
        """Test that TranscriptionResult has required fields."""
        from anyfile_to_ai.audio_processor import TranscriptionResult

        field_names = [f.name for f in fields(TranscriptionResult)]
        expected_fields = [
            "audio_path",
            "text",
            "confidence_score",
            "processing_time",
            "model_used",
            "quantization",
            "detected_language",
            "success",
            "error_message",
        ]
        for field in expected_fields:
            assert field in field_names, f"Missing field: {field}"

    def test_transcription_config_class_exists(self):
        """Test that TranscriptionConfig class exists."""
        from anyfile_to_ai.audio_processor import TranscriptionConfig

        assert TranscriptionConfig is not None

    def test_transcription_config_fields(self):
        """Test that TranscriptionConfig has required fields."""
        from anyfile_to_ai.audio_processor import TranscriptionConfig

        field_names = [f.name for f in fields(TranscriptionConfig)]
        expected_fields = [
            "model",
            "quantization",
            "batch_size",
            "language",
            "output_format",
            "timeout_seconds",
            "progress_callback",
            "verbose",
            "max_duration_seconds",
        ]
        for field in expected_fields:
            assert field in field_names, f"Missing field: {field}"

    def test_processing_result_class_exists(self):
        """Test that ProcessingResult class exists."""
        from anyfile_to_ai.audio_processor import ProcessingResult

        assert ProcessingResult is not None

    def test_processing_result_fields(self):
        """Test that ProcessingResult has required fields."""
        from anyfile_to_ai.audio_processor import ProcessingResult

        field_names = [f.name for f in fields(ProcessingResult)]
        expected_fields = [
            "success",
            "results",
            "total_files",
            "successful_count",
            "failed_count",
            "total_processing_time",
            "average_processing_time",
            "error_summary",
        ]
        for field in expected_fields:
            assert field in field_names, f"Missing field: {field}"

    def test_audio_document_instantiation(self):
        """Test that AudioDocument can be instantiated."""
        from anyfile_to_ai.audio_processor import AudioDocument

        doc = AudioDocument(
            file_path="/path/to/audio.mp3",
            format="mp3",
            duration=120.5,
            sample_rate=44100,
            file_size=1024000,
            channels=2,
        )
        assert doc.file_path == "/path/to/audio.mp3"
        assert doc.format == "mp3"
        assert doc.duration == 120.5

    def test_transcription_result_instantiation(self):
        """Test that TranscriptionResult can be instantiated."""
        from anyfile_to_ai.audio_processor import TranscriptionResult

        result = TranscriptionResult(
            audio_path="/path/to/audio.mp3",
            text="Test transcription",
            confidence_score=0.95,
            processing_time=10.5,
            model_used="medium",
            quantization="4bit",
            detected_language="en",
            success=True,
            error_message=None,
        )
        assert result.audio_path == "/path/to/audio.mp3"
        assert result.text == "Test transcription"
        assert result.success is True

    def test_transcription_config_instantiation(self):
        """Test that TranscriptionConfig can be instantiated."""
        from anyfile_to_ai.audio_processor import TranscriptionConfig

        config = TranscriptionConfig(
            model="medium",
            quantization="4bit",
            batch_size=12,
            language=None,
            output_format="plain",
            timeout_seconds=600,
            progress_callback=None,
            verbose=False,
            max_duration_seconds=7200,
        )
        assert config.model == "medium"
        assert config.quantization == "4bit"
        assert config.batch_size == 12

    def test_processing_result_instantiation(self):
        """Test that ProcessingResult can be instantiated."""
        from anyfile_to_ai.audio_processor import ProcessingResult

        result = ProcessingResult(
            success=True,
            results=[],
            total_files=0,
            successful_count=0,
            failed_count=0,
            total_processing_time=0.0,
            average_processing_time=0.0,
            error_summary=None,
        )
        assert result.success is True
        assert result.total_files == 0
