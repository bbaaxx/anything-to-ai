# Data Model: Text Summarizer Module

**Phase**: 1 - Design & Contracts
**Created**: 2025-10-01

## Overview

This document defines the data models and their relationships for the text summarizer module. All models use Pydantic for validation and type safety, following the pattern established in other modules (image_processor, audio_processor).

## Core Entities

### 1. SummaryRequest

Represents a request to summarize text.

**Fields**:
- `text` (str, required): The input text to summarize. Must be non-empty UTF-8 encoded string.
- `format` (OutputFormat, default="json"): Desired output format (json or plain).
- `include_metadata` (bool, default=True): Whether to include processing metadata in output.

**Validation Rules**:
- `text` must not be empty or whitespace-only
- `text` must be valid UTF-8
- If `text` length is 0 after stripping, raise ValidationError

**State**: Immutable input data (no state transitions)

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class SummaryRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to summarize")
    format: Literal["json", "plain"] = Field(default="json", description="Output format")
    include_metadata: bool = Field(default=True, description="Include processing metadata")

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text must not be empty or whitespace-only")
        # UTF-8 validation happens automatically via Pydantic str type
        return v
```

### 2. SummaryResult

Represents the result of text summarization.

**Fields**:
- `summary` (str, required): The generated summary text. Length determined by LLM based on content density.
- `tags` (List[str], required): List of categorization tags. Must contain at least 3 tags.
- `metadata` (Optional[SummaryMetadata], optional): Processing metadata if requested.

**Validation Rules**:
- `summary` must not be empty
- `tags` must contain at least 3 elements
- Each tag must be non-empty string
- `metadata` can be None if not requested

**Relationships**:
- Contains one SummaryMetadata object (optional)

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class SummaryResult(BaseModel):
    summary: str = Field(..., min_length=1, description="Generated summary")
    tags: List[str] = Field(..., min_length=3, description="Content tags (minimum 3)")
    metadata: Optional['SummaryMetadata'] = Field(default=None, description="Processing metadata")

    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        if len(v) < 3:
            raise ValueError("Must have at least 3 tags")
        if any(not tag.strip() for tag in v):
            raise ValueError("Tags must be non-empty strings")
        return v
```

### 3. SummaryMetadata

Processing metadata for a summarization operation.

**Fields**:
- `input_length` (int, required): Word count of input text.
- `chunked` (bool, required): Whether text was chunked for processing (>10k words).
- `chunk_count` (Optional[int], optional): Number of chunks if chunking was used.
- `detected_language` (Optional[str], optional): Detected language code (e.g., "en", "es", "fr").
- `processing_time` (float, required): Time taken in seconds.

**Validation Rules**:
- `input_length` must be positive
- `processing_time` must be non-negative
- If `chunked` is True, `chunk_count` should be provided
- `detected_language` should be ISO 639-1 code if provided

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional

class SummaryMetadata(BaseModel):
    input_length: int = Field(..., gt=0, description="Word count of input")
    chunked: bool = Field(..., description="Whether text was chunked")
    chunk_count: Optional[int] = Field(default=None, ge=1, description="Number of chunks")
    detected_language: Optional[str] = Field(default=None, description="ISO 639-1 language code")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")

    @field_validator('chunk_count')
    @classmethod
    def validate_chunk_count(cls, v: Optional[int], info) -> Optional[int]:
        values = info.data
        if values.get('chunked') and v is None:
            raise ValueError("chunk_count required when chunked=True")
        return v
```

### 4. TextChunk

Represents a chunk of text for processing large documents.

**Fields**:
- `index` (int, required): Sequential index of this chunk (0-based).
- `content` (str, required): The text content of this chunk.
- `start_word` (int, required): Starting word index in original text.
- `end_word` (int, required): Ending word index in original text.

**Validation Rules**:
- `index` must be non-negative
- `content` must not be empty
- `start_word` must be less than `end_word`
- `end_word - start_word` should approximately equal word count of content

```python
from pydantic import BaseModel, Field, field_validator

class TextChunk(BaseModel):
    index: int = Field(..., ge=0, description="Chunk index")
    content: str = Field(..., min_length=1, description="Chunk text content")
    start_word: int = Field(..., ge=0, description="Start word index")
    end_word: int = Field(..., gt=0, description="End word index")

    @field_validator('end_word')
    @classmethod
    def validate_word_range(cls, v: int, info) -> int:
        values = info.data
        start = values.get('start_word', 0)
        if v <= start:
            raise ValueError("end_word must be greater than start_word")
        return v
```

## Entity Relationships

```
SummaryRequest (1) ──> (1) SummaryResult
                              │
                              └──> (0..1) SummaryMetadata

For large texts (>10k words):
Text ──> (1..n) TextChunk ──> (n) SummaryResult ──> (1) Final SummaryResult
```

**Processing Flow**:
1. User creates `SummaryRequest` with text
2. System processes text (possibly via multiple `TextChunk` objects)
3. System returns `SummaryResult` with `SummaryMetadata`

## Data Constraints Summary

| Entity | Key Constraints |
|--------|----------------|
| SummaryRequest | Non-empty text, valid UTF-8, valid format enum |
| SummaryResult | Non-empty summary, ≥3 tags, valid metadata |
| SummaryMetadata | Positive input_length, non-negative processing_time |
| TextChunk | Valid word range, non-empty content, sequential index |

## Storage

No persistent storage required. All data is in-memory during processing:
- Requests are short-lived (duration of one API call)
- Results are returned immediately
- Chunks are temporary intermediate data

## Error Handling

Invalid data raises Pydantic `ValidationError` with specific field errors:
- Empty text → "Text must not be empty or whitespace-only"
- Too few tags → "Must have at least 3 tags"
- Invalid word range → "end_word must be greater than start_word"

These errors are caught and wrapped in `InvalidInputError` or `ValidationError` by the processor layer.

---

**Status**: ✅ Complete
**Next**: Generate API contracts and tests
