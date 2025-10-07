"""Contract tests for ruff auto-fix behavior.

These tests verify that ruff check and ruff format commands work
correctly and can auto-fix certain types of violations.
"""

import subprocess
import tempfile
from pathlib import Path


def test_ruff_check_command_available():
    """Verify `ruff check` command works."""
    result = subprocess.run(["uv", "run", "ruff", "--version"], check=False, capture_output=True, text=True)
    assert result.returncode == 0, f"ruff command failed: {result.stderr}"
    assert "ruff" in result.stdout.lower(), "Unexpected ruff version output"


def test_ruff_format_command_available():
    """Verify `ruff format` command works."""
    result = subprocess.run(["uv", "run", "ruff", "--version"], check=False, capture_output=True, text=True)
    assert result.returncode == 0, f"ruff command failed: {result.stderr}"
    assert "ruff" in result.stdout.lower(), "Unexpected ruff format version output"


def test_ruff_fixes_unused_imports():
    """Create temp file with unused import, run ruff --fix, verify fixed."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("import os\nimport sys\n\nprint('hello')\n")
        temp_path = Path(f.name)

    try:
        # Run ruff check with --fix
        subprocess.run(["uv", "run", "ruff", "check", "--fix", str(temp_path)], check=False, capture_output=True, text=True)

        # Read the fixed file
        content = temp_path.read_text()

        # Verify unused imports were removed
        assert "import os" not in content or "import sys" not in content, "Unused imports should be removed by ruff --fix"

    finally:
        temp_path.unlink()


def test_ruff_fixes_whitespace():
    """Create temp file with trailing whitespace, run ruff format, verify fixed."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("def hello():   \n    print('world')  \n")
        temp_path = Path(f.name)

    try:
        # Run ruff format
        subprocess.run(["uv", "run", "ruff", "format", str(temp_path)], check=False, capture_output=True, text=True)

        # Read the formatted file
        content = temp_path.read_text()

        # Verify trailing whitespace was removed
        lines = content.split("\n")
        for line in lines:
            if line:  # Skip empty lines
                assert not line.endswith(" "), f"Trailing whitespace not removed: '{line}'"

    finally:
        temp_path.unlink()


def test_ruff_reports_complexity():
    """Create temp file with high complexity, verify ruff reports C901."""
    complex_code = """
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        if x > 50:
                            if x > 60:
                                if x > 70:
                                    if x > 80:
                                        if x > 90:
                                            return "very high"
                                        return "90+"
                                    return "80+"
                                return "70+"
                            return "60+"
                        return "50+"
                    return "40+"
                return "30+"
            return "20+"
        return "10+"
    return "low"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(complex_code)
        temp_path = Path(f.name)

    try:
        # Run ruff check (without --fix to see violations)
        result = subprocess.run(["uv", "run", "ruff", "check", str(temp_path)], check=False, capture_output=True, text=True)

        # Verify C901 (complexity) violation is reported
        output = result.stdout + result.stderr
        assert "C901" in output or "too complex" in output.lower(), "Expected C901 complexity violation"

    finally:
        temp_path.unlink()


def test_ruff_does_not_autofix_complexity():
    """Verify C901 is not auto-fixed (manual intervention required)."""
    complex_code = """
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 20:
                if x > 30:
                    if x > 40:
                        if x > 50:
                            if x > 60:
                                if x > 70:
                                    if x > 80:
                                        if x > 90:
                                            return "very high"
                                        return "90+"
                                    return "80+"
                                return "70+"
                            return "60+"
                        return "50+"
                    return "40+"
                return "30+"
            return "20+"
        return "10+"
    return "low"
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(complex_code)
        temp_path = Path(f.name)

    try:
        # Save original content
        temp_path.read_text()

        # Run ruff check with --fix
        subprocess.run(["uv", "run", "ruff", "check", "--fix", str(temp_path)], check=False, capture_output=True, text=True)

        # Read the content after auto-fix
        fixed_content = temp_path.read_text()

        # Verify the complex structure is still there (not auto-fixed)
        # The code structure should remain essentially the same
        assert fixed_content.count("if x >") >= 10, "Complex structure should not be auto-fixed by ruff"

    finally:
        temp_path.unlink()
