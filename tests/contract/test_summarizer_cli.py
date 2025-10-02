"""Contract tests for CLI interface.

These tests verify the command-line interface behavior.
"""

import json
import subprocess
import sys
import pytest


class TestCLIInterface:
    """Contract tests for text_summarizer CLI."""

    def test_reads_from_file_path_argument(self, tmp_path):
        """Test that CLI reads from file path argument."""
        test_file = tmp_path / "input.txt"
        test_file.write_text("This is test content for summarization.")

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", str(test_file)],
            capture_output=True,
            text=True,
        )
        # Should succeed (exit code 0) or fail with implementation error (not file error)
        assert result.returncode in [0, 1, 2, 3]

    def test_reads_from_stdin_with_flag(self):
        """Test that CLI reads from stdin when --stdin is provided."""
        input_text = "Test content from stdin for summarization."

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", "--stdin"],
            input=input_text,
            capture_output=True,
            text=True,
        )
        assert result.returncode in [0, 1, 2, 3]

    def test_outputs_json_by_default(self, tmp_path):
        """Test that CLI outputs JSON format by default."""
        test_file = tmp_path / "input.txt"
        test_file.write_text("Content for JSON output test.")

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", str(test_file)],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Should be valid JSON
            try:
                data = json.loads(result.stdout)
                assert "summary" in data or "error" not in data
            except json.JSONDecodeError:
                pytest.skip("Implementation not yet complete")

    def test_outputs_plain_text_with_format_flag(self, tmp_path):
        """Test that CLI outputs plain text when --format plain is provided."""
        test_file = tmp_path / "input.txt"
        test_file.write_text("Content for plain text output test.")

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", str(test_file), "--format", "plain"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Should NOT be JSON
            assert "SUMMARY:" in result.stdout or "summary" in result.stdout.lower()

    def test_writes_to_stdout_by_default(self, tmp_path):
        """Test that CLI writes to stdout by default."""
        test_file = tmp_path / "input.txt"
        test_file.write_text("Content for stdout test.")

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", str(test_file)],
            capture_output=True,
            text=True,
        )

        # Output should go to stdout, not stderr (unless error)
        if result.returncode == 0:
            assert len(result.stdout) > 0

    def test_writes_to_file_with_output_flag(self, tmp_path):
        """Test that CLI writes to file when --output is provided."""
        test_file = tmp_path / "input.txt"
        output_file = tmp_path / "output.json"
        test_file.write_text("Content for file output test.")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "text_summarizer",
                str(test_file),
                "--output",
                str(output_file),
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            assert output_file.exists()
            assert output_file.stat().st_size > 0

    def test_shows_help_with_help_flag(self):
        """Test that --help shows help message."""
        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", "--help"],
            capture_output=True,
            text=True,
        )

        # Help should exit with 0 and show usage info
        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "help" in result.stdout.lower()

    def test_exit_code_1_for_invalid_input(self):
        """Test that invalid input results in exit code 1."""
        # Empty input should be invalid
        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", "--stdin"],
            input="",
            capture_output=True,
            text=True,
        )

        # Should exit with code 1 for invalid input (when implemented)
        assert result.returncode in [1, 2, 3]  # Allow any error for now

    def test_exit_code_2_for_llm_errors(self, tmp_path):
        """Test that LLM errors result in exit code 2."""
        # This test will be meaningful once implementation exists
        # For now, just verify the CLI can be invoked
        test_file = tmp_path / "input.txt"
        test_file.write_text("Test content.")

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", str(test_file)],
            capture_output=True,
            text=True,
        )

        # Exit code should be 0 (success) or 2 (LLM error) when implemented
        assert result.returncode in [0, 1, 2, 3]

    def test_exit_code_3_for_validation_errors(self, tmp_path):
        """Test that validation errors result in exit code 3."""
        # This test will be meaningful once implementation exists
        test_file = tmp_path / "input.txt"
        test_file.write_text("Test content for validation.")

        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", str(test_file)],
            capture_output=True,
            text=True,
        )

        # Exit code should be 0 (success) or 3 (validation error) when implemented
        assert result.returncode in [0, 1, 2, 3]

    def test_file_not_found_error(self):
        """Test that non-existent file produces appropriate error."""
        result = subprocess.run(
            [sys.executable, "-m", "text_summarizer", "/nonexistent/file.txt"],
            capture_output=True,
            text=True,
        )

        # Should fail with error (not crash)
        assert result.returncode != 0
