## Why

Large token requests during VLM processing can fail due to memory constraints or context length issues, causing complete processing failure even when smaller token outputs would suffice. Users processing large images or complex documents currently have no automatic recovery when the model hits resource limits.

## What Changes

- Add token reduction fallback strategy to `VLMProcessor` that progressively tries smaller `max_tokens` values on failure
- Introduce `VLMMemoryError` and `VLMContextLengthError` exception types for granular error classification
- Add configuration option `enable_token_fallback` (default: `true`) and `token_fallback_levels` to `VLMConfig`
- Implement retry logic with progressive token reduction: `8192 → 4096 → 2048 → 1024 → 512`
- Preserve existing timeout/fallback behavior; token reduction runs before timeout handling

## Capabilities

### New Capabilities

- `token-reduction-fallback`: Progressive token reduction strategy when VLM processing fails due to memory or context length constraints. Provides automatic recovery without user intervention.

### Modified Capabilities

- None (new capability, no existing spec modifications)

## Impact

- **Code**: `anyfile_to_ai/image_processor/vlm_processor.py` - add `_process_with_token_fallback()`, `process_with_fallback()` methods
- **Code**: `anyfile_to_ai/image_processor/vlm_exceptions.py` - add `VLMMemoryError`, `VLMContextLengthError` exceptions
- **Code**: `anyfile_to_ai/image_processor/vlm_config.py` - add fallback configuration options
- **API**: New methods on `VLMProcessor` class, backward compatible
- **Dependencies**: None (uses existing infrastructure)
- **Systems**: No external system changes