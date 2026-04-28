# Integration Test Failures Summary

**Date:** 2026-03-22
**Pipeline Run:** Full pytest suite with LM Studio provider

## Test Results Overview

| Category | Result |
|----------|--------|
| Lint | ✅ Pass |
| Format | ✅ Pass |
| Unit Tests | ✅ Pass |
| Contract Tests | ✅ 431 passed, 37 skipped |
| LLM Client Tests | ✅ 15 passed, 1 skipped |
| Integration Tests | ❌ 58 failed |

---

## Failed Integration Test Files

### 1. `tests/integration/test_batch_processing.py`
- `test_basic_batch_processing`
- `test_batch_processing_with_custom_config`
- `test_batch_processing_different_formats`

**Error:** `BASE_URL environment variable required for provider 'lmstudio'`

---

### 2. `tests/integration/test_cli_scenarios.py`
- `test_cli_single_image_processing`
- `test_cli_multiple_images_with_style`
- `test_cli_batch_processing_with_options`
- `test_cli_json_output_format`
- `test_cli_csv_output_format`
- `test_cli_plain_text_output`
- `test_cli_verbose_output_mode`
- `test_cli_quiet_output_mode`
- `test_cli_timeout_parameter`

**Error:** Missing BASE_URL / VISION_MODEL configuration

---

### 3. `tests/integration/test_invalid_model.py`
- `test_model_validation_failure`
- `test_processing_with_invalid_model`
- `test_malformed_model_name_handling`

**Error:** Environment configuration issues

---

### 4. `tests/integration/test_lmstudio_integration.py`
- `test_basic_generation`

**Error:** Likely requires longer timeout or model loading

---

### 5. `tests/integration/test_model_config.py`
- `test_missing_vision_model_environment`
- `test_empty_vision_model_environment`
- `test_configuration_defaults`

**Error:** VISION_MODEL environment variable handling

---

### 6. `tests/integration/test_module_api_compat.py`
- `test_validate_model_availability_api`
- `test_enhanced_result_structure`
- `test_technical_metadata_structure`
- `test_model_info_in_results`
- `test_confidence_scoring_api`
- `test_separate_timing_metrics`
- `test_environment_configuration_api`
- `test_batch_processing_api_enhancement`

**Error:** Configuration/API compatibility issues

---

### 7. `tests/integration/test_single_image.py`
- `test_basic_single_image_processing`
- `test_single_image_with_custom_config`
- `test_single_image_detailed_style`
- `test_single_image_technical_style`
- `test_single_image_performance_requirements`
- `test_single_image_metadata_completeness`

**Error:** VLM processing failures / environment issues

---

### 8. `tests/integration/test_timeout_behavior.py`
- `test_timeout_behavior_error`
- `test_timeout_behavior_fallback`
- `test_timeout_behavior_continue`
- `test_reasonable_timeout_succeeds`
- `test_timeout_affects_only_vlm_processing`

**Error:** Timeout configuration and VLM inference timeouts

---

## Root Causes

### 1. Missing `BASE_URL` Environment Variable
**Impact:** 15+ tests

When `PROVIDER=lmstudio` is set, the code requires `BASE_URL` to be explicitly set. The error message:
```
BASE_URL environment variable required for provider 'lmstudio'
```

**Fix:** Add `BASE_URL=http://localhost:1234` to test environment

---

### 2. VLM Model Download/First-Run Latency
**Impact:** All VLM-related tests

First VLM test runs require downloading model files (~5 min). Subsequent runs are faster but still slow.

**Error:** `httpx.ReadTimeout` or inference hangs

**Fix:** 
- Use `VLM_TIMEOUT_SECONDS=600` for first run
- Ensure model is pre-downloaded

---

### 3. Missing `VISION_MODEL` Variable
**Impact:** ~25 tests

Some integration tests explicitly check for `VISION_MODEL` environment variable handling, which may not be set in all test environments.

**Fix:** Set `VISION_MODEL="mlx-community/GLM-4.6V-Flash-4bit"`

---

### 4. Ollama Only Has Cloud Models
**Impact:** LLM client tests with default provider

Ollama service has `glm-4.6:cloud` and `minimax-m2:cloud` (cloud models) but no local models.

**Fix:** Use `PROVIDER=lmstudio` for text generation tests

---

## Recommended Test Commands

### Fast Validation (No External Services)
```bash
uv run pytest tests/unit tests/contract -k "not llm_client" -q
```

### With LM Studio (Text Generation)
```bash
PROVIDER=lmstudio BASE_URL=http://localhost:1234 uv run pytest tests/contract/test_llm_client_api.py -v
```

### With VLM Support (Full Integration)
```bash
VISION_MODEL="mlx-community/GLM-4.6V-Flash-4bit" \
VLM_TIMEOUT_SECONDS=600 \
PROVIDER=lmstudio \
BASE_URL=http://localhost:1234 \
uv run pytest -q
```

---

## Action Items

1. [ ] Add `BASE_URL` to integration test fixtures or environment
2. [ ] Pre-download VLM model before CI runs
3. [ ] Add pytest marker for "requires-vlm" tests
4. [ ] Document minimum environment requirements in test README
5. [ ] Consider mocking VLM responses for faster unit-style integration tests
