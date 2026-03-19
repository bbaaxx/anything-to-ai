# Feature Specification: Metadata Dictionary for Result Models

**Feature Branch**: `015-extend-all-result`
**Created**: 2025-10-25
**Status**: Draft
**Input**: User description: "Extend all result models to include a `metadata` dictionary that preserves source document information similar to MarkItDown. For PDFs: page count, file size, creation date. For images: EXIF data, dimensions, camera info. For audio: duration, sample rate, detected language confidence. For all modules: processing timestamps, model versions, and configuration used. Make metadata optional but consistent across modules, accessible via `--include-metadata` flag."

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## Clarifications

### Session 2025-10-25
- Q: How should the system handle missing or unavailable metadata fields? → A: Set field to descriptive placeholder like "unavailable" or "unknown"
- Q: Which sensitive information should be filtered from metadata (specifically from EXIF data)? → A: No filtering - include all metadata (user responsibility)
- Q: What EXIF fields should be included in image metadata? → A: All available EXIF tags (complete preservation)
- Q: What timestamp format should be used for processing timestamps? → A: ISO 8601 with timezone (e.g., "2025-10-25T14:30:00-07:00") - standard, unambiguous
- Q: How should configuration parameters be represented in metadata? → A: Both explicit and effective config (verbose but comprehensive)

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As a user processing documents, images, or audio files, I want to access detailed information about the source files and the processing that occurred so that I can verify processing quality, track processing history, audit results, and understand the context of the extracted content.

### Acceptance Scenarios
1. **Given** a PDF file, **When** processing with metadata enabled, **Then** the result includes page count, file size, creation date, processing timestamp, and model version used
2. **Given** an image file, **When** processing with metadata enabled, **Then** the result includes EXIF data, dimensions, camera information, processing timestamp, and model version
3. **Given** an audio file, **When** processing with metadata enabled, **Then** the result includes duration, sample rate, detected language confidence score, processing timestamp, and model version
4. **Given** any file type, **When** processing without metadata flag, **Then** the result excludes metadata information (default behavior)
5. **Given** any file type, **When** processing with metadata flag, **Then** all processing configuration parameters used are included in metadata
6. **Given** multiple files of different types, **When** processing all with metadata enabled, **Then** each result contains consistent metadata structure with type-specific fields populated

### Edge Cases
- What happens when source file has no metadata (e.g., generated PDF with no creation date)? → System sets field to "unavailable"
- How does system handle corrupted or missing EXIF data in images? → System sets affected fields to "unavailable"
- What happens when audio language detection has low confidence scores? → System includes actual confidence score regardless of value
- How are processing errors reflected in metadata? → System includes error information in metadata when available
- What happens when file size cannot be determined? → System sets file_size field to "unavailable"
- How does metadata behave when processing from stdin or piped input? → System sets source-file-specific fields (like file size, creation date) to "unavailable"

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST support an optional metadata dictionary in all result models across PDF, image, audio, and text processing modules
- **FR-002**: System MUST provide a command-line flag `--include-metadata` to control metadata inclusion in output. Exception: text_summarizer uses existing `--no-metadata` flag (inverse logic) to disable metadata, as metadata is enabled by default for this module only.
- **FR-003**: System MUST default to excluding metadata when the flag is not provided (backward compatible)
- **FR-004**: System MUST include the following metadata for PDF processing when metadata is enabled: page count, file size in bytes, file creation date in ISO 8601 format with timezone
- **FR-005**: System MUST include the following metadata for image processing when metadata is enabled: all available EXIF tags (complete preservation), image dimensions (width and height), and camera information extracted from EXIF data
- **FR-006**: System MUST include the following metadata for audio processing when metadata is enabled: duration, sample rate, detected language confidence score
- **FR-007**: System MUST include the following metadata for all processing modules when metadata is enabled: processing timestamp in ISO 8601 format with timezone, model version used, configuration parameters (both user-provided explicit parameters and effective configuration after defaults applied)
- **FR-008**: System MUST maintain consistent metadata structure across all modules with a common schema for universal fields and type-specific fields for source-specific metadata
- **FR-009**: System MUST gracefully handle missing or unavailable metadata fields by setting them to descriptive placeholders ("unavailable" or "unknown"), ensuring consistent schema across all outputs
- **FR-010**: System MUST preserve metadata through output format conversions with format-specific rendering:
  - JSON: Nested metadata object at top level
  - Markdown: YAML frontmatter or dedicated metadata section
  - CSV: Flattened metadata columns with dot notation (e.g., `metadata.processing.timestamp`)
  - Plain text: MUST exclude metadata to maintain human readability (metadata only available in structured formats)
- **FR-011**: System MUST include metadata in piped/chained processing workflows when flag is provided
- **FR-012**: System MUST include all available metadata without filtering sensitive information (GPS coordinates, user names, device identifiers, etc.), leaving privacy management as user responsibility

### Key Entities *(include if feature involves data)*
- **Metadata Dictionary**: A structured collection of information about source documents and processing operations, containing both universal fields (processing timestamp, model version, configuration) and type-specific fields (PDF: page count, file size, creation date; Image: EXIF data, dimensions, camera info; Audio: duration, sample rate, language confidence)
- **Universal Metadata**: Common metadata fields present across all processing modules including processing timestamp in ISO 8601 format (when the file was processed), model version (version identifier of the processing model used), and configuration parameters (both explicit user-provided parameters and effective configuration after defaults applied)
- **Source Metadata**: Type-specific metadata extracted from source files including file properties (size, creation date), embedded metadata (EXIF, ID3 tags), and content properties (page count, dimensions, duration, sample rate)
- **Processing Metadata**: Metadata generated during processing including quality metrics (language confidence scores), processing outcomes, and model-specific outputs

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
