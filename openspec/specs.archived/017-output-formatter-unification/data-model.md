# Data Model: Shared Output Formatter Unification

Date: 2026-02-13
Feature: `specs/017-output-formatter-unification/spec.md`

## Entity: FormatterProfile

- **Description**: Module-specific rendering contract selector.
- **Values**: `pdf`, `image`, `audio`, `text`, `document_converter`
- **Validation Rules**:
  - Must match one supported profile.
  - Unsupported values raise stable formatter errors.

## Entity: FormatterPayload

- **Description**: Input payload from module processors for rendering.
- **Fields**:
  - `content` (string, required)
  - `metadata` (object | null, optional)
  - `extensions` (object, optional, unknown-key pass-through)
  - `segments` (array, optional, audio profile)
- **Validation Rules**:
  - Successful formatting requires `content`.
  - `segments`, when present, remain chronological.

## Entity: NormalizedMetadata

- **Description**: Canonical metadata structure used by shared formatters.
- **Groups**:
  - `processing`: `timestamp` (required), `model_version` (required), `processing_time_seconds` (optional)
  - `configuration`: `user_provided` (optional), `effective` (optional)
  - `source`: `file_path` (required), backend-specific source attributes (optional)
  - `extensions`: unknown/backend-specific fields (optional, preserved)
- **Validation Rules**:
  - Required fields must remain present when metadata is included.
  - Unknown keys must not be dropped.

## Entity: OutputContract

- **Description**: Rendered output representation for each target format.
- **Formats**:
  - `plain`: `output` (string)
  - `markdown`: `output` (string)
  - `json`: `output` (object), optional `metadata` per include rules
- **Validation Rules**:
  - Plain/markdown preserve module-specific wording and ordering.
  - JSON key presence is deterministic per profile.

## Entity: AudioTimestampSegment

- **Description**: Audio segment/timestamp rendering unit.
- **Fields**:
  - `start_seconds` (float)
  - `end_seconds` (float)
  - `text` (string)
  - `display_timestamp` (derived, `HH:MM:SS.CC`)
- **Validation Rules**:
  - `0 <= timestamp <= 7200`.
  - Invalid bounds raise explicit formatter errors.

## Entity: MigrationCheckpoint

- **Description**: Gate state for each phase/module migration slice.
- **Fields**:
  - `phase` (`A` | `B` | `C`)
  - `module` (`shared` or one `FormatterProfile`)
  - `unit_passed` (bool)
  - `integration_passed` (bool)
  - `contract_passed` (bool)
  - `rollback_path` (string)
  - `status` (`pending` | `passed` | `rolled_back`)
- **Validation Rules**:
  - Must be `passed` before moving to next module/phase.
  - Rollback must be module-local.

## Relationships

- One `FormatterProfile` applies to many `FormatterPayload` instances.
- One `FormatterPayload` may contain one `NormalizedMetadata` object.
- One `FormatterPayload` yields one `OutputContract` per requested format.
- Audio payloads may include many `AudioTimestampSegment` entries.

## State Transitions

1. `legacy_only` -> `phase_a_adapted`
2. `phase_a_adapted` -> `phase_b_module_migrated`
3. `phase_b_module_migrated` -> `phase_c_retired_duplicates`
4. Any state -> `rolled_back`
