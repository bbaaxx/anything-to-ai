"""Integration tests for PDF markdown output."""

from anyfile_to_ai.pdf_extractor.markdown_formatter import format_markdown


class TestPDFMarkdownIntegration:
    """Integration tests for PDF markdown formatting."""

    def test_simple_pdf_markdown_structure(self):
        """Test PDF with simple structure outputs valid markdown."""
        result = {
            "filename": "test.pdf",
            "pages": [
                {"number": 1, "text": "This is the first page with some content."},
                {"number": 2, "text": "This is the second page with more content."},
            ],
        }

        output = format_markdown(result)

        # Verify structure
        assert output.startswith("# PDF Document: test.pdf")
        assert "## Page 1" in output
        assert "## Page 2" in output
        assert "This is the first page" in output
        assert "This is the second page" in output

    def test_pdf_without_structure_plain_paragraphs(self):
        """Test PDF without structure falls back to plain paragraphs."""
        result = {
            "filename": "plain.pdf",
            "pages": [{"number": 1, "text": "Simple paragraph text without any structure markers or headings."}],
        }

        output = format_markdown(result)

        # Should output as plain text (no false structure detection)
        assert "# PDF Document: plain.pdf" in output
        assert "## Page 1" in output
        assert "Simple paragraph text" in output

    def test_special_characters_preserved(self):
        """Test special characters are not escaped."""
        result = {
            "filename": "special.pdf",
            "pages": [{"number": 1, "text": "Text with *asterisks*, [brackets], and #hashtags should be preserved."}],
        }

        output = format_markdown(result)

        # Characters should NOT be escaped
        assert "*asterisks*" in output
        assert "[brackets]" in output
        assert "#hashtags" in output

    def test_large_pdf_no_performance_degradation(self):
        """Test large PDF with many pages performs well."""
        # Create a large result with 100 pages
        pages = [{"number": i, "text": f"Page {i} content " * 100} for i in range(1, 101)]
        result = {"filename": "large.pdf", "pages": pages}

        output = format_markdown(result)

        # Verify it completes and has correct structure
        assert output.startswith("# PDF Document: large.pdf")
        assert "## Page 1" in output
        assert "## Page 100" in output

    def test_empty_page_handling(self):
        """Test handling of empty pages."""
        result = {"filename": "empty.pdf", "pages": [{"number": 1, "text": ""}]}

        output = format_markdown(result)

        assert "# PDF Document: empty.pdf" in output
        assert "## Page 1" in output
        assert "(empty page)" in output

    def test_markdown_syntax_validity(self):
        """Test output is valid markdown."""
        result = {
            "filename": "valid.pdf",
            "pages": [{"number": 1, "text": "Test content"}, {"number": 2, "text": "More content"}],
        }

        output = format_markdown(result)

        # Check markdown structure
        lines = output.split("\n")
        h1_count = sum(1 for line in lines if line.startswith("# ") and not line.startswith("## "))
        h2_count = sum(1 for line in lines if line.startswith("## "))

        assert h1_count == 1  # One document title
        assert h2_count == 2  # Two pages
