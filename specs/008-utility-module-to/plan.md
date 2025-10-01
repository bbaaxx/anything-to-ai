# Implementation Plan: LLM Utility Module

**Branch**: `008-utility-module-to` | **Date**: 2025-09-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-utility-module-to/spec.md`

## Execution Flow (/plan command scope)

```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:

- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

Create a unified LLM utility module that provides consistent access to multiple LLM service providers (MLX-optimized models, LM Studio, Ollama) via OpenAI-compatible APIs. The module will support configuration of base URLs and API keys, model listing with caching, configurable error handling with retry and fallback mechanisms, and both programmatic and CLI-based model selection. This utility will be usable by all existing processing modules (PDF extractor, image processor, audio processor) while maintaining compatibility with existing MLX functionality.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: Standard library (urllib, json), OpenAI-compatible client libraries (to be researched - potentially openai SDK or httpx for direct API calls)
**Storage**: In-memory caching for model listings, no persistent storage
**Testing**: pytest with contract, integration, and unit tests; 70% coverage requirement
**Target Platform**: macOS (Apple Silicon with MLX support), Linux compatibility for Ollama/LM Studio services
**Project Type**: single (existing modular architecture with pdf_extractor, image_processor, audio_processor)
**Performance Goals**: Model listing < 5s first call, < 100ms cached; LLM requests depend on service; cache invalidation configurable
**Constraints**: 250-line file limit per constitution; minimal dependencies; must not break existing MLX integration in image_processor
**Scale/Scope**: 3 consumer modules initially (pdf_extractor, image_processor, audio_processor); 3 service providers (MLX, LM Studio, Ollama); single-user local execution

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

**Composition-First Check**:

- [x] All components are independently functional and testable (config, client, cache, error handler modules)
- [x] No monolithic structures proposed (small focused modules)
- [x] Complexity emerges through composition, not component complexity (simple modules composed via facade)

**250-Line Rule Check**:

- [x] No single file planned exceeds 250 lines (including comments/whitespace)
- [x] Large modules identified for modular breakdown (client split into base + provider-specific adapters)
- [x] Clear refactoring strategy for size violations (split by responsibility: config, client, cache, errors, adapters)

**Minimal Dependencies Check**:

- [x] All dependencies justified with clear rationale (OpenAI SDK or httpx for API calls - to be researched in Phase 0)
- [x] Standard library solutions preferred over external packages (urllib, json for basic operations; only add client lib if significantly beneficial)
- [x] Dependency audit plan included (Phase 0 research will compare alternatives)

**Experimental Mindset Check**:

- [x] Learning objectives documented (explore OpenAI-compatible API patterns, caching strategies, retry/fallback mechanisms)
- [x] Quick iteration approach planned (start with single provider, expand to multi-provider)
- [x] Breaking changes acceptable for architectural improvements (experimental project per constitution)

**Modular Architecture Check**:

- [x] Single responsibility per module (config=configuration; client=API communication; cache=model list caching; adapters=provider-specific logic)
- [x] Clear interface definitions between modules (contracts defined in Phase 1)
- [x] Modules designed for replaceability (provider adapters can be swapped; cache strategies can be replaced)

## Project Structure

### Documentation (this feature)

```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)

```
llm_client/                    # New module for LLM utility
├── __init__.py               # Public API facade
├── models.py                 # Data models (Config, Request, Response, ModelInfo)
├── config.py                 # Configuration handling
├── client.py                 # Base LLM client interface
├── cache.py                  # Model listing cache
├── retry.py                  # Retry/fallback logic
├── exceptions.py             # LLM-specific exceptions
└── adapters/                 # Provider-specific implementations
    ├── __init__.py
    ├── base.py              # Base adapter interface
    ├── mlx_adapter.py       # MLX provider adapter
    ├── ollama_adapter.py    # Ollama provider adapter
    └── lmstudio_adapter.py  # LM Studio provider adapter

tests/
├── contract/
│   ├── test_llm_client_api.py        # Public API contracts
│   ├── test_adapter_interface.py     # Adapter interface contracts
│   └── test_config_interface.py      # Configuration contracts
├── integration/
│   ├── test_ollama_integration.py    # Ollama service integration
│   ├── test_lmstudio_integration.py  # LM Studio integration
│   ├── test_caching_behavior.py      # Cache behavior
│   └── test_retry_fallback.py        # Retry/fallback scenarios
└── unit/
    ├── test_config.py               # Configuration logic
    ├── test_cache.py                # Cache implementation
    ├── test_retry.py                # Retry logic
    └── test_models.py               # Data models
