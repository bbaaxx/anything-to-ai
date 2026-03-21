# Improvements to Processing Pipeline

> **Date**: 2026-03-18  
> **Source Analysis**: MLX-Video-OCR-DeepSeek-Apple-Silicon, LegalAI, anything-to-ai  
> **Purpose**: Document findings and recommended improvements for the anything-to-ai processing pipeline

---

## Executive Summary

This document captures insights from analyzing MLX-Video-OCR-DeepSeek-Apple-Silicon, a mature Apple Silicon-optimized OCR implementation, and identifies improvements that can be applied to enhance anything-to-ai's reliability, scalability, and user experience.

**Key Finding**: anything-to-ai has a superior extraction strategy (native text first, VLM as fallback) but lacks the operational robustness of MLX-Video-OCR for large file handling and error recovery.

---

## Repository Comparison Overview

### Technology Stack Comparison

| Aspect | MLX-Video-OCR | LegalAI | anything-to-ai |
|--------|---------------|---------|----------------|
| **OCR Engine** | DeepSeek-OCR via MLX-VLM | Tesseract (CPU-only) | MLX-VLM (fallback) + pdfplumber (native) |
| **Hardware Acceleration** | Metal GPU (Neural Engine) | CPU only | Metal GPU (via MLX) |
| **Text Extraction** | Image rendering + VLM | Image rendering + Tesseract | Native PDF text + VLM fallback |
| **Architecture** | VLM-first (all images) | OCR + LLM pipeline | Intelligent routing |

### Strengths by Repository

| Repository | Key Strengths |
|------------|---------------|
| **MLX-Video-OCR** | Subprocess isolation, timeout protection, task state persistence, cancellation API, batch processing with progress |
| **LegalAI** | LLM post-processing for structured data extraction, domain-specific analysis |
| **anything-to-ai** | Native text extraction first (efficient), intelligent routing, modular architecture, multiple output formats, multi-format support (PDF/Image/Audio/Text) |

---

## Recommended Improvements

### Priority 1: Critical for Production Reliability

#### 1.1 Subprocess + Timeout Protection

**Problem**: VLM inference can hang indefinitely on problematic images or memory pressure.

**MLX-Video-OCR Solution** (`engines/ocr_engine.py`):
```python
def generate_with_timeout_and_process(image, prompt, max_tokens=8192, timeout=160):
    output_queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=_run_ocr_in_process,
        args=(image_bytes, prompt, max_tokens, output_queue)
    )
    process.start()
    process.join(timeout=timeout)

    if process.is_alive():
        print(f"⏰ OCR processing timed out. Terminating subprocess.")
        process.terminate()
        process.join(timeout=5)
        if process.is_alive():
            process.kill()
        raise TimeoutError("OCR processing timeout")
```

**Recommendation**: Add `TimeoutContext` class or wrap VLM calls in subprocess with configurable timeout.

**Implementation Location**: `anyfile_to_ai/image_processor/vlm_processor.py`

---

#### 1.2 Task State Persistence

**Problem**: Large file processing is lost if the process crashes or is interrupted.

**MLX-Video-OCR Solution** (`routes/pdf.py`, `shared_state.py`):
```python
# Task state structure
pdf_tasks[task_id] = {
    "pdf_path": str(pdf_save_path),
    "thumbnails": thumbnails,
    "extracted_images": image_files,
    "processed_pages": {},  # Track which pages are done
    "content_type": content_type,
    "subcategory": subcategory,
    "complexity": complexity,
    "batch_index": 0,
    "created_at": datetime.now(),
    "total_pages": total_pages,
}
```

**Recommendation**: Add `TaskManager` class that:
- Persists task state to JSON file (`.anything-to-ai/tasks/{task_id}.json`)
- Allows resuming from last checkpoint
- Tracks which pages/images have been successfully processed
- Auto-cleanup of old tasks (configurable TTL)

