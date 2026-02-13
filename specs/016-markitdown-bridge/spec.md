# Feature Specification: MarkItDown Bridge Contracts (Formatter Unification Deferred)

**Feature Branch**: `016-markitdown-bridge`
**Created**: 2026-02-12
**Status**: Draft
**Input**: User description: "Create a new formal spec package for the MarkItDown bridge with an explicit defer-formatter-unification decision; formalize routing, API/CLI, errors, output compatibility, decision record, and test requirements while preserving backward compatibility."

## Clarifications

### Session 2026-02-12

- Q: Should this phase require a dedicated `document_converter` CLI contract and implementation? → A: Yes; include a minimal CLI contract surface in this phase to preserve Python/CLI parity for user-facing conversion capability.
- Q: How should `include_metadata` apply to MarkItDown-routed conversions in this phase? → A: Guarantee metadata toggle behavior for specialized backends only; MarkItDown metadata remains best-effort and may be present regardless of the flag.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deterministic Routing Contract (Priority: P1)

As a maintainer of document conversion workflows, I need deterministic source-to-backend routing so that conversions remain predictable and backward-compatible across file types and URLs.

**Why this priority**: Routing behavior is the highest-risk compatibility surface; any drift breaks existing automation and tests.

**Independent Test**: Can be fully tested by route classification and delegation tests that assert route selection for each supported input category.

**Acceptance Scenarios**:

1. **Given** a local `.pdf` source, **When** route determination is requested, **Then** the selected backend is `pdf_extractor`.
2. **Given** a local image source (`.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`), **When** route determination is requested, **Then** the selected backend is `image_processor`.
3. **Given** a local audio source (`.mp3`, `.wav`, `.m4a`), **When** route determination is requested, **Then** the selected backend is `audio_processor`.
4. **Given** a local Office/HTML/EPUB/ZIP source, **When** route determination is requested, **Then** the selected backend is MarkItDown.
5. **Given** an HTTP/HTTPS URL (including YouTube hosts), **When** route determination is requested, **Then** the selected backend is MarkItDown.

---

### User Story 2 - Stable API and Error Semantics (Priority: P2)

As a Python API consumer, I need stable conversion outputs and explicit error semantics so that I can safely integrate conversion into pipelines and handle failures correctly.

**Why this priority**: A clear API and error contract prevents fragile caller-side workarounds and preserves trust in module behavior.

**Independent Test**: Can be fully tested by unit and contract tests for `convert_document`, including validation errors, missing dependency errors, and wrapped vs non-wrapped exceptions.

**Acceptance Scenarios**:

1. **Given** an empty source string, **When** conversion is requested, **Then** `UnsupportedInputError` is raised with actionable input guidance.
2. **Given** a MarkItDown-routed input and unavailable MarkItDown dependency, **When** conversion is requested, **Then** `MissingDependencyError` is raised with install guidance.
3. **Given** an unexpected backend exception during conversion, **When** conversion fails, **Then** `DocumentConversionError` wraps the original exception and includes source and route context.
4. **Given** a successful conversion, **When** result is returned, **Then** the output contains at minimum `source`, `route`, and `content`, with optional `metadata` and backend-native `raw_result`.

---

### User Story 3 - Explicitly Deferred Formatter Unification (Priority: P3)

As an architect, I need a formal decision record that defers cross-backend formatter unification so that this phase can lock contracts now without forcing formatter refactors.

**Why this priority**: This prevents scope creep while still adding guardrails against output contract drift.

**Independent Test**: Can be tested by reviewing the decision record and by contract tests that enforce minimum normalized output guarantees while allowing backend-specific differences.

**Acceptance Scenarios**:

1. **Given** this feature scope, **When** implementation planning begins, **Then** formatter unification is explicitly out of scope.
2. **Given** backend-local formatters remain in place, **When** output contracts are validated, **Then** stable minimum guarantees are enforced and backend-specific fields are allowed to vary.

