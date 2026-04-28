# API Contract: Text Summarizer with Metadata

**Module**: `anyfile_to_ai.text_summarizer`
**Version**: 0.2.0 (with enhanced metadata support)

---

## CLI Interface

### Command

```bash
uv run python -m text_summarizer <text_file> [OPTIONS]
uv run python -m text_summarizer --stdin [OPTIONS]
```

### Existing Options

```
--include-metadata / --no-metadata    Include/exclude processing metadata (default: include)
```

Note: text_summarizer already has metadata support via `--no-metadata` flag. This contract extends the existing SummaryMetadata to match universal metadata structure.

### Examples

```bash
# Summarize with metadata (default)
uv run python -m text_summarizer article.txt --format json

# Summarize without metadata
uv run python -m text_summarizer article.txt --format json --no-metadata

# Summarize from stdin with metadata
cat article.txt | uv run python -m text_summarizer --stdin --format json
```

---

## Data Model Changes

### SummaryMetadata Extension

**Current Model** (Pydantic):
```python
class SummaryMetadata(BaseModel):
    input_length: int  # Word count
    chunked: bool
    chunk_count: int | None
    detected_language: str | None
    processing_time: float
```

**Extended Model** (aligned with universal metadata):
```python
class SummaryMetadata(BaseModel):
    # Existing fields (preserved for backward compatibility)
    input_length: int
    chunked: bool
    chunk_count: int | None
    detected_language: str | None
    processing_time: float

    # NEW: Universal metadata fields
    processing_timestamp: str | None = None  # ISO 8601
    model_version: str | None = None
    configuration: dict | None = None  # user_provided + effective
    source: dict | None = None  # TextSourceMetadata
```

### Universal Metadata Structure (when enabled)

```python
"metadata": {
    # Existing fields (flat structure for backward compatibility)
    "input_length": 5000,
    "chunked": true,
    "chunk_count": 5,
    "detected_language": "en",
    "processing_time": 3.2,

    # NEW: Universal metadata fields
    "processing_timestamp": "2025-10-25T14:45:00+00:00",
    "model_version": "llama2",
    "configuration": {
        "user_provided": {
            "model": "llama2",
            "provider": "ollama"
        },
        "effective": {
            "model": "llama2",
            "provider": "ollama",
            "format": "json",
            "max_tokens": 4096
        }
    },
    "source": {
        "file_path": "/path/to/article.txt",
        "file_size_bytes": 102400,
        "input_length_words": 5000,
        "input_length_chars": 30000,
        "detected_language": "en",
        "chunked": true,
        "chunk_count": 5
    }
}
```

---

## JSON Output Contract

### With Metadata Enabled (Default)

```json
{
  "summary": "This article discusses artificial intelligence and its impact on society...",
  "tags": ["AI", "technology", "society"],
  "metadata": {
    "input_length": 5000,
    "chunked": true,
    "chunk_count": 5,
    "detected_language": "en",
    "processing_time": 3.2,
    "processing_timestamp": "2025-10-25T14:45:00+00:00",
    "model_version": "llama2",
    "configuration": {
      "user_provided": {
        "model": "llama2",
        "provider": "ollama"
      },
      "effective": {
        "model": "llama2",
        "provider": "ollama",
        "format": "json",
        "max_tokens": 4096
      }
    },
    "source": {
      "file_path": "/path/to/article.txt",
      "file_size_bytes": 102400,
      "input_length_words": 5000,
      "input_length_chars": 30000,
      "detected_language": "en",
      "chunked": true,
      "chunk_count": 5
    }
  }
}
```

### Without Metadata

```json
{
  "summary": "This article discusses artificial intelligence...",
  "tags": ["AI", "technology", "society"],
  "metadata": null
}
```

---

## Markdown Output Contract

### With Metadata Enabled

```markdown
---
processing_timestamp: 2025-10-25T14:45:00+00:00
model_version: llama2
input_length: 5000 words
detected_language: en
---

# Summary

This article discusses artificial intelligence and its impact on society...

## Tags

- AI
- technology
- society

## Metadata

### Processing
- **Timestamp**: 2025-10-25T14:45:00+00:00
- **Model**: llama2
- **Processing Time**: 3.2s

### Source
- **File**: article.txt
- **Size**: 100 KB
- **Length**: 5000 words (30000 chars)
- **Language**: en (English)
- **Chunked**: Yes (5 chunks)
```

