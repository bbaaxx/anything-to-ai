"""Contract tests for optional dependencies schema."""

from pathlib import Path

def test_optional_dependencies_exist():
    """Test that optional dependencies are configured in pyproject.toml."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    
    # Check for optional dependencies section
    assert "[project.optional-dependencies]" in content, "Should have [project.optional-dependencies] section"
    
    # Check for required optional dependency groups
    required_groups = ["pdf", "image", "audio", "text", "all", "dev"]
    
    for group in required_groups:
        assert f"{group} = [" in content, f"Optional dependency group '{group}' should exist"

def test_optional_dependencies_contract():
    """Test that optional dependencies follow contract requirements."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    
    # Validate specific dependencies for each group
    assert "pdfplumber" in content, "PDF group should include pdfplumber"
    assert "mlx-vlm" in content, "Image group should include mlx-vlm"
    assert "pillow" in content, "Image group should include pillow"
    assert "lightning-whisper-mlx" in content, "Audio group should include lightning-whisper-mlx"
    assert "httpx" in content, "Text group should include httpx"
    
    # Check that 'all' group combines dependencies
    all_section = content.split('all = [')[1].split(']')[0] if 'all = [' in content else ""
    assert "pdfplumber" in all_section, "All group should include PDF dependencies"
    assert "mlx-vlm" in all_section, "All group should include image dependencies"
    assert "lightning-whisper-mlx" in all_section, "All group should include audio dependencies"
    
    # Check dev dependencies
    dev_section = content.split('dev = [')[1].split(']')[0] if 'dev = [' in content else ""
    assert "pytest" in dev_section, "Dev group should include pytest"
    assert "ruff" in dev_section, "Dev group should include ruff"

def test_optional_dependencies_format():
    """Test that optional dependencies follow proper format."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    
    # Check that dependencies use proper version constraints
    dependency_lines = [line.strip() for line in content.split('\n') 
                       if any(op in line for op in ['>=', '==', '!=', '~=', '<', '>', '<=']) 
                       and not line.strip().startswith('#')]
    
    assert len(dependency_lines) > 0, "Should have dependencies with version constraints"
    
    for line in dependency_lines:
        # Should follow pattern: "package>=version"
        assert any(op in line for op in ['>=', '==', '!=', '~=', '<', '>', '<=']), \
            f"Dependency should have version constraint: {line}"