# Output Formatter Migration Guide

This guide tracks migration from module-local formatter implementations to the shared package at `anyfile_to_ai/output_formatter/`.

## Scope

- Shared profiles: `pdf`, `image`, `audio`, `text`, `document_converter`
- Shared output types: `plain`, `markdown`, `json`
- Compatibility guarantee: existing CLI/Python interfaces remain callable during rollout

## Rollback Toggles

- `ANYFILE_OUTPUT_FORMATTER_TEXT_SHARED=0`
- `ANYFILE_OUTPUT_FORMATTER_IMAGE_SHARED=0`
- `ANYFILE_OUTPUT_FORMATTER_PDF_SHARED=0`
- `ANYFILE_OUTPUT_FORMATTER_AUDIO_SHARED=0`

## Migration Order

1. Shared package and contract tests
2. Text summarizer path
3. Image processor path
4. PDF extractor path
5. Audio processor path

## Verification

Run focused verification after each migration slice:

```bash
uv run pytest tests/unit/test_shared_output_formatter_plain.py tests/unit/test_shared_output_formatter_markdown.py tests/unit/test_shared_output_formatter_json.py -q
uv run pytest tests/integration/test_formatter_equivalence_text.py tests/integration/test_formatter_equivalence_image.py tests/integration/test_formatter_equivalence_pdf.py tests/integration/test_formatter_equivalence_audio.py -q
uv run pytest tests/contract/test_output_formatter_unified_contract.py -q
```
