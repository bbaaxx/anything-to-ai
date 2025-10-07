"""Contract tests for audio markdown output format."""

import subprocess


class TestAudioMarkdownContract:
    """Contract tests for audio markdown format output."""

    def test_markdown_flag_accepted(self, tmp_path):
        """Verify --format markdown flag is accepted."""
        # Create a minimal test audio file
        test_file = tmp_path / "test.mp3"
        # Minimal MP3 header
        test_file.write_bytes(b"\xff\xfb\x90\x00")

        result = subprocess.run(
            ["python", "-m", "audio_processor", str(test_file), "--format", "markdown"],
            check=False,
            capture_output=True,
            text=True,
        )
        # Should not fail with "invalid choice" error
        assert "invalid choice" not in result.stderr.lower()

    def test_output_starts_with_transcription_heading(self):
        """Assert output starts with '# Transcription:'."""
        from anything_to_ai.audio_processor.markdown_formatter import format_markdown

        result = {
            "filename": "test.mp3",
            "duration": 123.45,
            "model": "whisper-large-v3",
            "language": "en",
            "segments": [],
        }
        output = format_markdown(result)

        assert output.startswith("# Transcription:"), "Output must start with transcription heading"

    def test_metadata_section_present(self):
        """Assert metadata section with Duration, Model, Language."""
        from anything_to_ai.audio_processor.markdown_formatter import format_markdown

        result = {
            "filename": "test.mp3",
            "duration": 123.45,
            "model": "whisper-large-v3",
            "language": "en",
            "segments": [],
        }
        output = format_markdown(result)

        assert "- Duration:" in output
        assert "- Model:" in output
        assert "- Language:" in output

    def test_timestamp_speaker_format(self):
        """Assert '## [timestamp] Speaker' format when available."""
        from anything_to_ai.audio_processor.markdown_formatter import format_markdown

        result = {
            "filename": "test.mp3",
            "duration": 30.0,
            "model": "whisper-large-v3",
            "language": "en",
            "segments": [
                {
                    "start": 0.0,
                    "end": 5.0,
                    "text": "Hello world",
                    "speaker": "Speaker 1",
                },
                {"start": 5.0, "end": 10.0, "text": "Goodbye", "speaker": "Speaker 2"},
            ],
        }
        output = format_markdown(result)

        # Should have timestamp and speaker headings
        assert "## [" in output
        assert "Speaker 1" in output or "Speaker 2" in output

    def test_fallback_no_speakers(self):
        """Test fallback: no speakers/timestamps → plain paragraphs."""
        from anything_to_ai.audio_processor.markdown_formatter import format_markdown

        result = {
            "filename": "test.mp3",
            "duration": 30.0,
            "model": "whisper-large-v3",
            "language": "en",
            "segments": [
                {
                    "start": 0.0,
                    "end": 10.0,
                    "text": "Plain transcript text without speakers.",
                },
            ],
        }
        output = format_markdown(result)

        # Should contain the transcript text
        assert "Plain transcript text" in output

    def test_special_characters_not_escaped(self):
        """Test special characters in transcript are not escaped."""
        from anything_to_ai.audio_processor.markdown_formatter import format_markdown

        result = {
            "filename": "test.mp3",
            "duration": 30.0,
            "model": "whisper-large-v3",
            "language": "en",
            "segments": [
                {"start": 0.0, "end": 10.0, "text": "Text with *emphasis* and [notes]"},
            ],
        }
        output = format_markdown(result)

        # Characters should NOT be escaped
        assert "*emphasis*" in output
        assert "[notes]" in output
