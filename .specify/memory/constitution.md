<!--
Sync Impact Report:
- Version change: template → 1.0.0 (initial constitution)
- New principles added: Composition-First, 250-Line Rule, Minimal Dependencies, Experimental Mindset, Modular Architecture
- New sections added: Quality Gates, Development Workflow
- Templates requiring updates: ✅ updated
- Follow-up TODOs: None
-->

# MakeMeAPodcastFromDocs Constitution

## Core Principles

### I. Composition-First

Every feature MUST be built from simple, composable components. Components MUST be
independently functional and testable. Complexity emerges through composition, not
through individual component complexity. No monolithic structures allowed.

### II. 250-Line Rule (NON-NEGOTIABLE)

No single file SHALL exceed 250 lines of code. This includes comments and whitespace.
Files approaching this limit MUST be refactored into smaller, focused modules.
This constraint forces clarity and proper separation of concerns.

### III. Minimal Dependencies

Dependencies MUST be justified and minimal. Prefer standard library solutions over
external packages. When external dependencies are required, they MUST serve a clear,
non-replaceable purpose. Regular dependency audits required.

### IV. Experimental Mindset

This is an experimental project prioritizing learning over production concerns.
Quick iterations and proof-of-concepts are valued. Breaking changes are acceptable
if they improve the architectural foundation. Document experiments and learnings.

### V. Modular Architecture

Each module MUST have a single, well-defined responsibility. Inter-module
communication MUST use clear, documented interfaces. Modules MUST be replaceable
without affecting other system components.

## Quality Gates

File size validation MUST be automated and enforced in CI/CD. Code reviews MUST
verify compliance with the 250-line rule and composition principles. Integration
tests MUST validate module interactions and interface contracts.

## Development Workflow

All changes MUST start with the smallest possible working solution. Refactoring
for composition happens iteratively. Each commit MUST maintain system functionality
while improving modular structure. Experimental branches encouraged for exploration.

## Governance

This constitution supersedes all other development practices. Changes require
documented justification and impact analysis. The 250-line rule and composition-first
principle are non-negotiable. Compliance reviews are mandatory for all contributions.

**Version**: 1.0.0 | **Ratified**: 2025-09-28 | **Last Amended**: 2025-09-28
