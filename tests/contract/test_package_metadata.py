"""Contract tests for package metadata schema."""

from pathlib import Path

def test_package_metadata_exists():
    """Test that pyproject.toml exists and has required structure."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    assert pyproject_path.exists(), "pyproject.toml should exist"
    
    # Read file content to verify basic structure
    content = pyproject_path.read_text()
    
    # Check for required sections
    assert "[project]" in content, "pyproject.toml should have [project] section"
    assert 'name = "anyfile_to_ai"' in content, "Package name should be anyfile_to_ai"
    assert "version =" in content, "Version should be specified"
    assert 'requires-python = ">=3.11"' in content, "Should require Python 3.11+"
    assert "authors =" in content, "Authors should be specified"
    assert "[build-system]" in content, "Should have build system configuration"
    assert "setuptools" in content, "Should use setuptools"

def test_package_metadata_contract():
    """Test that package metadata follows contract requirements."""
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    
    # Validate specific contract requirements
    assert 'name = "anyfile_to_ai"' in content
    assert 'description =' in content
    assert 'readme = "README.md"' in content
    assert 'license =' in content
    
    # Check that it's not the old pdf-extractor package
    assert 'name = "pdf-extractor"' not in content, "Should not be pdf-extractor package anymore"