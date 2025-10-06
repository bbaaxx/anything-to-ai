# Implementation Handoff: LLM Utility Module

**Session Date**: 2025-09-30
**Progress**: 55% complete (22/40 tasks)
**Branch**: `008-utility-module-to`

## Quick Start for Next Session

```bash
# Verify current state
cd <project_root>
git status
uv run pytest tests/contract/test_config_interface.py -v  # Should pass (24/24)
uv run pytest tests/unit/test_cache.py tests/unit/test_retry.py -v  # Should pass (16/16)
uv run python check_file_lengths.py  # Should pass - all files < 250 lines
```

## What's Complete ✅

### Infrastructure (100%)

- ✅ Project structure setup (llm_client/ module)
- ✅ Dependencies installed (httpx>=0.27.0)
- ✅ Configuration for testing and linting

### Data Layer (100%)

- ✅ `llm_client/models.py` - All data models (Message, Usage, ModelInfo, LLMRequest, LLMResponse)
- ✅ `llm_client/exceptions.py` - Complete error hierarchy (9 exception types)
- ✅ `llm_client/config.py` - LLMConfig with validation
- ✅ `llm_client/cache.py` - ModelCache with TTL
- ✅ `llm_client/retry.py` - RetryHandler with exponential backoff

### Adapter Layer (40%)

- ✅ `llm_client/adapters/base.py` - BaseAdapter abstract class
- ✅ `llm_client/adapters/__init__.py` - Factory pattern (ADAPTER_REGISTRY empty)
- ✅ `llm_client/adapters/ollama_adapter.py` - Complete (153 lines)
- ✅ `llm_client/adapters/lmstudio_adapter.py` - Complete (169 lines)
- ❌ `llm_client/adapters/mlx_adapter.py` - **NOT STARTED** ← Next task

### Testing (40/90+ tests implemented)

- ✅ Contract tests copied (90 tests total, only config tests passing)
- ✅ Unit tests created and passing (16 tests)
- ❌ Integration tests not started

## What's Next 🎯

### Immediate Priority: Complete Phase 3.6 (3 tasks)

**T023: Implement MLXAdapter** ⬅️ START HERE

- File: `llm_client/adapters/mlx_adapter.py`
- Must wrap existing `image_processor` VLM functionality
- Translate OpenAI chat format → MLX image processing
- Maintain compatibility with `VISION_MODEL` environment variable
- Target: < 200 lines

**T024: Register Adapters**

- Update `llm_client/adapters/__init__.py`
- Add to ADAPTER_REGISTRY:

  ```python
  from llm_client.adapters.ollama_adapter import OllamaAdapter
  from llm_client.adapters.lmstudio_adapter import LMStudioAdapter
  from llm_client.adapters.mlx_adapter import MLXAdapter

  ADAPTER_REGISTRY = {
      "ollama": OllamaAdapter,
      "lmstudio": LMStudioAdapter,
      "mlx": MLXAdapter,
  }
  ```

**T025: Validate Adapters**

- Run: `uv run pytest tests/contract/test_adapter_interface.py::TestAdapterInterface -v`
- Should pass base adapter contract tests

### Phase 3.7: Main LLM Client (5 tasks)

**T026-T028: Implement LLMClient**

- File: `llm_client/client.py`
- Constructor: Initialize adapter (via factory), cache, retry handler
- `generate()` method: Orchestrate retry, fallback, latency measurement
- `list_models()` method: Use cache (check → fetch → store)
- `invalidate_cache()` method
- `_execute_with_fallback()` helper
- Target: < 250 lines total

**T029: Public API Facade**

- Update `llm_client/__init__.py` to expose:
  - LLMClient (new)
  - LLMConfig, LLMRequest, LLMResponse, Message, ModelInfo, Usage (already exposed)
  - All exception classes (already exposed)
  - `__version__` (already exposed)

**T030: Validate Client**

- Run: `uv run pytest tests/contract/test_llm_client_api.py -v`
- Should pass 30 client API contract tests
- Note: Tests requiring running services may be skipped

### Phase 3.8: Integration Tests (5 tasks)

Create integration test files:

- `tests/integration/test_ollama_integration.py`
- `tests/integration/test_lmstudio_integration.py`
- `tests/integration/test_caching_behavior.py`
- `tests/integration/test_retry_fallback.py`

Mark all with `@pytest.mark.integration`

### Phase 3.9: Documentation & Polish (5 tasks)

- Add docstrings to public APIs
- Verify ≥70% test coverage
- Run linting with ruff
- Verify file sizes < 250 lines
- Test quickstart examples manually

## File Status

