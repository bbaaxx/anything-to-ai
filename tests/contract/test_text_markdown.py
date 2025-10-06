"""Contract tests for text summary markdown output format."""

import subprocess


class TestTextMarkdownContract:
    """Contract tests for text summary markdown format output."""

    def test_markdown_flag_accepted(self, tmp_path):
        """Verify --format markdown flag is accepted."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content for summarization")

        result = subprocess.run(
            ["python", "-m", "text_summarizer", str(test_file), "--format", "markdown"],
            capture_output=True,
            text=True,
        )
        # Should not fail with "invalid choice" error
        assert "invalid choice" not in result.stderr.lower()

    def test_output_starts_with_summary_heading(self):
        """Assert output starts with '# Summary'."""
        from anyfile_to_ai.text_summarizer.markdown_formatter import format_markdown

        result = {
            "summary": "This is a test summary",
            "tags": ["test", "example"],
        }
        output = format_markdown(result)

        assert output.startswith("# Summary"), "Output must start with Summary heading"

    def test_contains_tags_section(self):
        """Assert contains '## Tags' section."""
        from anyfile_to_ai.text_summarizer.markdown_formatter import format_markdown

        result = {
            "summary": "This is a test summary",
            "tags": ["test", "example"],
        }
        output = format_markdown(result)

        assert "## Tags" in output

    def test_tags_formatted_as_bullets(self):
        """Assert tags formatted as bullet list ('- tag')."""
        from anyfile_to_ai.text_summarizer.markdown_formatter import format_markdown

        result = {
            "summary": "This is a test summary",
            "tags": ["test", "example", "markdown"],
        }
        output = format_markdown(result)

        assert "- test" in output
        assert "- example" in output
        assert "- markdown" in output

    def test_heading_hierarchy(self):
        """Verify heading hierarchy (H1, H2)."""
        from anyfile_to_ai.text_summarizer.markdown_formatter import format_markdown

        result = {
            "summary": "This is a test summary",
            "tags": ["test"],
        }
        output = format_markdown(result)

        lines = output.split("\n")
        # Should have exactly one H1 and at least one H2
        h1_count = sum(1 for line in lines if line.startswith("# ") and not line.startswith("## "))
        h2_count = sum(1 for line in lines if line.startswith("## "))

        assert h1_count == 1, "Should have exactly one H1 heading"
        assert h2_count >= 1, "Should have at least one H2 heading"

    def test_special_characters_not_escaped(self):
        """Test special characters in summary are not escaped."""
        from anyfile_to_ai.text_summarizer.markdown_formatter import format_markdown

        result = {
            "summary": "Summary with *asterisks* and [brackets] and #hashtags",
            "tags": ["test"],
        }
        output = format_markdown(result)

        # Characters should NOT be escaped
        assert "*asterisks*" in output
        assert "[brackets]" in output
        assert "#hashtags" in output
