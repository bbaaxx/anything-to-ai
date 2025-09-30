"""Contract tests for coverage configuration.

These tests verify that pyproject.toml is correctly configured
with coverage settings for pytest-cov.
"""

from pathlib import Path

import pytest

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for older versions


@pytest.fixture
def repo_root():
    """Return the repository root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def pyproject_toml(repo_root):
    """Load and return the pyproject.toml configuration."""
    pyproject_path = repo_root / "pyproject.toml"
    if not pyproject_path.exists():
        pytest.fail(f"pyproject.toml not found at {pyproject_path}")
    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def test_coverage_config_exists_in_pyproject(pyproject_toml):
    """Verify [tool.coverage.run] section exists in pyproject.toml."""
    assert "tool" in pyproject_toml, "Missing [tool] section"
    assert "coverage" in pyproject_toml["tool"], "Missing [tool.coverage] section"
    assert "run" in pyproject_toml["tool"]["coverage"], "Missing [tool.coverage.run] section"


def test_coverage_sources_include_all_modules(pyproject_toml):
    """Verify pdf_extractor, audio_processor, image_processor in source."""
    required_modules = {"pdf_extractor", "audio_processor", "image_processor"}
    coverage_run = pyproject_toml.get("tool", {}).get("coverage", {}).get("run", {})
    sources = set(coverage_run.get("source", []))

    missing_modules = required_modules - sources
    assert not missing_modules, f"Missing modules in coverage source: {missing_modules}"


def test_coverage_minimum_threshold(pyproject_toml):
    """Verify fail_under = 70 in coverage report configuration."""
    coverage_report = pyproject_toml.get("tool", {}).get("coverage", {}).get("report", {})
    fail_under = coverage_report.get("fail_under", 0)
    assert fail_under == 70, f"Expected fail_under=70, got {fail_under}"


def test_coverage_omits_test_files(pyproject_toml):
    """Verify */tests/* in omit patterns."""
    coverage_run = pyproject_toml.get("tool", {}).get("coverage", {}).get("run", {})
    omit_patterns = coverage_run.get("omit", [])

    # Check if any omit pattern matches test files
    test_patterns = [p for p in omit_patterns if "test" in p.lower()]
    assert len(test_patterns) > 0, "No test file patterns in omit list"


def test_pytest_addopts_includes_coverage(pyproject_toml):
    """Verify --cov flags in pytest configuration."""
    pytest_config = pyproject_toml.get("tool", {}).get("pytest", {}).get("ini_options", {})
    addopts = pytest_config.get("addopts", [])

    # Convert to string to handle both list and string formats
    addopts_str = " ".join(addopts) if isinstance(addopts, list) else addopts

    assert "--cov=" in addopts_str or "--cov" in addopts_str, "Missing --cov flags in pytest addopts"
    assert "--cov-fail-under" in addopts_str, "Missing --cov-fail-under in pytest addopts"


def test_coverage_excludes_boilerplate(pyproject_toml):
    """Verify __init__.py, __main__.py in omit patterns."""
    coverage_run = pyproject_toml.get("tool", {}).get("coverage", {}).get("run", {})
    omit_patterns = coverage_run.get("omit", [])

    # Check for init and main patterns
    has_init_pattern = any("__init__.py" in p for p in omit_patterns)
    has_main_pattern = any("__main__.py" in p for p in omit_patterns)

    assert has_init_pattern, "__init__.py not in omit patterns"
    assert has_main_pattern, "__main__.py not in omit patterns"