---

## Stdin/Piped Input Handling

### Metadata for Stdin Input

```python
"source": {
    "file_path": "unavailable",  # No file path for stdin
    "file_size_bytes": "unavailable",  # No file size
    "input_length_words": 5000,  # Calculated from stdin text
    "input_length_chars": 30000,  # Calculated from stdin text
    "detected_language": "en",
    "chunked": true,
    "chunk_count": 5
}
```

### Pipeline Example

```bash
# PDF -> summarizer pipeline with metadata
uv run python -m pdf_extractor extract document.pdf --format plain | \
  uv run python -m text_summarizer --stdin --format json
```

Result metadata will show:
- Source file_path: "unavailable" (came from stdin)
- Input length calculated from piped text
- Processing timestamp and model version included

---

## Contract Tests

### Test Scenarios

1. **Metadata enabled (default)**:
   - Summarize without `--no-metadata`
   - Assert `result.metadata is not None`
   - Assert metadata contains all universal fields

2. **Metadata disabled**:
   - Summarize with `--no-metadata`
   - Assert `result.metadata is None`

3. **Universal metadata fields**:
   - Assert processing_timestamp is ISO 8601
   - Assert model_version matches LLM model used
   - Assert configuration has user_provided and effective

4. **Source metadata for file input**:
   - Summarize from file
   - Assert source.file_path is actual path
   - Assert source.file_size_bytes is correct
   - Assert word/char counts match

5. **Source metadata for stdin input**:
   - Summarize from stdin
   - Assert source.file_path = "unavailable"
   - Assert source.file_size_bytes = "unavailable"
   - Assert word/char counts still calculated

6. **Backward compatibility**:
   - Assert existing metadata fields preserved (input_length, chunked, etc.)
   - Assert flat structure maintained for existing fields
   - Assert new fields added without breaking changes

---

## Backward Compatibility

✅ **Fully backward compatible**:
- Existing metadata fields preserved (input_length, chunked, chunk_count, detected_language, processing_time)
- Flat structure maintained for backward compatibility
- New universal fields added as optional (None if not available)
- `--no-metadata` flag behavior unchanged
- Default is still metadata enabled (matches existing behavior)

---

## Migration from SummaryMetadata to Universal Schema

### Existing vs. New Structure

**Before** (existing):
```json
{
  "metadata": {
    "input_length": 5000,
    "chunked": true,
    "chunk_count": 5,
    "detected_language": "en",
    "processing_time": 3.2
  }
}
```

**After** (extended, backward compatible):
```json
{
  "metadata": {
    "input_length": 5000,
    "chunked": true,
    "chunk_count": 5,
    "detected_language": "en",
    "processing_time": 3.2,
    "processing_timestamp": "2025-10-25T14:45:00+00:00",
    "model_version": "llama2",
    "configuration": {...},
    "source": {...}
  }
}
```

All existing code consuming SummaryMetadata continues to work. New fields are optional additions.

---

## Error Handling

### Missing File

```json
{
  "summary": "",
  "tags": [],
  "metadata": null,
  "error": "File not found: article.txt"
}
```

### LLM API Failure (with metadata enabled)

```json
{
  "summary": "",
  "tags": [],
  "metadata": {
    "input_length": 5000,
    "chunked": false,
    "chunk_count": null,
    "detected_language": "en",
    "processing_time": 0.1,
    "processing_timestamp": "2025-10-25T14:45:00+00:00",
    "model_version": "unavailable",
    "source": {
      "file_path": "/path/to/article.txt",
      "file_size_bytes": 102400,
      "input_length_words": 5000
    }
  },
  "error": "LLM API unavailable"
}
```

---

## LLM Model Version

### Model Version Extraction

- **Ollama**: Extract from model name (e.g., "llama2", "mistral:latest")
- **LM Studio**: Extract from model endpoint/name
- **MLX**: Extract from model path (e.g., "mlx-community/llama-3")

```python
"model_version": "llama2"  # Ollama
"model_version": "mistral:latest"  # Ollama with tag
"model_version": "mlx-community/llama-3"  # MLX
```

---

**Contract Version**: 1.0
**Schema**: [metadata-schema.json](./metadata-schema.json)
**Note**: This contract extends existing SummaryMetadata to align with universal metadata structure while maintaining full backward compatibility.
