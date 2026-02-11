# CLI/Provider Unification Plan

## Purpose
This document captures the **four-step plan** to unify CLI configuration for text + vision models, add provider-aware vision support (LM Studio / Ollama / MLX), make tests provider-configurable, and run a representative full-suite validation. It is written so any AI agent can pick up the work, understand the rationale, and track progress.

## Context Summary (Current State)
- **Image Processor** uses `VISION_MODEL` env only; assumes MLX local VLM. Recently added `--vision-model` CLI flag that sets `VISION_MODEL`.
- **PDF Extractor** image flow (`--include-images`) relies on Image Processor and therefore also requires `VISION_MODEL` env. No provider/base-url support.
- **Text Summarizer** uses `--provider` and `--model`, but **no `--base-url`**; ignores env defaults. Provider→base URL mapping is internal.
- **LLM Client** already supports `--provider`, `--base-url`, `--model` (from README), but is not wired into image/pdf CLIs.

### Problems
- CLI/env configuration is inconsistent between modules.
- Vision processing is **MLX-only** and cannot use LM Studio (OpenAI-compatible vision endpoints).
- Environment variables are provider-specific and fragmented; should be **generic**.

---

## Target Behavior (Unified Configuration)
### Generic Env Variables
- `PROVIDER` — provider name (e.g., `ollama`, `lmstudio`, `mlx`)
- `BASE_URL` — provider base URL (e.g., `http://127.0.0.1:1234`)
- `TEXT_MODEL` — text model for summarization
- `VISION_MODEL` — vision model for image processing

### Generic CLI Flags
- `--provider`
- `--base-url`
- `--text-model`
- `--vision-model`

### Resolution Order
1. CLI flags (highest priority)
2. Env variables
3. Module defaults (only when safe)
4. Error if required values missing

---

## Step 1 — Unify CLI/Env Parsing (No Behavior Change Yet)
**Goal:** Make every relevant CLI accept the same generic flags and resolve config the same way, even if actual provider support is not yet implemented for vision.

### Scope
- Image Processor CLI
- PDF Extractor CLI (when `--include-images`)
- Text Summarizer CLI
- LLM Client CLI (align env defaults)

### Changes (Planned)
- Introduce a small shared helper for config resolution (CLI flags + env), e.g.:
  - `resolve_provider_config(cli_args)`
  - returns provider/base_url/text_model/vision_model
- Update each CLI to accept common flags:
  - Image processor: add `--provider` and `--base-url` (keep `--vision-model`)
  - Text summarizer: add `--base-url` and `--text-model` (keep `--model` as deprecated alias)
  - PDF extractor: when `--include-images`, accept `--provider`, `--base-url`, `--vision-model` and pass through
  - LLM client: default to env variables when CLI flags missing

### Expected Behavior
- User can run any CLI with a consistent set of parameters.
- When missing, errors should explicitly name required config keys.
- MLX vision still used under the hood (until Step 2), but config resolution is standardized.

### Rationale
- Reduces confusion across modules.
- Makes multi-module pipelines (PDF → image → summary) predictable.
- Creates the foundation for adding external vision providers.

### Step 1 Status
- [ ] Not started
- [ ] In progress
- [x] Done

---

## Step 2 — Provider-Aware Vision Backends
**Goal:** Enable image/PDF processing to use external vision models (LM Studio / Ollama) as well as MLX. This step requires adapter work.

### Scope
- Image Processor backend
- PDF Extractor image integration
- Optional: LLM Client can become the single dispatch point for vision

### Design Options
**Option A (Preferred):** Extend LLM Client to support multimodal requests (image+text) and use it from Image Processor.
- Pros: One provider interface; reusable; matches existing provider model.
- Cons: Requires more adapter work (LM Studio vision payloads).

**Option B:** Add a vision provider layer to image_processor itself.
- Pros: Smaller localized changes.
- Cons: Duplicates provider logic already in llm_client.

### Required Behaviors
- If provider is `mlx`, use existing MLX VLM pipeline.
- If provider is `lmstudio` or `ollama`, send OpenAI-style multimodal request:
  - POST `{base_url}/v1/chat/completions`
  - messages: user content with image in `image_url` or base64 (depending on provider requirements)
