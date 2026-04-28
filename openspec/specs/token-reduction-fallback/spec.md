## ADDED Requirements

### Requirement: Token reduction fallback automatically retries with smaller max_tokens

The system SHALL automatically retry VLM processing with progressively smaller `max_tokens` values when memory or context length errors occur.

#### Scenario: Memory error triggers fallback to smaller tokens
- **WHEN** VLM processing raises a memory-related error
- **THEN** the system SHALL retry with the next smaller token level from the configured fallback sequence
- **AND** the system SHALL continue retrying until success or all levels exhausted

#### Scenario: Context length error triggers fallback
- **WHEN** VLM processing raises a context length error
- **THEN** the system SHALL retry with the next smaller token level
- **AND** the system SHALL continue until success or all levels exhausted

#### Scenario: All token levels exhausted returns error
- **WHEN** all configured token fallback levels have been tried without success
- **THEN** the system SHALL raise `VLMProcessingError` with details about the failure cascade
- **AND** the error message SHALL include all attempted token levels

### Requirement: Configurable token fallback levels

The system SHALL allow users to configure token fallback levels via `VLMConfig`.

#### Scenario: Default fallback levels applied
- **WHEN** no `token_fallback_levels` is specified in configuration
- **THEN** the system SHALL use default levels `[min(original_max_tokens, 8192), 4096, 2048, 1024, 512]`

#### Scenario: Custom fallback levels used
- **WHEN** `token_fallback_levels` is specified in configuration
- **THEN** the system SHALL use the custom levels in the specified order
- **AND** the first level SHALL be capped at the original `max_tokens` value

#### Scenario: Fallback disabled via configuration
- **WHEN** `enable_token_fallback` is set to `False`
- **THEN** the system SHALL NOT attempt token reduction on failure
- **AND** the system SHALL propagate the original error immediately

### Requirement: Granular exception types for failure classification

The system SHALL provide specific exception types for memory and context length failures.

#### Scenario: Memory errorraised on out-of-memory
- **WHEN** VLM processing fails due to memory constraints
- **THEN** the system SHALL raise `VLMMemoryError`

#### Scenario: Context length error raised on context exceeded
- **WHEN** VLM processing fails due to context length limits
- **THEN** the system SHALL raise `VLMContextLengthError`

#### Scenario: Exceptions inherit from VLMProcessingError
- **WHEN** any new exception type is defined
- **THEN** it SHALL inherit from `VLMProcessingError`
- **AND** existing `except VLMProcessingError` catches SHALL continue to work

### Requirement: Backward compatible API extension

The system SHALL extend `VLMProcessor` with fallback functionality without breaking existing API contracts.

#### Scenario: Existing process_image_with_vlm unchanged
- **WHEN** calling `process_image_with_vlm()` with existing configuration
- **THEN** the system SHALL behave identically to current implementation
- **AND** no token fallback SHALL be applied unless explicitly enabled

#### Scenario: New process_with_fallback method available
- **WHEN** calling the new `process_with_fallback()` method
- **THEN** the system SHALL apply token reduction fallback on applicable errors
- **AND** return results following the same contract as `process_image_with_vlm()`