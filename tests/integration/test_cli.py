"""Contract tests for CLI interface."""

from anything_to_ai.pdf_extractor.cli import CLICommands


class TestCLIExtractContract:
    """Test CLI extract command contract."""

    def test_extract_command_returns_exit_code(self):
        """Test extract command returns integer exit code."""
        exit_code = CLICommands.extract("sample.pdf")
        assert isinstance(exit_code, int)
        assert exit_code >= 0

    def test_extract_command_with_stream_option(self):
        """Test extract command accepts stream parameter."""
        exit_code = CLICommands.extract("sample.pdf", stream=True)
        assert isinstance(exit_code, int)

    def test_extract_command_with_format_option(self):
        """Test extract command accepts format_type parameter."""
        exit_code = CLICommands.extract("sample.pdf", format_type="json")
        assert isinstance(exit_code, int)

    def test_extract_command_with_progress_option(self):
        """Test extract command accepts progress parameter."""
        exit_code = CLICommands.extract("sample.pdf", progress=True)
        assert isinstance(exit_code, int)

    def test_extract_command_with_all_options(self):
        """Test extract command with all options combined."""
        exit_code = CLICommands.extract("sample.pdf", stream=True, format_type="json", progress=True)
        assert isinstance(exit_code, int)


class TestCLIInfoContract:
    """Test CLI info command contract."""

    def test_info_command_returns_exit_code(self):
        """Test info command returns integer exit code."""
        exit_code = CLICommands.info("sample.pdf")
        assert isinstance(exit_code, int)
        assert exit_code >= 0
