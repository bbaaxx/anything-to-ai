"""Integration test for metadata disabled (backward compatibility)."""

from unittest.mock import MagicMock, patch

import pytest


class TestMetadataBackwardCompatibility:
    """Tests ensuring metadata flag preserves backward compatibility."""

    def test_pdf_default_no_metadata(self, tmp_path):
        """Test PDF extraction defaults to no metadata (backward compatible)."""
        from anyfile_to_ai.pdf_extractor.reader import extract_text

        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"pdf data")

        with patch("pdfplumber.open") as mock_pdf_open:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Text"

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.metadata = {}
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf_open.return_value = mock_pdf

            result = extract_text(str(test_pdf))

            assert result.success is True
            assert result.metadata is None

    def test_image_default_no_metadata(self, tmp_path):
        """Test image processing defaults to no metadata."""
        from anyfile_to_ai.image_processor import process_image
        from anyfile_to_ai.image_processor.models import DescriptionResult

        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"jpeg data")

        mock_result = DescriptionResult(
            image_path=str(test_image),
            description="Image",
            confidence_score=0.9,
            processing_time=0.1,
            model_used="mock-model",
            prompt_used="Describe this image in a detailed manner.",
            success=True,
            technical_metadata={"format": "JPEG", "dimensions": [800, 600], "file_size": 9},
            vlm_processing_time=0.05,
            model_version="mock",
            metadata=None,
        )

        mock_processor = MagicMock()
        mock_processor.validate_image.return_value = MagicMock(file_path=str(test_image))
        mock_processor.process_single_image.return_value = mock_result

        with patch("anyfile_to_ai.image_processor._get_processor", return_value=mock_processor):
            result = process_image(str(test_image))

            assert result.success is True
            assert result.metadata is None

    def test_audio_default_no_metadata(self, tmp_path):
        """Test audio processing defaults to no metadata."""
        from anyfile_to_ai.audio_processor.processor import process_audio
        from anyfile_to_ai.audio_processor.models import AudioDocument

        test_audio = tmp_path / "test.mp3"
        test_audio.write_bytes(b"audio data")

        mock_audio_doc = AudioDocument(file_path=str(test_audio), file_size=1000, duration=30.0, sample_rate=44100, channels=2, format="mp3")

        with patch("anyfile_to_ai.audio_processor.processor.validate_audio") as mock_validate:
            mock_validate.return_value = mock_audio_doc

            mock_model = MagicMock()
            mock_model.transcribe.return_value = {
                "text": "Audio",
                "segments": [],
                "language": None,
                "language_probability": None,
            }
            mock_loader = MagicMock()
            mock_loader.load_model.return_value = mock_model

            with patch("anyfile_to_ai.audio_processor.processor.get_model_loader", return_value=mock_loader):
                result = process_audio(str(test_audio))

                assert result.success is True
                assert result.metadata is None

    def test_explicit_metadata_disabled(self, tmp_path):
        """Test explicitly disabling metadata works."""
        from anyfile_to_ai.pdf_extractor.reader import extract_text

        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"pdf")

        with patch("pdfplumber.open") as mock_pdf_open:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Content"

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.metadata = {"Title": "Doc"}
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf_open.return_value = mock_pdf

            result = extract_text(str(test_pdf), include_metadata=False)

            assert result.metadata is None
