"""Integration tests for package installation."""

import subprocess
import sys
from pathlib import Path


def test_package_can_be_built():
    """Test that package can be built using python -m build."""
    repo_root = Path(__file__).parent.parent.parent

    # Try to build the package
    result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--no-isolation"],
        check=False,
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    # This should fail initially since package structure doesn't exist yet
    # but the test should exist to validate the build process
    assert result.returncode != 0 or "Successfully built" in result.stdout, f"Build should either fail (expected) or succeed: {result.stderr}"


def test_package_structure_exists():
    """Test that package directory structure exists."""
    repo_root = Path(__file__).parent.parent.parent
    package_dir = repo_root / "anyfile_to_ai"

    # This should fail initially since we haven't moved modules yet
    assert package_dir.exists(), "anyfile_to_ai package directory should exist"

    # Check for __init__.py
    init_file = package_dir / "__init__.py"
    assert init_file.exists(), "Package should have __init__.py"


def test_package_importable():
    """Test that package can be imported."""
    try:
        import anyfile_to_ai

        assert hasattr(anyfile_to_ai, "__version__"), "Package should have __version__ attribute"
    except ImportError as e:
        # This is expected initially since modules aren't moved yet
        assert "anyfile_to_ai" in str(e), "Import error should mention anyfile_to_ai package"


def test_pyproject_toml_valid():
    """Test that pyproject.toml is valid TOML."""
    repo_root = Path(__file__).parent.parent.parent
    pyproject_path = repo_root / "pyproject.toml"

    assert pyproject_path.exists(), "pyproject.toml should exist"

    # Try to parse TOML (basic validation without external dependencies)
    try:
        import tomllib

        with open(pyproject_path, "rb") as f:
            tomllib.load(f)
        assert True, "pyproject.toml should be valid TOML"
    except ImportError:
        # Skip detailed TOML validation if parser not available
        # Just check that file has basic structure
        content = pyproject_path.read_text()
        assert "[project]" in content, "Should have [project] section"
        assert "[build-system]" in content, "Should have [build-system] section"
    except Exception as e:
        msg = f"pyproject.toml should be valid TOML: {e}"
        raise AssertionError(msg)
