"""Pytest configuration and fixtures."""

import os
import pytest


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up environment variables for tests."""
    # Set VISION_MODEL for tests that require it
    original_vision_model = os.environ.get("VISION_MODEL")
    os.environ["VISION_MODEL"] = "mlx-community/Qwen2-VL-2B-Instruct-4bit"

    yield

    # Restore original value
    if original_vision_model is not None:
        os.environ["VISION_MODEL"] = original_vision_model
    elif "VISION_MODEL" in os.environ:
        del os.environ["VISION_MODEL"]
