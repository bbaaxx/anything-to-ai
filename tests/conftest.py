"""Pytest configuration and fixtures."""

import os
import pytest

from provider_env import default_vision_model, mlx_available, whisper_available

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

_MLX_VLM_REQUIRED_MODULES = {
    "tests/integration/test_basic_vlm.py",
}

_WHISPER_REQUIRED_MODULES = {
    "tests/integration/test_audio_error_workflows.py",
    "tests/integration/test_batch_audio_processing.py",
    "tests/integration/test_language_detection.py",
    "tests/integration/test_output_formats.py",
    "tests/integration/test_single_audio.py",
    "tests/integration/test_timestamp_integration.py",
}


def pytest_configure(config):
    """Register custom markers used by test gating hooks."""
    config.addinivalue_line(
        "markers",
        "requires_vision_model: marks tests that require explicit VISION_MODEL environment configuration",
    )
    config.addinivalue_line(
        "markers",
        "requires_mlx_vlm: marks tests that require the mlx_vlm optional dependency",
    )
    config.addinivalue_line(
        "markers",
        "requires_whisper: marks tests that require the lightning_whisper_mlx optional dependency",
    )


def pytest_collection_modifyitems(items):
    """Skip test suites when their required optional dependencies are unavailable."""
    _gate_vision_model(items)
    _gate_mlx_vlm(items)
    _gate_whisper(items)


def _gate_vision_model(items):
    if os.environ.get("VISION_MODEL"):
        return

    skip_marker = pytest.mark.skip(reason="VISION_MODEL not set; skipping vision-model dependent tests")
    for item in items:
        test_module = item.nodeid.split("::", 1)[0]
        if test_module in _VISION_REQUIRED_MODULES:
            item.add_marker(skip_marker)
            item.add_marker("requires_vision_model")


def _gate_mlx_vlm(items):
    if mlx_available():
        return

    skip_marker = pytest.mark.skip(reason="mlx_vlm not installed; skipping MLX VLM dependent tests")
    for item in items:
        test_module = item.nodeid.split("::", 1)[0]
        if test_module in _MLX_VLM_REQUIRED_MODULES:
            item.add_marker(skip_marker)
            item.add_marker("requires_mlx_vlm")


def _gate_whisper(items):
    if whisper_available():
        return

    skip_marker = pytest.mark.skip(reason="lightning_whisper_mlx not installed; skipping Whisper dependent tests")
    for item in items:
        test_module = item.nodeid.split("::", 1)[0]
        if test_module in _WHISPER_REQUIRED_MODULES:
            item.add_marker(skip_marker)
            item.add_marker("requires_whisper")


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
