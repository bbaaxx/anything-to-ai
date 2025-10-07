"""Integration tests for image markdown output."""

from anyfile_to_ai.image_processor.markdown_formatter import format_markdown


class TestImageMarkdownIntegration:
    """Integration tests for image markdown formatting."""

    def test_single_image_markdown(self):
        """Test single image with VLM description."""
        results = [
            {
                "filename": "test.jpg",
                "image_path": "/path/to/test.jpg",
                "description": "A red car on a highway",
                "processing_success": True,
            },
        ]

        output = format_markdown(results)

        # Verify structure
        assert output.startswith("# Image Descriptions")
        assert "## test.jpg" in output
        assert "![A red car on a highway](/path/to/test.jpg)" in output
        assert "A red car on a highway" in output  # Detailed description

    def test_batch_images_all_in_one_document(self):
        """Test batch of images combined into one markdown document."""
        results = [
            {
                "filename": "image1.jpg",
                "image_path": "image1.jpg",
                "description": "First image description",
                "processing_success": True,
            },
            {
                "filename": "image2.jpg",
                "image_path": "image2.jpg",
                "description": "Second image description",
                "processing_success": True,
            },
            {
                "filename": "image3.png",
                "image_path": "image3.png",
                "description": "Third image description",
                "processing_success": True,
            },
        ]

        output = format_markdown(results)

        # All images in one document
        assert output.count("# Image Descriptions") == 1
        assert "## image1.jpg" in output
        assert "## image2.jpg" in output
        assert "## image3.png" in output

    def test_vlm_failure_generic_fallback(self):
        """Test VLM failure uses generic fallback."""
        results = [
            {
                "filename": "failed.jpg",
                "image_path": "failed.jpg",
                "description": None,
                "processing_success": False,
            },
        ]

        output = format_markdown(results)

        # Should have generic fallback
        assert "![Image](failed.jpg)" in output
        assert "description unavailable" in output.lower()

    def test_special_characters_in_descriptions(self):
        """Test special characters in descriptions are preserved."""
        results = [
            {
                "filename": "test.jpg",
                "image_path": "test.jpg",
                "description": "Image with *emphasis* and [notes] and #tags",
                "processing_success": True,
            },
        ]

        output = format_markdown(results)

        # Characters should NOT be escaped
        assert "*emphasis*" in output
        assert "[notes]" in output
        assert "#tags" in output

    def test_markdown_syntax_validity(self):
        """Test output markdown is syntactically valid."""
        results = [
            {
                "filename": "img1.jpg",
                "image_path": "img1.jpg",
                "description": "First",
                "processing_success": True,
            },
            {
                "filename": "img2.jpg",
                "image_path": "img2.jpg",
                "description": "Second",
                "processing_success": True,
            },
        ]

        output = format_markdown(results)

        # Check markdown structure
        assert output.count("![") == 2  # Two image references
        assert output.count("](") == 2  # Two image paths
        assert output.count("## ") == 2  # Two section headings

    def test_mixed_success_and_failure(self):
        """Test batch with both successful and failed images."""
        results = [
            {
                "filename": "good.jpg",
                "image_path": "good.jpg",
                "description": "Success",
                "processing_success": True,
            },
            {
                "filename": "bad.jpg",
                "image_path": "bad.jpg",
                "description": None,
                "processing_success": False,
            },
            {
                "filename": "good2.jpg",
                "image_path": "good2.jpg",
                "description": "Also success",
                "processing_success": True,
            },
        ]

        output = format_markdown(results)

        # All images included, with appropriate formatting
        assert "## good.jpg" in output
        assert "## bad.jpg" in output
        assert "## good2.jpg" in output
        assert "![Success](good.jpg)" in output
        assert "![Image](bad.jpg)" in output  # Fallback
        assert "![Also success](good2.jpg)" in output