```

**Structure Decision**: Single project structure following existing pattern. New `llm_client` module sits alongside `pdf_extractor`, `image_processor`, and `audio_processor`. The module uses adapter pattern for provider-specific implementations, keeping each file under 250 lines per constitution. Tests follow existing three-tier structure (contract/integration/unit).

## Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:

   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts

_Prerequisites: research.md complete_

1. **Extract entities from feature spec** → `data-model.md`:

   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:

   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:

   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:

   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/\*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach

_This section describes what the /tasks command will do - DO NOT execute during /plan_

**Task Generation Strategy**:

The `/tasks` command will:

1. Load `.specify/templates/tasks-template.md` as base structure
2. Generate tasks from Phase 1 artifacts in this order:
   - Contract test tasks (from `contracts/` directory) - **[P]** parallel
   - Data model implementation tasks (from `data-model.md`) - **[P]** parallel
   - Core module implementation tasks (client, config, cache, retry) - Sequential dependencies
   - Adapter implementation tasks (ollama, lmstudio, mlx) - **[P]** parallel
   - Integration test tasks (from quickstart scenarios) - Sequential validation
   - Documentation tasks (docstrings, examples) - Final polish

**Specific Task Breakdown**:

**Phase 2A: Contract Tests (TDD - Write First)** [P]
1. Create `tests/contract/test_llm_client_api.py` with all API contracts
2. Create `tests/contract/test_adapter_interface.py` with adapter contracts
3. Create `tests/contract/test_config_interface.py` with config contracts
4. Run tests → All should FAIL (no implementation yet)

**Phase 2B: Data Models** [P]
5. Implement `llm_client/models.py` (Message, Usage, LLMRequest, LLMResponse, ModelInfo)
6. Implement `llm_client/exceptions.py` (error hierarchy)
7. Run model validation tests → Should PASS

**Phase 2C: Configuration**
8. Implement `llm_client/config.py` (LLMConfig with validation)
9. Run config contract tests → Should PASS

**Phase 2D: Core Infrastructure**
10. Implement `llm_client/cache.py` (in-memory cache with TTL)
11. Implement `llm_client/retry.py` (exponential backoff + fallback)
12. Add unit tests for cache and retry
13. Run unit tests → Should PASS

**Phase 2E: Adapter Base**
14. Implement `llm_client/adapters/base.py` (abstract adapter interface)
15. Implement `llm_client/adapters/__init__.py` (adapter factory/registry)

**Phase 2F: Provider Adapters** [P]
16. Implement `llm_client/adapters/ollama_adapter.py` (Ollama OpenAI-compatible)
17. Implement `llm_client/adapters/lmstudio_adapter.py` (LM Studio OpenAI-compatible)
18. Implement `llm_client/adapters/mlx_adapter.py` (MLX wrapper)
19. Run adapter contract tests → Should PASS for implemented adapters

**Phase 2G: Main Client**
20. Implement `llm_client/client.py` (LLMClient with retry/fallback/cache orchestration)
21. Implement `llm_client/__init__.py` (public API facade)
22. Run client API contract tests → Should PASS

**Phase 2H: Integration Tests**
23. Create `tests/integration/test_ollama_integration.py` (real Ollama service)
24. Create `tests/integration/test_lmstudio_integration.py` (real LM Studio)
25. Create `tests/integration/test_caching_behavior.py` (cache validation)
26. Create `tests/integration/test_retry_fallback.py` (retry/fallback scenarios)
27. Run integration tests → Should PASS (requires running services)

**Phase 2I: CLI (Optional - Future)**
28. Create `llm_client/__main__.py` (CLI entry point)
29. Add argparse for list-models and generate commands

**Phase 2J: Documentation & Polish**
30. Add comprehensive docstrings to all public APIs
31. Update quickstart.md with actual working examples
32. Run full test suite with coverage check (>70%)
33. Run ruff linting and formatting
34. Verify all files < 250 lines

**Ordering Strategy**:

- **TDD order**: Contract tests before implementation (Phase 2A before 2B-2G)
- **Dependency order**: Models → Config → Infrastructure → Adapters → Client
- **Parallel execution**: Mark [P] for independent files (models, adapters, contract tests)
- **Validation order**: Unit tests → Integration tests → Full system tests

**Estimated Task Count**: 34 tasks

**Estimated Completion Time**: 3-4 hours (assuming running LLM services available)

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation

_These phases are beyond the scope of the /plan command_

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking

_Fill ONLY if Constitution Check has violations that must be justified_

| Violation                  | Why Needed         | Simpler Alternative Rejected Because |
| -------------------------- | ------------------ | ------------------------------------ |
| [e.g., 4th project]        | [current need]     | [why 3 projects insufficient]        |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient]  |

## Progress Tracking

_This checklist is updated during execution flow_

**Phase Status**:

- [x] Phase 0: Research complete (/plan command) ✅ 2025-09-30
- [x] Phase 1: Design complete (/plan command) ✅ 2025-09-30
- [x] Phase 2: Task planning complete (/plan command - describe approach only) ✅ 2025-09-30
- [x] Phase 3: Tasks generated (/tasks command) ✅ 2025-09-30 - **40 tasks ready**
- [ ] Phase 4: Implementation complete - **Start with T001**
- [ ] Phase 5: Validation passed

**Gate Status**:

- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved ✅
- [x] Complexity deviations documented: N/A (no deviations)

**Artifacts Generated**:

- ✅ `research.md` - Technical decisions and dependency choices
- ✅ `data-model.md` - Complete data model with 10 entities, all files <250 lines
- ✅ `contracts/client_api.py` - 30 client API contract tests
- ✅ `contracts/adapter_interface.py` - 25 adapter contract tests
- ✅ `contracts/config_interface.py` - 35 configuration contract tests
- ✅ `quickstart.md` - 10 usage examples + integration guide
- ✅ `CLAUDE.md` - Updated with llm_client context
- ✅ `tasks.md` - 40 implementation tasks with TDD ordering and parallel execution guidance

**Next Steps**: Begin implementation with T001 (Setup) from `tasks.md`

---

_Based on Constitution v1.0.0 - See `/memory/constitution.md`_
