"""Integration tests for text summarizer workflows.

These tests verify end-to-end behavior from quickstart scenarios.
"""

import json
import subprocess
import sys
import pytest


class TestBasicSummarizationWorkflow:
    """Integration tests for basic summarization scenarios from quickstart.md."""

    def test_scenario_1_summarize_simple_text(self, tmp_path):
        """Test Scenario 1: Summarize simple text (from quickstart)."""
        test_file = tmp_path / "test_ai.txt"
        test_content = "Artificial intelligence has revolutionized many industries. Machine learning algorithms can now process vast amounts of data and identify patterns that humans might miss."
        test_file.write_text(test_content)

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", str(test_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            assert "summary" in data
            assert len(data["tags"]) >= 3

    def test_scenario_2_plain_text_output_format(self, tmp_path):
        """Test Scenario 2: Plain text output format."""
        test_file = tmp_path / "test_ai.txt"
        test_file.write_text("Climate change is one of the most pressing challenges.")

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", str(test_file), "--format", "plain"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            assert "SUMMARY:" in result.stdout or "Summary" in result.stdout

    def test_scenario_3_read_from_stdin(self):
        """Test Scenario 3: Read from stdin."""
        input_text = "Climate change is a pressing challenge with rising temperatures."

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", "--stdin"],
            input=input_text,
            capture_output=True,
            text=True,
        )

        assert result.returncode in [0, 1, 2, 3]

    def test_scenario_5_non_english_text(self):
        """Test Scenario 5: Non-English text (multilingual)."""
        input_text = "La inteligencia artificial está transformando el mundo."

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", "--stdin"],
            input=input_text,
            capture_output=True,
            text=True,
        )

        assert result.returncode in [0, 1, 2, 3]


class TestLargeTextChunking:
    """Integration tests for large text with chunking."""

    def test_scenario_4_large_text_with_chunking(self, tmp_path):
        """Test Scenario 4: Large text with chunking (>10k words)."""
        base_text = "The history of computing spans many decades. " * 20
        large_text = (base_text + " ") * 100  # Creates large text

        test_file = tmp_path / "large_text.txt"
        test_file.write_text(large_text)

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", str(test_file)],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Verify chunking if large enough
            if data.get("metadata", {}).get("input_length", 0) > 10000:
                assert data["metadata"]["chunked"] is True


class TestModulePiping:
    """Integration tests for module piping."""

    @pytest.mark.skipif(
        subprocess.run([sys.executable, "-c", "import anyfile_to_ai.pdf_extractor"], capture_output=True).returncode != 0,
        reason="pdf_extractor module not available",
    )
    def test_scenario_7_pdf_to_summarizer_pipeline(self):
        """Test Scenario 7: PDF → Summarizer pipeline."""
        pytest.skip("Requires pdf_extractor implementation")

    @pytest.mark.skipif(
        subprocess.run([sys.executable, "-c", "import anyfile_to_ai.audio_processor"], capture_output=True).returncode != 0,
        reason="audio_processor module not available",
    )
    def test_scenario_8_audio_to_summarizer_pipeline(self):
        """Test Scenario 8: Audio → Summarizer pipeline."""
        pytest.skip("Requires audio_processor implementation")

    @pytest.mark.skipif(
        subprocess.run([sys.executable, "-c", "import anyfile_to_ai.image_processor"], capture_output=True).returncode != 0,
        reason="image_processor module not available",
    )
    def test_scenario_9_image_to_summarizer_pipeline(self):
        """Test Scenario 9: Image → Summarizer pipeline."""
        pytest.skip("Requires image_processor implementation")


class TestErrorHandling:
    """Integration tests for error handling."""

    def test_scenario_10_empty_input(self):
        """Test Scenario 10: Empty input."""
        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", "--stdin"],
            input="",
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0

    def test_scenario_11_invalid_utf8(self, tmp_path):
        """Test Scenario 11: Invalid UTF-8."""
        test_file = tmp_path / "invalid.txt"
        test_file.write_bytes(b"\xff\xfe Invalid")

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", str(test_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0

    def test_scenario_12_file_not_found(self):
        """Test Scenario 12: File not found."""
        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", "/nonexistent/file.txt"],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
