# Feature Specification: Shared Output Formatter Unification

**Feature Branch**: `017-output-formatter-unification`
**Created**: 2026-02-13
**Status**: Draft
**Input**: User description: "Create a new spec package to decide and implement shared output formatter unification with ADR, target design, migration, implementation-ready tasks, tests, and docs while preserving compatibility."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Approve a Single Formatter Architecture (Priority: P1)

As a maintainer, I need an explicit architecture decision for formatter unification so that future implementation follows one agreed contract and avoids duplicate, drifting formatter logic.

**Why this priority**: Without an accepted decision record, module-by-module implementation can diverge and break stable output contracts.

**Independent Test**: Review the spec to confirm an ADR exists with a final decision, alternatives, tradeoffs, risks, scope boundaries, compatibility guarantees, and deprecation policy.

**Acceptance Scenarios**:

1. **Given** the spec package, **When** maintainers review architecture sections, **Then** they find a single accepted target architecture and explicit non-goals.
2. **Given** existing module formatter differences, **When** maintainers evaluate the ADR, **Then** they can trace why shared abstraction is selected and why alternatives were rejected.

---

### User Story 2 - Migrate Incrementally Without Regressions (Priority: P2)

As a module owner, I need a phased migration strategy with rollback paths so each backend can adopt shared formatters safely while preserving current CLI and Python behavior.

**Why this priority**: Migration risk is highest where output contracts are already consumed by scripts and tests.

**Independent Test**: Validate that the spec defines Phase A/B/C with per-phase code areas, compatibility risks, rollback strategy, checkpoints, and acceptance criteria.

**Acceptance Scenarios**:

1. **Given** the migration section, **When** implementation starts, **Then** teams can execute one module migration at a time with explicit gates before moving forward.
2. **Given** a regression in a migrated module, **When** rollback is required, **Then** the spec provides a module-local fallback that does not block unrelated modules.

---

### User Story 3 - Implement With Test and Documentation Parity (Priority: P3)

As a contributor, I need implementation-ready tasks and a mapped test/doc plan so I can deliver the unification work in small steps while keeping contracts stable.

**Why this priority**: Planning completeness reduces rework and ensures constitution-required test and documentation updates are delivered with code changes.

**Independent Test**: Validate that concrete files, new tests, verification gates, and documentation updates are listed and traceable to requirements.

**Acceptance Scenarios**:

1. **Given** the implementation plan, **When** contributors pick up work, **Then** each task identifies expected file changes and compatibility shims.
2. **Given** the test plan, **When** contributors run required suites, **Then** they can verify output equivalence, metadata consistency, timestamp stability, and error-path compatibility.

---

### Edge Cases

- Module-specific outputs differ in wording/order today; migration MUST preserve existing externally visible output per module unless a separate approved contract change is recorded.
- Unknown metadata keys may appear from backends; shared normalization MUST preserve them in extension space and MUST NOT drop keys silently.
- Audio timestamp boundaries (negative values, >2 hours, rounding rollovers) MUST keep current validation and formatting behavior.
- Some flows do not currently expose metadata in plain/markdown output; shared abstraction MUST keep these current behaviors until explicitly deprecated.
- Optional dependencies may be missing at runtime; formatter unification MUST NOT introduce hard import-time coupling.

## Requirements *(mandatory)*

### Functional Requirements

#### Architecture Decision (ADR)

- **FR-001**: The spec MUST include an ADR section that explicitly accepts a final target architecture: a shared formatter abstraction used across PDF, image, audio, text summarizer, and document conversion entry points.
- **FR-002**: The ADR MUST include rationale, alternatives considered, tradeoffs, risks, scope boundaries, and explicit non-goals.
- **FR-003**: The ADR MUST define backward-compatibility guarantees for existing CLI and Python formatter behavior and a deprecation policy for duplicate formatter logic.
- **FR-004**: The ADR MUST state that migration is incremental and additive-first, and MUST reject big-bang replacement.

#### Target Design and Canonical Contracts

