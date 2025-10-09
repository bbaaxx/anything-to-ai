#!/usr/bin/env python3
"""
Script to enforce 250-line limit per constitutional requirement.
Checks all Python files in pdf_extractor/ directory.
"""

import sys
from pathlib import Path

MAX_LINES = 250
SOURCE_DIRS = ["pdf_extractor", "image_processor", "llm_client"]


def check_file_lengths():
    """Check all Python files for line count compliance."""
    violations = []

    for source_dir in SOURCE_DIRS:
        if not Path(source_dir).exists():
            continue

        for python_file in Path(source_dir).rglob("*.py"):
            with open(python_file, encoding="utf-8") as f:
                lines = f.readlines()
                line_count = len([line for line in lines if line.strip()])  # Count non-empty lines

                if line_count > MAX_LINES:
                    violations.append((python_file, line_count))

    if violations:
        for _file_path, line_count in violations:
            pass
        return False
    return True


if __name__ == "__main__":
    success = check_file_lengths()
    sys.exit(0 if success else 1)
