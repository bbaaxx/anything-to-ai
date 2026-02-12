<!--
Sync Impact Report
- Version change: 0.0.0-template -> 1.0.0
- Modified principles:
  - PRINCIPLE_1_NAME -> I. Module-First Design
  - PRINCIPLE_2_NAME -> II. Stable CLI and Python Contracts
  - PRINCIPLE_3_NAME -> III. Test-First Quality Gates (NON-NEGOTIABLE)
  - PRINCIPLE_4_NAME -> IV. Secure and Configurable Model Integrations
  - PRINCIPLE_5_NAME -> V. Documentation and Observability Discipline
- Added sections:
  - Engineering Constraints
  - Development Workflow & Quality Gates
- Removed sections:
  - None
- Templates requiring updates:
  - ✅ updated `.specify/templates/plan-template.md`
  - ✅ updated `.specify/templates/spec-template.md`
  - ✅ updated `.specify/templates/tasks-template.md`
  - ⚠ pending `.specify/templates/commands/*.md` (directory not present in repository)
- Deferred follow-ups:
  - TODO(RATIFICATION_DATE): Original ratification date was not found in repository docs/history snapshot.
-->

# anyfile_to_ai Constitution

## Core Principles

### I. Module-First Design
All new end-user capabilities MUST be implemented in a focused module under
`anyfile_to_ai/` with a clear scope, explicit interfaces, and isolated tests.
Each module MUST preserve parity between Python API usage and CLI usage when
that capability is user-facing. Rationale: this repository is intentionally
modular, and consistent boundaries keep features composable and maintainable.

### II. Stable CLI and Python Contracts
Public behavior changes MUST be reflected in both CLI and Python interfaces, and
contract changes MUST be explicit in specs, tests, and release notes. CLI tools
MUST send machine-readable results to stdout and diagnostics to stderr with
non-zero exit codes on failure. Rationale: predictable contracts are required for
automation, pipelines, and downstream integrations.

### III. Test-First Quality Gates (NON-NEGOTIABLE)
Implementation work MUST be accompanied by tests that fail before code changes
and pass afterward. Every change MUST include right-sized coverage in `tests/`
(unit, integration, and contract when applicable), and the full quality gate
MUST pass via `uv run pytest` with the enforced coverage threshold. Rationale:
this project processes varied file formats and model backends, so regressions
must be detected early and reproducibly.

### IV. Secure and Configurable Model Integrations
Credentials and provider secrets MUST NOT be committed. Model/provider behavior
MUST be configured through environment variables or explicit CLI flags with
documented defaults and precedence. Tests MUST avoid hard dependence on external
network services unless explicitly marked and justified. Rationale: secure,
portable configuration is necessary for local, CI, and production-like runs.

### V. Documentation and Observability Discipline
User-visible behavior changes MUST update relevant README/CLI help and usage
examples in the same change. Long-running or batch workflows MUST provide clear
progress visibility and actionable error output. Rationale: this toolset is used
interactively and in pipelines, so operability depends on current docs and
debuggable runtime feedback.

## Engineering Constraints

- Runtime target MUST remain Python 3.11+ and follow configured Ruff/formatting
  rules.
- Code changes MUST preserve modular package boundaries in `anyfile_to_ai/` and
  test suite structure in `tests/unit`, `tests/integration`, and
  `tests/contract`.
- New processor capabilities MUST document required environment variables and
  fallback behavior in module README files.
- Network-dependent or model-heavy tests SHOULD be marked appropriately
  (`slow`, `integration`, `contract`, `flaky`) with rationale in test code.

## Development Workflow & Quality Gates

Changes MUST follow this sequence:

1. Define behavior in spec artifacts, including contract impact and test intent.
2. Add or update failing tests first.
3. Implement minimally to satisfy tests.
4. Run and pass quality checks: `uv run ruff check .`, `uv run ruff format .`,
   and `uv run pytest`.
5. Update user-facing documentation for any changed behavior or configuration.

Pull requests MUST include evidence of relevant checks and identify any
intentional constitution exceptions in a dedicated justification section.

## Governance

- This constitution is the authoritative engineering policy for this repository;
  when guidance conflicts, this document takes precedence.
- Amendments MUST include: (a) proposed text diff, (b) migration impact on
  templates/docs, and (c) version bump rationale following semantic versioning.
- Versioning policy for this constitution is mandatory:
  - MAJOR for backward-incompatible governance changes or principle removal/
    redefinition.
  - MINOR for new principles/sections or materially expanded obligations.
  - PATCH for clarifications, wording improvements, and non-semantic edits.
- Compliance review is required in planning artifacts and pull requests; each
  change MUST either satisfy all principles or document explicit, approved
  exceptions.

**Version**: 1.0.0 | **Ratified**: TODO(RATIFICATION_DATE): Original adoption date not found. | **Last Amended**: 2026-02-12
