"""Contract tests for document converter result and error semantics."""

import pytest

from anyfile_to_ai.document_converter import ConversionResult, ConversionRoute, convert_document
from anyfile_to_ai.document_converter.exceptions import DocumentConversionError, MissingDependencyError, UnsupportedInputError


@pytest.mark.contract
def test_convert_contract_requires_source_route_content(monkeypatch):
    monkeypatch.setattr(
        "anyfile_to_ai.document_converter.converter._convert_with_pdf_extractor",
        lambda source, include_metadata: ConversionResult(source="different", route=ConversionRoute.MARKITDOWN, content="ok"),
    )

    result = convert_document("/tmp/input.pdf")

    assert result.source == "/tmp/input.pdf"
    assert result.route == ConversionRoute.PDF
    assert isinstance(result.content, str)


@pytest.mark.contract
def test_convert_contract_allows_metadata_and_raw_result_variance(monkeypatch):
    monkeypatch.setattr(
        "anyfile_to_ai.document_converter.converter._convert_with_markitdown",
        lambda source: ConversionResult(source=source, route=ConversionRoute.MARKITDOWN, content="ok", metadata={"title": "Doc"}, raw_result=[1, 2, 3]),
    )

    result = convert_document("/tmp/file.docx")

    assert result.metadata == {"title": "Doc"}
    assert result.raw_result == [1, 2, 3]


@pytest.mark.contract
def test_convert_contract_maps_empty_source_to_unsupported_error():
    with pytest.raises(UnsupportedInputError):
        convert_document("   ")


@pytest.mark.contract
def test_convert_contract_maps_missing_dependency_error_passthrough(monkeypatch):
    error = MissingDependencyError("install markitdown[all]")
    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_markitdown", lambda source: (_ for _ in ()).throw(error))

    with pytest.raises(MissingDependencyError) as exc:
        convert_document("/tmp/file.docx")

    assert exc.value is error


@pytest.mark.contract
def test_convert_contract_wraps_unexpected_exception_as_document_conversion_error(monkeypatch):
    monkeypatch.setattr("anyfile_to_ai.document_converter.converter._convert_with_markitdown", lambda source: (_ for _ in ()).throw(RuntimeError("boom")))

    with pytest.raises(DocumentConversionError) as exc:
        convert_document("/tmp/file.docx")

    assert isinstance(exc.value.__cause__, RuntimeError)
