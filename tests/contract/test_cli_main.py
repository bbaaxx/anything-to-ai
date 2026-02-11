"""Contract tests for CLI main() function."""

from unittest.mock import MagicMock, patch
from anyfile_to_ai.image_processor.cli import main


class TestCliMainContract:
    """Contract tests for CLI main entry point."""

    def test_main_function_exists(self):
        """Test main function exists and is callable."""
        assert callable(main)

    def test_main_returns_exit_code(self):
        """Test main function returns integer exit code."""
        with patch("anyfile_to_ai.image_processor.cli.create_cli_parser") as mock_parser:
            mock_parser.return_value.parse_args.return_value = type(
                "Args",
                (),
                {
                    "images": ["test.jpg"],
                    "style": "detailed",
                    "max_length": 500,
                    "batch_size": 4,
                    "timeout": 60,
                    "output": None,
                    "format": "plain",
                    "verbose": False,
                    "quiet": False,
                    "include_metadata": False,
                    "vision_model": "google/gemma-3-4b",
                    "provider": None,
                    "base_url": None,
                },
            )()

            with (
                patch("anyfile_to_ai.image_processor.cli.expand_image_paths", return_value=["test.jpg"]),
                patch("anyfile_to_ai.image_processor.cli._create_image_config", return_value=MagicMock()),
                patch("anyfile_to_ai.image_processor.process_images") as mock_process,
            ):
                mock_process.return_value = type(
                    "Result",
                    (),
                    {
                        "success": True,
                        "results": [],
                        "total_images": 1,
                        "successful_count": 1,
                        "failed_count": 0,
                        "total_processing_time": 0.01,
                    },
                )()

                result = main(["test.jpg"])
                assert isinstance(result, int)

    def test_main_success_exit_code(self):
        """Test main returns 0 for successful processing."""
        with patch("anyfile_to_ai.image_processor.cli.create_cli_parser") as mock_parser:
            mock_parser.return_value.parse_args.return_value = type(
                "Args",
                (),
                {
                    "images": ["test.jpg"],
                    "style": "detailed",
                    "max_length": 500,
                    "batch_size": 4,
                    "timeout": 60,
                    "output": None,
                    "format": "plain",
                    "verbose": False,
                    "quiet": False,
                    "include_metadata": False,
                    "vision_model": "google/gemma-3-4b",
                    "provider": None,
                    "base_url": None,
                },
            )()

            with (
                patch("anyfile_to_ai.image_processor.cli.expand_image_paths", return_value=["test.jpg"]),
                patch("anyfile_to_ai.image_processor.cli._create_image_config", return_value=MagicMock()),
                patch("anyfile_to_ai.image_processor.process_images") as mock_process,
            ):
                mock_process.return_value = type(
                    "Result",
                    (),
                    {
                        "success": True,
                        "results": [],
                        "total_images": 1,
                        "successful_count": 1,
                        "failed_count": 0,
                        "total_processing_time": 0.01,
                    },
                )()

                result = main(["test.jpg"])
                assert result == 0

    def test_main_failure_exit_code(self):
        """Test main returns non-zero for processing failures."""
        with patch("anyfile_to_ai.image_processor.cli.create_cli_parser") as mock_parser:
            mock_parser.return_value.parse_args.return_value = type(
                "Args",
                (),
                {
                    "images": ["nonexistent.jpg"],
                    "style": "detailed",
                    "max_length": 500,
                    "batch_size": 4,
                    "timeout": 60,
                    "output": None,
                    "format": "plain",
                    "verbose": False,
                    "quiet": False,
                    "include_metadata": False,
                    "vision_model": "google/gemma-3-4b",
                    "provider": None,
                    "base_url": None,
                },
            )()

            with (
                patch("anyfile_to_ai.image_processor.cli.expand_image_paths", return_value=["nonexistent.jpg"]),
                patch("anyfile_to_ai.image_processor.cli._create_image_config", return_value=MagicMock()),
                patch("anyfile_to_ai.image_processor.process_images") as mock_process,
            ):
                mock_process.return_value = type(
                    "Result",
                    (),
                    {
                        "success": False,
                        "results": [],
                        "total_images": 1,
                        "successful_count": 0,
                        "failed_count": 1,
                        "total_processing_time": 0.01,
                        "error_message": "File not found",
                    },
                )()

                result = main(["nonexistent.jpg"])
                assert result != 0

    def test_main_handles_exceptions(self):
        """Test main handles exceptions gracefully."""
        with patch("anyfile_to_ai.image_processor.cli.create_cli_parser") as mock_parser:
            mock_parser.side_effect = Exception("Parser error")

            result = main(["test.jpg"])
            assert isinstance(result, int)
            assert result != 0

    def test_main_with_no_args_uses_sys_argv(self):
        """Test main with no args parameter uses sys.argv."""
        with patch("sys.argv", ["program", "test.jpg"]), patch("anyfile_to_ai.image_processor.cli.create_cli_parser") as mock_parser:
            mock_parser.return_value.parse_args.return_value = type(
                "Args",
                (),
                {
                    "images": ["test.jpg"],
                    "style": "detailed",
                    "max_length": 500,
                    "batch_size": 4,
                    "timeout": 60,
                    "output": None,
                    "format": "plain",
                    "verbose": False,
                    "quiet": False,
                    "include_metadata": False,
                    "vision_model": "google/gemma-3-4b",
                    "provider": None,
                    "base_url": None,
                },
            )()

            with (
                patch("anyfile_to_ai.image_processor.cli.expand_image_paths", return_value=["test.jpg"]),
                patch("anyfile_to_ai.image_processor.cli._create_image_config", return_value=MagicMock()),
                patch("anyfile_to_ai.image_processor.process_images") as mock_process,
            ):
                mock_process.return_value = type(
                    "Result",
                    (),
                    {
                        "success": True,
                        "results": [],
                        "total_images": 1,
                        "successful_count": 1,
                        "failed_count": 0,
                        "total_processing_time": 0.01,
                    },
                )()

                result = main()
                assert isinstance(result, int)
