# Quickstart: Implementing Spec 017

Feature: `specs/017-output-formatter-unification/spec.md`

## 1) Validate Baseline

```bash
uv run pytest tests/contract/test_cli_output.py -q
uv run pytest tests/contract/test_timestamp_contracts.py -q
```

## 2) Add Failing Tests First (Phase A)

Create tests in this order before implementation:

1. `tests/unit/test_shared_output_formatter_plain.py`
2. `tests/unit/test_shared_output_formatter_markdown.py`
3. `tests/unit/test_shared_output_formatter_json.py`
4. `tests/unit/test_shared_output_metadata_normalization.py`
5. `tests/unit/test_shared_output_formatter_errors.py`

Required failing assertions:

- profile-specific plain/markdown/json parity for baseline fixtures
- metadata include/exclude behavior by caller flag
- unknown metadata key pass-through under extension space
- deterministic JSON serialization for equivalent payloads
- stable explicit errors for unsupported format/profile

## 3) Implement Phase A (No Behavior Change)

- Add `anyfile_to_ai/output_formatter/` package and shared interfaces.
- Add module-local adapter shims without changing public signatures.
- Keep existing formatter entry points callable.

## 4) Run Phase A Gates

```bash
uv run pytest tests/unit/test_shared_output_formatter_plain.py tests/unit/test_shared_output_formatter_markdown.py tests/unit/test_shared_output_formatter_json.py tests/unit/test_shared_output_metadata_normalization.py tests/unit/test_shared_output_formatter_errors.py -q
uv run pytest tests/contract/test_output_formatter_unified_contract.py tests/contract/test_cli_output.py tests/contract/test_timestamp_contracts.py -q
```

## 5) Migrate Modules in Phase B Order

Migration order:

1. `text_summarizer`
2. `image_processor`
3. `pdf_extractor`
4. `audio_processor`

For each module:

- add/extend failing integration equivalence test (`tests/integration/test_formatter_equivalence_<module>.py`)
- route formatter calls to shared profile through shim
- run unit + integration + contract suites before advancing
- keep module-local rollback path

## 6) Complete Phase C Retirement

- remove duplicate module-local formatter internals after parity gates and deprecation window
- keep compatibility wrappers for one release cycle

## 7) Run Full Quality Gates

```bash
uv run ruff check .
uv run ruff format .
uv run pytest
```

## 8) Documentation Sync

- Update `README.md` with architecture + compatibility policy.
- Update module READMEs for `pdf_extractor`, `image_processor`, `audio_processor`, and `text_summarizer`.
- Update CLI help/docs where formatter behavior and metadata flags are described.

## Verification Outcomes (2026-02-13)

- `uv run pytest tests/unit/test_shared_output_formatter_plain.py tests/unit/test_shared_output_formatter_markdown.py tests/unit/test_shared_output_formatter_json.py tests/unit/test_shared_output_metadata_normalization.py tests/unit/test_shared_output_formatter_errors.py -q` -> passed.
- `uv run pytest tests/contract/test_output_formatter_unified_contract.py tests/contract/test_cli_output.py tests/contract/test_timestamp_contracts.py -q` -> passed.
- `uv run pytest tests/integration/test_formatter_equivalence_text.py tests/integration/test_formatter_equivalence_image.py tests/integration/test_formatter_equivalence_pdf.py tests/integration/test_formatter_equivalence_audio.py tests/integration/test_formatter_cli_api_parity.py -q` -> passed.
- `uv run ruff check .` -> passed.
- `uv run ruff format .` -> no formatting changes needed.
- `uv run pytest` -> passed (`957 passed, 231 skipped`).
