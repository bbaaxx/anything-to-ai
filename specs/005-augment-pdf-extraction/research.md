# Research: Enhanced PDF Extraction with Image Description

**Date**: 2025-09-29
**Feature**: 005-augment-pdf-extraction

## Decision Summary

### PDF Image Extraction Approach
**Decision**: Use pdfplumber's crop-and-convert strategy with position context preservation
**Rationale**: pdfplumber provides rich metadata (coordinates, dimensions) but not direct image bytes; crop/to_image workflow provides clean PIL images suitable for VLM processing
**Alternatives considered**: Direct image byte extraction (not available in pdfplumber), external PDF parsing libraries (violates minimal dependencies principle)

### Module Integration Pattern
**Decision**: Adapter pattern with dependency injection between pdf_extractor and image_processor modules
**Rationale**: Maintains loose coupling, preserves existing module boundaries, enables testing in isolation
**Alternatives considered**: Direct import coupling (violates modular architecture), new monolithic module (violates composition-first principle)

### Error Handling Strategy
**Decision**: Progressive degradation with hierarchical error handling
**Rationale**: Individual image failures should not break entire PDF extraction; provides graceful fallbacks
**Alternatives considered**: Fail-fast on any error (poor UX), silent failures (loss of information)

### Performance Architecture
**Decision**: Dynamic batch processing with memory monitoring and backpressure controls
**Rationale**: Large PDFs with many images require resource management; parallel processing improves throughput
**Alternatives considered**: Sequential processing (too slow), fixed batch sizes (memory issues), unlimited parallelism (resource exhaustion)

### Backward Compatibility Approach
**Decision**: Feature flags with configuration extension pattern
**Rationale**: Preserves existing API behavior, allows gradual adoption, maintains constitutional compliance
**Alternatives considered**: Breaking API changes (violates experimental mindset), separate module (code duplication)

## Technical Findings

### Image Position Context Preservation
- pdfplumber provides precise bounding box coordinates (x0, x1, y0, y1)
- Page height coordinate transformation needed: `page.height - y_coordinate`
- Image sequence numbering enables inline text placement: `[Image 1: description]`

### Resource Management Requirements
- MLX-VLM memory usage: ~512MB per model load
- Recommended batch size: 2-4 images for memory efficiency
- PIL image cleanup critical for long-running processes
- ThreadPoolExecutor preferred over ProcessPoolExecutor (shared model memory)

### Configuration Extension Pattern
```python
@dataclass
class EnhancedExtractionConfig(ExtractionConfig):
    include_images: bool = False
    image_processing_config: Optional[ProcessingConfig] = None
    image_fallback_text: str = "[Image: processing failed]"
    max_images_per_page: Optional[int] = None
```

### Error Hierarchy Integration
- Extend existing PDFExtractionError hierarchy
- New exceptions: ImageExtractionError, VLMConfigurationError
- Circuit breaker pattern for VLM service failures
- Fallback text injection when individual images fail

## Implementation Patterns

### Streaming Architecture Extension
Leverage existing streaming infrastructure with async image processing pipeline

### Position-Aware Text Insertion
Calculate insertion points based on image coordinates and reading flow order

### Memory-Aware Batch Processing
Dynamic batch size adjustment based on available memory and image dimensions

### Configuration Validation
Early validation of VISION_MODEL environment variable and model availability

## Dependencies Confirmed

### Existing Dependencies (Reused)
- pdfplumber: PDF parsing and text extraction
- mlx-vlm: Vision language model processing
- PIL/Pillow: Image handling and format conversion
- pytest: Testing framework

### No New Dependencies Required
All functionality achievable with existing project dependencies, maintaining minimal dependencies principle

## Performance Considerations

### Bottlenecks Identified
1. Image cropping and conversion (manageable with batch processing)
2. VLM inference time (mitigated with parallel processing)
3. Memory usage for large images (controlled with batch sizing)

### Optimization Strategies
1. Lazy image loading to reduce peak memory
2. Parallel processing with resource limits
3. Progressive enhancement (text first, images async)
4. Intelligent batching based on image sizes

## Constitutional Compliance

### 250-Line Rule
- Integration logic: <150 lines (focused on orchestration)
- Enhanced models: <100 lines (data structure extensions)
- Configuration validation: <75 lines (simple validation rules)

### Composition-First
- PDF extraction module remains independent
- Image processing module remains independent
- New integration layer composes existing modules
- Clear separation of concerns maintained

### Minimal Dependencies
- No new external dependencies required
- Reuses all existing project dependencies
- Leverages standard library for coordination logic

This research provides the foundation for Phase 1 design and contract generation.
