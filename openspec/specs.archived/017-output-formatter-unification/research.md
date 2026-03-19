# Phase 0 Research: Shared Output Formatter Unification

Date: 2026-02-13
Feature: `specs/017-output-formatter-unification/spec.md`

## Shared Formatter Architecture

### Decision

Create a shared `anyfile_to_ai/output_formatter/` package with profile-based rendering and a compatibility shim layer in each existing module formatter entry point.

### Rationale

- Keeps module boundaries intact while eliminating formatter duplication.
- Enables incremental migration without import/path breakage.
- Preserves stable CLI and Python contracts during transition.

### Alternatives considered

- Keep module-local formatters indefinitely (rejected: long-term drift risk).
- Big-bang replacement (rejected: high regression risk).
- Central formatter coupled directly to module internals (rejected: boundary violations).

## Deterministic JSON and Metadata Normalization

### Decision

Use deterministic JSON serialization and schema-guided metadata normalization with unknown key preservation in extension space.

### Rationale

- Deterministic output prevents fixture/contract flakiness.
- Unknown key pass-through preserves forward compatibility.
- Normalized known fields reduce cross-module contract drift.

### Alternatives considered

- Strict unknown-key rejection (rejected: harms compatibility).
- Ad hoc per-module normalization (rejected: inconsistent behavior).
- Always-on metadata output regardless of caller/include rules (rejected: contract mismatch).

## Phased Migration and Rollback

### Decision

Apply a three-phase adapter migration:

- Phase A: add shared interfaces/adapters with no behavior changes.
- Phase B: migrate modules in risk-ordered sequence with per-module parity gates.
- Phase C: retire duplicate internals after deprecation window and stable parity history.

### Rationale

- Minimizes blast radius and isolates regressions.
- Supports module-local rollback without blocking unrelated modules.
- Aligns with test-first constitution gates.

### Alternatives considered

- Full dual-render everywhere (rejected: excessive complexity).
- Commit-revert-only rollback (rejected: slower operational recovery).

## Technical Context Clarifications

### Decision

No unresolved `NEEDS CLARIFICATION` items remain for this plan.

### Rationale

- Runtime, test stack, module boundaries, and contract constraints are explicit in spec and repository constitution.

### Alternatives considered

- Deferring decisions to implementation (rejected: increased rework risk).
