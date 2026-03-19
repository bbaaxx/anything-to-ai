# Phase 0 Research: MarkItDown Bridge Contracts

Date: 2026-02-12
Feature: `specs/016-markitdown-bridge/spec.md`

## Routing Precedence and Ambiguity

### Decision

Adopt and preserve a deterministic ordered classifier: validate input -> classify HTTP/HTTPS URLs -> classify local extension for specialized backends -> fallback to MarkItDown for remaining local/unknown extensions.

### Rationale

- Keeps behavior reproducible across local and CI environments.
- Preserves current compatibility expectations for existing consumers.
- Avoids ambiguous adaptive behavior tied to transient state (filesystem, DNS, or network reachability).

### Alternatives Considered

- **Existence/reachability-based routing**: rejected as non-deterministic and environment-sensitive.
- **Heuristic URL-first for host-like strings**: rejected due to accidental network routing risk and compatibility drift.

## Error Taxonomy and Wrapping Boundaries

### Decision

Keep a typed bridge hierarchy (`UnsupportedInputError`, `MissingDependencyError`, `DocumentConversionError`) and wrap only unexpected exceptions at the adapter boundary while preserving causal chains.

### Rationale

- Typed errors support deterministic caller handling and stable test expectations.
- Wrapping unknown backend failures prevents third-party exception leakage while retaining debug context.
- Dedicated missing-dependency typing enables actionable remediation messaging.

### Alternatives Considered

- **Propagate backend-native exceptions directly**: rejected for portability and contract stability reasons.
- **Single generic bridge error for all failures**: rejected because callers lose remediation-specific behavior.

## Optional Dependency and Test Isolation Strategy

### Decision

Use a three-layer test strategy: unit tests without heavy optional deps, focused integration tests for route wiring with lightweight doubles, and contract tests for stable output/error guarantees.

### Rationale

- Maintains fast, deterministic baseline tests.
- Isolates dependency-sensitive behavior without sacrificing contract coverage.
- Aligns with constitution-required unit/integration/contract quality gates.

### Alternatives Considered

- **Only end-to-end tests with real optional dependencies**: rejected as slow/flaky and CI-fragile.
- **Extensive deep mocking of third-party internals**: rejected as brittle and implementation-coupled.

## Metadata Behavior for MarkItDown Route

### Decision

Maintain specialized-backend metadata toggle behavior as stable contract; treat MarkItDown metadata as best-effort and potentially present when available.

### Rationale

- Matches current implementation behavior and avoids unnecessary refactor scope.
- Preserves compatibility while still defining clear stable vs variable fields.

### Alternatives Considered

- **Force strict metadata toggle on MarkItDown route**: rejected for current-phase scope and behavior-change risk.

## Scope Guardrail: Deferred Formatter Unification

### Decision

Keep formatter unification deferred to a future phase and enforce drift guardrails via contract tests and explicit stable-field guarantees.

### Rationale

- Protects delivery focus on bridge contract stabilization.
- Prevents coupling broad formatter refactors to routing/error contract work.

### Alternatives Considered

- **Start cross-module formatter refactor in this phase**: rejected due to high scope expansion and compatibility risk.
