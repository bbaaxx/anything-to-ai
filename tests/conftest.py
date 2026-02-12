"""Pytest configuration and fixtures."""

import os
import pytest

from provider_env import default_vision_model, mlx_available

_VISION_REQUIRED_MODULES = {
    "tests/contract/test_api_config.py",
    "tests/contract/test_api_process_image.py",
    "tests/contract/test_api_process_images.py",
    "tests/contract/test_api_streaming.py",
    "tests/contract/test_module_api.py",
    "tests/integration/test_backward_compat_metadata.py",
    "tests/integration/test_batch_processing.py",
    "tests/integration/test_cli_scenarios.py",
    "tests/integration/test_image_metadata_integration.py",
    "tests/integration/test_pdf_integration.py",
    "tests/integration/test_single_image.py",
    "tests/integration/test_unavailable_metadata.py",
}


def pytest_configure(config):
    """Register custom markers used by test gating hooks."""
    config.addinivalue_line(
        "markers",
        "requires_vision_model: marks tests that require explicit VISION_MODEL environment configuration",
    )


def pytest_collection_modifyitems(items):
    """Skip vision-model dependent suites when VISION_MODEL is not explicitly configured."""
    if os.environ.get("VISION_MODEL"):
        return

    skip_marker = pytest.mark.skip(reason="VISION_MODEL not set; skipping vision-model dependent tests")
    for item in items:
        test_module = item.nodeid.split("::", 1)[0]
        if test_module in _VISION_REQUIRED_MODULES:
            item.add_marker(skip_marker)
            item.add_marker("requires_vision_model")


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
