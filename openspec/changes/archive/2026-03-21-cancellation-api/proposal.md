## Why

Users cannot cancel long-running operations (PDF extraction, image processing, audio transcription) without killing the entire process. This leads to wasted resources, inability to abort expensive API calls, and poor user experience in interactive contexts. As processing operations grow longer with larger files and more complex models, the need for graceful cancellation becomes critical.

## What Changes

- Add `CancellationToken` class to enable cooperative cancellation of long-running operations
- Add `OperationCancelledError` exception for clean error handling
- Integrate cancellation support into streaming operations across all processors
- Add cancellation endpoint to CLI and programmatic API
- Ensure proper resource cleanup on cancellation (temp files, memory, API connections)

## Capabilities

### New Capabilities

- `operation-cancellation`: Cooperative cancellation mechanism for long-running operations, including token management, error handling, and resource cleanup

### Modified Capabilities

<!-- No existing capabilities are being modified - this is a new feature -->

## Impact

**Affected Modules:**
- `anyfile_to_ai/progress_tracker/` - New `cancellation.py` module
- `anyfile_to_ai/pdf_extractor/` - Streaming operations with cancellation support
- `anyfile_to_ai/image_processor/` - Batch processing with cancellation support
- `anyfile_to_ai/audio_processor/` - Transcription operations with cancellation support
- `anyfile_to_ai/document_converter/` - Conversion operations with cancellation support

**API Changes:**
- New `CancellationToken` class with `cancel()` and `is_cancelled` property
- New `OperationCancelledError` exception
- Updated function signatures for streaming operations to accept optional `cancel_token` parameter

**Dependencies:**
- No new external dependencies required
- Internal dependency: progress_tracker module provides cancellation primitives