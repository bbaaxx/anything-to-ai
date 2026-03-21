## ADDED Requirements

### Requirement: CancellationToken creation and state management

The system SHALL provide a `CancellationToken` class that allows operations to be cooperatively cancelled.

#### Scenario: Create token in non-cancelled state
- **WHEN** a new `CancellationToken` is instantiated
- **THEN** the `is_cancelled` property SHALL return `False`

#### Scenario: Cancel token changes state
- **WHEN** the `cancel()` method is called on a `CancellationToken`
- **THEN** the `is_cancelled` property SHALL return `True` for all subsequent checks

#### Scenario: Token state is mutable and shared
- **WHEN** a token reference is shared between caller and operation
- **THEN** changes to the token state SHALL be visible to all holders of the reference

### Requirement: Operation cancellation support

Streaming operations SHALL support cooperative cancellation via an optional `cancel_token` parameter.

#### Scenario: Operation completes without cancellation
- **WHEN** a streaming operation is called with `cancel_token=None` or no cancellation occurs
- **THEN** the operation SHALL complete normally and yield all results

#### Scenario: Operation respects cancellation request
- **WHEN** a streaming operation receives a `CancellationToken` that becomes cancelled during execution
- **THEN** the operation SHALL raise `OperationCancelledError` at the next iteration boundary

#### Scenario: Cancellation preserves partial results
- **WHEN** an operation is cancelled mid-execution
- **THEN** the operation SHALL yield all completed iterations before raising `OperationCancelledError`

### Requirement: OperationCancelledError exception

The system SHALL provide a dedicated exception for cancelled operations.

#### Scenario: Exception indicates cancellation source
- **WHEN** an `OperationCancelledError` is raised
- **THEN** the exception message SHALL indicate the operation was cancelled by user request

#### Scenario: Exception is catchable separately from other errors
- **WHEN** catching exceptions from streaming operations
- **THEN** `OperationCancelledError` SHALL be catchable without catching `KeyboardInterrupt` or `SystemExit`

### Requirement: Resource cleanup on cancellation

Operations SHALL clean up resources when cancelled.

#### Scenario: Temporary files cleaned on cancellation
- **WHEN** an operation creates temporary files and is cancelled
- **THEN** the operation SHALL remove temporary files before raising `OperationCancelledError`

#### Scenario: Memory released on cancellation
- **WHEN** an operation holds significant memory and is cancelled
- **THEN** the operation SHALL release references to allow garbage collection before raising `OperationCancelledError`

### Requirement: Backward compatibility

Existing code SHALL continue to work without modification.

#### Scenario: Existing calls work unchanged
- **WHEN** existing code calls streaming operations without a `cancel_token` parameter
- **THEN** the operation SHALL behave identically to the current implementation

#### Scenario: Optional parameter is truly optional
- **WHEN** a streaming operation is called with `cancel_token=None` (explicitly or by default)
- **THEN** the operation SHALL proceed without cancellation support overhead