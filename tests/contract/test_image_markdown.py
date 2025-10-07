"""Contract tests for image markdown output format."""

import subprocess


class TestImageMarkdownContract:
    """Contract tests for image markdown format output."""

    def test_markdown_flag_accepted(self, tmp_path):
        """Verify --format markdown flag is accepted."""
        # Create a minimal test image
        test_file = tmp_path / "test.jpg"
        # Minimal JPEG header
        test_file.write_bytes(b"\xff\xd8\xff\xe0\x00\x10JFIF")

        result = subprocess.run(
            ["python", "-m", "image_processor", str(test_file), "--format", "markdown"],
            check=False,
            capture_output=True,
            text=True,
        )
        # Should not fail with "invalid choice" error
        assert "invalid choice" not in result.stderr.lower()

    def test_output_starts_with_heading(self):
        """Assert output starts with '# Image Descriptions'."""
        from anyfile_to_ai.image_processor.markdown_formatter import format_markdown

        results = [
            {
                "filename": "test.jpg",
                "image_path": "/path/test.jpg",
                "description": "A test image",
            },
        ]
        output = format_markdown(results)

        assert output.startswith("# Image Descriptions"), "Output must start with main heading"

    def test_contains_markdown_image_syntax(self):
        """Assert contains '![alt](path)' markdown image syntax."""
        from anyfile_to_ai.image_processor.markdown_formatter import format_markdown

        results = [
            {
                "filename": "test.jpg",
                "image_path": "test.jpg",
                "description": "A test image",
                "processing_success": True,
            },
        ]
        output = format_markdown(results)

        assert "![" in output and "](" in output, "Must contain markdown image syntax"
        assert "](test.jpg)" in output

    def test_each_image_has_section(self):
        """Verify each image has '## filename' section."""
        from anyfile_to_ai.image_processor.markdown_formatter import format_markdown

        results = [
            {
                "filename": "image1.jpg",
                "image_path": "image1.jpg",
                "description": "First image",
                "processing_success": True,
            },
            {
                "filename": "image2.jpg",
                "image_path": "image2.jpg",
                "description": "Second image",
                "processing_success": True,
            },
        ]
        output = format_markdown(results)

        assert "## image1.jpg" in output
        assert "## image2.jpg" in output

    def test_vlm_failure_fallback(self):
        """Test VLM failure fallback: generic 'Description unavailable'."""
        from anyfile_to_ai.image_processor.markdown_formatter import format_markdown

        results = [
            {
                "filename": "test.jpg",
                "image_path": "test.jpg",
                "description": None,
                "processing_success": False,
            },
        ]
        output = format_markdown(results)

        # Should have generic fallback
        assert "![Image](test.jpg)" in output or "Description unavailable" in output.lower()

    def test_special_characters_not_escaped(self):
        """Test special characters in descriptions are not escaped."""
        from anyfile_to_ai.image_processor.markdown_formatter import format_markdown

        results = [
            {
                "filename": "test.jpg",
                "image_path": "test.jpg",
                "description": "Image with *asterisks* and [brackets]",
                "processing_success": True,
            },
        ]
        output = format_markdown(results)

        # Characters should NOT be escaped in description
        assert "*asterisks*" in output
        assert "[brackets]" in output
