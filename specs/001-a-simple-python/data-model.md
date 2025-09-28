# Data Model: PDF Text Extraction Module

## Core Entities

### PDFDocument
**Purpose**: Represents a PDF file being processed
**Fields**:
- `file_path: str` - Path to the PDF file
- `page_count: int` - Total number of pages in the document
- `file_size: int` - Size of the PDF file in bytes
- `is_large_file: bool` - Whether file requires streaming (>20 pages)

**Validation Rules**:
- file_path must exist and be readable
- file_path must have .pdf extension
- page_count must be positive integer
- file_size must be non-negative

**State Transitions**:
- Unloaded → Loaded (when document is opened)
- Loaded → Processing (when extraction begins)
- Processing → Complete (when extraction finishes)
- Any state → Error (on processing failure)

### TextContent
**Purpose**: Extracted text data from PDF pages
**Fields**:
- `page_number: int` - Source page number (1-indexed)
- `text: str` - Extracted text content
- `char_count: int` - Number of characters extracted
- `extraction_time: float` - Time taken to extract (seconds)

**Validation Rules**:
- page_number must be positive integer
- text can be empty string (for pages with no extractable text)
- char_count must match actual text length
- extraction_time must be non-negative

### ProgressInfo
**Purpose**: Tracks processing progress and status
**Fields**:
- `pages_processed: int` - Number of pages completed
- `total_pages: int` - Total pages to process
- `percentage: float` - Completion percentage (0.0-100.0)
- `current_page: int` - Currently processing page number
- `estimated_remaining: float` - Estimated time remaining (seconds)

**Validation Rules**:
- pages_processed <= total_pages
- percentage must be between 0.0 and 100.0
- current_page must be valid page number or 0
- estimated_remaining must be non-negative

**State Transitions**:
- Started (pages_processed = 0)
- InProgress (0 < pages_processed < total_pages)
- Complete (pages_processed = total_pages)

### ProcessingSession
**Purpose**: Configuration and state for an extraction operation
**Fields**:
- `document: PDFDocument` - The PDF being processed
- `streaming_enabled: bool` - Whether to use streaming mode
- `progress_callback: Optional[Callable]` - Progress reporting function
- `output_format: str` - Output format ("plain" or "json")
- `created_at: datetime` - Session creation timestamp

**Validation Rules**:
- document must be valid PDFDocument instance
- output_format must be "plain" or "json"
- progress_callback must be callable or None

### ExtractionResult
**Purpose**: Complete result of text extraction operation
**Fields**:
- `success: bool` - Whether extraction completed successfully
- `content: List[TextContent]` - Extracted text by page
- `total_pages: int` - Number of pages processed
- `total_chars: int` - Total characters extracted
- `processing_time: float` - Total processing time (seconds)
- `error_message: Optional[str]` - Error details if failed

**Validation Rules**:
- If success=True, error_message must be None
- If success=False, error_message must be provided
- total_pages must match length of content list
- total_chars must sum char_count from all content items
- processing_time must be positive

## Entity Relationships

```
ProcessingSession
├── contains: PDFDocument (1:1)
├── produces: ExtractionResult (1:1)
└── tracks: ProgressInfo (1:1)

ExtractionResult
└── contains: TextContent[] (1:many)

ProgressInfo
└── references: PDFDocument.page_count (for validation)
```

## Error Conditions

### PDFNotFoundError
- Triggered when: file_path does not exist
- Recovery: Verify file path and permissions

### PDFCorruptedError
- Triggered when: PDF structure is invalid
- Recovery: Try alternative PDF processing or manual inspection

### PDFPasswordProtectedError
- Triggered when: PDF requires password for access
- Recovery: Obtain password or skip file

### PDFNoTextError
- Triggered when: PDF contains no extractable text (images only)
- Recovery: Consider OCR processing or skip file

### ProcessingInterruptedError
- Triggered when: Extraction stopped mid-process
- Recovery: Restart extraction from beginning