| File                                      | Lines | Status         | Notes              |
| ----------------------------------------- | ----- | -------------- | ------------------ |
| `llm_client/models.py`                    | 152   | ✅ Complete    | Under limit        |
| `llm_client/exceptions.py`                | 76    | ✅ Complete    | Under limit        |
| `llm_client/config.py`                    | 79    | ✅ Complete    | Under limit        |
| `llm_client/cache.py`                     | 88    | ✅ Complete    | Under limit        |
| `llm_client/retry.py`                     | 92    | ✅ Complete    | Under limit        |
| `llm_client/adapters/base.py`             | 61    | ✅ Complete    | Under limit        |
| `llm_client/adapters/__init__.py`         | 42    | ⚠️ Incomplete  | Needs registration |
| `llm_client/adapters/ollama_adapter.py`   | 153   | ✅ Complete    | Under limit        |
| `llm_client/adapters/lmstudio_adapter.py` | 169   | ✅ Complete    | Under limit        |
| `llm_client/adapters/mlx_adapter.py`      | 0     | ❌ Not started | Target < 200       |
| `llm_client/client.py`                    | 0     | ❌ Not started | Target < 250       |
| `llm_client/__init__.py`                  | 32    | ⚠️ Incomplete  | Needs LLMClient    |

## Test Commands

```bash
# Config tests (should pass)
uv run pytest tests/contract/test_config_interface.py -v

# Unit tests (should pass)
uv run pytest tests/unit/test_cache.py tests/unit/test_retry.py -v

# All llm_client tests
uv run pytest tests/contract/test_config_interface.py tests/unit/test_cache.py tests/unit/test_retry.py -v

# File length check (should pass)
uv run python check_file_lengths.py

# After T025 - adapter tests (will fail until T023-T024 complete)
uv run pytest tests/contract/test_adapter_interface.py -v

# After T030 - client tests (will fail until T026-T029 complete)
uv run pytest tests/contract/test_llm_client_api.py -v

# After T035 - integration tests (requires Ollama/LM Studio running)
uv run pytest tests/integration/ -v -m integration

# Final coverage check (target ≥70%)
uv run pytest --cov=llm_client --cov-report=term-missing
```

## Key Design Decisions

1. **Architecture**: Adapter pattern for provider abstraction
2. **Caching**: In-memory with TTL (default 5 minutes)
3. **Retry**: Exponential backoff with configurable fallback providers
4. **Error Handling**: Rich exception hierarchy with original error tracking
5. **HTTP Client**: httpx for async/sync support and retry capabilities
6. **Testing**: TDD approach - contract tests written before implementation

## Integration Notes

### MLX Adapter Specifics (T023)

The MLX adapter is special because it wraps the existing `image_processor` module:

- Must maintain compatibility with `VISION_MODEL` environment variable
- Translates OpenAI chat format to MLX image processing calls
- May need to extract image paths from message content
- Should reuse existing VLM error handling from `image_processor.vlm_exceptions`

Example pattern:

```python
from image_processor import process_image, ProcessingConfig
from llm_client.adapters.base import BaseAdapter

class MLXAdapter(BaseAdapter):
    def generate(self, request):
        # Extract image path from message content
        # Call process_image()
        # Translate result to LLMResponse format
        pass
```

### Fallback Behavior (T026-T028)

The client must implement cascading fallback:

1. Try primary provider with retries
2. If all retries fail, try first fallback provider
3. Continue through fallback list
4. Track which provider succeeded in response metadata

## Common Issues & Solutions

**Issue**: Import errors when running tests
**Solution**: Ensure you're in the repo root and use `uv run pytest`

**Issue**: File length violations
**Solution**: Run `uv run python check_file_lengths.py` to identify, then refactor

**Issue**: MLX tests require VISION_MODEL env var
**Solution**: Set before running tests: `export VISION_MODEL=google/gemma-3-4b`

**Issue**: Integration tests fail with ConnectionError
**Solution**: Ensure Ollama/LM Studio running locally, or skip with `-m "not integration"`

## Resources

- **Tasks file**: `specs/008-utility-module-to/tasks.md` (primary reference)
- **Plan**: `specs/008-utility-module-to/plan.md`
- **Data model**: `specs/008-utility-module-to/data-model.md`
- **Contracts**: `specs/008-utility-module-to/contracts/*.py`
- **Quickstart**: `specs/008-utility-module-to/quickstart.md`
- **Research**: `specs/008-utility-module-to/research.md`

## Questions?

Check the design documents in `specs/008-utility-module-to/` for detailed specifications. All contract tests define the expected behavior - when in doubt, consult the test files.

---

**Ready to continue?** Start with T023: Implement MLXAdapter in `llm_client/adapters/mlx_adapter.py`