**Implementation Location**: New module `anyfile_to_ai/task_manager/`

---

### Priority 2: High Impact on User Experience

#### 2.1 Cancellation API

**Problem**: Users cannot cancel long-running operations without killing the process.

**MLX-Video-OCR Solution** (`routes/pdf.py`):
```python
@pdf_bp.route("/api/pdf/cancel", methods=["POST"])
def cancel_pdf_task():
    data = request.get_json()
    task_id = data.get("task_id")
    
    if task_id in pdf_tasks:
        # Cleanup resources
        pdf_file_path = pdf_tasks[task_id].get("pdf_path")
        if pdf_file_path and os.path.exists(pdf_file_path):
            os.remove(pdf_file_path)
        del pdf_tasks[task_id]
        gc.collect()
        return jsonify({"success": True})
```

**Recommendation**: Add `CancellationToken` support:
```python
class CancellationToken:
    def __init__(self):
        self._cancelled = False
    
    def cancel(self):
        self._cancelled = True
    
    @property
    def is_cancelled(self):
        return self._cancelled

def extract_text_streaming(file_path, config, cancel_token=None):
    for page_num, page in enumerate(pdf.pages):
        if cancel_token and cancel_token.is_cancelled:
            raise OperationCancelledError("Extraction cancelled by user")
        yield page_result
```

**Implementation Location**: New module `anyfile_to_ai/progress_tracker/cancellation.py`

---

#### 2.2 Retry with Token Reduction Fallback

**Problem**: Large token requests can fail due to memory constraints or context length issues.

**MLX-Video-OCR Solution** (`engines/ocr_engine.py`):
```python
max_retries = 3
retry_tokens = [min(max_tokens, 2048), min(max_tokens, 512), 256]

for attempt in range(max_retries):
    try:
        current_max_tokens = retry_tokens[attempt]
        res = generate(
            model=_model_instance,
            processor=_processor_instance,
            image=img,
            prompt=prompt,
            max_tokens=current_max_tokens,
            temperature=0.0,
        )
        if res is not None:
            break
    except Exception as e:
        if attempt < max_retries - 1:
            time.sleep(1)
            continue
        else:
            raise
```

**Recommendation**: Extend `CircuitBreaker` with token reduction strategy:
```python
class VLMProcessor:
    def process_with_fallback(self, image, max_tokens=8192):
        token_levels = [min(max_tokens, 8192), 4096, 2048, 1024, 512]
        
        for tokens in token_levels:
            try:
                return self.generate(image, max_tokens=tokens)
            except (MemoryError, ContextLengthError) as e:
                continue  # Try smaller token count
            except Exception:
                raise  # Other errors should not retry
        
        raise VLMProcessingError("Failed at all token levels")
```

**Implementation Location**: `anyfile_to_ai/image_processor/vlm_processor.py`

---

### Priority 3: Quality and Performance

#### 3.1 Image Preprocessing Pipeline

**Problem**: Raw images may not be optimal for VLM OCR accuracy.

**MLX-Video-OCR Solution** (`preprocessing.py`):
```python
PREPROCESSING_CONFIG = {
    "Document": {
        "Academic": {
            "Tiny": {"image_size": (512, 512), "max_tokens": 512},
            "Medium": {"image_size": (1024, 1024), "max_tokens": 2048},
            "Large": {"image_size": (1536, 1536), "max_tokens": 8192},
        },
        "Handwritten": {...},
        "Receipt": {...},
    },
    "Video": {...},
}

def preprocess_image_by_config(img, target_size):
    # Apply contrast enhancement
    # Apply sharpening
    # Resize to target_size
    return processed_img
```

**Recommendation**: Extend `image_adapter.py` with preprocessing options:
- Contrast enhancement
- Deskewing (rotation correction)
- Noise reduction
- Adaptive image sizing based on content complexity
- DPI normalization for scanned documents

**Implementation Location**: `anyfile_to_ai/image_processor/preprocessing.py` (new module)

