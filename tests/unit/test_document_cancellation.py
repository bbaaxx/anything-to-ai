"""Unit tests for document converter cancellation support."""

from unittest.mock import MagicMock, patch

import pytest

from anyfile_to_ai.document_converter.converter import convert_document
from anyfile_to_ai.document_converter.models import ConversionRoute, ConversionResult
from anyfile_to_ai.document_converter.exceptions import DocumentConversionError
from anyfile_to_ai.progress_tracker import CancellationToken, OperationCancelledError


class TestDocumentConverterCancellation:
    """Tests for cancellation support in document converter."""

    def test_convert_without_cancel_token(self):
        """Test that conversion works normally without cancel token."""
        with patch("anyfile_to_ai.document_converter.converter.determine_route") as mock_route:
            with patch("anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor") as mock_convert:
                mock_route.return_value = ConversionRoute.PDF
                mock_convert.return_value = ConversionResult(
                    source="test.pdf",
                    route=ConversionRoute.PDF,
                    content="Test content",
                    metadata={},
                )
                result = convert_document("test.pdf")

        assert result.content == "Test content"

    def test_convert_with_cancel_token_not_cancelled(self):
        """Test that conversion works when token is not cancelled."""
        token = CancellationToken()  # Not cancelled

        with patch("anyfile_to_ai.document_converter.converter.determine_route") as mock_route:
            with patch("anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor") as mock_convert:
                mock_route.return_value = ConversionRoute.PDF
                mock_convert.return_value = ConversionResult(
                    source="test.pdf",
                    route=ConversionRoute.PDF,
                    content="Test content",
                    metadata={},
                )
                result = convert_document("test.pdf", cancel_token=token)

        assert result.content == "Test content"

    def test_convert_cancelled_before_start(self):
        """Test that cancellation before starting raises immediately."""
        token = CancellationToken()
        token.cancel()  # Cancel before processing

        with patch("anyfile_to_ai.document_converter.converter.determine_route") as mock_route:
            with pytest.raises(OperationCancelledError) as exc_info:
                convert_document("test.pdf", cancel_token=token)

        assert "cancelled" in str(exc_info.value).lower()
        mock_route.assert_not_called()  # Should not have determined route

    def test_convert_preserves_other_exceptions(self):
        """Test that non-cancellation exceptions are preserved."""
        with patch("anyfile_to_ai.document_converter.converter.determine_route") as mock_route:
            with patch("anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor") as mock_convert:
                mock_route.return_value = ConversionRoute.PDF
                mock_convert.side_effect = DocumentConversionError("Conversion failed")

                with pytest.raises(DocumentConversionError):
                    convert_document("test.pdf")

    def test_convert_with_image_route(self):
        """Test that cancellation works with image route."""
        token = CancellationToken()

        with patch("anyfile_to_ai.document_converter.converter.determine_route") as mock_route:
            with patch("anyfile_to_ai.document_converter.converter._convert_with_image_processor") as mock_convert:
                mock_route.return_value = ConversionRoute.IMAGE
                mock_convert.return_value = ConversionResult(
                    source="test.jpg",
                    route=ConversionRoute.IMAGE,
                    content="Image description",
                    metadata={},
                )
                result = convert_document("test.jpg", cancel_token=token)

        assert result.content == "Image description"

    def test_convert_with_audio_route(self):
        """Test that cancellation works with audio route."""
        token = CancellationToken()

        with patch("anyfile_to_ai.document_converter.converter.determine_route") as mock_route:
            with patch("anyfile_to_ai.document_converter.converter._convert_with_audio_processor") as mock_convert:
                mock_route.return_value = ConversionRoute.AUDIO
                mock_convert.return_value = ConversionResult(
                    source="test.mp3",
                    route=ConversionRoute.AUDIO,
                    content="Audio transcription",
                    metadata={},
                )
                result = convert_document("test.mp3", cancel_token=token)

        assert result.content == "Audio transcription"

    def test_convert_with_markitdown_route(self):
        """Test that cancellation works with markitdown route."""
        token = CancellationToken()

        with patch("anyfile_to_ai.document_converter.converter.determine_route") as mock_route:
            with patch("anyfile_to_ai.document_converter.converter._convert_with_markitdown") as mock_convert:
                mock_route.return_value = ConversionRoute.MARKITDOWN
                mock_convert.return_value = ConversionResult(
                    source="test.docx",
                    route=ConversionRoute.MARKITDOWN,
                    content="Markdown content",
                    metadata={},
                )
                result = convert_document("test.docx", cancel_token=token)

        assert result.content == "Markdown content"

    def test_convert_cancelled_re_raises_without_wrapping(self):
        """Test that OperationCancelledError is re-raised without wrapping."""
        token = CancellationToken()
        token.cancel()

        with pytest.raises(OperationCancelledError):
            convert_document("test.pdf", cancel_token=token)

    def test_convert_with_include_metadata(self):
        """Test that include_metadata works with cancel_token."""
        token = CancellationToken()

        with patch("anyfile_to_ai.document_converter.converter.determine_route") as mock_route:
            with patch("anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor") as mock_convert:
                mock_route.return_value = ConversionRoute.PDF
                mock_convert.return_value = ConversionResult(
                    source="test.pdf",
                    route=ConversionRoute.PDF,
                    content="Test content",
                    metadata={"pages": 1},
                )
                result = convert_document("test.pdf", include_metadata=True, cancel_token=token)

        assert result.content == "Test content"
        mock_convert.assert_called_once()

    def test_convert_cancel_token_none_works(self):
        """Test that passing None as cancel_token works."""
        with patch("anyfile_to_ai.document_converter.converter.determine_route") as mock_route:
            with patch("anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor") as mock_convert:
                mock_route.return_value = ConversionRoute.PDF
                mock_convert.return_value = ConversionResult(
                    source="test.pdf",
                    route=ConversionRoute.PDF,
                    content="Test content",
                    metadata={},
                )
                result = convert_document("test.pdf", cancel_token=None)

        assert result.content == "Test content"