- **FR-005**: The design MUST define a shared formatter package under `anyfile_to_ai/` with a public interface for formatting to `text/plain`, `markdown`, and `json`.
- **FR-006**: The design MUST define canonical `text/plain` contract semantics: human-readable text output with module-preserved phrasing and ordering, with metadata shown only where currently supported or explicitly enabled.
- **FR-007**: The design MUST define canonical `markdown` contract semantics: deterministic heading and section structure per module profile, preserving current markdown content expectations and ordering.
- **FR-008**: The design MUST define canonical `json` contract semantics: machine-readable object output, stable core fields, deterministic key presence rules, and explicit metadata inclusion behavior.
- **FR-009**: The design MUST define metadata inclusion policy for JSON: metadata is included only when requested by caller flag and when available from backend, except previously documented route-specific best-effort behavior that must remain unchanged.
- **FR-010**: The design MUST define audio-specific timestamp and segment formatting rules, including `HH:MM:SS.CC` formatting for timestamp utility outputs, segment ordering requirements, and boundary validation behavior.
- **FR-011**: The design MUST define compatibility treatment for legacy audio markdown section headings that currently use whole-second display.

#### Metadata Normalization Model

- **FR-012**: The design MUST define common metadata groups (`processing`, `configuration`, `source`) with required and optional fields and clear null/unavailable handling.
- **FR-013**: The design MUST define backend-specific extension fields and where they are represented without polluting common required fields.
- **FR-014**: Unknown or extra metadata keys from backends MUST be preserved in normalized output under an extension container and MUST NOT cause formatter failure.
- **FR-015**: Metadata normalization MUST be deterministic and round-trip safe for JSON consumers during migration.

#### Error Behavior and Contract Stability

- **FR-016**: Shared formatter interfaces MUST raise stable, explicit formatting errors for unsupported format requests while preserving current CLI exit-code and stdout/stderr contract behavior.
- **FR-017**: Formatter layers MUST NOT swallow backend errors; they must preserve current exception semantics and diagnostics pathways.
- **FR-018**: Contract stability requirements MUST guarantee no user-facing behavior regressions in existing CLI/API usage during migration unless separately approved.

#### Migration Strategy (Phased)

- **FR-019**: The spec MUST define a Phase A introducing shared interfaces and adapters with no behavioral change.
- **FR-020**: The spec MUST define a Phase B module-by-module migration order with justification and per-module checkpoints.
- **FR-021**: The spec MUST define a Phase C retirement of duplicate formatter logic only after equivalence tests and contract gates pass.
- **FR-022**: Each migration phase MUST include code areas to change, compatibility risks, rollback strategy, and acceptance criteria.

#### Implementation Planning

- **FR-023**: The spec MUST provide an implementation-ready task sequence with explicit file/module create/update targets.
- **FR-024**: The spec MUST identify API surface changes, compatibility shims, and expected deprecation notices.
- **FR-025**: The implementation plan MUST preserve module boundaries and avoid introducing unnecessary cross-module coupling.

#### Test and Documentation Planning

- **FR-026**: The spec MUST define unit, integration, and contract tests covering output equivalence, metadata consistency, timestamp stability, and error-path compatibility.
- **FR-027**: The test plan MUST require deterministic fixtures and minimal optional dependency coupling.
- **FR-028**: The test plan MUST map required coverage to concrete test files and new test cases.
- **FR-029**: The spec MUST list README/module README/CLI help updates needed for maintainers and contributors.

### Assumptions

- Existing module-specific formatter outputs in current tests are the baseline compatibility target.
- No new output format beyond `plain`, `markdown`, and `json` is in scope for unification in this feature.
- Existing metadata contract tests remain authoritative for required/optional metadata behavior.
- Deprecation policy can be release-based and additive, without immediate removal in the same migration phase.

### Non-Goals

- Changing output wording/structure for end users beyond what is required to preserve current behavior.
- Introducing new model/provider configuration, credentials, or network behavior.
- Reworking unrelated processing logic (extraction/transcription/summarization internals).
- Forcing strict cross-module textual identity in plain/markdown output where modules intentionally differ.

### Decision Record (ADR): Adopt Shared Formatter Abstraction

**Status**: Accepted

**Decision**: Introduce a shared formatter package and common formatter interface, then migrate modules incrementally behind compatibility adapters until duplicate formatter logic can be safely retired.

**Context**:

- Formatter behavior exists in multiple modules with overlapping concerns (`plain`, `markdown`, `json`) and diverging implementation paths.
- The previous bridge spec explicitly deferred formatter unification; this spec resolves that deferment with an implementation-ready architecture decision.
- Existing tests encode user-visible contracts that must remain stable.

**Alternatives Considered**:

1. Keep module-local formatters indefinitely and rely on contract tests only.
2. Big-bang replacement of all formatters with a new shared formatter layer in one release.
3. Shared interface plus incremental adapter-based migration (selected).

