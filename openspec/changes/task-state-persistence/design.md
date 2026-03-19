## Context

Large file processing (PDFs, images, audio, video) involves multiple stages: thumbnail generation, text extraction, OCR, summarization. When processing is interrupted (crash, network failure, user cancellation), all progress is lost. The user must restart from the beginning, wasting time and resources.

Currently, `routes/pdf.py` maintains an in-memory `pdf_tasks` dict with task state. This state is lost on process restart.

## Goals / Non-Goals

**Goals:**
- Provide reliable task state persistence across process restarts
- Enable checkpoint-based resume so partially completed tasks can continue
- Track page/image-level progress for granular recovery
- Auto-cleanup stale tasks to prevent disk accumulation

**Non-Goals:**
- Real-time synchronization across multiple workers (single-process focus)
- Distributed task queue or job scheduling
- Cloud backup or replication of task state
- Support for concurrent access to the same task from multiple processes

## Decisions

### 1. JSON File Storage in `.anything-to-ai/tasks/`

**Decision:** Store task state as individual JSON files in a dedicated directory.

**Rationale:**
- Simple, human-readable format for debugging
- No database dependency
- Filesystem-level atomicity for writes
- Easy cleanup with standard file operations

**Alternative Considered:** SQLite database
- Overkill for single-process use case
- Adds external dependency
- Harder to inspect/debug

### 2. TaskManager Class with Synchronous I/O

**Decision:** `TaskManager` class with methods like `save()`, `load()`, `checkpoint()` that perform synchronous file I/O.

**Rationale:**
- Simpler mental model for callers
- `routes/pdf.py` is already synchronous
- Easier to reason about consistency
- No async/await complexity

**Alternative Considered:** Async TaskManager
- Would require async everywhere in callers
- No current async use case in pdf.py

### 3. Data Model Matches Existing `pdf_tasks` Structure

**Decision:** JSON schema mirrors the existing in-memory structure from user's proposal.

**Rationale:**
- Minimal refactoring of existing code
- Clear migration path
- Drop-in replacement for in-memory dict

### 4. TTL-Based Auto-Cleanup

**Decision:** Configurable TTL (default 7 days) for automatic task cleanup.

**Rationale:**
- Prevents unbounded disk growth
- Configurable for different deployment scenarios
- Simple implementation using file mtime

**Alternative Considered:** Manual cleanup API
- Requires user intervention
- Easy to forget, leading to disk bloat

### 5. Per-File Lock for Write Safety

**Decision:** Use file locking (via `fcntl`) during writes to prevent corruption.

**Rationale:**
- Protects against concurrent writes
- Standard approach for file-based state
- Graceful handling if another process accesses same file

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| **Partial writes** if process killed mid-write | Write to temp file, then atomic rename |
| **Corrupt JSON** from bad writes | Validate JSON on load, raise clear error |
| **Disk full** during save | Catch IOError, propagate with context |
| **Stale task files** from crashed processes | TTL cleanup handles this |
| **Race condition** on concurrent access | File locking + error propagation |

## Migration Plan

1. **Create** `anyfile_to_ai/task_manager/` module with initial implementation
2. **Add unit tests** for TaskManager class
3. **Integrate** `routes/pdf.py` to use TaskManager (new endpoint or gradual migration)
4. **Deploy** with feature flag to control behavior
5. **Monitor** for issues before enabling for all users

**Rollback:** If issues arise, disable TaskManager and fall back to in-memory state.

## Open Questions

1. **Should existing in-memory tasks be migrated?** Decision: No automatic migration. Old in-memory tasks are lost on restart; new tasks use persistent storage.

2. **What's the max task size?** Set reasonable limit (10MB) to prevent abuse. Tasks larger than this will log a warning.

3. **Should we support task deletion?** Yes, add `delete_task()` method for explicit cleanup when user wants to restart from scratch.
