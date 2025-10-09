# Contract: Timestamp Formatting API

## Function: format_timestamp()

**Module**: `anyfile_to_ai.audio_processor.markdown_formatter` (new function)

### Signature

```python
def format_timestamp(seconds: float) -> str
```

### Contract

**Purpose**: Convert seconds to HH:MM:SS.CC format for human-readable display

**Input**:
- `seconds` (float): Time in seconds, range [0.0, 7200.0] (2 hours max)

**Output**:
- String in format "HH:MM:SS.CC" where CC is centiseconds (hundredths)

**Format Rules**:
- Hours: 2 digits, zero-padded (00-02)
- Minutes: 2 digits, zero-padded (00-59)
- Seconds: 2 digits, zero-padded (00-59)
- Centiseconds: 2 digits, zero-padded (00-99)
- Separator: colon (:) between H:M:S, period (.) before centiseconds

**Examples**:
```python
format_timestamp(0.0)      # "00:00:00.00"
format_timestamp(5.23)     # "00:00:05.23"
format_timestamp(65.45)    # "00:01:05.45"
format_timestamp(3661.12)  # "01:01:01.12"
format_timestamp(7199.99)  # "01:59:59.99"
```

**Edge Cases**:
- Input 0.0 → "00:00:00.00"
- Input with milliseconds (e.g., 5.234) → rounds to centiseconds: "00:00:05.23"
- Negative input → raises ValueError
- Input > 7200.0 → raises ValueError (exceeds max audio duration)

### Test Coverage

**Unit test**: `tests/unit/test_timestamp_formatting.py::test_format_timestamp`

---

## Function: format_segments_markdown()

**Module**: `anyfile_to_ai.audio_processor.markdown_formatter` (new function)

### Signature

```python
def format_segments_markdown(
    segments: list[TranscriptionSegment],
    include_text: bool = True
) -> str
```

### Contract

**Purpose**: Format timestamped segments for markdown output

**Input**:
- `segments`: List of TranscriptionSegment objects
- `include_text`: Whether to include full text (default: True)

**Output**: Formatted string with one line per segment

**Format**:
```
[HH:MM:SS.CC] Segment text here.
[HH:MM:SS.CC] Next segment text here.
```

**Examples**:

```python
segments = [
    TranscriptionSegment(start=0.0, end=5.23, text="First segment."),
    TranscriptionSegment(start=5.23, end=12.45, text="Second segment."),
]

format_segments_markdown(segments)
# Returns:
# "[00:00:00.00] First segment.\n[00:00:05.23] Second segment."
```

**Edge Cases**:
- Empty list → returns ""
- Single segment → single line with timestamp
- Very long text → no line wrapping (preserve full text)

### Test Coverage

**Unit test**: `tests/unit/test_timestamp_formatting.py::test_format_segments_markdown`

---

## Function: format_output_with_timestamps()

**Module**: `anyfile_to_ai.audio_processor.markdown_formatter` (modified)

### Signature

```python
def format_output_with_timestamps(
    result: TranscriptionResult,
    format_type: str
) -> str
```

### Contract

**Purpose**: Format TranscriptionResult based on output format, respecting timestamps

**Input**:
- `result`: TranscriptionResult with optional segments
- `format_type`: One of ["markdown", "json", "plain", "csv"]

**Output**: Formatted string according to format_type

**Behavior by format**:

**markdown**:
- If result.segments is not None: use format_segments_markdown()
- If result.segments is None: return result.text (existing behavior)

**json**:
- If result.segments is not None: include "segments" key in JSON
- If result.segments is None: omit "segments" key (existing behavior)

**plain**:
- Always return result.text only (timestamps not suitable for plain format)

**csv**:
- If result.segments is not None: each segment as a row with start,end,text
- If result.segments is None: single row with full text (existing behavior)

### Examples

**Markdown with timestamps**:
```python
result = TranscriptionResult(
    text="Full text",
    segments=[TranscriptionSegment(start=0.0, end=5.0, text="Full text")]
)
format_output_with_timestamps(result, "markdown")
# Returns: "[00:00:00.00] Full text"
```

**JSON with timestamps**:
```python
format_output_with_timestamps(result, "json")
# Returns: '{"text": "Full text", "segments": [{"start": 0.0, ...}], ...}'
```

**Plain (no timestamps)**:
```python
format_output_with_timestamps(result, "plain")
# Returns: "Full text"
```

### Test Coverage

**Integration test**: `tests/integration/test_timestamp_integration.py::test_format_output_with_timestamps`

---

## CSV Format Extension

**Format when timestamps enabled**:
```csv
start,end,text
0.00,5.23,"First segment text"
5.23,12.45,"Second segment text"
```

**Format when timestamps disabled** (unchanged):
```csv
text
"Full transcription text here"
```

**Contract**:
- Header row always present
- Timestamps formatted as decimal seconds (not HH:MM:SS)
- Text properly escaped (quotes around text, doubled quotes inside text)
- One row per segment

### Test Coverage

**Unit test**: `tests/unit/test_timestamp_formatting.py::test_format_csv_with_timestamps`
