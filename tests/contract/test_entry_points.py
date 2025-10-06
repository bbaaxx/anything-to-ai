"""Contract tests for CLI entry points schema."""

from pathlib import Path

def test_entry_points_exist():
    """Test that CLI entry points are configured in pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    
    # Check for entry points section
    assert "[project.scripts]" in content, "Should have [project.scripts] section"
    
    # Check for required entry points
    required_entry_points = [
        'pdf-extractor = "anyfile_to_ai.pdf_extractor.__main__:main"',
        'image-processor = "anyfile_to_ai.image_processor.__main__:main"',
        'audio-processor = "anyfile_to_ai.audio_processor.__main__:main"',
        'text-summarizer = "anyfile_to_ai.text_summarizer.__main__:main"',
    ]
    
    for entry_point in required_entry_points:
        assert entry_point in content, f"Entry point missing: {entry_point}"

def test_entry_points_contract():
    """Test that entry points follow contract format."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    
    # Validate entry point format: module.function
    entry_point_lines = [line.strip() for line in content.split('\n') 
                        if line.strip().startswith(('pdf-extractor', 'image-processor', 'audio-processor', 'text-summarizer'))]
    
    assert len(entry_point_lines) >= 4, "Should have at least 4 entry points"
    
    for line in entry_point_lines:
        # Should follow pattern: name = "package.module:function"
        assert '=' in line, f"Entry point should have '=': {line}"
        assert ':' in line, f"Entry point should have ':' separator: {line}"
        assert 'anyfile_to_ai.' in line, f"Entry point should reference anyfile_to_ai package: {line}"
        assert '__main__:main' in line, f"Entry point should reference __main__:main: {line}"