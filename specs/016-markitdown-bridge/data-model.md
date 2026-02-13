# Data Model: MarkItDown Bridge Contracts

Date: 2026-02-12
Feature: `specs/016-markitdown-bridge/spec.md`

## Entity: SourceInput

- **Description**: Caller-provided conversion source identifier.
- **Fields**:
  - `value` (string, required): original user-provided source.
  - `kind` (enum, derived): `url_http_https` or `local_like`.
  - `normalized_suffix` (string, derived, lowercase): extension/suffix used for routing.
- **Validation Rules**:
  - Empty or whitespace-only values are invalid.
  - URL classification is only for `http` and `https` schemes.

## Entity: ConversionRoute

- **Description**: Backend selected for conversion execution.
- **Values**:
  - `pdf_extractor`
  - `image_processor`
  - `audio_processor`
  - `markitdown`
- **Routing Rules**:
  - Local PDF -> `pdf_extractor`
  - Local image -> `image_processor`
  - Local audio -> `audio_processor`
  - Local Office/HTML/EPUB/ZIP -> `markitdown`
  - HTTP/HTTPS URLs (including YouTube hosts) -> `markitdown`
  - Unknown local suffix -> `markitdown` fallback

## Entity: ConversionResultContract

- **Description**: Normalized output returned from conversion entry point.
- **Fields**:
  - `source` (string, required): original source input.
  - `route` (ConversionRoute, required): selected backend route.
  - `content` (string, required): normalized text content.
  - `metadata` (object | null, optional): backend metadata; best-effort by route.
  - `raw_result` (opaque, optional): backend-native response object for advanced callers.
- **Stability Classification**:
  - Stable required: `source`, `route`, `content`.
  - Best-effort/variable: `metadata` shape/coverage, `raw_result` structure.

## Entity: ConversionErrorContract

- **Description**: Typed error outcomes from route determination and conversion.
- **Types**:
  - `UnsupportedInputError`: invalid routing-time input (currently empty/whitespace source).
  - `MissingDependencyError`: selected route dependency unavailable; includes install guidance.
  - `DocumentConversionError`: unexpected backend/runtime failure wrapper with route/source context.
- **Boundary Rules**:
  - Existing `DocumentConversionError` subclasses are propagated without rewrapping.
  - Unknown exceptions are wrapped as `DocumentConversionError` with chained cause.

## Relationships

- `SourceInput` determines exactly one `ConversionRoute`.
- `ConversionRoute` produces one `ConversionResultContract` on success.
- `SourceInput` + `ConversionRoute` can produce one `ConversionErrorContract` on failure.

## State Transitions

1. `received` -> input validation
2. `validated` -> route determination
3. `routed` -> backend conversion execution
4. `converted` (success) -> normalized result returned
5. `failed` (error) -> typed error raised per boundary rules

## Invariants

- Route choice is deterministic for a given source string.
- Successful results always include stable required fields.
- Missing optional dependency errors provide actionable install guidance.
- Formatter unification is not required to satisfy this contract model.
