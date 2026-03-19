# Research: Real VLM Integration

## Technology Research Findings

### VLM Model Selection and Configuration

**Decision**: Use configurable VLM models via VISION_MODEL environment variable, with google/gemma-3-4b as initial testing model.

**Rationale**:
- Environment-based configuration enables flexible model switching without code changes
- MLX framework provides optimal Apple Silicon performance for local VLM inference
- Configurable approach supports different environments (development, testing, production)
- No default model prevents accidental resource consumption

**Alternatives considered**:
- Hard-coded model selection (rejected: lacks flexibility for different environments)
- Configuration files (rejected: environment variables simpler for model switching)
- Multiple model support simultaneously (rejected: excessive memory usage)

### Integration Strategy with Existing Implementation

**Decision**: Replace mock implementation while preserving exact API compatibility and technical metadata.

**Rationale**:
- Existing image_processor module has well-defined interfaces and patterns
- Users depend on current CLI arguments, output formats, and module API
- Technical metadata (format, dimensions, file size) provides value alongside AI descriptions
- Seamless transition from mock to real implementation without breaking changes

**Alternatives considered**:
- Complete rewrite (rejected: breaks existing users and loses proven patterns)
- Parallel implementation (rejected: maintenance complexity)
- Gradual feature flags (rejected: adds complexity without benefit)

### Model Loading and Memory Management

**Decision**: Implement singleton pattern with lazy loading and automatic cleanup after batch processing.

**Rationale**:
- Building on proven patterns from 002 research: singleton prevents multiple model instances
- Lazy loading improves startup performance when VLM not immediately needed
- Automatic cleanup after batch operations prevents memory leaks
- MLX unified memory model benefits from careful resource management

**Alternatives considered**:
- Model loading per request (rejected: inefficient initialization overhead)
- Manual cleanup (rejected: error-prone, user responsibility)
- Keep models loaded indefinitely (rejected: memory consumption)

### Error Handling and Validation

**Decision**: Extend existing exception hierarchy with VLM-specific error types and model validation.

**Rationale**:
- Consistent with existing image_processor.exceptions patterns
- Specific errors for model loading, configuration, and processing failures
- Graceful degradation when models unavailable or invalid
- Clear error messages guide users to proper configuration

**Alternatives considered**:
- Generic exception handling (rejected: poor user experience)
- Silent fallback to mock (rejected: unclear behavior)
- System exit on errors (rejected: breaks module usage)

### Performance and Timeout Management

**Decision**: Implement configurable timeout with user-defined timeout behavior (error, fallback, continue).

**Rationale**:
- VLM processing can be time-consuming depending on model and image complexity
- Different use cases require different timeout strategies
- Configurable approach supports both interactive and batch processing scenarios
- Prevents hung processes while allowing flexibility

**Alternatives considered**:
- Fixed timeout (rejected: different models have different performance characteristics)
- No timeout (rejected: risk of hung processes)
- Always fallback to mock (rejected: unclear user intent)

### Model Registry and Validation

**Decision**: Implement model validation before loading with clear error messages for unavailable models.

**Rationale**:
- Fail fast with clear error messages when configured model unavailable
- Automatic download with progress indication for new models
- Network failure handling for model downloads
- Model compatibility validation before resource allocation

**Alternatives considered**:
- Load and fail (rejected: wastes resources)
- Silent model substitution (rejected: unclear behavior)
- No validation (rejected: poor error messages)

## Architecture Insights

### Enhanced Component Design

Building on existing image_processor architecture:

- **Models**: Extend existing data structures with VLM configuration and enhanced results
- **Processor**: Replace mock implementation with real VLM processing while maintaining interface
- **VLM Integration**: New module for VLM-specific functionality (model loading, inference)
- **Streaming**: Extend batch processing to handle VLM resource management
- **Exceptions**: Add VLM-specific exception types to existing hierarchy
- **CLI**: Maintain exact compatibility with existing command-line interface

### Integration Points

Key integration requirements identified:

- **Environment Configuration**: VISION_MODEL variable for model selection
- **API Compatibility**: Preserve all existing method signatures and return types
- **Output Formats**: Enhance JSON/CSV/plain formats with VLM descriptions alongside metadata
- **Progress Tracking**: Extend existing progress callbacks for VLM operations
- **Error Handling**: Integrate VLM errors into existing error handling patterns

### Performance Considerations

Based on 002 research and VLM requirements:

- **Model Initialization**: One-time cost per batch, amortized across multiple images
- **Memory Management**: Critical for VLM models, use MLX cache clearing strategies
- **Batch Processing**: Optimize for VLM model reuse within batches
- **Resource Cleanup**: Automatic cleanup prevents memory accumulation

## Implementation Readiness

All technical unknowns resolved through research. Ready for detailed design with:

- Clear integration strategy maintaining API compatibility
- Proven architectural patterns from existing implementation
- Specific error handling and timeout strategies
- Model management and validation approach
- Performance optimization based on MLX best practices

No additional research dependencies for proceeding to design phase.
