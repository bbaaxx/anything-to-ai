"""Integration tests for document converter routing matrix."""

import pytest

from anyfile_to_ai.document_converter import ConversionRoute, convert_document
from tests.helpers import SOURCE_ROUTE_MATRIX, build_conversion_result


@pytest.mark.integration
@pytest.mark.parametrize(("source", "expected_route"), SOURCE_ROUTE_MATRIX)
def test_routing_matrix_dispatches_to_expected_backend(monkeypatch, source: str, expected_route: ConversionRoute):
    calls: list[str] = []

    def _pdf(value: str, include_metadata: bool):
        calls.append("pdf")
        return build_conversion_result(value, ConversionRoute.PDF)

    def _image(value: str, include_metadata: bool):
        calls.append("image")
        return build_conversion_result(value, ConversionRoute.IMAGE)

    def _audio(value: str, include_metadata: bool):
        calls.append("audio")
        return build_conversion_result(value, ConversionRoute.AUDIO)

    def _markitdown(value: str):
        calls.append("markitdown")
        return build_conversion_result(value, ConversionRoute.MARKITDOWN)

    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor", _pdf)
    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_image_processor", _image)
    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_audio_processor", _audio)
    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_markitdown", _markitdown)

    result = convert_document(source)

    assert result.route == expected_route
    assert calls[-1] == expected_route.value.replace("_processor", "").replace("_extractor", "")


@pytest.mark.integration
def test_local_routes_never_enter_network_bound_handler(monkeypatch):
    forbidden_called = False

    def _forbidden_markitdown(source: str):
        nonlocal forbidden_called
        forbidden_called = True
        raise AssertionError("markitdown should not be called for local pdf source")

    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_markitdown", _forbidden_markitdown)
    monkeypatch.setattr(
        "anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor",
        lambda source, include_metadata: build_conversion_result(source, ConversionRoute.PDF),
    )

    result = convert_document("/tmp/local.pdf")

    assert result.route == ConversionRoute.PDF
    assert forbidden_called is False


@pytest.mark.integration
def test_markitdown_route_allows_best_effort_metadata(monkeypatch):
    monkeypatch.setattr(
        "anyfile_to_ai.document_converter.converter._convert_with_markitdown",
        lambda source: build_conversion_result(source, ConversionRoute.MARKITDOWN, metadata={"title": "Doc"}, raw_result={"raw": True}),
    )

    result = convert_document("/tmp/local.docx", include_metadata=False)

    assert result.route == ConversionRoute.MARKITDOWN
    assert result.metadata == {"title": "Doc"}
    assert result.raw_result == {"raw": True}
