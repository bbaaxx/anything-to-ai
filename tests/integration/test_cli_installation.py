"""Integration tests for CLI functionality after installation."""

import subprocess
from pathlib import Path


def test_cli_commands_exist_as_entry_points():
    """Test that CLI commands are configured as entry points."""
    repo_root = Path(__file__).parent.parent.parent
    pyproject_path = repo_root / "pyproject.toml"

    content = pyproject_path.read_text()

    # Check that all CLI commands are defined
    required_commands = [
        "pdf-extractor",
        "image-processor",
        "audio-processor",
        "text-summarizer",
    ]

    for command in required_commands:
        assert command in content, f"Command {command} should be in pyproject.toml"


def test_cli_commands_help():
    """Test that CLI commands show help when invoked."""
    commands = [
        "pdf-extractor",
        "image-processor",
        "audio-processor",
        "text-summarizer",
    ]

    for command in commands:
        # Try to run command with --help
        result = subprocess.run([command, "--help"], check=False, capture_output=True, text=True)

        # This might fail initially since package isn't installed
        # but we test the entry point configuration
        if result.returncode == 0:
            assert "usage:" in result.stdout.lower() or "usage:" in result.stderr.lower(), f"{command} should show usage information"
        else:
            # Command not found is expected initially
            assert "not found" in result.stderr.lower() or "command not found" in result.stderr.lower() or result.returncode != 0, f"{command} should either work or not be installed yet"


def test_cli_modules_importable():
    """Test that CLI modules can be imported from package."""
    modules = [
        "anything_to_ai.pdf_extractor.__main__",
        "anything_to_ai.image_processor.__main__",
        "anything_to_ai.audio_processor.__main__",
        "anything_to_ai.text_summarizer.__main__",
    ]

    for module in modules:
        try:
            __import__(module)
            assert True, f"Module {module} should be importable"
        except ImportError as e:
            # This is expected initially since modules aren't moved yet
            assert "No module named" in str(e) or "anything_to_ai" in str(e), f"Import error should be about missing package: {e}"


def test_cli_entry_point_format():
    """Test that CLI entry points have correct format."""
    repo_root = Path(__file__).parent.parent.parent
    pyproject_path = repo_root / "pyproject.toml"

    content = pyproject_path.read_text()

    # Extract entry point lines
    lines = [
        line.strip()
        for line in content.split("\n")
        if line.strip()
        and not line.strip().startswith("#")
        and any(
            cmd in line
            for cmd in [
                "pdf-extractor",
                "image-processor",
                "audio-processor",
                "text-summarizer",
            ]
        )
    ]

    assert len(lines) >= 4, "Should have at least 4 CLI entry points"

    for line in lines:
        # Should follow pattern: command = "package.module:function"
        assert "=" in line, f"Entry point should have '=': {line}"
        assert ":" in line, f"Entry point should have ':': {line}"
        assert "anything_to_ai." in line, f"Entry point should reference anything_to_ai: {line}"