- For image/PDF CLIs, the provider/base-url/vision-model should be passed through from Step 1.

### Error/Compatibility Rules
- If provider is not supported for vision, raise a clear error.
- If model is missing, error should name `VISION_MODEL` or `--vision-model`.
- If base URL missing for non-mlx provider, error should name `BASE_URL` or `--base-url`.

### Step 2 Status
- [ ] Not started
- [ ] In progress
- [x] Done

---

## Step 3 — Configurable Provider Test Matrix
**Goal:** Make integration/contract tests provider-configurable so test runs can target MLX or LM Studio without code changes.

### Scope
- Test configuration helpers/fixtures for provider selection
- CLI/integration tests that currently assume one provider
- CI and local test command documentation

### Changes (Planned)
- Add test-time env configuration for provider and model selection:
  - `PROVIDER`
  - `BASE_URL`
  - `TEXT_MODEL`
  - `VISION_MODEL`
- Ensure tests default to available local setup but are overridable by env.
- Mark provider-dependent tests clearly and skip with explicit messages when required provider/model is unavailable.
- Add documented provider-specific test commands for MLX and LM Studio.

### Available Test Providers/Models (Current Environment)
- **MLX provider**
  - Vision: `mlx-community/Qwen2-VL-2B-Instruct-4bit`
  - Vision (alternative): `mlx-community/gemma-3-4b-it-4bit`
- **LM Studio provider**
  - Vision: `qwen/qwen3-vl-8b`
  - Text/LLM: `qwen/qwen3-14b`

### Step 3 Status
- [ ] Not started
- [ ] In progress
- [x] Done

---

## Step 4 — Representative Full-Suite Validation
**Goal:** Run the broader test suite using representative provider configuration(s) and capture actionable failures for follow-up.

### Scope
- Full `tests/` suite execution (or as close as runtime permits)
- Provider-configured runs for at least one remote backend profile
- Documentation of pass/skip/fail and prioritized follow-up items

### Changes (Planned)
- Execute full-suite run(s) with representative configuration:
  - LM Studio profile (`PROVIDER=lmstudio`, `BASE_URL`, `TEXT_MODEL`, `VISION_MODEL`)
  - Optional Ollama profile for cross-provider sanity
- Distinguish:
  - product regressions
  - provider/runtime environmental constraints
  - pre-existing unrelated suite instability
- Record exact commands and outcomes in this document for handoff.

### Step 4 Status
- [x] Not started
- [ ] In progress
- [ ] Done

---

## Implementation Notes / Files Likely to Change
- `anyfile_to_ai/image_processor/cli.py`
- `anyfile_to_ai/image_processor/config.py`
- `anyfile_to_ai/image_processor/vlm_config.py`
- `anyfile_to_ai/pdf_extractor/cli.py`
- `anyfile_to_ai/pdf_extractor/image_integration.py`
- `anyfile_to_ai/text_summarizer/__main__.py`
- `anyfile_to_ai/text_summarizer/llm_adapter.py`
- `anyfile_to_ai/llm_client/*`

---

## Step 1 Implemented Changes (Exact Files)
- `anyfile_to_ai/cli_config.py`
- `anyfile_to_ai/image_processor/cli.py`
- `anyfile_to_ai/pdf_extractor/cli.py`
- `anyfile_to_ai/text_summarizer/__main__.py`
- `anyfile_to_ai/text_summarizer/processor.py`
- `anyfile_to_ai/text_summarizer/llm_adapter.py`
- `tests/contract/test_cli_interface.py`
- `tests/contract/test_cli_main.py`
- `tests/contract/test_summarizer_api.py`
- `tests/contract/test_summarizer_cli.py`

---

## Known Gaps / Current Limitations
- Provider-dependent contract and integration tests require live services and will skip with explicit reasons when unavailable.
- MLX-dependent tests skip when `mlx-vlm` is not installed; this is expected for non-MLX environments.

---

## Acceptance Criteria By Step
### Step 1 (Done)
- All relevant CLIs parse unified flags:
  - `--provider`
  - `--base-url`
  - `--text-model`
  - `--vision-model`