**Rationale**:

- Option 1 preserves short-term stability but continues duplication and drift risk.
- Option 2 reduces duplication quickly but has highest regression risk and weakest rollback isolation.
- Option 3 balances stability and maintainability by preserving behavior first, then converging implementations with measurable gates.

**Tradeoffs**:

- Additional temporary adapter/shim complexity during migration.
- Longer delivery timeline than a full rewrite, but substantially lower compatibility risk.
- Parallel maintenance of old and new formatter paths until Phase C completion.

**Risks**:

- Hidden behavior differences may surface when adapters normalize metadata.
- Audio timestamp formatting can regress if precision and heading compatibility are conflated.
- Duplicate logic may linger if retirement gates are not enforced.

**Scope Boundaries**:

- In scope: shared interface/module, metadata normalization model, phased migration, compatibility shims, and tests/docs updates.
- Out of scope: new output formats, rewriting backend processing, or broad CLI redesign.

**Backward-Compatibility Guarantees**:

- Existing CLI flags and defaults remain unchanged.
- Existing Python API function signatures remain unchanged unless additive.
- Existing contract tests for markdown, metadata, timestamp, and CLI output continue to pass during and after migration.

**Deprecation Policy**:

- Phase A/B: Keep existing module formatter entry points as compatibility shims.
- Start deprecation notices only after a module completes migration and equivalence tests pass.
- Remove duplicate module-local formatter implementations only in Phase C and only after at least one release cycle with deprecation notices and stable contract test history.

### Target Design

#### Shared Package and Public Interfaces

- Shared package location: `anyfile_to_ai/output_formatter/`.
- Public interfaces:
  - `format_plain(payload, profile, include_metadata=False) -> str`
  - `format_markdown(payload, profile, include_metadata=False) -> str`
  - `format_json(payload, profile, include_metadata=False) -> dict`
  - `serialize_json(data) -> str` (deterministic JSON string rendering)
- Profile-based behavior supports module-specific contracts (`pdf`, `image`, `audio`, `text`, `document_converter`) without changing caller signatures.

#### Canonical Output Contracts

- `text/plain`:
  - Returns a string suitable for stdout.
  - Preserves module-specific wording and ordering used today.
  - Includes metadata section only when currently supported in that module and metadata is available.
- `markdown`:
  - Returns markdown text with deterministic section ordering.
  - Preserves existing module heading patterns (`# PDF Document`, `# Image Descriptions`, `# Transcription`, `# Summary`).
  - Preserves existing handling of special characters (no added escaping behavior changes).
- `json`:
  - Returns a JSON-serializable object with deterministic required keys per module profile.
  - Includes `metadata` only according to current include rules and backend availability constraints.
  - Preserves backend-specific fields (for example technical/image/audio extras) as extension fields.

#### Timestamp and Segment Rules (Audio Extension)

- Timestamp utility contract remains `HH:MM:SS.CC` with centisecond rounding.
- Invalid timestamps (<0 or >2 hours) remain explicit errors.
- Segment ordering remains chronological.
- Legacy markdown transcription section headings remain compatible with current display convention until explicitly versioned.

#### Metadata Normalization Model

- Common required groups:
  - `processing`: `timestamp`, `model_version`, optional `processing_time_seconds`
  - `configuration`: optional `user_provided`, optional `effective`
  - `source`: required `file_path`, optional backend-specific source attributes
- Common optional cross-module fields include `file_size_bytes`, `format`, language and dimension fields where available.
- Backend-specific extension fields are grouped under module profile extension space and preserved for JSON output.
- Unknown keys are retained under extension space; formatter behavior is permissive-pass-through, not strict-drop.

#### Error Behavior and Stability Rules

- Unsupported format selection yields stable formatter-layer error that maps to existing CLI/API failure behavior.
- Formatter functions are pure formatting transforms and do not mutate backend result data.
- Shared formatter changes require contract test parity before replacing module-local behavior.

### Migration Strategy (Incremental, Module-Safe)

#### Phase A - Shared Interfaces + Adapters

- **Code areas**:
  - Create `anyfile_to_ai/output_formatter/` package.
  - Add adapter wrappers in module-local formatter entry points without changing public module APIs.
  - Add baseline equivalence fixtures/tests.
