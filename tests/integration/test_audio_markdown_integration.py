"""Integration tests for audio markdown output."""

from anyfile_to_ai.audio_processor.markdown_formatter import format_markdown


class TestAudioMarkdownIntegration:
    """Integration tests for audio markdown formatting."""

    def test_audio_with_speakers_and_timestamps(self):
        """Test audio with speakers produces markdown with sections."""
        result = {
            "filename": "podcast.mp3",
            "duration": 300.0,
            "model": "whisper-large-v3",
            "language": "en",
            "segments": [
                {"start": 0.0, "end": 10.0, "text": "Welcome to the podcast.", "speaker": "Speaker 1"},
                {"start": 10.0, "end": 25.0, "text": "Thanks for having me.", "speaker": "Speaker 2"},
                {"start": 25.0, "end": 45.0, "text": "Let's discuss markdown.", "speaker": "Speaker 1"},
            ],
        }

        output = format_markdown(result)

        # Verify structure
        assert output.startswith("# Transcription: podcast.mp3")
        assert "- Duration: 00:05:00" in output
        assert "- Model: whisper-large-v3" in output
        assert "- Language: en" in output
        assert "## [00:00:00] Speaker 1" in output
        assert "## [00:00:10] Speaker 2" in output
        assert "## [00:00:25] Speaker 1" in output

    def test_audio_without_speakers_plain_paragraphs(self):
        """Test audio without speakers falls back to plain paragraphs."""
        result = {
            "filename": "simple.mp3",
            "duration": 60.0,
            "model": "whisper-medium",
            "language": "en",
            "segments": [{"start": 0.0, "end": 60.0, "text": "This is a simple transcription without speaker labels."}],
        }

        output = format_markdown(result)

        # Should have metadata
        assert "# Transcription: simple.mp3" in output
        assert "- Duration:" in output
        # Should have content
        assert "This is a simple transcription" in output

    def test_metadata_section_complete(self):
        """Test metadata section has all required fields."""
        result = {
            "filename": "test.mp3",
            "duration": 123.45,
            "model": "whisper-large-v3",
            "language": "es",
            "segments": [],
        }

        output = format_markdown(result)

        # Check all metadata fields
        assert "- Duration: 00:02:03" in output
        assert "- Model: whisper-large-v3" in output
        assert "- Language: es" in output

    def test_special_characters_in_transcript(self):
        """Test special characters in transcript are preserved."""
        result = {
            "filename": "special.mp3",
            "duration": 30.0,
            "model": "whisper-medium",
            "language": "en",
            "segments": [{"start": 0.0, "end": 10.0, "text": "Text with *emphasis*, [notes], and #hashtags"}],
        }

        output = format_markdown(result)

        # Characters should NOT be escaped
        assert "*emphasis*" in output
        assert "[notes]" in output
        assert "#hashtags" in output

    def test_long_audio_multiple_segments(self):
        """Test long audio with many segments."""
        segments = [{"start": i * 10.0, "end": (i + 1) * 10.0, "text": f"Segment {i} content", "speaker": f"Speaker {i % 2 + 1}"} for i in range(50)]
        result = {"filename": "long.mp3", "duration": 500.0, "model": "whisper-medium", "language": "en", "segments": segments}

        output = format_markdown(result)

        # Verify it handles many segments
        assert "# Transcription: long.mp3" in output
        assert output.count("## [") == 50  # 50 segment headings

    def test_timestamp_formatting(self):
        """Test timestamp formatting is correct."""
        result = {
            "filename": "time.mp3",
            "duration": 3661.0,
            "model": "whisper-medium",
            "language": "en",
            "segments": [
                {"start": 0.0, "end": 1.0, "text": "Zero"},
                {"start": 61.0, "end": 62.0, "text": "One minute"},
                {"start": 3600.0, "end": 3601.0, "text": "One hour"},
            ],
        }

        output = format_markdown(result)

        # Check timestamp formats
        assert "## [00:00:00]" in output  # HH:MM:SS for hour-long files
        assert "## [00:01:01]" in output
        assert "## [01:00:00]" in output
        assert "- Duration: 01:01:01" in output
