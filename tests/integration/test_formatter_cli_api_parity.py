"""Integration checks for CLI/API parity across shared formatter migration."""

import json
from types import SimpleNamespace

from anyfile_to_ai.output_formatter import format_json
from anyfile_to_ai.text_summarizer.__main__ import format_output as format_text_cli


def test_text_cli_json_matches_shared_schema(monkeypatch):
    result = SimpleNamespace(
        summary="A concise summary.",
        tags=["alpha", "beta", "gamma"],
        metadata=None,
    )

    monkeypatch.setenv("ANYFILE_OUTPUT_FORMATTER_TEXT_SHARED", "1")
    cli_output = json.loads(format_text_cli(result, "json", include_metadata=False))
    shared_output = json.loads(
        format_json(
            "text",
            {
                "content": "A concise summary.",
                "tags": ["alpha", "beta", "gamma"],
            },
            include_metadata=False,
        )
    )

    assert cli_output == shared_output
