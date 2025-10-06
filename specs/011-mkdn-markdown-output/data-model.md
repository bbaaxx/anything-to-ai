# Data Model: Markdown Output Format Support

**Feature**: 011-mkdn-markdown-output
**Date**: 2025-10-02
**Phase**: 1 - Design

## Overview

This document defines the data models for markdown output formatting across all processing modules. These models represent the structured data used to generate markdown output from various document types.

## Shared Models

### MarkdownContent

Represents generated markdown content with metadata.

**Fields**:
- `content: str` - The generated markdown text
- `syntax_version: str` - Markdown syntax used ("commonmark", "gfm")
- `encoding: str` - Character encoding (default: "utf-8")
- `line_count: int` - Number of lines in output
- `char_count: int` - Total character count

**Usage**: Returned by all markdown formatting functions

**Validation Rules**:
- `content` must not be empty
- `syntax_version` must be one of: "commonmark", "gfm"
- `encoding` must be valid Python codec
- `line_count` and `char_count` must be positive

**Example**:
```python
MarkdownContent(
    content="# Document\n\nContent here",
    syntax_version="commonmark",
    encoding="utf-8",
    line_count=3,
    char_count=25
)
```

### MarkdownSection

Represents a section of markdown content with heading.

**Fields**:
- `level: int` - Heading level (1=H1, 2=H2, 3=H3)
- `title: str` - Section heading text
- `content: str` - Section body content
- `subsections: List[MarkdownSection]` - Nested subsections

**Usage**: Building hierarchical document structure

**Validation Rules**:
- `level` must be 1-6 (markdown heading limit)
- `title` must not be empty
- `subsections` nesting must not exceed 6 levels

## PDF Extractor Models

### DocumentStructure

Represents detected structure in PDF documents.

**Fields**:
- `headings: List[Heading]` - Detected heading elements
- `lists: List[ListItem]` - Detected list items
- `paragraphs: List[Paragraph]` - Regular text blocks
- `tables: List[Table]` - Detected tables (optional)
- `confidence: float` - Structure detection confidence (0.0-1.0)

**Usage**: Used by PDF markdown formatter to preserve document structure

**Relationships**:
- Contains multiple `Heading`, `ListItem`, and `Paragraph` objects
- Structure flattened into markdown output

### Heading

Represents a detected heading in PDF.

**Fields**:
- `level: int` - Inferred heading level (1-3)
- `text: str` - Heading text content
- `font_size: float` - Original font size (for detection)
- `page_number: int` - Page where heading appears
- `confidence: float` - Detection confidence (0.0-1.0)

**Validation Rules**:
- `level` must be 1-3
- `text` must not be empty
- `confidence` >= 0.7 for inclusion (threshold)

### ListItem

Represents detected list item in PDF.

**Fields**:
- `text: str` - List item content
- `level: int` - Nesting level (0=root, 1=nested)
- `ordered: bool` - True for numbered lists, False for bullets
- `page_number: int` - Page where item appears

### Paragraph

Represents regular text block in PDF.

**Fields**:
- `text: str` - Paragraph content
- `page_number: int` - Page where paragraph appears

## Image Processor Models

### MarkdownImageReference

Represents an image with VLM-generated description formatted for markdown.

**Fields**:
- `image_path: str` - Path to source image file
- `filename: str` - Image filename only
- `description: str` - VLM-generated description (raw)
- `alt_text: str` - Escaped description for markdown alt text
- `detailed_description: Optional[str]` - Extended description (if requested)
- `processing_success: bool` - Whether VLM processing succeeded

**Usage**: Building markdown image references with captions

**Validation Rules**:
- `image_path` must exist and be readable
- `alt_text` must have markdown special chars escaped
- If `processing_success` is False, use fallback alt text

**Example**:
```python
MarkdownImageReference(
    image_path="/path/to/image.jpg",
    filename="image.jpg",
    description="A red car on a highway",
    alt_text="A red car on a highway",  # escaped
    detailed_description="The image shows a vintage red sports car...",
    processing_success=True
)
```

### ImageBatch

Represents a batch of images processed together.

**Fields**:
- `images: List[MarkdownImageReference]` - Processed images
- `total_count: int` - Total images in batch
- `success_count: int` - Successfully processed count
- `failed_count: int` - Failed processing count

## Audio Processor Models

### TranscriptSegment

Represents a segment of audio transcription with timing.

**Fields**:
- `start_time: float` - Segment start time in seconds
- `end_time: float` - Segment end time in seconds
- `timestamp_formatted: str` - Formatted timestamp (HH:MM:SS or MM:SS)
- `speaker: Optional[str]` - Speaker identifier/name
- `text: str` - Transcript text for this segment
- `confidence: Optional[float]` - Transcription confidence (0.0-1.0)

