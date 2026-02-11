"""Pytest configuration and fixtures."""

import os
import pytest

from provider_env import default_vision_model, mlx_available


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up environment variables for tests."""
    original_vision_model = os.environ.get("VISION_MODEL")
    original_defaulted = os.environ.get("VISION_MODEL_DEFAULTED")

    if not original_vision_model and mlx_available():
        os.environ["VISION_MODEL"] = default_vision_model()
        os.environ["VISION_MODEL_DEFAULTED"] = "1"

    yield

    if original_vision_model is not None:
        os.environ["VISION_MODEL"] = original_vision_model
    elif "VISION_MODEL" in os.environ:
        del os.environ["VISION_MODEL"]

    if original_defaulted is not None:
        os.environ["VISION_MODEL_DEFAULTED"] = original_defaulted
    elif "VISION_MODEL_DEFAULTED" in os.environ:
        del os.environ["VISION_MODEL_DEFAULTED"]
