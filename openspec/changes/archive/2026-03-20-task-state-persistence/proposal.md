## Why

Large file processing (PDFs, videos, images) is a long-running operation that can be interrupted by crashes, network issues, or user cancellation. Currently, if a process is interrupted mid-way through extracting thumbnails, OCR, or page processing, all progress is lost and the entire file must be reprocessed from scratch. This is wasteful and unacceptable for users processing large documents.

## What Changes

- **New `TaskManager` module** in `anyfile_to_ai/task_manager/` with persistent state storage
- **JSON-based task state persistence** to `.anything-to-ai/tasks/{task_id}.json`
- **Checkpoint-based resume** allowing processing to continue from the last successful step
- **Page/image-level tracking** so individual pages can be marked complete independently
- **Auto-cleanup mechanism** with configurable TTL to prevent stale task files from accumulating

## Capabilities

### New Capabilities

- `task-state-persistence`: Core capability for persisting and resuming large file processing tasks. Includes:
  - `TaskManager` class with save/load/checkpoint operations
  - JSON schema for task state structure matching existing `pdf_tasks` dict
  - Automatic cleanup of tasks older than configurable TTL
  - Integration points for `routes/pdf.py` and other processors

### Modified Capabilities

- `routes/pdf.py`: Integration with TaskManager for checkpointing page-level progress
- (Other processors can be integrated later - out of scope for initial implementation)

## Impact

- **New Module**: `anyfile_to_ai/task_manager/` directory with `__init__.py`, `task_manager.py`, `models.py`, `exceptions.py`
- **Modified Files**: `routes/pdf.py` to use TaskManager for state persistence
- **Data Directory**: Creates `.anything-to-ai/tasks/` for JSON state files
- **No Breaking Changes**: New functionality only; existing behavior unchanged