---

### Edge Cases

- Empty or whitespace-only source MUST fail fast with `UnsupportedInputError`.
- URL-like values with unsupported schemes (for example `ftp://`) are treated as non-HTTP/HTTPS inputs and follow non-URL routing rules.
- Local files with unknown or missing extensions default to MarkItDown routing for compatibility and long-tail format support.
- URL inputs that look like specialized formats (for example `.pdf`) still route to MarkItDown by URL precedence.
- MarkItDown outputs that do not expose structured metadata still return valid normalized output with `metadata` omitted.

## Requirements *(mandatory)*

### Functional Requirements

#### Routing Contract

- **FR-001**: The system MUST implement a deterministic routing matrix with the following mappings: local PDF -> `pdf_extractor`; local images -> `image_processor`; local audio -> `audio_processor`; local Office/HTML/EPUB/ZIP -> MarkItDown; all HTTP/HTTPS URLs (including YouTube hosts) -> MarkItDown.
- **FR-002**: The system MUST apply routing precedence in this order: input validation first, URL classification second, local extension classification third, fallback-to-MarkItDown last.
- **FR-003**: The system MUST treat URL origin as higher precedence than file suffix backend specialization; URL inputs do not route to local specialized backends.
- **FR-004**: The system MUST classify empty or whitespace-only input as unsupported and raise `UnsupportedInputError` with an error message containing the exact phrase `source cannot be empty`.

#### API and CLI Contract

- **FR-005**: The Python API entry point MUST accept a `source` string and optional metadata inclusion preference, and MUST return a normalized conversion result containing `source`, `route`, and `content`.
- **FR-006**: The normalized result MAY include `metadata` and backend-native `raw_result`. For specialized routed backends (PDF, image, audio), metadata preference/flag behavior MUST be preserved. For MarkItDown-routed inputs, metadata is best-effort: absence of `metadata` MUST NOT fail conversion, and presence of `metadata` is valid regardless of metadata preference when provided by the backend.
- **FR-007**: Existing consumers of routed backends MUST remain backward-compatible in behavior and exception hierarchy for already-supported PDF, image, and audio routes.
- **FR-008**: The system MUST provide a minimal `document_converter` CLI entry point with parity for source input, metadata flag behavior, stdout/stderr separation, and non-zero failure exit codes. The minimal CLI MUST accept a source positional argument and an optional `--include-metadata` flag, print conversion result payloads to stdout, diagnostics to stderr, and return non-zero on failure.
- **FR-009**: Formatter behavior convergence across modules is deferred in this phase per `FR-020`; no shared formatter layer is introduced under this scope.

#### Error Contract

- **FR-010**: `MissingDependencyError` MUST represent absent optional runtime dependencies for a selected route and MUST include install guidance text containing `install` and the missing dependency package name.
- **FR-011**: For MarkItDown-routed conversions, missing MarkItDown dependency guidance MUST include the exact token `markitdown[all]`.
- **FR-012**: `UnsupportedInputError` MUST represent routing-time invalid input (currently empty source), not runtime backend processing failures.
- **FR-013**: `DocumentConversionError` MUST wrap unexpected backend/runtime failures with route and source context.
- **FR-014**: Errors already typed as `DocumentConversionError` (including subclasses) MUST NOT be rewrapped.
- **FR-015**: Optional dependencies MUST be lazily imported on route demand so importing the converter module does not require all heavy runtime backends.

#### Output Compatibility Contract

- **FR-016**: The stable minimum output contract across all routes MUST guarantee `source` (original input), `route` (selected backend), and `content` (string output).
- **FR-017**: The following fields are allowed to vary by backend and are best-effort: metadata field names/coverage depth, ordering/shape of backend-native `raw_result`, and content style nuances produced by module-local formatters.
- **FR-018**: The system MUST preserve backend-specific enrichment; formatter harmonization remains deferred as defined by `FR-020`.
- **FR-019**: Guardrails MUST be defined to prevent contract drift while formatters remain module-local: stable required fields, explicit allowed-variance fields, and contract tests that fail on required-field regressions.

