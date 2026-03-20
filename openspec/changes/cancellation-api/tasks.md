## 1. Core Cancellation Module

- [ ] 1.1 Create `anyfile_to_ai/progress_tracker/cancellation.py` module
- [ ] 1.2 Implement `CancellationToken` class with `cancel()` method and `is_cancelled` property
- [ ] 1.3 Implement `OperationCancelledError` exception class
- [ ] 1.4 Add `__all__` exports and module docstring
- [ ] 1.5 Export cancellation types from `progress_tracker/__init__.py`

## 2. PDF Extractor Integration

- [ ] 2.1 Add `cancel_token: CancellationToken | None = None` parameter to `extract_text_streaming()` in `pdf_extractor`
- [ ] 2.2 Add cancellation check at each page iteration in streaming extraction
- [ ] 2.3 Yield partial results before raising `OperationCancelledError`
- [ ] 2.4 Clean up temporary PDF files on cancellation

## 3. Image Processor Integration

- [ ] 3.1 Add `cancel_token` parameter to batch processing functions in `image_processor`
- [ ] 3.2 Add cancellation check at each image iteration
- [ ] 3.3 Yield partial results before raising `OperationCancelledError`

## 4. Audio Processor Integration

- [ ] 4.1 Add `cancel_token` parameter to transcription functions in `audio_processor`
- [ ] 4.2 Add cancellation check at chunk/segment boundaries
- [ ] 4.3 Yield partial results before raising `OperationCancelledError`

## 5. Document Converter Integration

- [ ] 5.1 Add `cancel_token` parameter to conversion functions in `document_converter`
- [ ] 5.2 Add cancellation check at conversion boundaries
- [ ] 5.3 Clean up temporary conversion files on cancellation

## 6. Unit Tests

- [ ] 6.1 Create `tests/unit/test_cancellation.py` with tests for `CancellationToken`
- [ ] 6.2 Add tests for `OperationCancelledError` exception
- [ ] 6.3 Add tests for cancellation in PDF extractor streaming
- [ ] 6.4 Add tests for cancellation in image processor batch operations
- [ ] 6.5 Add tests for cancellation in audio processor transcription
- [ ] 6.6 Add tests for cancellation in document converter operations
- [ ] 6.7 Add tests for partial result yielding on cancellation
- [ ] 6.8 Add tests for resource cleanup on cancellation

## 7. Integration Tests

- [ ] 7.1 Create `tests/integration/test_cancellation_integration.py`
- [ ] 7.2 Test end-to-end cancellation across module boundaries
- [ ] 7.3 Test cancellation with actual file processing

## 8. Documentation

- [ ] 8.1 Update `progress_tracker/README.md` with cancellation usage examples
- [ ] 8.2 Add cancellation examples to module READMEs (pdf_extractor, image_processor, audio_processor)
- [ ] 8.3 Update main `README.md` with cancellation feature overview