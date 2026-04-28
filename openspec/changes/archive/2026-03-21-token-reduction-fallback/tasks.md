## 1. Exception Types

- [x] 1.1 Add `VLMMemoryError` exception class to `vlm_exceptions.py` inheriting from `VLMProcessingError`
- [x] 1.2 Add `VLMContextLengthError` exception class to `vlm_exceptions.py` inheriting from `VLMProcessingError`
- [x] 1.3 Update `vlm_exceptions.py` `__all__` exports to include new exception types
- [x] 1.4 Add memory/context error detection helper function `_is_memory_or_context_error()` in `vlm_processor.py`

## 2. Configuration

- [x] 2.1 Add `enable_token_fallback: bool = True` field to `VLMConfig` dataclass
- [x] 2.2 Add `token_fallback_levels: list[int] | None = None` field to `VLMConfig` dataclass
- [x] 2.3 Add `_get_default_fallback_levels()` helper to compute default levels from initial max_tokens
- [x] 2.4 Update `ModelConfiguration` conversion in `_convert_config()` to preserve fallback settings

## 3. Core Implementation

- [x] 3.1 Add `_process_with_token_fallback()` private method to `VLMProcessor` class
- [x] 3.2 Implement token reduction loop with configurable levels
- [x] 3.3 Add `process_with_fallback()` public method to `VLMProcessor` class
- [x] 3.4 Update `__init__.py` exports if needed for new public API

## 4. Tests

- [x] 4.1 Add unit tests for `VLMMemoryError` and `VLMContextLengthError` exception classes
- [x] 4.2 Add unit tests for `_is_memory_or_context_error()` detection helper
- [x] 4.3 Add unit tests for `VLMConfig` fallback configuration fields
- [x] 4.4 Add unit tests for `_process_with_token_fallback()` retry logic
- [x] 4.5 Add unit tests for `process_with_fallback()` public method
- [x] 4.6 Add integration test for fallback cascade with exhausted levels
- [x] 4.7 Add test for backward compatibility: `process_image_with_vlm()` behavior unchanged

## 5. Documentation

- [x] 5.1 Update `anyfile_to_ai/image_processor/README.md` with fallback configuration options
- [x] 5.2 Add docstrings to new methods with parameter descriptions and return types