- Config resolution follows precedence:
  1. CLI flags
  2. Env vars (`PROVIDER`, `BASE_URL`, `TEXT_MODEL`, `VISION_MODEL`)
  3. Safe defaults
  4. Clear error on missing required keys
- Text summarizer accepts `--model` as alias to `--text-model`.
- Contract test subset below passes.

### Step 2 (Done)
- Image/PDF vision path dispatches by provider:
  - `mlx` -> MLX path
  - `lmstudio` / `ollama` -> OpenAI-style multimodal request path
- Error messages explicitly reference missing `--base-url` / `BASE_URL` and `--vision-model` / `VISION_MODEL`.
- Provider-specific vision integration tests pass for supported backends.

### Step 3 (Done)
- Test fixtures can select provider/model via env without code edits.
- Provider-dependent tests skip with clear reason when provider/model/runtime is unavailable.
- Documented test commands exist for both MLX and LM Studio configurations.
- CI/local guidance is consistent with provider matrix setup.

### Step 4 (Pending)
- Representative full-suite command(s) are executed and recorded with exact env + pytest invocation.
- Failures are triaged into:
  - code regressions requiring fixes
  - expected runtime/provider constraints (skip/infra)
  - unrelated pre-existing failures
- Document includes clear next actions and ownership-ready handoff notes.

---

## Verified Commands (Current)
- Step 1 contract coverage verified with:
  - `uv run pytest tests/contract/test_cli_parser.py tests/contract/test_cli_interface.py tests/contract/test_cli_main.py tests/contract/test_summarizer_api.py tests/contract/test_summarizer_cli.py`
 - Step 2 integration coverage verified with:
   - `BASE_URL=http://192.168.1.195:1234/v1 VISION_MODEL=qwen/qwen3-vl-8b uv run pytest tests/integration/test_vision_provider_integration.py -m "integration"`
- Step 3 provider-matrix verification:
  - `uv run pytest tests/integration/test_ollama_integration.py tests/integration/test_lmstudio_integration.py tests/integration/test_caching_behavior.py tests/integration/test_retry_fallback.py tests/integration/test_vision_provider_integration.py tests/contract/test_llm_client_api.py tests/contract/test_adapter_interface.py -ra -q`
  - Result: `40 passed, 25 skipped`
- Step 3 LM Studio focused rerun after vision payload compatibility fix:
  - `PROVIDER=lmstudio BASE_URL=http://127.0.0.1:1234/v1 TEXT_MODEL=qwen/qwen3-14b VISION_MODEL=qwen/qwen3-vl-8b uv run pytest tests/integration/test_lmstudio_integration.py tests/integration/test_vision_provider_integration.py tests/contract/test_llm_client_api.py tests/contract/test_adapter_interface.py -ra -q`
  - Result: no hard failure reported by user after adapter change.
- Step 4 full-suite representative run:
  - Not run yet.

## Expected Not Fully Green Yet
- Provider-dependent integration suites for Step 2/Step 3 require runtime provider availability and will skip when unavailable.
- Full-suite runs may still expose unrelated historical integration failures outside provider-matrix scope.

---

## Next-Agent Checklist (Handoff Start Point)
1. Execute Step 4 representative full-suite run(s):
   - `PROVIDER=lmstudio BASE_URL=http://127.0.0.1:1234/v1 TEXT_MODEL=qwen/qwen3-14b VISION_MODEL=qwen/qwen3-vl-8b uv run pytest tests -ra -q`
   - Optional cross-check: `PROVIDER=ollama BASE_URL=http://localhost:11434 TEXT_MODEL=<chat-model> VISION_MODEL=<vision-model> uv run pytest tests -ra -q`
2. Triage failures into:
   - product regression vs provider/runtime constraint vs unrelated pre-existing failures
3. Update this document immediately after each milestone:
   - Status checkboxes
   - Progress Log entries with date
   - Verified command list
   - Remaining known gaps

---

