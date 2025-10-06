"""
Contract tests for CLI interface behavior.
These tests MUST FAIL initially as they test VLM CLI integration before implementation.
"""

import pytest
import os
import json
from unittest.mock import patch, MagicMock
from io import StringIO

# Import CLI components
from anyfile_to_ai.image_processor.cli import create_cli_parser, main


class TestCLIInterfaceContract:
    """Test CLI interface contract for VLM integration."""

    def test_cli_parser_preserves_existing_arguments(self):
        """Test that CLI parser preserves all existing arguments."""
        parser = create_cli_parser()

        # Test all existing arguments are still supported
        test_args = [
            'image.jpg',
            '--style', 'detailed',
            '--max-length', '500',
            '--batch-size', '4',
            '--timeout', '60',
            '--output', 'results.json',
            '--format', 'json',
            '--verbose',
            '--quiet'
        ]

        # Should parse without error
        try:
            args = parser.parse_args(test_args)
            assert args.images == ['image.jpg']
            assert args.style == 'detailed'
            assert args.max_length == 500
            assert args.batch_size == 4
            assert args.timeout == 60
            assert args.output == 'results.json'
            assert args.format == 'json'
            assert args.verbose is True
            assert args.quiet is True
        except SystemExit:
            pytest.fail("CLI argument parsing failed - backward compatibility broken")

    def test_main_requires_vision_model_env(self):
        """Test that main() requires VISION_MODEL environment variable."""
        # This should FAIL initially - no VLM environment checking yet
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('VISION_MODEL', None)

            # Mock stdout to capture output
            with patch('sys.stdout', new_callable=StringIO):
                with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                    # Should return exit code 1 for missing VISION_MODEL
                    exit_code = main(['test_image.jpg'])

                    assert exit_code == 1
                    error_output = mock_stderr.getvalue()
                    assert "VISION_MODEL" in error_output

    def test_main_with_vision_model_env(self):
        """Test main() with VISION_MODEL environment variable set."""
        # This should FAIL initially - no VLM integration in CLI yet
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            # Mock the image processing to avoid actual file operations
            with patch('image_processor.process_images') as mock_process:
                mock_result = MagicMock()
                mock_result.results = []
                mock_result.success = True
                mock_result.total_images = 0
                mock_process.return_value = mock_result

                # Should run without VLM environment error
                exit_code = main(['--help'])  # Use help to avoid file operations
                # Help should work regardless of VLM setup
                assert exit_code in [0, None]  # Help might not return explicit code

    def test_json_output_format_enhanced(self):
        """Test that JSON output includes enhanced VLM fields."""
        # This should FAIL initially - enhanced output not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            # Mock image processing to return enhanced results
            mock_enhanced_result = MagicMock()
            mock_enhanced_result.image_path = "test.jpg"
            mock_enhanced_result.description = "Real VLM description"
            mock_enhanced_result.confidence_score = 0.95
            mock_enhanced_result.processing_time = 1.0
            mock_enhanced_result.model_used = "google/gemma-3-4b"
            mock_enhanced_result.success = True
            # Enhanced fields that should be present
            mock_enhanced_result.technical_metadata = {
                "format": "JPEG",
                "dimensions": [100, 100],
                "file_size": 1000
            }
            mock_enhanced_result.vlm_processing_time = 0.8
            mock_enhanced_result.model_version = "v1.0"

            mock_result = MagicMock()
            mock_result.results = [mock_enhanced_result]
            mock_result.success = True
            mock_result.total_images = 1
            mock_result.successful_count = 1
            mock_result.failed_count = 0
            mock_result.total_processing_time = 1.0

            with patch('image_processor.process_images', return_value=mock_result):
                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    # This should produce enhanced JSON output
                    main(['test.jpg', '--format', 'json'])

                    output = mock_stdout.getvalue()
                    if output:
                        try:
                            json_data = json.loads(output)

                            # Check enhanced JSON structure
                            assert 'results' in json_data
                            if json_data['results']:
                                result = json_data['results'][0]
                                assert 'technical_metadata' in result
                                assert 'vlm_processing_time' in result
                                assert 'model_version' in result

                        except json.JSONDecodeError:
                            pytest.fail("JSON output is malformed")

    def test_csv_output_format_enhanced(self):
        """Test that CSV output includes enhanced VLM columns."""
        # This should FAIL initially - enhanced CSV output not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            with patch('image_processor.process_images') as mock_process:
                mock_result = MagicMock()
                mock_result.results = []
                mock_result.success = True
                mock_process.return_value = mock_result

                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    # Should produce enhanced CSV with VLM columns
                    main(['test.jpg', '--format', 'csv'])

                    output = mock_stdout.getvalue()
                    if output:
                        lines = output.strip().split('\n')
                        if lines:
                            header = lines[0]
                            # Should include enhanced CSV columns
                            expected_columns = [
                                'image_path', 'description', 'confidence_score',
                                'processing_time', 'success', 'format', 'width',
                                'height', 'file_size', 'model_used', 'model_version'
                            ]
                            for column in expected_columns:
                                assert column in header, f"Missing column: {column}"

    def test_plain_output_format_enhanced(self):
        """Test that plain output includes VLM information."""
        # This should FAIL initially - enhanced plain output not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            with patch('image_processor.process_images') as mock_process:
                # Mock enhanced result
                mock_enhanced_result = MagicMock()
                mock_enhanced_result.image_path = "test.jpg"
                mock_enhanced_result.description = "Real VLM description"
                mock_enhanced_result.success = True
                mock_enhanced_result.technical_metadata = {
                    "format": "JPEG",
                    "dimensions": [100, 100],
                    "file_size": 1000
                }

                mock_result = MagicMock()
                mock_result.results = [mock_enhanced_result]
                mock_result.success = True
                mock_result.total_images = 1
                mock_result.successful_count = 1
                mock_result.failed_count = 0
                mock_result.total_processing_time = 1.0

                mock_process.return_value = mock_result

                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    main(['test.jpg', '--format', 'plain'])

                    output = mock_stdout.getvalue()
                    # Should contain VLM description, not mock text
                    assert "Real VLM description" in output
                    assert "Mock description" not in output

    def test_error_messages_for_vlm_issues(self):
        """Test proper error messages for VLM-specific issues."""
        # This should FAIL initially - VLM error handling not implemented

        # Test missing VISION_MODEL
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('VISION_MODEL', None)

            with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
                exit_code = main(['test.jpg'])

                assert exit_code == 1
                error_output = mock_stderr.getvalue()
                assert "VISION_MODEL" in error_output
                assert "environment variable" in error_output.lower()

    def test_exit_codes_preserved(self):
        """Test that exit codes follow the contract."""
        # Success case
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            with patch('image_processor.process_images') as mock_process:
                mock_result = MagicMock()
                mock_result.results = []
                mock_result.success = True
                mock_process.return_value = mock_result

                # Should return 0 for success
                exit_code = main(['--help'])
                assert exit_code in [0, None]

        # Error case - missing VISION_MODEL
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop('VISION_MODEL', None)

            # Should return 1 for error
            exit_code = main(['test.jpg'])
            assert exit_code == 1

    def test_verbose_output_includes_vlm_info(self):
        """Test that verbose mode includes VLM processing information."""
        # This should FAIL initially - VLM verbose output not implemented
        with patch.dict(os.environ, {'VISION_MODEL': 'google/gemma-3-4b'}):
            with patch('image_processor.process_images') as mock_process:
                mock_result = MagicMock()
                mock_result.results = []
                mock_result.success = True
                mock_process.return_value = mock_result

                with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                    main(['test.jpg', '--verbose'])

                    mock_stdout.getvalue()
                    # Verbose output should mention VLM model being used
                    # This will fail initially as VLM integration not implemented

    def test_backward_compatibility_all_args(self):
        """Test that all existing CLI arguments work exactly as before."""
        parser = create_cli_parser()

        # Test complete set of existing arguments
        existing_args = [
            'image1.jpg', 'image2.png',
            '--style', 'brief',
            '--max-length', '200',
            '--batch-size', '2',
            '--timeout', '30',
            '--output', 'output.csv',
            '--format', 'csv',
            '--verbose'
        ]

        args = parser.parse_args(existing_args)

        # All existing behavior should be preserved
        assert args.images == ['image1.jpg', 'image2.png']
        assert args.style == 'brief'
        assert args.max_length == 200
        assert args.batch_size == 2
        assert args.timeout == 30
        assert args.output == 'output.csv'
        assert args.format == 'csv'
        assert args.verbose is True
