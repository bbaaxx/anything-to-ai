"""Contract tests for document converter CLI behavior."""

import json

import pytest

from anyfile_to_ai.document_converter import ConversionResult, ConversionRoute
from anyfile_to_ai.document_converter.__main__ import main
from anyfile_to_ai.document_converter.exceptions import UnsupportedInputError


@pytest.mark.contract
def test_cli_success_writes_payload_to_stdout(monkeypatch, capsys):
    monkeypatch.setattr(
        "anyfile_to_ai.document_converter.__main__.convert_document",
        lambda source, include_metadata=False: ConversionResult(source=source, route=ConversionRoute.MARKITDOWN, content="hello", metadata={"title": "Doc"}),
    )

    exit_code = main(["/tmp/doc.docx", "--include-metadata"])

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert exit_code == 0
    assert captured.err == ""
    assert payload["source"] == "/tmp/doc.docx"
    assert payload["route"] == "markitdown"
    assert payload["content"] == "hello"
    assert payload["metadata"] == {"title": "Doc"}


@pytest.mark.contract
def test_cli_failure_writes_diagnostics_to_stderr(monkeypatch, capsys):
    monkeypatch.setattr(
        "anyfile_to_ai.document_converter.__main__.convert_document",
        lambda source, include_metadata=False: (_ for _ in ()).throw(UnsupportedInputError("source cannot be empty")),
    )

    exit_code = main(["   "])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "source cannot be empty" in captured.err