- **Compatibility risks**: accidental whitespace/order drift in string outputs; metadata key ordering drift in JSON serialization.
- **Rollback strategy**: route affected module back to existing local formatter implementation by toggling adapter call path, keep shared package unused for that module.
- **Acceptance criteria**:
  - Shared package exists with public interface and profile support.
  - No module output behavior changes in existing contract tests.
  - New equivalence tests pass for baseline fixtures.

#### Phase B - Module-by-Module Migration

- **Migration order (justified)**:
  1. `text_summarizer` (smallest formatter surface and least structural metadata complexity).
  2. `image_processor` (batch/single outputs but straightforward formatting profiles).
  3. `pdf_extractor` (multiple output paths and metadata sections; moderate complexity).
  4. `audio_processor` (timestamp/segment rules and strict formatting contracts; highest risk).
- **Code areas**:
  - Update each module formatter call site to shared formatter profile.
  - Keep module-local functions/classes as shims delegating to shared package.
  - Expand per-module equivalence tests.
- **Compatibility risks**: per-module metadata section formatting and legacy heading text divergence.
- **Rollback strategy**: rollback only the in-flight module by restoring shim target to local implementation while leaving previous migrated modules unchanged.
- **Acceptance criteria**:
  - For each module, old and new outputs are equivalent for representative fixtures.
  - Module-specific contract tests and relevant integration tests pass before moving to next module.

#### Phase C - Duplicate Logic Retirement

- **Code areas**:
  - Remove retired duplicate formatter logic from module-local implementations.
  - Keep compatibility shims and deprecation guidance where external imports depend on old paths.
  - Finalize shared formatter documentation and contributor guidance.
- **Compatibility risks**: hidden third-party imports of removed internals.
- **Rollback strategy**: restore removed wrapper functions from tagged pre-removal commit while keeping shared formatter unchanged.
- **Acceptance criteria**:
  - All formatter flows execute through shared module.
  - Deprecated paths remain functional or clearly redirected for one release cycle.
  - Full unit/integration/contract suite passes with unchanged user-facing outputs.

### Implementation Plan

#### Task Breakdown and Sequencing

1. Establish shared formatter package interfaces and metadata normalization models (Phase A).
2. Add adapter shims in each module, initially no-op behavior change.
3. Add equivalence test harness and baseline fixtures.
4. Migrate modules in Phase B order with per-module test gates.
5. Apply deprecation notices for duplicated logic once module parity is proven.
6. Retire duplicated logic in Phase C and complete docs updates.

#### Expected File/Module Changes

- New files (planned):
  - `anyfile_to_ai/output_formatter/__init__.py`
  - `anyfile_to_ai/output_formatter/interfaces.py`
  - `anyfile_to_ai/output_formatter/profiles.py`
  - `anyfile_to_ai/output_formatter/metadata.py`
  - `anyfile_to_ai/output_formatter/plain.py`
  - `anyfile_to_ai/output_formatter/markdown.py`
  - `anyfile_to_ai/output_formatter/json_formatter.py`
  - `anyfile_to_ai/output_formatter/errors.py`
- Updated files (planned):
  - `anyfile_to_ai/pdf_extractor/output_formatters.py`
  - `anyfile_to_ai/pdf_extractor/markdown_formatter.py`
  - `anyfile_to_ai/image_processor/cli.py`
  - `anyfile_to_ai/audio_processor/markdown_formatter.py`
  - `anyfile_to_ai/text_summarizer/__main__.py`
  - `anyfile_to_ai/document_converter/` formatter-adjacent output adapters (if needed for parity)

#### API Surface Changes and Shims

- Keep existing public functions/classes callable from current import paths.
- Any new shared formatter API is additive and internal-first.
- Existing call signatures remain unchanged; shims adapt legacy payloads to shared profile contracts.
- Deprecation notices apply to internal duplicate implementations, not to existing public module entry points in this feature.

### Test Plan

#### Unit Tests

- Add shared formatter unit tests:
  - `tests/unit/test_shared_output_formatter_plain.py`
  - `tests/unit/test_shared_output_formatter_markdown.py`
  - `tests/unit/test_shared_output_formatter_json.py`
  - `tests/unit/test_shared_output_metadata_normalization.py`
  - `tests/unit/test_shared_output_formatter_errors.py`
- Extend timestamp-focused unit checks:
  - Update `tests/unit/test_timestamp_formatting.py` to validate shared formatter audio profile parity.

#### Integration Tests

