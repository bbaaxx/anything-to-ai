"""Integration test for unavailable metadata field handling."""

from unittest.mock import MagicMock, patch

import pytest


class TestUnavailableMetadataHandling:
    """Tests for handling unavailable metadata fields in real workflows."""

    def test_pdf_missing_metadata_fields(self, tmp_path):
        """Test PDF with missing metadata fields returns unavailable."""
        from anyfile_to_ai.pdf_extractor.reader import extract_text

        test_pdf = tmp_path / "no_metadata.pdf"
        test_pdf.write_bytes(b"pdf")

        with patch("pdfplumber.open") as mock_pdf_open:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Text"

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.metadata = None
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf_open.return_value = mock_pdf

            result = extract_text(str(test_pdf), include_metadata=True)

            assert result.metadata is not None
            assert result.metadata["source"]["creation_date"] == "unavailable"
            assert result.metadata["source"]["author"] == "unavailable"
            assert result.metadata["source"]["title"] == "unavailable"

    def test_image_no_exif_data(self, tmp_path):
        """Test image without EXIF data has empty exif dict."""
        from anyfile_to_ai.image_processor.processor import process_image
        from PIL import Image

        test_image = tmp_path / "no_exif.png"
        test_image.write_bytes(b"png")

        with patch("PIL.Image.open") as mock_image_open:
            mock_img = MagicMock(spec=Image.Image)
            mock_img.width = 100
            mock_img.height = 100
            mock_img.format = "PNG"
            mock_img.getexif.return_value = {}
            mock_image_open.return_value = mock_img

            with patch("anyfile_to_ai.image_processor.processor.generate_description") as mock_gen:
                mock_gen.return_value = ("Image", 0.85, "model", 0.5)

                result = process_image(str(test_image), include_metadata=True)

                assert result.metadata is not None
                assert result.metadata["source"]["exif"] == {}
                assert "camera_info" not in result.metadata["source"]

    def test_audio_no_language_detection(self, tmp_path):
        """Test audio without language detection returns unavailable."""
        from anyfile_to_ai.audio_processor.processor import process_audio
        from anyfile_to_ai.audio_processor.models import AudioDocument

        test_audio = tmp_path / "no_lang.wav"
        test_audio.write_bytes(b"wav")

        mock_audio_doc = AudioDocument(file_path=str(test_audio), file_size=800, duration=20.0, sample_rate=16000, channels=1, format="wav")

        with patch("anyfile_to_ai.audio_processor.processor.validate_audio_file") as mock_validate:
            mock_validate.return_value = mock_audio_doc

            with patch("anyfile_to_ai.audio_processor.processor.transcribe_audio") as mock_transcribe:
                mock_transcribe.return_value = MagicMock(text="Transcription", segments=[], language=None, language_probability=None)

                result = process_audio(str(test_audio), include_metadata=True)

                assert result.metadata is not None
                assert result.metadata["source"]["detected_language"] == "unavailable"
                assert result.metadata["source"]["language_confidence"] == "unavailable"

    def test_text_stdin_input_unavailable_path(self):
        """Test text from stdin has unavailable file path."""
        from anyfile_to_ai.text_summarizer.metadata import _extract_text_source_metadata

        result = _extract_text_source_metadata("Sample text from stdin", None, "en", False, None)

        assert result["file_path"] == "unavailable"
        assert result["file_size_bytes"] == "unavailable"

    def test_unavailable_fields_json_serializable(self, tmp_path):
        """Test unavailable fields serialize correctly to JSON."""
        import json

        from anyfile_to_ai.pdf_extractor.reader import extract_text

        test_pdf = tmp_path / "test.pdf"
        test_pdf.write_bytes(b"pdf")

        with patch("pdfplumber.open") as mock_pdf_open:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "Text"

            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_pdf.metadata = None
            mock_pdf.__enter__.return_value = mock_pdf
            mock_pdf_open.return_value = mock_pdf

            result = extract_text(str(test_pdf), include_metadata=True)

            metadata_json = json.dumps(result.metadata)
            parsed = json.loads(metadata_json)

            assert parsed["source"]["creation_date"] == "unavailable"
            assert parsed["source"]["author"] == "unavailable"
