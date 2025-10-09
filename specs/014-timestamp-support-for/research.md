# Phase 0: Research - Timestamp Support for Audio Transcription

**Date**: 2025-10-06
**Status**: Complete

## Research Questions & Findings

### Q1: How does lightning-whisper-mlx provide timestamp data?

**Finding**: lightning-whisper-mlx's `transcribe_audio()` function returns a dictionary with three keys:
- `text`: Full transcription text
- `segments`: List of segment data
- `language`: Detected or specified language

**Source**: `.venv/lib/python3.13/site-packages/lightning_whisper_mlx/transcribe.py:448-452`

```python
return dict(
    text=tokenizer.decode(all_tokens[len(initial_prompt_tokens) :]),
    segments=all_segments,
    language=language,
)
```

### Q2: What format are timestamps returned in?

**Finding**: Segments are stored as lists with format: `[start_seek, end_seek, text]` where:
- `start_seek` and `end_seek` are in mel spectrogram frame positions (not seconds)
- Need conversion using time precision: `time = seek_position * HOP_LENGTH / SAMPLE_RATE`
- Constants: `HOP_LENGTH = 160`, `SAMPLE_RATE = 16000`
- Time precision per frame: `~0.01 seconds` (10ms)

**Source**: `.venv/lib/python3.13/site-packages/lightning_whisper_mlx/transcribe.py:435`

**Implication**: We need to convert seek positions to seconds with centisecond precision (HH:MM:SS.CC).

### Q3: Segment-level vs word-level timestamps?

**Finding**:
- **Segment-level**: ✅ Available by default in `segments` list
- **Word-level**: Has parameter `word_timestamps: bool = False` in transcribe_audio (line 74), but implementation appears incomplete in lightning-whisper-mlx
- Import exists for `add_word_timestamps` from timing module but not actively used in current version

**Decision**: Use segment-level timestamps only (aligns with clarification decision from spec).

### Q4: How to enable timestamp extraction?

**Finding**: Timestamps are **always extracted** in lightning-whisper-mlx. The `segments` key is always present in the return value. No special flag needed to enable them - they're included by default.

**Implementation Impact**:
- Existing `processor.py:203` already gets the result dict, just not using `segments` key
- Simply access `result.get("segments", [])` to get timestamp data
- No changes needed to transcribe call itself

### Q5: Precision and accuracy considerations

**Findings**:
- Raw precision: ~10ms per frame position
- Requirement: Centisecond precision (HH:MM:SS.CC = 10ms granularity)
- **Perfect match**: Native precision matches required output precision
- Conversion formula: `seconds = seek_position * 0.01` (from HOP_LENGTH/SAMPLE_RATE)

### Q6: Existing codebase patterns

**Current audio_processor structure**:
- `models.py` (83 lines): Data models - **needs timestamp fields added**
- `processor.py` (203 lines): Core logic - **needs segment extraction**
- `cli.py` (240 lines): CLI interface - **needs --timestamps flag**
- `config.py`: Configuration - **needs timestamps option**
- `markdown_formatter.py`: Markdown output - **needs timestamp formatting**

**Test structure**:
- `tests/contract/`: Contract/API tests
- `tests/integration/`: End-to-end tests
- `tests/unit/`: Unit tests

## Technical Decisions

### Decision 1: Data Model Structure

**Choice**: Add optional `segments` field to `TranscriptionResult` dataclass

**Rationale**:
- Maintains backward compatibility (optional field)
- Aligns with Whisper's native output structure
- Simple to serialize to JSON

**Structure**:
```python
@dataclass
class TranscriptionSegment:
    start: float  # seconds
    end: float    # seconds
    text: str

@dataclass
class TranscriptionResult:
    # ... existing fields ...
    segments: list[TranscriptionSegment] | None = None
```

### Decision 2: Time Conversion

**Choice**: Convert seek positions to seconds immediately after transcription

**Formula**: `seconds = seek_position * (HOP_LENGTH / SAMPLE_RATE)`
- Where HOP_LENGTH = 160, SAMPLE_RATE = 16000
- Simplifies to: `seconds = seek_position * 0.01`

**Rationale**:
- Centralize conversion logic in processor
- Store human-readable format (seconds) in model
- Formatters only need to format, not convert

### Decision 3: Timestamp Formatting

**Choice**: Separate formatting functions for markdown vs JSON

**Markdown format**: `[HH:MM:SS.CC] text`
- Example: `[00:01:23.45] This is the transcribed text.`
- Function: `format_timestamp(seconds: float) -> str` returns HH:MM:SS.CC
- Function: `format_segments_markdown(segments) -> str` builds full output

**JSON format**: Structured array
```json
{
  "text": "full transcription",
  "segments": [
    {"start": 83.45, "end": 91.23, "text": "segment text"}
  ]
}
```

### Decision 4: CLI Flag Handling

**Choice**: Add boolean `--timestamps` flag to CLI

**Rationale**:
- Simple on/off switch (no additional parameters needed)
- Passes to config.timestamps boolean
- Processor checks config and includes/excludes segments accordingly

### Decision 5: Error Handling for Missing Timestamps

**Choice**: Warn and continue without timestamps (per clarification)

**Implementation**:
- If `result.get("segments")` is None or empty, log warning
- Set `TranscriptionResult.segments = None`
- Continue normal transcription processing
- User sees warning but gets transcription text

## Dependencies Analysis

**Existing dependencies** (no new dependencies needed):
- `lightning-whisper-mlx`: Already in use, provides timestamps natively
- Python `dataclasses`: Standard library, already used for models
- Python `datetime`/`time`: Standard library, for timestamp formatting

**Conclusion**: Zero new external dependencies required ✅

## Implementation Complexity Estimate

**File Changes Required**:
1. `models.py`: +20 lines (new TranscriptionSegment class, extend TranscriptionResult)
2. `processor.py`: +15 lines (extract and convert segments)
3. `cli.py`: +3 lines (add --timestamps flag)
4. `config.py`: +2 lines (add timestamps: bool field)
5. `markdown_formatter.py`: +25 lines (timestamp formatting functions)
6. New test files: ~150 lines total

**Total**: ~215 new lines, all well under 250-line limit per file ✅

## Risks & Mitigations

**Risk 1**: Segment format changes in lightning-whisper-mlx updates
- **Mitigation**: Contract tests will catch API changes, version pin in requirements

**Risk 2**: Timestamp accuracy for very long audio files
- **Mitigation**: Test with 2-hour file (max supported duration), validate precision

**Risk 3**: Performance impact of timestamp extraction
- **Mitigation**: Timestamps already extracted by default, no performance impact

## References

- lightning-whisper-mlx source: `.venv/lib/python3.13/site-packages/lightning_whisper_mlx/transcribe.py`
- Whisper timestamp documentation: OpenAI Whisper timing conventions
- Existing audio_processor code: `anyfile_to_ai/audio_processor/`

## Next Steps → Phase 1

With research complete and zero ambiguities remaining, proceed to Phase 1:
1. Create data model (data-model.md)
2. Define API contracts (contracts/)
3. Generate quickstart guide (quickstart.md)
4. Write failing contract tests
