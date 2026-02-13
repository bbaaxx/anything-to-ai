"""Unit tests focused on converter error and optional dependency behavior."""

import importlib
import sys
from types import ModuleType

import pytest

from anyfile_to_ai.document_converter.converter import _extract_markitdown_metadata, _extract_markitdown_text, convert_document
from anyfile_to_ai.document_converter.models import ConversionResult, ConversionRoute
from anyfile_to_ai.document_converter.exceptions import MissingDependencyError


class _DummyMarkItDownResult:
    def __init__(self, text_content: str | None = None, title: str | None = None):
        self.text_content = text_content
        self.title = title


def test_missing_dependency_error_includes_install_guidance(monkeypatch):
    monkeypatch.setitem(sys.modules, "markitdown", None)

    with pytest.raises(MissingDependencyError) as exc:
        convert_document("input.docx")

    message = str(exc.value)
    assert "install" in message.lower()
    assert "markitdown" in message.lower()
    assert "markitdown[all]" in message


def test_converter_module_import_does_not_require_markitdown(monkeypatch):
    monkeypatch.delitem(sys.modules, "markitdown", raising=False)

    module = importlib.reload(importlib.import_module("anyfile_to_ai.document_converter.converter"))

    assert hasattr(module, "convert_document")


def test_markitdown_lazy_import_only_on_markitdown_route(monkeypatch):
    called = {"imported": False}

    real_import = __import__

    def _tracking_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "markitdown":
            called["imported"] = True
            fake_module = ModuleType("markitdown")

            class _FakeMarkItDown:
                def convert(self, source: str):
                    return _DummyMarkItDownResult(text_content="md")

            fake_module.MarkItDown = _FakeMarkItDown
            return fake_module
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr("builtins.__import__", _tracking_import)
    monkeypatch.setattr(
        "anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor",
        lambda source, include_metadata: ConversionResult(source=source, route=ConversionRoute.PDF, content="pdf"),
    )

    convert_document("/tmp/local.pdf")
    assert called["imported"] is False

    convert_document("/tmp/file.docx")
    assert called["imported"] is True


def test_extract_markitdown_text_handles_edge_values():
    assert _extract_markitdown_text(_DummyMarkItDownResult(text_content="hello")) == "hello"
    assert _extract_markitdown_text("raw-string") == "raw-string"
    assert _extract_markitdown_text(_DummyMarkItDownResult(text_content=None))


def test_extract_markitdown_metadata_returns_none_when_empty():
    assert _extract_markitdown_metadata(object()) is None


def test_extract_markitdown_metadata_collects_known_fields():
    value = _DummyMarkItDownResult(text_content="x", title="Test")
    metadata = _extract_markitdown_metadata(value)

    assert metadata == {"title": "Test"}