---

#### 3.2 Batch API with Progress State

**Problem**: Current streaming is stateless; clients cannot resume or track partial progress.

**MLX-Video-OCR Solution** (`routes/pdf.py`):
```python
@pdf_bp.route("/api/pdf/process-batch", methods=["POST"])
def process_pdf_batch():
    data = request.get_json()
    task_id = data.get("task_id")
    batch_index = data.get("batch_index", 0)
    batch_size = data.get("batch_size", 2)
    processed_images = data.get("processed_images", {})  # Track what's done

    # Process only unprocessed items
    start_page_idx = batch_index * batch_size
    end_page_idx = min(start_page_idx + batch_size, total_pages)
    
    return {
        "success": True,
        "results": results,
        "has_more": end_page_idx < total_pages,
        "next_batch_index": batch_index + 1 if has_more else None,
        "processed_pages": end_page_idx,
    }
```

**Recommendation**: Add stateful batch processor:
```python
class BatchProcessor:
    def __init__(self, task_id, source_path, config):
        self.state = TaskState.load_or_create(task_id, source_path, config)
    
    def process_next_batch(self, batch_size=5):
        # Find unprocessed items
        unprocessed = self.state.get_unprocessed()
        batch = unprocessed[:batch_size]
        
        for item in batch:
            result = self.process_item(item)
            self.state.mark_completed(item.id, result)
        
        self.state.save()
        return BatchResult(
            results=batch,
            has_more=len(unprocessed) > batch_size,
            next_batch_index=self.state.next_index,
            total_processed=self.state.completed_count,
        )
```

**Implementation Location**: `anyfile_to_ai/task_manager/batch_processor.py`

---

#### 3.3 Explicit Memory Management

**Problem**: Python's garbage collection may not be fast enough for large batch processing.

**MLX-Video-OCR Solution** (`routes/pdf.py`):
```python
try:
    for page_num in range(start_page_idx, end_page_idx):
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        text = generate_with_timeout_and_process(...)
        results.append({"page": page_num, "text": text})
        
        # Explicit cleanup
        img.close()
        if pix is not None:
            del pix
        del img
        gc.collect()  # Force garbage collection
finally:
    if doc:
        doc.close()
    gc.collect()
```

**Recommendation**: Add context managers for resource cleanup:
```python
@contextmanager
def pdf_page_context(doc, page_num):
    try:
        page = doc[page_num]
        yield page
    finally:
        del page
        gc.collect()

@contextmanager  
def image_resource(pil_image):
    try:
        yield pil_image
    finally:
        pil_image.close()
        gc.collect()

# Usage
with pdf_page_context(doc, page_num) as page:
    pix = page.get_pixmap(...)
    # ... process ...
```

**Implementation Location**: `anyfile_to_ai/utils/resource_management.py` (new module)

---

### Priority 4: Feature Parity

#### 4.1 Video Frame Extraction

**MLX-Video-OCR Solution** (`utils/video_utils.py`):
- Intelligent frame extraction (scene change detection)
- Fixed interval extraction
- Adaptive extraction based on video content
- Preview thumbnails generation

**Recommendation**: Add `video_processor` module (similar to audio_processor pattern):
```python
# anyfile_to_ai/video_processor/
# - extractor.py: Frame extraction with multiple methods
# - detector.py: Scene change detection
# - cli.py: Command-line interface
# - formatters.py: Output formatting
```

---

#### 4.2 LLM Post-Processing (from LegalAI)

**LegalAI Solution** (`llm_analyzer.py`):
```python
# Two-stage pipeline: OCR → Raw Text → LLM → Structured Data
result = model.respond(prompt, response_format=schema)
return result.parsed  # Returns structured JSON
```

