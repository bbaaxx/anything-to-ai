# MarkItDown-Inspired Enhancements

**Context**: We are integrating MarkItDown as a dependency to handle unsupported formats (Office docs, HTML, EPUB) while maintaining our specialized modules (PDF, images, audio) for AI-enhanced processing.

**Goal**: Adopt MarkItDown's best output practices across all our modules while maintaining our AI-first modular architecture and production-grade features.

---

## 1. Markdown Output Format Support

Add `--format markdown` option to all modules (pdf_extractor, image_processor, audio_processor, text_summarizer) to output results in structured markdown. For PDFs, preserve headings and structure. For images, create markdown with image references and VLM descriptions as captions. For audio, format transcriptions with speaker labels and timestamps as markdown sections. For summarizer, output summaries with proper heading hierarchy and bullet points. This makes all modules compatible with LLM consumption workflows while remaining human-readable.

---

## 2. Timestamp Support for Audio Transcription

Enhance `TranscriptionResult` model to include optional word-level or segment-level timestamps from Whisper. Add `--timestamps` CLI flag to audio_processor that outputs transcriptions with temporal markers (e.g., `[00:01:23] Speaker: text here`). This enables downstream use cases like video subtitles, podcast chapter markers, and time-indexed search. Output formats should support both markdown (human-readable) and JSON (machine-readable) with timestamp arrays.

---

## 3. Rich Metadata Preservation

Extend all result models to include a `metadata` dictionary that preserves source document information similar to MarkItDown. For PDFs: page count, file size, creation date. For images: EXIF data, dimensions, camera info. For audio: duration, sample rate, detected language confidence. For all modules: processing timestamps, model versions, and configuration used. Make metadata optional but consistent across modules, accessible via `--include-metadata` flag.

---

## 4. Document Structure Preservation

Enhance PDF extractor to detect and preserve document structure (headings, lists, tables, code blocks) in markdown output format. Use heuristics like font size changes, indentation, and bullet characters to infer structure. When outputting to markdown, convert detected structures to proper markdown syntax (# headers, - lists, | tables |). This bridges the gap between raw text extraction and MarkItDown's structure-aware conversion, making our PDF output more useful for LLM processing.

---

## 5. Unified Output Formatter Module

Create a new `output_formatters` shared module that provides consistent formatting functions across all processors. Include formatters for: plain text, JSON, CSV, markdown, and structured (with metadata). Each module imports and uses these formatters instead of implementing their own, ensuring consistent output structure project-wide. This makes it easier to add new output formats (like HTML or XML) in the future and reduces code duplication.

---

## 6. MarkItDown Integration Module

Create `document_converter` module as a bridge to MarkItDown for unsupported formats. This module wraps MarkItDown's API with our standard data models and interfaces, providing consistent CLI and Python API patterns. Include intelligent format routing that directs PDF/images/audio to our specialized processors (which have VLM, streaming, and MLX optimizations) while routing Office documents, HTML, EPUB, ZIP, and YouTube URLs to MarkItDown. Output follows our existing format patterns (plain, JSON, markdown) and integrates seamlessly with downstream modules like text_summarizer.

---

## Implementation Priority

**Phase 1 (This Week)** - MarkItDown Integration
- Create document_converter module with MarkItDown wrapper
- Implement format router for intelligent processor selection
- Add markitdown[all] dependency to pyproject.toml

**Phase 2 (2-4 Weeks)** - Output Format Enhancements
- Add markdown formatter to output_formatters module
- Extend existing models with optional metadata fields
- Implement timestamp support in audio_processor

**Phase 3 (2-3 Months)** - Advanced Features
- Add structure detection to pdf_extractor for markdown output
- Unify all output formatting across modules
- Add comprehensive metadata to all result objects

**Ongoing** - Selective Replacement
- Monitor which MarkItDown formats are most used
- Replace high-traffic formats with custom implementations as needed
- Maintain MarkItDown for long-tail format support
