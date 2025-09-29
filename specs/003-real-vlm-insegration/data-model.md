# Data Model: Real VLM Integration

## Core Entities

### ModelConfiguration
Represents environment-based VLM model configuration.

**Fields**:
- `model_name: str` - Model identifier from VISION_MODEL environment variable
- `timeout_seconds: Optional[int]` - Configurable processing timeout
- `timeout_behavior: str` - Action on timeout ("error", "fallback", "continue")
- `auto_download: bool` - Whether to automatically download missing models
- `validation_enabled: bool` - Whether to validate model before loading

**Validation Rules**:
- model_name must be non-empty when VLM processing enabled
- timeout_seconds must be positive if specified
- timeout_behavior must be one of valid options
- Must fail fast if model_name not configured when VLM required

**State Transitions**:
- UNCONFIGURED → CONFIGURED (when environment variable set)
- CONFIGURED → VALIDATED (after model availability check)
- VALIDATED → READY (after successful model loading)

### LoadedModel
Represents an active VLM model instance in memory.

**Fields**:
- `model_instance: Any` - MLX VLM model object
- `model_name: str` - Loaded model identifier
- `model_version: str` - Model version information
- `memory_usage: int` - Estimated memory consumption in bytes
- `load_time: float` - Time taken to load model
- `capabilities: Dict[str, Any]` - Model-specific capabilities

**Validation Rules**:
- model_instance must be valid MLX VLM object
- memory_usage must be tracked for cleanup decisions
- Only one instance per process to prevent memory issues

**State Transitions**:
- LOADING → READY (successful model initialization)
- READY → IN_USE (during image processing)
- IN_USE → READY (after processing completion)
- READY → CLEANUP (when batch processing complete)

### EnhancedResult
Combined result containing both VLM description and technical metadata.

**Fields**:
- `vlm_description: str` - AI-generated image description
- `technical_metadata: TechnicalMetadata` - Preserved technical analysis
- `model_info: Dict[str, str]` - Model name and version used
- `processing_time: float` - Time taken for VLM processing
- `confidence_score: Optional[float]` - Model confidence if available

**Validation Rules**:
- vlm_description must be non-empty for successful processing
- technical_metadata must always be present (backward compatibility)
- processing_time must be positive
- All fields required for complete result

**Relationships**:
- Contains one TechnicalMetadata instance
- References LoadedModel information via model_info

### TechnicalMetadata
Structured technical analysis data (existing, preserved).

**Fields**:
- `format: str` - Image format (PNG, JPEG, etc.)
- `dimensions: Tuple[int, int]` - Width and height in pixels
- `file_size: int` - File size in bytes
- `processing_time: float` - Time for technical analysis
- `file_path: str` - Source image file path

**Validation Rules**:
- format must be valid image format
- dimensions must be positive integers
- file_size must be non-negative
- Maintains exact compatibility with existing implementation

### ModelRegistry
System component managing model lifecycle and validation.

**Fields**:
- `available_models: Dict[str, ModelInfo]` - Registry of available models
- `loaded_model: Optional[LoadedModel]` - Currently loaded model instance
- `download_progress: Optional[DownloadProgress]` - Model download status
- `validation_cache: Dict[str, bool]` - Cached validation results

**Validation Rules**:
- available_models updated on registry initialization
- Only one loaded_model at a time
- validation_cache prevents repeated validation calls
- Must handle network failures gracefully

**State Transitions**:
- INITIALIZING → READY (after model registry scan)
- READY → LOADING (when model load requested)
- LOADING → MODEL_LOADED (successful load)
- MODEL_LOADED → CLEANUP (batch completion)

## Entity Relationships

```
ModelConfiguration → ModelRegistry → LoadedModel
                                  ↓
TechnicalMetadata ← EnhancedResult ← LoadedModel
```

## Data Flow

1. **Configuration Phase**:
   - ModelConfiguration reads VISION_MODEL environment variable
   - ModelRegistry validates model availability
   - System fails fast if configuration invalid

2. **Processing Phase**:
   - LoadedModel performs VLM inference
   - TechnicalMetadata generated via existing pipeline
   - EnhancedResult combines both data sources

3. **Cleanup Phase**:
   - ModelRegistry manages LoadedModel lifecycle
   - Memory cleanup after batch processing
   - Resources released for next operation

## Backward Compatibility

All entities designed to maintain exact API compatibility:

- **Existing Interfaces**: No changes to public method signatures
- **Output Formats**: Enhanced but backward-compatible JSON/CSV/plain formats
- **Error Types**: Extended exception hierarchy, existing types preserved
- **CLI Arguments**: All existing arguments preserved, new ones optional

## Validation Strategy

- **Input Validation**: Environment variables, file paths, model names
- **Model Validation**: Availability check before resource allocation
- **Output Validation**: Ensure both VLM and technical data present
- **Error Handling**: Specific exceptions for each validation failure type