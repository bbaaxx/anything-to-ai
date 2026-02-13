# Deferred Actions Tracker

Date: 2026-02-12
Scope reference: `specs/016-markitdown-bridge/spec.md`

Purpose: Track work explicitly deferred from the MarkItDown bridge contract formalization but identified as required or recommended before broader rollout continues.

## How To Use

- `Required` means the item should be completed before declaring the bridge fully production-ready.
- `Recommended` means strong guidance to reduce risk, but not a hard blocker for `/speckit.plan`.
- Update `Status` and `Notes` as work progresses.

## Deferred Actions

| ID | Action | Priority | Why Deferred | Trigger / When to Revisit | Status | Notes |
|----|--------|----------|--------------|----------------------------|--------|-------|
| DA-001 | Build shared cross-backend formatter strategy | Required (next phase) | Explicitly out of scope for spec 016 to avoid scope creep and preserve backward compatibility | Revisit after two consecutive release cycles with stable bridge contract tests, or earlier if inconsistency support load rises | Deferred | ADR in `specs/016-markitdown-bridge/spec.md` defers unification intentionally |
| DA-002 | Add contract tests to guard output drift | Required | Spec formalized stable vs best-effort fields, but tests are not yet fully implemented | Before completing implementation tied to spec 016 | Completed | Implemented in `tests/contract/test_document_converter_contracts.py` and `tests/contract/test_document_converter_cli_contracts.py` |
| DA-003 | Add integration routing coverage for bridge | Required | Integration suite does not yet enforce deterministic route-to-backend behavior end to end | Before merge of bridge contract implementation work | Completed | Implemented in `tests/integration/test_document_converter_routing.py` |
| DA-004 | Expand unit tests for error boundaries and precedence | Required | Gaps remain for URL precedence, unknown extension fallback, wrapping/no-rewrap semantics | During implementation tasks for spec 016 | Completed | Implemented in `tests/unit/test_document_converter.py` and `tests/unit/test_document_converter_errors.py` |
| DA-005 | Define stricter non-functional targets (latency/reliability/observability) for converter operations | Recommended | Current spec focuses on functional contract stability first; NFRs intentionally light | During planning or prior to production-hardening milestone | Deferred | Can be added in plan/tasks without changing core routing contract |
| DA-006 | Evaluate and decide on future `document_converter` CLI entry point | Recommended | Clarification locked this phase to API-first only | Revisit only if product workflow requires direct converter CLI usage | Completed | Minimal CLI parity now implemented with stdout/stderr/exit-code contract tests |

## Immediate Next Step Before Continuing

1. Keep DA-001 as the only required deferred item for the next formatter-focused phase.
2. Revisit DA-005 when production-hardening non-functional requirements are prioritized.
