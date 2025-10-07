"""Contract tests for create_cli_parser() function."""

import pytest
import argparse
from anything_to_ai.image_processor.cli import create_cli_parser


class TestCliParserContract:
    """Contract tests for CLI argument parser creation."""

    def test_create_cli_parser_basic_call(self):
        """Test basic create_cli_parser call returns ArgumentParser."""
        parser = create_cli_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_cli_parser_required_positional_args(self):
        """Test CLI parser requires image paths."""
        parser = create_cli_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])  # Should fail without image paths

    def test_cli_parser_accepts_single_image(self):
        """Test CLI parser accepts single image path."""
        parser = create_cli_parser()
        args = parser.parse_args(["image.jpg"])
        assert args.images == ["image.jpg"]

    def test_cli_parser_accepts_multiple_images(self):
        """Test CLI parser accepts multiple image paths."""
        parser = create_cli_parser()
        args = parser.parse_args(["image1.jpg", "image2.png", "image3.gif"])
        assert args.images == ["image1.jpg", "image2.png", "image3.gif"]

    def test_cli_parser_style_argument(self):
        """Test CLI parser accepts style argument."""
        parser = create_cli_parser()
        args = parser.parse_args(["image.jpg", "--style", "brief"])
        assert args.style == "brief"

        # Test default value
        args = parser.parse_args(["image.jpg"])
        assert args.style == "detailed"

        # Test invalid style
        with pytest.raises(SystemExit):
            parser.parse_args(["image.jpg", "--style", "invalid"])

    def test_cli_parser_max_length_argument(self):
        """Test CLI parser accepts max-length argument."""
        parser = create_cli_parser()
        args = parser.parse_args(["image.jpg", "--max-length", "200"])
        assert args.max_length == 200

        # Test default value
        args = parser.parse_args(["image.jpg"])
        assert args.max_length == 500

    def test_cli_parser_batch_size_argument(self):
        """Test CLI parser accepts batch-size argument."""
        parser = create_cli_parser()
        args = parser.parse_args(["image.jpg", "--batch-size", "2"])
        assert args.batch_size == 2

        # Test default value
        args = parser.parse_args(["image.jpg"])
        assert args.batch_size == 4

    def test_cli_parser_timeout_argument(self):
        """Test CLI parser accepts timeout argument."""
        parser = create_cli_parser()
        args = parser.parse_args(["image.jpg", "--timeout", "120"])
        assert args.timeout == 120

        # Test default value
        args = parser.parse_args(["image.jpg"])
        assert args.timeout == 60

    def test_cli_parser_output_arguments(self):
        """Test CLI parser accepts output-related arguments."""
        parser = create_cli_parser()

        # Test output file
        args = parser.parse_args(["image.jpg", "--output", "results.json"])
        assert args.output == "results.json"

        # Test format
        args = parser.parse_args(["image.jpg", "--format", "json"])
        assert args.format == "json"

        # Test verbose flag
        args = parser.parse_args(["image.jpg", "--verbose"])
        assert args.verbose is True

        # Test quiet flag
        args = parser.parse_args(["image.jpg", "--quiet"])
        assert args.quiet is True