#### Decision Record and Scope Control

- **FR-020**: This specification MUST include an explicit ADR-style decision that formatter unification is deferred and not in implementation scope for this phase.
- **FR-021**: The decision record MUST include rationale, consequences, risks, review triggers, and revisit timeline criteria.
- **FR-022**: Rollout notes MUST state that this phase formalizes existing bridge behavior rather than introducing formatter refactor obligations.

#### Test Requirements

- **FR-023**: Unit tests MUST cover routing matrix, precedence rules, unsupported input handling, delegation behavior, and exception wrapping boundaries.
- **FR-024**: Integration tests MUST verify end-to-end conversion behavior for representative routed backends using deterministic fixtures and dependency-safe mocking where heavy optional runtimes are unavailable.
- **FR-025**: Contract tests MUST enforce stable normalized output fields and explicitly permit backend-specific best-effort fields.
- **FR-026**: Test plans MUST map required coverage to concrete files/cases and identify current gaps before implementation work.

### Assumptions

- The existing `document_converter` bridge behavior in code is the baseline contract to formalize.
- URL handling scope is limited to HTTP/HTTPS inputs for URL-specific routing behavior.
- Existing backend modules keep their current formatter implementations during this phase.
- No new secrets, credentials, or provider configuration changes are required for this spec package.

### Non-Goals

- Building a shared formatter module or refactoring module-local formatter code.
- Enforcing identical textual formatting across PDF/image/audio/MarkItDown outputs.
- Expanding specialized backend routing beyond current PDF/image/audio mappings.
- Adding new external provider integrations beyond current bridge dependencies.

### Acceptance Criteria

- The routing contract is fully specified with precedence, ambiguity rules, and unsupported input behavior.
- API/output/error contracts are explicit, testable, and backward-compatible for existing routed backends.
- Formatter unification deferral is documented as an ADR-style decision with guardrails and revisit triggers.
- Required tests are mapped to concrete files/cases with current coverage gaps identified.

### Test Requirements and Gap Mapping

- **Existing coverage (`tests/unit/test_document_converter.py`)**: routing matrix for key extensions and URLs, empty-source rejection, and backend delegation.
- **Required additions in `tests/unit/test_document_converter.py`**: URL precedence over suffix-specialized routing, unknown-extension fallback behavior, whitespace-only input case, `DocumentConversionError` wrapping behavior, and no-rewrap behavior for typed conversion errors.
- **Required new unit file (`tests/unit/test_document_converter_errors.py`)**: `MissingDependencyError` guidance text assertion, lazy import behavior expectations, and MarkItDown metadata/content extraction edge cases.
- **Required integration file (`tests/integration/test_document_converter_routing.py`)**: deterministic end-to-end route-to-backend contract with lightweight doubles for optional heavy backends.
- **Required contract file (`tests/contract/test_document_converter_contracts.py`)**: stable-field assertions (`source`, `route`, `content`), allowed-variance checks for metadata/raw backend output, and backward-compatibility assertions for existing consumers.
- **Required CLI contract file (`tests/contract/test_document_converter_cli_contracts.py`)**: stdout/stderr separation, metadata flag parity checks, and non-zero exit code behavior for failure scenarios.
- **Isolation requirement**: Tests MUST avoid mandatory heavy optional runtime dependencies by using monkeypatch/stubs unless the test explicitly targets dependency-availability behavior.

### Decision Record (ADR): Formatter Unification Is Deferred

**Status**: Accepted for this phase

**Decision**: Formatter unification across backends is deferred and explicitly out of scope for implementation under this spec.

**Context**:

- The bridge routing and error/output contracts now exist and need formalization based on current behavior.
- Specialized backends already expose module-local formatter behavior that existing consumers depend on.
- Forcing formatter convergence now increases risk and broadens scope beyond contract stabilization.

