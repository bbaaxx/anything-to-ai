"""Integration tests for CLI usage scenarios."""

import pytest
import tempfile
import os
import json
from PIL import Image
from image_processor.cli import main, create_cli_parser, expand_image_paths


class TestCliScenarios:
    """Integration tests for complete CLI usage workflows."""

    @pytest.fixture
    def sample_images_dir(self):
        """Create a temporary directory with sample images."""
        temp_dir = tempfile.mkdtemp()
        images = []

        # Create images in the directory
        for i, ext in enumerate(['jpg', 'png', 'gif']):
            img_path = os.path.join(temp_dir, f'image{i+1}.{ext}')
            img = Image.new('RGB', (100, 100), color=['red', 'green', 'blue'][i])
            img.save(img_path)
            images.append(img_path)

        yield temp_dir, images

        # Cleanup
        for img_path in images:
            if os.path.exists(img_path):
                os.unlink(img_path)
        os.rmdir(temp_dir)

    def test_cli_single_image_processing(self, sample_images_dir):
        """Test CLI processing of single image."""
        temp_dir, images = sample_images_dir

        # Scenario: python -m image_processor photo.jpg
        exit_code = main([images[0]])
        assert exit_code == 0

    def test_cli_multiple_images_with_style(self, sample_images_dir):
        """Test CLI processing multiple images with custom style."""
        temp_dir, images = sample_images_dir

        # Scenario: python -m image_processor *.png --style brief
        exit_code = main([images[1], '--style', 'brief', '--max-length', '200'])
        assert exit_code == 0

    def test_cli_batch_processing_with_options(self, sample_images_dir):
        """Test CLI batch processing with various options."""
        temp_dir, images = sample_images_dir

        # Scenario: python -m image_processor images/ --verbose --batch-size 2
        exit_code = main(images + ['--verbose', '--batch-size', '2'])
        assert exit_code == 0

    def test_cli_json_output_format(self, sample_images_dir):
        """Test CLI with JSON output format."""
        temp_dir, images = sample_images_dir

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name

        try:
            # Scenario: python -m image_processor images/ --format json --output results.json
            exit_code = main([images[0], '--format', 'json', '--output', output_file])
            assert exit_code == 0

            # Verify JSON output was created
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    json_data = json.load(f)
                    assert isinstance(json_data, dict)
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_cli_csv_output_format(self, sample_images_dir):
        """Test CLI with CSV output format."""
        temp_dir, images = sample_images_dir

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            output_file = f.name

        try:
            # Scenario: python -m image_processor *.jpg --format csv --output descriptions.csv
            exit_code = main([images[0], '--format', 'csv', '--output', output_file])
            assert exit_code == 0

            # Verify CSV output was created
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    csv_content = f.read()
                    assert len(csv_content) > 0
                    assert ',' in csv_content  # Basic CSV check
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_cli_plain_text_output(self, sample_images_dir):
        """Test CLI with plain text output to stdout."""
        temp_dir, images = sample_images_dir

        # Scenario: python -m image_processor image.jpg --format plain
        exit_code = main([images[0], '--format', 'plain'])
        assert exit_code == 0

    def test_cli_path_expansion_functionality(self, sample_images_dir):
        """Test CLI path expansion for directories and patterns."""
        temp_dir, images = sample_images_dir

        # Test expand_image_paths function
        expanded_paths = expand_image_paths([temp_dir])
        assert len(expanded_paths) >= 3  # Should find all images

        # All expanded paths should be image files
        for path in expanded_paths:
            assert path.lower().endswith(('.jpg', '.png', '.gif', '.jpeg', '.bmp', '.webp'))

    def test_cli_error_handling_nonexistent_file(self):
        """Test CLI error handling for nonexistent files."""
        # Should handle missing files gracefully
        exit_code = main(['nonexistent.jpg'])
        assert exit_code != 0  # Should indicate failure

    def test_cli_error_handling_invalid_arguments(self):
        """Test CLI error handling for invalid arguments."""
        # Test invalid style
        exit_code = main(['image.jpg', '--style', 'invalid'])
        assert exit_code != 0

        # Test invalid format
        exit_code = main(['image.jpg', '--format', 'invalid'])
        assert exit_code != 0

    def test_cli_verbose_output_mode(self, sample_images_dir):
        """Test CLI verbose mode produces appropriate output."""
        temp_dir, images = sample_images_dir

        # Verbose mode should provide progress information
        exit_code = main([images[0], '--verbose'])
        assert exit_code == 0

    def test_cli_quiet_output_mode(self, sample_images_dir):
        """Test CLI quiet mode suppresses output."""
        temp_dir, images = sample_images_dir

        # Quiet mode should suppress progress but show results
        exit_code = main([images[0], '--quiet'])
        assert exit_code == 0

    def test_cli_timeout_parameter(self, sample_images_dir):
        """Test CLI timeout parameter is respected."""
        temp_dir, images = sample_images_dir

        # Test with custom timeout
        exit_code = main([images[0], '--timeout', '120'])
        assert exit_code == 0

    def test_cli_argument_validation_consistency(self):
        """Test CLI argument validation consistency."""
        parser = create_cli_parser()

        # Test that all expected arguments are present
        args = parser.parse_args(['test.jpg'])
        expected_attrs = [
            'images', 'style', 'max_length', 'batch_size',
            'timeout', 'output', 'format', 'verbose', 'quiet'
        ]

        for attr in expected_attrs:
            assert hasattr(args, attr)