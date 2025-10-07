# Data Model: Enhanced PDF Extraction with Image Description

**Date**: 2025-09-29
**Feature**: 005-augment-pdf-extraction

## Core Entities

### EnhancedExtractionConfig
Extended configuration for PDF extraction with optional image processing capabilities.

```python
@dataclass
class EnhancedExtractionConfig(ExtractionConfig):
    """Configuration for PDF extraction with optional image description processing."""

    # Image processing settings
    include_images: bool = False
    image_processing_config: Optional[ProcessingConfig] = None

    # Error handling settings
    image_fallback_text: str = "[Image: processing failed]"
    max_images_per_page: Optional[int] = None

    # Performance settings
    image_batch_size: int = 4
    parallel_image_processing: bool = True
```

**Validation Rules**:
- `include_images` requires VISION_MODEL environment variable
- `image_batch_size` must be between 1 and 10
- `max_images_per_page` must be positive when set
- `image_processing_config` validated against ProcessingConfig schema

### ImageContext
Represents extracted image with position and processing context.

```python
@dataclass
class ImageContext:
    """Context information for an image extracted from a PDF page."""

    # Position information
    page_number: int
    sequence_number: int  # Order within page
    bounding_box: tuple  # (x0, y0, x1, y1)

    # Image properties
    width: int
    height: int
    format: str  # e.g., "JPEG", "PNG"

    # Processing results
    pil_image: Optional[object] = None  # PIL Image object
    description: Optional[str] = None
    processing_status: str = "pending"  # pending, success, failed
    error_message: Optional[str] = None
```

**State Transitions**:
- pending → success (description generated)
- pending → failed (processing error)
- failed → success (retry successful)

### EnhancedPageResult
Extended page result including image descriptions.

```python
@dataclass
class EnhancedPageResult(PageResult):
    """Page extraction result with optional image descriptions."""

    # Inherited from PageResult: page_number, text, metadata

    # Image-specific additions
    images_found: int = 0
    images_processed: int = 0
    images_failed: int = 0
    image_contexts: List[ImageContext] = field(default_factory=list)
    enhanced_text: Optional[str] = None  # Text with inline image descriptions
```

**Relationships**:
- Contains multiple ImageContext objects
- Extends base PageResult functionality
- enhanced_text integrates original text with image descriptions

### EnhancedExtractionResult
Complete extraction result with image processing summary.

```python
@dataclass
class EnhancedExtractionResult(ExtractionResult):
    """Complete PDF extraction result with image processing summary."""

    # Inherited from ExtractionResult: pages, total_pages, metadata

    # Image processing summary
    total_images_found: int = 0
    total_images_processed: int = 0
    total_images_failed: int = 0
    image_processing_time: float = 0.0
    vision_model_used: Optional[str] = None

    # Enhanced content
    enhanced_pages: List[EnhancedPageResult] = field(default_factory=list)
    combined_enhanced_text: Optional[str] = None
```

**Aggregation Rules**:
- `total_images_found` = sum of `images_found` across all pages
- `total_images_processed` = sum of `images_processed` across all pages
- `total_images_failed` = sum of `images_failed` across all pages
- `combined_enhanced_text` = concatenation of all `enhanced_text`

## Integration Entities

### PDFImageProcessor
Service class for orchestrating PDF extraction with image processing.

```python
class PDFImageProcessor:
    """Orchestrates PDF text extraction with optional image description processing."""

    def __init__(self, image_processor=None):
        self.image_processor = image_processor
        self.circuit_breaker = VLMCircuitBreaker()

    def extract_with_images(
        self,
        file_path: str,
        config: EnhancedExtractionConfig
    ) -> EnhancedExtractionResult:
        """Extract PDF text with optional image descriptions."""
        pass

    def extract_with_images_streaming(
        self,
        file_path: str,
        config: EnhancedExtractionConfig
    ) -> Iterator[EnhancedPageResult]:
        """Stream PDF extraction with image processing."""
        pass
```

### VLMCircuitBreaker
Handles VLM service failure management.

```python
@dataclass
class VLMCircuitBreaker:
    """Circuit breaker for VLM service failures."""

    failure_count: int = 0
    failure_threshold: int = 3
    last_failure_time: Optional[float] = None
    recovery_timeout: float = 60.0
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_process(self) -> bool:
        """Check if VLM processing is allowed."""
        pass

    def record_success(self) -> None:
        """Record successful VLM operation."""
        pass

    def record_failure(self) -> None:
        """Record VLM operation failure."""
        pass
```

## Data Flow

### Input Flow
1. PDF file path → pdfplumber extraction
2. Page images → ImageContext objects
3. ImageContext → VLM processing
4. Descriptions → enhanced text integration

### Processing Flow
```
PDF → Pages → [Text + Images] → [Text + Descriptions] → EnhancedResult
```

### Error Flow
```
Image Processing Error → Fallback Text → Continue Extraction
VLM Service Error → Circuit Breaker → Fallback Mode
```

## Validation Schema

### Configuration Validation
- Vision model availability check when `include_images=True`
- Image processing config validation
- Resource limit validation (batch sizes, timeouts)

### Result Validation
- Image count consistency across result objects
- Processing status consistency
- Enhanced text format validation (inline image references)

### Error State Validation
- Failed image count tracking
- Error message preservation
- Graceful degradation validation

## Performance Considerations

### Memory Management
- PIL image cleanup after processing
- Batch size limits based on available memory
- Lazy loading for large image collections

### Processing Optimization
- Parallel image processing within constitutional constraints
- Progressive enhancement (text first, images async)
- Smart batching based on image dimensions

This data model provides the foundation for implementing enhanced PDF extraction while maintaining compatibility with existing interfaces and respecting constitutional constraints.
