"""Contract tests for PDF markdown output format."""

import subprocess


class TestPDFMarkdownContract:
    """Contract tests for PDF markdown format output."""

    def test_markdown_flag_accepted(self, tmp_path):
        """Verify --format markdown flag is accepted."""
        # Create a minimal test PDF (will fail without real PDF, but tests CLI)
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4\n%%EOF\n")  # Minimal invalid PDF to test CLI

        result = subprocess.run(
            ["python", "-m", "pdf_extractor", "extract", str(test_file), "--format", "markdown"],
            capture_output=True,
            text=True,
        )
        # Should not fail with "invalid choice" error for format
        assert "invalid choice: 'markdown'" not in result.stderr.lower()

    def test_output_starts_with_document_heading(self):
        """Assert output starts with '# PDF Document:'."""
        # This test will be implemented after formatter exists
        # For now, it should fail (TDD requirement)
        from pdf_extractor.markdown_formatter import format_markdown

        result = {"filename": "test.pdf", "pages": []}
        output = format_markdown(result)

        assert output.startswith("# PDF Document:"), "Output must start with document heading"

    def test_contains_page_sections(self):
        """Assert contains '## Page N' sections."""
        from pdf_extractor.markdown_formatter import format_markdown

        result = {"filename": "test.pdf", "pages": [{"number": 1, "text": "Content"}]}
        output = format_markdown(result)

        assert "## Page 1" in output, "Output must contain page sections"

    def test_markdown_syntax_valid(self):
        """Verify markdown syntax validity."""
        from pdf_extractor.markdown_formatter import format_markdown

        result = {"filename": "test.pdf", "pages": [{"number": 1, "text": "Test content"}]}
        output = format_markdown(result)

        # Basic markdown structure checks
        lines = output.split("\n")
        assert any(line.startswith("# ") for line in lines), "Must have H1 heading"
        assert any(line.startswith("## ") for line in lines), "Must have H2 headings"

    def test_fallback_no_structure(self):
        """Test fallback: no structure → plain paragraphs."""
        from pdf_extractor.markdown_formatter import format_markdown

        result = {"filename": "test.pdf", "pages": [{"number": 1, "text": "Simple paragraph text without structure."}]}
        output = format_markdown(result)

        # Should output as plain paragraphs, not detect false structure
        assert "Simple paragraph text" in output
        assert "## Page 1" in output

    def test_special_characters_not_escaped(self):
        """Test special characters are not escaped (per research.md decision)."""
        from pdf_extractor.markdown_formatter import format_markdown

        result = {
            "filename": "test.pdf",
            "pages": [{"number": 1, "text": "Text with *asterisks* and [brackets] and #hashtags"}],
        }
        output = format_markdown(result)

        # Characters should NOT be escaped
        assert "*asterisks*" in output
        assert "[brackets]" in output
        assert "#hashtags" in output
