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
        from PIL import Image

        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"jpeg data")

        with patch("PIL.Image.open") as mock_image_open:
            mock_img = MagicMock(spec=Image.Image)
            mock_img.width = 800
            mock_img.height = 600
            mock_img.format = "JPEG"
            mock_img.getexif.return_value = {}
            mock_image_open.return_value = mock_img

            with patch("anyfile_to_ai.image_processor.processor.generate_description") as mock_gen:
                mock_gen.return_value = ("Image", 0.90, "model", 1.0)

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

            with patch("anyfile_to_ai.audio_processor.processor.transcribe_audio") as mock_transcribe:
                mock_transcribe.return_value = MagicMock(text="Audio", segments=[], language=None, language_probability=None)

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