**Usage**: Building markdown transcript with timestamps and speaker labels

**Validation Rules**:
- `start_time` <= `end_time`
- `timestamp_formatted` must match HH:MM:SS or MM:SS format
- `text` must not be empty

**Example**:
```python
TranscriptSegment(
    start_time=0.0,
    end_time=5.3,
    timestamp_formatted="00:00:00",
    speaker="Speaker 1",
    text="Welcome to the podcast.",
    confidence=0.95
)
```

### TranscriptionMetadata

Represents metadata about audio transcription.

**Fields**:
- `filename: str` - Audio filename
- `duration_seconds: float` - Total audio duration
- `duration_formatted: str` - Human-readable duration (HH:MM:SS)
- `model_name: str` - Whisper model used
- `language: str` - Detected or specified language code
- `segment_count: int` - Number of transcript segments

**Usage**: Header information for markdown transcript

## Text Summarizer Models

### SummaryHierarchy

Represents hierarchical structure of a summary.

**Fields**:
- `title: str` - Summary title
- `summary_text: str` - Main summary content
- `sections: List[SummarySection]` - Breakdown by section (if long text)
- `key_points: List[str]` - Bullet point highlights
- `tags: List[str]` - Categorization tags

**Usage**: Generating structured markdown summary

**Example**:
```python
SummaryHierarchy(
    title="Summary",
    summary_text="This document discusses...",
    sections=[],  # Simple summaries have no sections
    key_points=["Main idea 1", "Main idea 2"],
    tags=["technology", "AI", "documentation"]
)
```

### SummarySection

Represents a section within a long summary.

**Fields**:
- `heading: str` - Section heading
- `content: str` - Section summary content
- `order: int` - Section order (for sorting)

**Usage**: Breaking long summaries into subsections

## Shared Utility Types

### EscapedText

Type alias for markdown-escaped text.

**Type**: `str`

**Contract**: String with markdown special characters properly escaped

**Creation**:
```python
from markdown_utils import escape_markdown

escaped: EscapedText = escape_markdown(user_input)
```

### HeadingLevel

Type alias for heading levels.

**Type**: `int`

**Valid Values**: 1-6 (inclusive)

**Usage**: Ensuring heading level constraints

## State Transitions

### PDF Processing → Markdown

1. Extract pages → Analyze structure → Detect headings/lists/paragraphs
2. Create `DocumentStructure` with detected elements
3. Format each element type to markdown
4. Combine into `MarkdownContent`

### Image Processing → Markdown

1. Process images with VLM → Get descriptions
2. Create `MarkdownImageReference` for each image
3. Escape descriptions → Set `alt_text`
4. Format as markdown image syntax with heading sections
5. Combine into `MarkdownContent`

### Audio Processing → Markdown

1. Transcribe audio → Get segments with timestamps
2. Create `TranscriptSegment` for each
3. Format timestamps → Create headings with speaker labels
4. Create `TranscriptionMetadata` for header
5. Combine into `MarkdownContent`

### Text Summarization → Markdown

1. Summarize text → Get summary and tags
2. Create `SummaryHierarchy` with structure
3. Format summary with heading hierarchy
4. Format tags as bullet list
5. Combine into `MarkdownContent`

## Relationships

```
MarkdownContent (shared output format)
    ├─ used by all modules
    └─ contains rendered markdown text

PDF: DocumentStructure
    ├─ contains List[Heading]
    ├─ contains List[ListItem]
    └─ contains List[Paragraph]

Image: ImageBatch
    └─ contains List[MarkdownImageReference]

Audio: TranscriptionMetadata + List[TranscriptSegment]

Text: SummaryHierarchy
    └─ contains List[SummarySection]
```

## Implementation Notes

### No New Model Classes Required

Most models are informal structures. The actual implementation will:
- Use existing result models (PageResult, ProcessingResult, etc.)
- Add markdown formatting functions that take existing models
- Return plain strings (markdown text), not new model classes
- Keep formatters stateless and pure functions

### Type Hints

Use Python type hints for clarity:
```python
from typing import List, Optional

def format_pdf_markdown(
    pages: List[PageResult],
    detect_structure: bool = True
) -> str:
    """Format PDF pages as markdown."""
    ...
```

### Validation

Validation happens in:
1. Contract tests (assert markdown structure)
2. Integration tests (end-to-end validation)
3. Formatters themselves (basic checks)

---

*Design completed: 2025-10-02*
