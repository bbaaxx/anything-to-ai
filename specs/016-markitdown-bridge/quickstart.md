# Quickstart: Implementing Spec 016

Feature: `specs/016-markitdown-bridge/spec.md`

## 1) Validate Baseline

```bash
uv run pytest tests/unit/test_document_converter.py -q
```

## 2) Add Failing Tests First

Create/extend tests in this order:

1. `tests/unit/test_document_converter.py`
   - URL precedence over suffix-specialized routing
   - unknown extension fallback to MarkItDown
   - whitespace-only source handling
   - unknown-exception wrapping to `DocumentConversionError`
   - no-rewrap behavior for existing typed conversion errors
2. `tests/unit/test_document_converter_errors.py`
   - `MissingDependencyError` install guidance content
   - lazy import behavior for optional dependencies
   - MarkItDown metadata/content extraction edge handling
3. `tests/integration/test_document_converter_routing.py`
   - deterministic route-to-backend wiring using lightweight doubles
4. `tests/contract/test_document_converter_contracts.py`
    - stable required output fields (`source`, `route`, `content`)
    - allowed-variance fields (`metadata`, `raw_result`) semantics
5. `tests/contract/test_document_converter_cli_contracts.py`
   - stdout payloads on success
   - stderr diagnostics + non-zero exit code on failure

## 3) Implement Minimal Code Changes

- Modify only `anyfile_to_ai/document_converter/` unless tests prove another scoped adjustment is required.
- Preserve existing behavior for specialized routed backends.
- Keep formatter unification out of scope; implement only the minimal converter CLI parity contract.

## 4) Run Quality Gates

```bash
uv run ruff check anyfile_to_ai/document_converter tests/unit/test_document_converter.py tests/unit/test_document_converter_errors.py tests/integration/test_document_converter_routing.py tests/contract/test_document_converter_contracts.py
uv run ruff format anyfile_to_ai/document_converter tests/unit/test_document_converter.py tests/unit/test_document_converter_errors.py tests/integration/test_document_converter_routing.py tests/contract/test_document_converter_contracts.py tests/contract/test_document_converter_cli_contracts.py
uv run pytest tests/unit/test_document_converter.py tests/unit/test_document_converter_errors.py tests/integration/test_document_converter_routing.py tests/contract/test_document_converter_contracts.py tests/contract/test_document_converter_cli_contracts.py -q
uv run pytest
```

## 5) CLI Smoke Checks

```bash
uv run document-converter /tmp/file.docx
uv run document-converter "   "
```

Expected behavior:

- Success prints JSON payload to stdout and exits `0`.
- Failure prints diagnostics to stderr and exits non-zero.

## Runtime Budget Evidence

- Target converter-focused suite (`tests/unit/test_document_converter.py`) remains under the 30-second budget.
- Latest local run snapshot (2026-02-12): combined converter-focused suite completed in `0.07s`.

## 6) Documentation Sync

- Update relevant module/project docs only if runtime contract wording or user-visible behavior changed.
- Keep `DEFERRED_ACTIONS.md` updated for out-of-scope but required next-phase work.
