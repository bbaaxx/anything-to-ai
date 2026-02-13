"""Shared fake builders for document converter tests."""

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from anyfile_to_ai.document_converter.models import ConversionResult, ConversionRoute


@dataclass
class FakeCallTracker:
    calls: list[str]

    def record(self, label: str) -> None:
        self.calls.append(label)


def build_conversion_result(source: str, route: ConversionRoute, content: str = "content", metadata: dict[str, Any] | None = None, raw_result: Any | None = None) -> ConversionResult:
    return ConversionResult(source=source, route=route, content=content, metadata=metadata, raw_result=raw_result)


def build_pdf_backend_result(text: str = "pdf") -> SimpleNamespace:
    return SimpleNamespace(pages=[SimpleNamespace(text=text)], metadata={"type": "pdf"})


def build_image_backend_result(text: str = "image") -> SimpleNamespace:
    return SimpleNamespace(description=text, metadata={"type": "image"})


def build_audio_backend_result(text: str = "audio") -> SimpleNamespace:
    return SimpleNamespace(text=text, metadata={"type": "audio"})


def build_markitdown_backend_result(text: str = "markitdown", title: str | None = None) -> SimpleNamespace:
    return SimpleNamespace(text_content=text, title=title)
