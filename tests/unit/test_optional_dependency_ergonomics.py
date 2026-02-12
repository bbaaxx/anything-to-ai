"""Tests for optional dependency import ergonomics in package __init__ modules."""

import builtins
import importlib
import sys

import pytest


def _clear_module(module_name: str) -> None:
    to_remove = [name for name in sys.modules if name == module_name or name.startswith(f"{module_name}.")]
    for name in to_remove:
        sys.modules.pop(name, None)


def _block_imports(monkeypatch: pytest.MonkeyPatch, blocked_roots: set[str]) -> None:
    original_import = builtins.__import__

    def _blocked_import(name, globals=None, locals=None, fromlist=(), level=0):
        root = name.split(".", 1)[0]
        if root in blocked_roots:
            msg = f"No module named '{root}'"
            raise ImportError(msg)
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", _blocked_import)


def test_pdf_extractor_package_import_succeeds_without_pdfplumber(monkeypatch: pytest.MonkeyPatch):
    _clear_module("anyfile_to_ai.pdf_extractor")
    _block_imports(monkeypatch, {"pdfplumber"})

    module = importlib.import_module("anyfile_to_ai.pdf_extractor")

    # Model/exception surface should still be importable.
    assert hasattr(module, "ExtractionResult")
    assert hasattr(module, "PDFExtractionError")

    # Runtime APIs should fail with an actionable message when dependency is missing.
    with pytest.raises(ImportError, match="pdfplumber is required"):
        module.extract_text("fake.pdf")


def test_pdf_markdown_formatter_import_succeeds_without_pdfplumber(monkeypatch: pytest.MonkeyPatch):
    _clear_module("anyfile_to_ai.pdf_extractor")
    _block_imports(monkeypatch, {"pdfplumber"})

    formatter = importlib.import_module("anyfile_to_ai.pdf_extractor.markdown_formatter")
    assert hasattr(formatter, "format_markdown")


def test_image_and_audio_package_imports_do_not_require_heavy_runtime_backends(monkeypatch: pytest.MonkeyPatch):
    _clear_module("anyfile_to_ai.image_processor")
    _clear_module("anyfile_to_ai.audio_processor")
    _block_imports(monkeypatch, {"mlx_vlm", "lightning_whisper_mlx"})

    image_module = importlib.import_module("anyfile_to_ai.image_processor")
    audio_module = importlib.import_module("anyfile_to_ai.audio_processor")

    assert hasattr(image_module, "DescriptionResult")
    assert hasattr(audio_module, "TranscriptionResult")
