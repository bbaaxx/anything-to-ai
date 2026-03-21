"""Unit tests for image processor cancellation support."""

from unittest.mock import MagicMock, patch

import pytest

from anyfile_to_ai.image_processor.streaming import StreamingProcessor
from anyfile_to_ai.image_processor.models import ProcessingConfig, DescriptionResult
from anyfile_to_ai.image_processor.exceptions import ValidationError
from anyfile_to_ai.progress_tracker import CancellationToken, OperationCancelledError


class TestImageProcessorCancellation:
    """Tests for cancellation support in image processor."""

    @pytest.fixture
    def mock_processor(self):
        """Create a mock processor for testing."""
        processor = MagicMock()
        processor.validate_image.return_value = MagicMock()
        processor.process_single_image.return_value = DescriptionResult(
            image_path="test.jpg",
            description="Test description",
            confidence_score=0.9,
            processing_time=0.1,
            model_used="test-model",
            prompt_used="test-prompt",
            success=True,
        )
        return processor

    @pytest.fixture
    def config(self):
        """Create a test configuration."""
        return ProcessingConfig()

    def test_batch_without_cancel_token(self, mock_processor, config):
        """Test that batch processing works normally without cancel token."""
        streaming = StreamingProcessor(mock_processor)
        file_paths = ["image1.jpg", "image2.jpg"]

        with patch.object(streaming, "vlm_processor") as mock_vlm:
            mock_vlm.cleanup = MagicMock()
            result = streaming.process_batch(file_paths, config)

        assert result.success is True
        assert result.total_images == 2
        assert result.successful_count == 2

    def test_batch_with_cancel_token_not_cancelled(self, mock_processor, config):
        """Test that batch processing works when token is not cancelled."""
        streaming = StreamingProcessor(mock_processor)
        file_paths = ["image1.jpg"]
        token = CancellationToken()  # Not cancelled

        with patch.object(streaming, "vlm_processor") as mock_vlm:
            mock_vlm.cleanup = MagicMock()
            result = streaming.process_batch(file_paths, config, cancel_token=token)

        assert result.success is True
        assert result.successful_count == 1

    def test_batch_cancelled_before_start(self, mock_processor, config):
        """Test that cancellation before starting raises immediately."""
        streaming = StreamingProcessor(mock_processor)
        file_paths = ["image1.jpg", "image2.jpg"]
        token = CancellationToken()
        token.cancel()  # Cancel before processing

        with patch.object(streaming, "vlm_processor") as mock_vlm:
            mock_vlm.cleanup = MagicMock()
            with pytest.raises(OperationCancelledError) as exc_info:
                streaming.process_batch(file_paths, config, cancel_token=token)

        assert "image 1" in str(exc_info.value).lower()
        mock_vlm.cleanup.assert_called()  # Cleanup should be called

    def test_batch_cancelled_during_iteration(self, mock_processor, config):
        """Test that cancellation during iteration stops processing."""
        streaming = StreamingProcessor(mock_processor)
        file_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]
        token = CancellationToken()

        call_count = 0
        original_process = mock_processor.process_single_image

        def track_calls(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 2:
                token.cancel()
            return original_process(*args, **kwargs)

        mock_processor.process_single_image = track_calls

        with patch.object(streaming, "vlm_processor") as mock_vlm:
            mock_vlm.cleanup = MagicMock()
            with pytest.raises(OperationCancelledError):
                streaming.process_batch(file_paths, config, cancel_token=token)

        # Should have processed at least 1 image before cancellation
        assert call_count >= 1
        mock_vlm.cleanup.assert_called()  # Cleanup should be called

    def test_streaming_without_cancel_token(self, mock_processor, config):
        """Test that streaming works normally without cancel token."""
        streaming = StreamingProcessor(mock_processor)
        file_paths = ["image1.jpg", "image2.jpg"]

        with patch.object(streaming, "vlm_processor") as mock_vlm:
            mock_vlm.cleanup = MagicMock()
            results = list(streaming.process_streaming(file_paths, config))

        assert len(results) == 2
        assert all(r.success for r in results)

    def test_streaming_cancelled_before_start(self, mock_processor, config):
        """Test that streaming cancellation before starting raises immediately."""
        streaming = StreamingProcessor(mock_processor)
        file_paths = ["image1.jpg"]
        token = CancellationToken()
        token.cancel()

        with patch.object(streaming, "vlm_processor") as mock_vlm:
            mock_vlm.cleanup = MagicMock()
            with pytest.raises(OperationCancelledError) as exc_info:
                list(streaming.process_streaming(file_paths, config, cancel_token=token))

        assert "image 1" in str(exc_info.value).lower()

    def test_streaming_cancelled_during_iteration(self, mock_processor, config):
        """Test that streaming cancellation during iteration stops processing."""
        streaming = StreamingProcessor(mock_processor)
        file_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]
        token = CancellationToken()

        results = []
        call_count = 0

        def track_streaming(*args, **kwargs):
            nonlocal call_count
            for result in streaming.process_streaming.__wrapped__(streaming, file_paths, config, cancel_token=token):
                call_count += 1
                if call_count == 2:
                    token.cancel()
                results.append(result)
                yield result

        # This is a simplified test - in practice, cancellation would be checked
        # at each iteration boundary
        with patch.object(streaming, "vlm_processor") as mock_vlm:
            mock_vlm.cleanup = MagicMock()
            with pytest.raises(OperationCancelledError):
                for result in streaming.process_streaming(file_paths, config, cancel_token=token):
                    results.append(result)
                    if len(results) == 2:
                        token.cancel()

    def test_batch_preserves_other_exceptions(self, mock_processor, config):
        """Test that non-cancellation exceptions are preserved."""
        streaming = StreamingProcessor(mock_processor)
        file_paths = []  # Empty list should raise ValidationError

        with pytest.raises(ValidationError):
            streaming.process_batch(file_paths, config)

    def test_streaming_preserves_other_exceptions(self, mock_processor, config):
        """Test that streaming preserves non-cancellation exceptions."""
        streaming = StreamingProcessor(mock_processor)
        file_paths = []  # Empty list should raise ValidationError

        with pytest.raises(ValidationError):
            list(streaming.process_streaming(file_paths, config))

    def test_cleanup_on_successful_batch(self, mock_processor, config):
        """Test that VLM cleanup is called on successful batch."""
        streaming = StreamingProcessor(mock_processor)
        file_paths = ["image1.jpg"]

        with patch.object(streaming, "vlm_processor") as mock_vlm:
            mock_vlm.cleanup = MagicMock()
            streaming.process_batch(file_paths, config)

        mock_vlm.cleanup.assert_called_once()

    def test_cleanup_on_cancelled_batch(self, mock_processor, config):
        """Test that VLM cleanup is called on cancelled batch."""
        streaming = StreamingProcessor(mock_processor)
        file_paths = ["image1.jpg"]
        token = CancellationToken()
        token.cancel()

        with patch.object(streaming, "vlm_processor") as mock_vlm:
            mock_vlm.cleanup = MagicMock()
            with pytest.raises(OperationCancelledError):
                streaming.process_batch(file_paths, config, cancel_token=token)

        mock_vlm.cleanup.assert_called()
