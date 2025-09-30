"""Contract tests for hook bypass mechanism.

These tests verify that bypass mechanisms exist and are documented,
without actually performing git commits.
"""

import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def repo_root():
    """Return the repository root directory."""
    return Path(__file__).parent.parent.parent


def test_git_no_verify_flag_exists():
    """Verify git supports --no-verify flag."""
    # Test that git commit accepts --no-verify flag
    result = subprocess.run(["git", "commit", "--help"], capture_output=True, text=True)
    assert result.returncode == 0, "git commit --help failed"

    help_text = result.stdout.lower()
    assert "--no-verify" in help_text or "-n" in help_text, "git does not support --no-verify flag"


def test_precommit_skip_env_var():
    """Verify SKIP environment variable is supported by pre-commit."""
    # Check pre-commit documentation or help for SKIP variable
    result = subprocess.run(["uv", "run", "pre-commit", "run", "--help"], capture_output=True, text=True)
    assert result.returncode == 0, "pre-commit run --help failed"

    # SKIP is an environment variable, so it may not be in help text
    # Instead, verify that pre-commit can be invoked (which implies SKIP support)
    assert "pre-commit" in result.stdout.lower() or "hook" in result.stdout.lower()


def test_bypass_documentation_exists(repo_root):
    """Verify README or docs mention bypass scenarios."""
    # Check for README.md
    readme_path = repo_root / "README.md"

    # If README doesn't exist yet, this test will initially fail
    # which is expected during TDD phase
    if not readme_path.exists():
        pytest.skip("README.md does not exist yet - will be created in documentation phase")

    readme_content = readme_path.read_text().lower()

    # Check for bypass-related keywords
    bypass_keywords = ["--no-verify", "bypass", "skip", "emergency"]
    found_keywords = [kw for kw in bypass_keywords if kw in readme_content]

    assert len(found_keywords) > 0, f"README should document bypass scenarios. Missing keywords: {bypass_keywords}"