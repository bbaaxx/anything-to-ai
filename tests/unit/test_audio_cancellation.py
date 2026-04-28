"""Unit tests for audio processor cancellation support."""

from unittest.mock import MagicMock, patch

import pytest

from anyfile_to_ai.audio_processor.streaming import process_audio_batch
from anyfile_to_ai.audio_processor.models import TranscriptionConfig, TranscriptionResult
from anyfile_to_ai.audio_processor.exceptions import ValidationError
from anyfile_to_ai.progress_tracker import CancellationToken, OperationCancelledError


class TestAudioProcessorCancellation:
    """Tests for cancellation support in audio processor."""

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return TranscriptionConfig(model="test-model")

    @pytest.fixture
    def mock_result(self):
        """Create a mock transcription result."""
        return TranscriptionResult(
            audio_path="test.mp3",
            text="Test transcription",
            confidence_score=0.9,
            processing_time=0.1,
            model_used="test-model",
            quantization="int8",
            detected_language="en",
            success=True,
            error_message=None,
        )

    def test_batch_without_cancel_token(self, config, mock_result):
        """Test that batch processing works normally without cancel token."""
        file_paths = ["audio1.mp3", "audio2.mp3"]

        with patch("anyfile_to_ai.audio_processor.streaming.process_audio") as mock_process:
            mock_process.return_value = mock_result
            result = process_audio_batch(file_paths, config)

        assert result.success is True
        assert result.total_files == 2
        assert result.successful_count == 2

    def test_batch_with_cancel_token_not_cancelled(self, config, mock_result):
        """Test that batch processing works when token is not cancelled."""
        file_paths = ["audio1.mp3"]
        token = CancellationToken()  # Not cancelled

        with patch("anyfile_to_ai.audio_processor.streaming.process_audio") as mock_process:
            mock_process.return_value = mock_result
            result = process_audio_batch(file_paths, config, cancel_token=token)

        assert result.success is True
        assert result.successful_count == 1

    def test_batch_cancelled_before_start(self, config):
        """Test that cancellation before starting raises immediately."""
        file_paths = ["audio1.mp3", "audio2.mp3"]
        token = CancellationToken()
        token.cancel()  # Cancel before processing

        with patch("anyfile_to_ai.audio_processor.streaming.process_audio") as mock_process:
            with pytest.raises(OperationCancelledError) as exc_info:
                process_audio_batch(file_paths, config, cancel_token=token)

        assert "file 1" in str(exc_info.value).lower()
        mock_process.assert_not_called()  # Should not have processed any files

    def test_batch_cancelled_during_iteration(self, config, mock_result):
        """Test that cancellation during iteration stops processing."""
        file_paths = ["audio1.mp3", "audio2.mp3", "audio3.mp3"]
        token = CancellationToken()

        call_count = 0

        def track_calls(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                token.cancel()
            return mock_result

        with patch("anyfile_to_ai.audio_processor.streaming.process_audio") as mock_process:
            mock_process.side_effect = track_calls
            with pytest.raises(OperationCancelledError):
                process_audio_batch(file_paths, config, cancel_token=token)

        # Should have processed at least 1 file before cancellation
        assert call_count >= 1

    def test_batch_empty_file_paths_raises_validation_error(self, config):
        """Test that empty file paths raises ValidationError."""
        with pytest.raises(ValidationError):
            process_audio_batch([], config)

    def test_batch_empty_file_paths_with_cancel_token(self, config):
        """Test that empty file paths raises ValidationError even with cancel token."""
        token = CancellationToken()
        with pytest.raises(ValidationError):
            process_audio_batch([], config, cancel_token=token)

    def test_batch_preserves_other_exceptions(self, config):
        """Test that non-cancellation exceptions are preserved."""
        file_paths = ["audio1.mp3"]

        with patch("anyfile_to_ai.audio_processor.streaming.process_audio") as mock_process:
            mock_process.side_effect = RuntimeError("Processing error")
            result = process_audio_batch(file_paths, config)

        # Should return failed result, not raise
        assert result.success is False
        assert result.failed_count == 1

    def test_batch_with_failed_results(self, config):
        """Test that batch handles failed results correctly."""
        file_paths = ["audio1.mp3", "audio2.mp3"]

        failed_result = TranscriptionResult(
            audio_path="audio1.mp3",
            text="",
            confidence_score=None,
            processing_time=0.0,
            model_used="test-model",
            quantization="int8",
            detected_language=None,
            success=False,
            error_message="Processing failed",
        )

        success_result = TranscriptionResult(
            audio_path="audio2.mp3",
            text="Success",
            confidence_score=0.9,
            processing_time=0.1,
            model_used="test-model",
            quantization="int8",
            detected_language="en",
            success=True,
            error_message=None,
        )

        with patch("anyfile_to_ai.audio_processor.streaming.process_audio") as mock_process:
            mock_process.side_effect = [failed_result, success_result]
            result = process_audio_batch(file_paths, config)

        assert result.success is True
        assert result.successful_count == 1
        assert result.failed_count == 1

    def test_batch_cancel_token_none_works(self, config, mock_result):
        """Test that passing None as cancel_token works."""
        file_paths = ["audio1.mp3"]

        with patch("anyfile_to_ai.audio_processor.streaming.process_audio") as mock_process:
            mock_process.return_value = mock_result
            result = process_audio_batch(file_paths, config, cancel_token=None)

        assert result.success is True

    def test_batch_with_default_config(self, mock_result):
        """Test that batch works with default config."""
        file_paths = ["audio1.mp3"]

        with patch("anyfile_to_ai.audio_processor.streaming.process_audio") as mock_process:
            mock_process.return_value = mock_result
            result = process_audio_batch(file_paths)  # No config

        assert result.success is True