**Rationale**:

- Prioritize contract stability and backward compatibility for the bridge.
- Reduce delivery risk by separating routing/error/output contract hardening from formatter architecture changes.
- Preserve module-first boundaries and avoid coupling unrelated refactor work into this phase.

**Consequences**:

- Backend output style differences remain acceptable within defined best-effort fields.
- Cross-backend output parity is not guaranteed beyond stable minimum normalized fields.
- Additional guardrail contract tests become mandatory to prevent accidental drift.

**Risks**:

- Consumers may infer stronger formatting consistency than guaranteed.
- Backend-local formatter updates could unintentionally change expected output details.
- Deferred unification could increase future migration complexity if guardrails are weak.

**Guardrails While Deferred**:

- Maintain stable required normalized fields for every conversion route.
- Treat backend-specific formatting and metadata richness as allowed variance unless explicitly promoted to stable contract.
- Require contract tests for stable fields and explicit negative tests for unsupported assumptions.
- Require spec updates before promoting any best-effort field to stable guarantee.

**Review Triggers and Revisit Timeline**:

- Revisit after bridge contract tests remain stable for two consecutive release cycles.
- Revisit sooner if support burden increases due to output inconsistency reports.
- Revisit if a new cross-backend consumer requires strict output harmonization.
- At revisit, evaluate incremental formatter interface extraction under a separate spec/package.

### Key Entities *(include if feature involves data)*

- **Source Input**: A user-provided local path or HTTP/HTTPS URL used for route classification and conversion.
- **Conversion Route**: The selected backend identifier (`pdf_extractor`, `image_processor`, `audio_processor`, `markitdown`) used to execute conversion.
- **Conversion Result Contract**: Normalized response containing stable required fields (`source`, `route`, `content`) and optional best-effort fields (`metadata`, backend-native raw output).
- **Conversion Errors**: Typed failure outcomes (`UnsupportedInputError`, `MissingDependencyError`, `DocumentConversionError`) with explicit semantics and handling boundaries.
- **Deferral Decision Record**: Formal policy artifact defining why formatter unification is delayed, with guardrails and revisit criteria.

### Rollout Notes

- This phase is a retroactive contract formalization of current behavior, not a formatter refactor initiative.
- Existing routed backend behavior remains unchanged; new obligations are primarily contract clarity and test coverage.
- Any future formatter harmonization requires a separate scoped spec and plan.

## Constitution Alignment *(mandatory)*

- **Module Impact**: Scoped to `anyfile_to_ai/document_converter/` contracts and related tests; no new cross-module formatter package is introduced.
- **Contract Impact**: Formalizes deterministic routing, API result guarantees, error semantics, and compatibility boundaries while preserving existing routed backend behavior.
- **Test Plan**: Add failing-first updates to `tests/unit/test_document_converter.py`, plus new integration/contract coverage for routing, errors, output stability, and drift guardrails.
- **Configuration & Security**: No new secrets or credentials; optional dependency behavior is explicit, lazy-loaded, and documented through error guidance.
- **Documentation Impact**: Update spec package artifacts for routing/error/output contracts and explicit formatter-deferral decision; no user-facing formatter refactor docs required in this phase.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of defined routing matrix cases (PDF/image/audio/local MarkItDown formats/URL inputs) are covered by deterministic tests with no ambiguous outcomes.
- **SC-002**: 100% of conversion failures in covered scenarios resolve to documented typed error semantics (unsupported input, missing dependency, or wrapped conversion failure).
- **SC-003**: 100% of covered route outputs satisfy stable required normalized fields (`source`, `route`, `content`) in contract tests.
- **SC-004**: No formatter-refactor tasks are required to declare this phase complete; implementation scope remains limited to contract definition and drift-prevention tests.
- **SC-005**: Local routed inputs (non-URL sources) complete route determination and conversion dispatch without invoking URL/network-dependent handlers.