**Recommendation**: Add optional LLM analysis layer:
```python
def extract_with_analysis(source, analysis_schema, provider="lmstudio"):
    # Stage 1: Extract text
    text = extract_text(source)
    
    # Stage 2: Analyze with LLM
    analysis_prompt = build_prompt(text, analysis_schema)
    structured = llm_client.analyze(analysis_prompt, schema=analysis_schema)
    
    return ExtractionWithAnalysis(
        raw_text=text,
        structured_analysis=structured,
    )
```

---

## Implementation Priority Matrix

| Priority | Improvement | Impact | Effort | Risk |
|----------|-------------|--------|--------|------|
| 🔴 **P0** | Subprocess + Timeout | Prevents hangs/crashes | Medium | Low |
| 🔴 **P0** | Task State Persistence | Crash recovery | Medium | Low |
| 🟡 **P1** | Cancellation API | UX improvement | Low | Low |
| 🟡 **P1** | Retry with Fallback | Reliability | Low | Low |
| 🟡 **P1** | Memory Management | Stability | Medium | Medium |
| 🟢 **P2** | Image Preprocessing | Quality | High | Medium |
| 🟢 **P2** | Batch API State | UX improvement | Medium | Low |
| 🟢 **P2** | Video Support | Feature parity | High | Medium |
| 🟢 **P2** | LLM Post-Processing | Domain expertise | Medium | Medium |

---

## Architecture Considerations

### Backward Compatibility

All improvements must maintain backward compatibility:
- CLI interfaces should remain stable
- Output formats should not change without major version bump
- Existing code using current APIs should continue to work

### Module Boundaries

```
anyfile_to_ai/
├── pdf_extractor/       # Existing - add preprocessing.py, streaming enhancements
├── image_processor/     # Existing - add timeout protection, retry logic
├── audio_processor/     # Existing - consider timeout support
├── task_manager/        # NEW - task state, batch processing
│   ├── __init__.py
│   ├── models.py        # TaskState, BatchResult
│   ├── persistence.py   # JSON file persistence
│   ├── cancellation.py  # CancellationToken
│   └── batch_processor.py
├── utils/               # Existing - add resource_management.py
├── document_converter/   # Existing - integrate task_manager
└── ...
```

### Configuration

New configuration options should be added to existing config patterns:
```python
# Environment variables
ANYTHING2AI_TIMEOUT_SECONDS=300
ANYTHING2AI_MAX_RETRIES=3
ANYTHING2AI_TASK_TTL_HOURS=24
ANYTHING2AI_ENABLE_PREPROCESSING=true

# Or via config file
[processing]
timeout_seconds = 300
max_retries = 3
enable_preprocessing = true
preprocessing_dpi = 300

[tasks]
persistence_enabled = true
ttl_hours = 24
cleanup_interval_minutes = 60
```

---

## Testing Strategy

### Unit Tests
- `test_timeout_context.py` - Timeout behavior
- `test_cancellation_token.py` - Cancel flag behavior
- `test_retry_fallback.py` - Token reduction logic
- `test_memory_cleanup.py` - Resource cleanup

### Integration Tests
- Large PDF processing (100+ pages)
- Process interruption and resume
- Timeout during VLM inference
- Memory pressure scenarios

### Contract Tests
- CLI output format unchanged
- Streaming output backward compatible
- Error messages remain consistent

---

## References

- MLX-Video-OCR-DeepSeek-Apple-Silicon: `mlx_video_ocr/engines/ocr_engine.py`
- MLX-Video-OCR-DeepSeek-Apple-Silicon: `mlx_video_ocr/routes/pdf.py`
- MLX-Video-OCR-DeepSeek-Apple-Silicon: `mlx_video_ocr/shared_state.py`
- LegalAI: `llm_analyzer.py`
- anything-to-ai: `pdf_extractor/streaming.py`
- anything-to-ai: `image_processor/vlm_processor.py`

---

## Change Log

| Date | Author | Changes |
|------|--------|---------|
| 2026-03-18 | AI Analysis | Initial document creation |