- Add migration equivalence integration tests:
  - `tests/integration/test_formatter_equivalence_text.py`
  - `tests/integration/test_formatter_equivalence_image.py`
  - `tests/integration/test_formatter_equivalence_pdf.py`
  - `tests/integration/test_formatter_equivalence_audio.py`
- Ensure deterministic fixtures and mocked heavy dependencies for optional runtime paths.

#### Contract Tests

- Preserve and extend existing contracts:
  - `tests/contract/test_pdf_markdown.py`
  - `tests/contract/test_image_markdown.py`
  - `tests/contract/test_audio_markdown.py`
  - `tests/contract/test_text_markdown.py`
  - `tests/contract/test_timestamp_contracts.py`
  - `tests/contract/test_cli_output.py`
  - `tests/contract/test_pdf_metadata_contract.py`
  - `tests/contract/test_image_metadata_contract.py`
  - `tests/contract/test_audio_metadata_contract.py`
  - `tests/contract/test_text_metadata_contract.py`
- Add new cross-module contract suite:
  - `tests/contract/test_output_formatter_unified_contract.py` for shared required fields, metadata consistency, and error-path compatibility.

#### Verification Gates

- Per phase/module gate:
  - Relevant unit tests pass.
  - Relevant integration equivalence tests pass.
  - Relevant contract tests pass with no output diff regressions.
- Full gate before Phase C completion:
  - `uv run ruff check .`
  - `uv run ruff format .`
  - `uv run pytest`

### Documentation Updates

- Update root `README.md` with shared formatter architecture note and compatibility policy.
- Update module READMEs for `pdf_extractor`, `image_processor`, `audio_processor`, and `text_summarizer` to document stable output contracts and metadata behavior.
- Update CLI help/docs where formatter behavior and metadata flags are described.
- Add maintainer/contributor documentation for shared formatter profiles and migration guardrails.

### Key Entities *(include if feature involves data)*

- **Formatter Profile**: Module-specific behavior contract (`pdf`, `image`, `audio`, `text`, `document_converter`) used by shared formatter interfaces.
- **Formatter Payload**: Input data structure from module processors containing content, metadata, and extension fields needed for output rendering.
- **Normalized Metadata**: Common metadata model with required groups and extension-pass-through semantics.
- **Output Contract**: Stable module-facing representation for `plain`, `markdown`, and `json` outputs, including metadata inclusion rules.
- **Migration Checkpoint**: Phase/module gate that defines tests, rollback conditions, and acceptance criteria before advancing.

### Acceptance Criteria

- The spec includes an accepted ADR choosing shared formatter abstraction with rationale, alternatives, tradeoffs, risks, and deprecation/compatibility policy.
- The target design defines canonical contracts for plain/markdown/json, audio timestamp rules, metadata normalization, and error stability.
- The migration strategy is phased (A/B/C), module-safe, and includes code areas, risks, rollback, and acceptance criteria per phase.
- The implementation plan names concrete files/modules to create or update and identifies compatibility shims.
- The test plan maps unit/integration/contract coverage to concrete files and includes deterministic verification gates.

## Constitution Alignment *(mandatory)*

- **Module Impact**: Introduces a focused shared package under `anyfile_to_ai/output_formatter/` and updates formatter call paths in `pdf_extractor`, `image_processor`, `audio_processor`, `text_summarizer`, with optional bridge alignment in `document_converter`.
- **Contract Impact**: Preserves existing CLI and Python API formatter behavior while adding a shared abstraction behind compatibility shims; output/error contracts remain stable unless explicitly approved in a separate contract change.
- **Test Plan**: Requires failing-first updates and additions across `tests/unit`, `tests/integration`, and `tests/contract` for output equivalence, metadata consistency, timestamp stability, and error-path compatibility.
- **Configuration & Security**: No new secrets or credential handling; optional dependency behavior remains lazy and deterministic for tests.
- **Documentation Impact**: Updates root and module README content plus formatter contract guidance for maintainers/contributors in the same implementation scope.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of existing formatter-related contract tests pass unchanged during each migration phase.
- **SC-002**: For each migrated module, 100% of baseline equivalence fixtures produce identical plain/markdown/json outputs before and after adapter adoption.
- **SC-003**: 100% of covered metadata cases preserve required common fields and backend extension keys without silent key loss.
- **SC-004**: 100% of timestamp boundary and segment formatting contract checks remain stable for audio outputs across migration.
- **SC-005**: Duplicate formatter implementations are reduced to shared interface + shims by Phase C with no increase in formatter-related support regressions during one release cycle after rollout.
