"""Integration tests for text summary markdown output."""

from anyfile_to_ai.text_summarizer.markdown_formatter import format_markdown


class TestTextMarkdownIntegration:
    """Integration tests for text summary markdown formatting."""

    def test_simple_summary_with_tags(self):
        """Test simple summary produces valid markdown."""
        result = {"summary": "This is a test summary of the document.", "tags": ["test", "example", "documentation"]}

        output = format_markdown(result)

        # Verify structure
        assert output.startswith("# Summary")
        assert "This is a test summary" in output
        assert "## Tags" in output
        assert "- test" in output
        assert "- example" in output
        assert "- documentation" in output

    def test_multi_paragraph_summary(self):
        """Test summary with multiple paragraphs."""
        result = {
            "summary": "First paragraph of the summary.\n\nSecond paragraph with more details.\n\nThird paragraph conclusion.",
            "tags": ["multi-paragraph", "test", "formatting"],
        }

        output = format_markdown(result)

        # Should preserve paragraph structure
        assert "First paragraph" in output
        assert "Second paragraph" in output
        assert "Third paragraph" in output

    def test_summary_with_metadata(self):
        """Test summary with metadata section."""
        result = {
            "summary": "Summary text",
            "tags": ["test", "metadata", "integration"],
            "metadata": {"input_length": 1500, "chunked": False, "processing_time": 2.5},
        }

        output = format_markdown(result)

        # Should have metadata section
        assert "## Metadata" in output
        assert "- Input length: 1500 words" in output
        assert "- Chunked: No" in output
        assert "- Processing time: 2.5s" in output

    def test_heading_hierarchy_correct(self):
        """Test heading hierarchy is valid."""
        result = {"summary": "Test summary", "tags": ["test", "hierarchy", "validation"]}

        output = format_markdown(result)

        lines = output.split("\n")
        h1_count = sum(1 for line in lines if line.startswith("# ") and not line.startswith("## "))
        h2_count = sum(1 for line in lines if line.startswith("## "))

        assert h1_count == 1  # One H1 for Summary
        assert h2_count >= 1  # At least Tags section

    def test_special_characters_in_summary(self):
        """Test special characters in summary are preserved."""
        result = {
            "summary": "Summary with *emphasis*, [references], and #hashtags should be preserved.",
            "tags": ["test", "special-chars", "markdown"],
        }

        output = format_markdown(result)

        # Characters should NOT be escaped
        assert "*emphasis*" in output
        assert "[references]" in output
        assert "#hashtags" in output

    def test_many_tags(self):
        """Test handling of many tags."""
        tags = [f"tag-{i}" for i in range(20)]
        result = {"summary": "Summary with many tags", "tags": tags}

        output = format_markdown(result)

        # All tags should be present as bullets
        assert output.count("- tag-") == 20

    def test_minimal_summary(self):
        """Test minimal valid summary."""
        result = {"summary": "Short summary.", "tags": ["minimal", "test", "short"]}

        output = format_markdown(result)

        # Should still have all required sections
        assert "# Summary" in output
        assert "Short summary." in output
        assert "## Tags" in output

    def test_chunked_metadata(self):
        """Test metadata with chunked processing."""
        result = {
            "summary": "Summary from chunked processing",
            "tags": ["chunked", "large-document", "test"],
            "metadata": {"input_length": 50000, "chunked": True, "chunk_count": 5, "processing_time": 15.2},
        }

        output = format_markdown(result)

        assert "## Metadata" in output
        assert "- Input length: 50000 words" in output
        assert "- Chunked: Yes" in output
        assert "- Processing time: 15.2s" in output