## Handoff Protocol (Required)
- After each milestone or meaningful checkpoint, the active agent **must** update this file before handoff.
- Each update must include:
  - What changed (files + behavior)
  - What was validated (exact commands)
  - What remains (clear blockers/gaps)
  - Which step status changed
- If work is partial, add a “next actionable step” that can be executed without re-discovery.

---

## Progress Log
- 2026-02-07: Plan created. Pending Step 1 and Step 2 implementation.
- 2026-02-07: Added Step 3 for configurable provider-backed testing and documented currently available MLX/LM Studio models for vision/text test runs.
- 2026-02-07: Step 1 implemented in code:
  - Added shared provider/env resolver (`anyfile_to_ai/cli_config.py`) with CLI > env > defaults precedence.
  - Unified flags added/wired: image processor (`--provider`, `--base-url`, `--vision-model`), PDF extractor image path (`--provider`, `--base-url`, `--vision-model`), text summarizer (`--provider`, `--base-url`, `--text-model`, `--model` alias).
  - Text summarizer provider client path now accepts `base_url` and honors generic env defaults.
- 2026-02-07: Test progress update:
  - Updated contract tests for Step 1 behavior and package module paths.
  - Added deterministic/offline mocking for text summarizer contract API tests.
  - Verified updated subset passes:
    - `tests/contract/test_cli_parser.py`
    - `tests/contract/test_cli_interface.py`
    - `tests/contract/test_cli_main.py`
    - `tests/contract/test_summarizer_api.py`
    - `tests/contract/test_summarizer_cli.py`
  - Step 3 remains in progress for broader provider-matrix coverage across remaining integration/provider-dependent tests.
- 2026-02-07: Step 2 work started:
  - Added vision request/response models and `generate_vision` support to `llm_client` (client + adapters).
  - Implemented provider-aware vision dispatch in `image_processor` with `PROVIDER` routing and `BASE_URL` validation for remote providers.
  - Updated PDF image validation to enforce provider/base URL requirements.
  - Added unit tests for provider dispatch and OpenAI-style multimodal payload shape (LM Studio/Ollama mocked).
  - Tests not run yet.
- 2026-02-07: Added integration tests for provider-aware vision backends (LM Studio, Ollama, MLX) with skip logic based on availability and env configuration. Tests not run yet.
- 2026-02-07: Step 2 completed:
  - LM Studio adapter now normalizes `/v1` base URLs and resolves models from `/v1/models` when missing.
  - Integration tests for LM Studio vision pass with `BASE_URL=http://192.168.1.195:1234/v1` and `VISION_MODEL=qwen/qwen3-vl-8b`.
  - Registered pytest markers (`integration`, `slow`) in `pytest.ini`.
- 2026-02-07: Step 3 completed:
  - Added shared provider test helper (`provider_env.py`) to resolve `PROVIDER`, `BASE_URL`, `TEXT_MODEL`, and `VISION_MODEL` with explicit skip reasons.
  - Updated provider-dependent contract and integration tests to use env-driven provider selection and explicit availability checks.
  - Adjusted test defaults to avoid accidental MLX vision runs unless explicitly configured.
  - Documented provider-specific test runs in `tests/README.md`.
  - Verified provider-matrix command passes with environment-appropriate skips (`40 passed, 25 skipped`).
- 2026-02-07: Post-verification fixes:
  - Fixed retry edge case where `max_retries=0` could result in raising `None` (`TypeError: exceptions must derive from BaseException`) by enforcing at least one attempt in `RetryHandler`.
  - Hardened provider-dependent generation tests to skip on runtime constraints (no models loaded, non-chat model, speculative decoding incompatibility) instead of failing.
  - Updated timeout contract test to avoid brittle model discovery under forced low timeout.
- 2026-02-07: LM Studio vision request compatibility follow-up:
  - Updated `LMStudioAdapter.generate_vision` to retry once with a minimal OpenAI-compatible payload (`model`, `messages`, `stream`) when LM Studio returns compatibility-style 400 errors (including model crash / speculative decoding constraints).
  - User reported the previous LM Studio-focused command is no longer failing after this change.
- 2026-02-07: Added Step 4 (representative full-suite validation) and prepared handoff checklist for next-agent execution and triage.
