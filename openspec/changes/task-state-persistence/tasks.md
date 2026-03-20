## 1. Module Setup

- [ ] 1.1 Create `anyfile_to_ai/task_manager/` directory with `__init__.py`
- [ ] 1.2 Create `models.py` with `TaskState` dataclass and JSON schema
- [ ] 1.3 Create `exceptions.py` with `TaskStateError`, `TaskNotFoundError`, `TaskCorruptError`
- [ ] 1.4 Create `task_manager.py` with `TaskManager` class skeleton

## 2. Core TaskManager Implementation

- [ ] 2.1 Implement `TaskManager._get_tasks_dir()` to create and return `.anything-to-ai/tasks/` path
- [ ] 2.2 Implement `TaskManager.create_task()` to create new task with JSON persistence
- [ ] 2.3 Implement `TaskManager.load_task()` to load existing task from JSON file
- [ ] 2.4 Implement `TaskManager.save_task()` with atomic write (temp file + rename)
- [ ] 2.5 Implement `TaskManager.checkpoint()` to update `processed_pages` and persist immediately
- [ ] 2.6 Implement `TaskManager.delete_task()` for explicit task removal

## 3. Auto-Cleanup Implementation

- [ ] 3.1 Implement `TaskManager._cleanup_stale_tasks()` using TTL and file mtime
- [ ] 3.2 Call `_cleanup_stale_tasks()` in `TaskManager.__init__()`

## 4. Error Handling and Validation

- [ ] 4.1 Add JSON validation on load with descriptive error messages
- [ ] 4.2 Handle `IOError`, `OSError` during file operations with context
- [ ] 4.3 Add file locking via `fcntl` for write safety

## 5. Unit Tests

- [ ] 5.1 Write tests for `TaskManager.create_task()` and JSON file creation
- [ ] 5.2 Write tests for `TaskManager.load_task()` with valid JSON
- [ ] 5.3 Write tests for `TaskManager.checkpoint()` and page tracking
- [ ] 5.4 Write tests for `TaskManager.delete_task()`
- [ ] 5.5 Write tests for TTL cleanup of stale tasks
- [ ] 5.6 Write tests for error handling with corrupt JSON

## 6. Integration with routes/pdf.py

- [ ] 6.1 Import `TaskManager` in `routes/pdf.py`
- [ ] 6.2 Replace in-memory `pdf_tasks` dict with `TaskManager` instance
- [ ] 6.3 Call `task_manager.checkpoint()` after each page is processed
- [ ] 6.4 Load existing task on startup to resume from last checkpoint
