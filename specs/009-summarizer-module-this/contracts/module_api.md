# Module API Contract: Text Summarizer

**Version**: 1.0.0
**Created**: 2025-10-01

## Overview

This contract defines the public API for the `text_summarizer` module. All functions are importable from `text_summarizer` package.

## Core Functions

### `summarize_text`

Primary function for text summarization.

**Signature**:
```python
def summarize_text(
    text: str,
    *,
    format: Literal["json", "plain"] = "json",
    include_metadata: bool = True
) -> SummaryResult:
    """
    Summarize input text and generate categorization tags.

    Args:
        text: Input text to summarize (UTF-8 encoded)
        format: Output format preference (json or plain)
        include_metadata: Whether to include processing metadata

    Returns:
        SummaryResult with summary, tags (≥3), and optional metadata

    Raises:
        InvalidInputError: If text is empty or invalid UTF-8
        LLMError: If LLM client fails
        ValidationError: If output doesn't meet requirements (e.g., <3 tags)
    """
```

**Contract Tests**:
- ✓ Returns SummaryResult for valid input
- ✓ Result contains non-empty summary
- ✓ Result contains at least 3 tags
- ✓ Metadata included when include_metadata=True
- ✓ Metadata excluded when include_metadata=False
- ✓ Raises InvalidInputError for empty text
- ✓ Raises InvalidInputError for whitespace-only text
- ✓ Handles text < 1000 words (small text)
- ✓ Handles text 1000-10000 words (medium text)
- ✓ Handles text > 10000 words (large text, chunking)
- ✓ Handles non-English text (auto-translates to English)

### `create_summarizer`

Factory function to create summarizer with custom LLM client.

**Signature**:
```python
def create_summarizer(
    llm_client: Optional[Any] = None,
    *,
    chunk_size: int = 10000,
    chunk_overlap: int = 500
) -> TextSummarizer:
    """
    Create a text summarizer instance.

    Args:
        llm_client: Optional custom LLM client (uses default if None)
        chunk_size: Words per chunk for large texts (default: 10000)
        chunk_overlap: Overlap words between chunks (default: 500)

    Returns:
        TextSummarizer instance

    Raises:
        ValueError: If chunk_size < chunk_overlap or invalid values
    """
```

**Contract Tests**:
- ✓ Creates TextSummarizer with default client
- ✓ Creates TextSummarizer with custom client
- ✓ Sets custom chunk_size
- ✓ Sets custom chunk_overlap
- ✓ Raises ValueError if chunk_size < chunk_overlap
- ✓ Raises ValueError if chunk_size <= 0
- ✓ Raises ValueError if chunk_overlap < 0

### `chunk_text`

Utility function for splitting large texts.

**Signature**:
```python
def chunk_text(
    text: str,
    chunk_size: int = 10000,
    overlap: int = 500
) -> List[TextChunk]:
    """
    Split text into overlapping chunks.

    Args:
        text: Input text to chunk
        chunk_size: Target words per chunk (default: 10000)
        overlap: Overlap words between chunks (default: 500)

    Returns:
        List of TextChunk objects with sequential indices

    Raises:
        ValueError: If text is empty or invalid parameters
    """
```

**Contract Tests**:
- ✓ Returns single chunk for text <= chunk_size
- ✓ Returns multiple chunks for text > chunk_size
- ✓ Chunks have correct sequential indices (0, 1, 2, ...)
- ✓ Chunks have correct word ranges (start_word, end_word)
- ✓ Chunks overlap by specified amount
- ✓ Last chunk may be smaller than chunk_size
- ✓ Raises ValueError for empty text

## CLI Interface

### Command

```bash
python -m text_summarizer [OPTIONS] [TEXT_FILE]
```

### Options

```
--stdin                   Read from stdin instead of file
--format {json,plain}     Output format (default: json)
--output FILE             Write to file instead of stdout
--verbose                 Enable verbose logging
--help                    Show help message
```

### Exit Codes

- `0`: Success
- `1`: Invalid input (empty text, bad UTF-8, file not found)
- `2`: LLM error (API failure, timeout, etc.)
- `3`: Validation error (output doesn't meet requirements)

### Contract Tests

- ✓ Reads from file path argument
- ✓ Reads from stdin when --stdin provided
- ✓ Outputs JSON by default
- ✓ Outputs plain text when --format plain
- ✓ Writes to stdout by default
- ✓ Writes to file when --output provided
- ✓ Shows help with --help
- ✓ Exits with code 1 for invalid input
- ✓ Exits with code 2 for LLM errors
- ✓ Exits with code 3 for validation errors

## Module Exports

The `text_summarizer/__init__.py` exports:

```python
from .models import (
    SummaryRequest,
    SummaryResult,
    SummaryMetadata,
    TextChunk,
)
from .processor import summarize_text, TextSummarizer
from .chunker import chunk_text
from .exceptions import (
    SummarizerError,
    InvalidInputError,
    LLMError,
    ValidationError,
)

__all__ = [
    "summarize_text",
    "create_summarizer",
    "chunk_text",
    "SummaryRequest",
    "SummaryResult",
    "SummaryMetadata",
    "TextChunk",
    "TextSummarizer",
    "SummarizerError",
    "InvalidInputError",
    "LLMError",
    "ValidationError",
]
```

## Integration Points

### With LLM Client Module

```python
from llm_client import create_client

# Text summarizer uses llm_client
client = create_client()  # Default OpenAI-compatible client
result = summarize_text("Long text...", llm_client=client)
```

### With Other Modules (Piping)

```bash
# PDF → Summarizer
python -m pdf_extractor document.pdf | python -m text_summarizer --stdin

# Image → Summarizer
python -m image_processor image.jpg --format plain | python -m text_summarizer --stdin

# Audio → Summarizer
python -m audio_processor audio.mp3 --format plain | python -m text_summarizer --stdin
```

---

**Status**: ✅ Complete
**Test Location**: `tests/contract/test_summarizer_api.py`
