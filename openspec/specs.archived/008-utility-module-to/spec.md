# Feature Specification: LLM Utility Module

**Feature Branch**: `008-utility-module-to`
**Created**: 2025-09-30
**Status**: Draft
**Input**: User description: "Utility Module To access LLMS : We need a helper service or library that can be used by all three modules to access an LLM. Currently we support using an LLM on the image analyzer which is optimized for MLX This is perfectly fine but we need access to local LLM services provided initially by LM Studio and Ollama. Both offer an openAI compatible API service so we want a general-use library that allows any of the consumer modules to use an openai-compatible service configurable ( we should be able to configure base api url and api key, and we should implement a way to list the available models to allow for consumer selection of models or to pass this decision to userland. Research langchain or langgraph as integration options as these libraries may already expose some interfaces to allow this"

## Clarifications

### Session 2025-09-30
- Q: Which OpenAI API endpoints must the utility module support? → A: Only `/v1/chat/completions` (modern chat-based interface)
- Q: How should model selection work for consumer modules? → A: Programmatic and CLI flags
- Q: Should model listing be synchronous or asynchronous, and should results be cached? → A: Synchronous with caching (faster repeated queries)
- Q: What should the error handling behavior be when service connection errors occur? → A: Fixed retry logic and fallback to different service, both configurable
- Q: What validation rules should apply before attempting service connections? → A: URL format + API key (optional) + reachability check

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

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As a developer using the podcast generation system, I need to access different LLM services (MLX-optimized models, LM Studio, Ollama) from any processing module (PDF extractor, image processor, audio processor) so that I can leverage appropriate language models for content analysis and generation tasks without writing custom integration code for each module.

### Acceptance Scenarios
1. **Given** a PDF extractor module needs text enhancement, **When** the module requests LLM access with a specified service configuration, **Then** the system provides a working connection to the configured LLM service
2. **Given** multiple LLM services are available (MLX, LM Studio, Ollama), **When** a user queries available models, **Then** the system returns a list of models from the configured service
3. **Given** a configured LLM service requires authentication, **When** making a request, **Then** the system uses the provided API key for authentication
4. **Given** an image processor currently using MLX models, **When** switching to use the utility module, **Then** the existing MLX functionality continues to work without degradation
5. **Given** a user configures a custom base URL for their local Ollama instance, **When** the system connects, **Then** requests are sent to the custom URL rather than default endpoints

### Edge Cases
- What happens when the configured LLM service is unreachable or offline? System will retry with configurable attempts/backoff, then optionally fallback to alternative service if configured.
- How does the system handle API authentication failures or expired keys?
- What happens when a requested model is not available on the configured service?
- How does the system behave when switching between different service providers (MLX vs Ollama vs LM Studio)?
- What happens if configuration is missing or incomplete (no base URL)? System validates URL format and reachability before connection; invalid configuration fails validation early.
- What happens if API key validation fails during configuration check? System reports validation error if key is malformed, but allows missing keys for services that don't require authentication.
- How are rate limits or service quotas handled?
- What happens if all configured fallback services are also unreachable?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST provide a unified interface for accessing multiple LLM service providers (MLX-optimized, LM Studio, Ollama)
- **FR-002**: System MUST allow configuration of service-specific parameters including base API URL and API key
- **FR-003**: System MUST support querying available models from the configured LLM service
- **FR-004**: System MUST be usable by all existing processing modules (PDF extractor, image processor, audio processor)
- **FR-005**: System MUST maintain compatibility with existing MLX-optimized model usage in the image processor
- **FR-006**: System MUST support the `/v1/chat/completions` endpoint for OpenAI-compatible API interactions
- **FR-007**: System MUST handle authentication using API keys when required by the service
- **FR-008**: System MUST allow consumers to select models both programmatically (via code interface) and via command-line flags when invoking CLI tools
- **FR-009**: System MUST expose synchronous model listing functionality with caching to enable fast repeated queries for user or consumer module selection
- **FR-010**: System MUST handle service connection errors gracefully with configurable retry logic (attempts and backoff) and configurable fallback to alternative service providers
- **FR-011**: System MUST validate configuration before attempting service connections by checking URL format, verifying service reachability, and optionally validating API key if provided
- **FR-012**: System MUST allow switching between different LLM service providers [NEEDS CLARIFICATION: Should switching be possible at runtime or only via configuration change and restart?]

### Key Entities

- **LLM Service Configuration**: Represents connection parameters for an LLM service provider (service type, base URL, API key, timeout settings, any service-specific options)
- **Model Metadata**: Represents information about available models from a service (model identifier, display name, capabilities, parameter counts, context limits)
- **LLM Request**: Represents a request to generate or analyze content (prompt/messages, model selection, generation parameters, consumer module identifier)
- **LLM Response**: Represents the result from an LLM service (generated text, token usage, latency metrics, error information if applicable)

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [ ] Review checklist passed

---
