"""Integration test for Audio to summarizer pipeline with metadata."""

from unittest.mock import MagicMock, patch

import pytest


class TestAudioSummarizerPipeline:
    """Tests for Audio transcription -> text summarization pipeline with metadata."""

    def test_audio_to_summarizer_preserves_text(self, tmp_path):
        """Test transcribed text flows from audio processor to summarizer."""
        from anyfile_to_ai.audio_processor.processor import process_audio
        from anyfile_to_ai.audio_processor.models import AudioDocument

        test_audio = tmp_path / "podcast.mp3"
        test_audio.write_bytes(b"fake mp3 audio")

        mock_audio_doc = AudioDocument(file_path=str(test_audio), file_size=5000, duration=120.0, sample_rate=44100, channels=2, format="mp3")

        with patch("anyfile_to_ai.audio_processor.processor.validate_audio_file") as mock_validate:
            mock_validate.return_value = mock_audio_doc

            with patch("anyfile_to_ai.audio_processor.processor.transcribe_audio") as mock_transcribe:
                transcription_text = "This is a sample podcast transcript for testing the pipeline."
                mock_transcribe.return_value = MagicMock(text=transcription_text, segments=[], language="en", language_probability=0.92)

                result = process_audio(str(test_audio), include_metadata=True)

                assert result.success is True
                assert result.text == transcription_text
                assert result.metadata is not None

    def test_audio_plain_output_pipes_to_summarizer(self, tmp_path):
        """Test audio plain output can be piped to summarizer."""
        from anyfile_to_ai.audio_processor.processor import process_audio
        from anyfile_to_ai.audio_processor.models import AudioDocument

        test_audio = tmp_path / "speech.wav"
        test_audio.write_bytes(b"fake wav audio")

        mock_audio_doc = AudioDocument(file_path=str(test_audio), file_size=2000, duration=45.0, sample_rate=16000, channels=1, format="wav")

        with patch("anyfile_to_ai.audio_processor.processor.validate_audio_file") as mock_validate:
            mock_validate.return_value = mock_audio_doc

            with patch("anyfile_to_ai.audio_processor.processor.transcribe_audio") as mock_transcribe:
                transcription = "Speech recognition test for pipeline"
                mock_transcribe.return_value = MagicMock(text=transcription, segments=[], language="en", language_probability=0.88)

                result = process_audio(str(test_audio), include_metadata=False)

                assert result.success is True
                assert result.text == transcription
                assert result.metadata is None
