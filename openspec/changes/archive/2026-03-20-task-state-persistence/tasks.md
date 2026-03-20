## 1. Module Setup

- [x] 1.1 Create `anyfile_to_ai/task_manager/` directory with `__init__.py`
- [x] 1.2 Create `models.py` with `TaskState` dataclass and JSON schema
- [x] 1.3 Create `exceptions.py` with `TaskStateError`, `TaskNotFoundError`, `TaskCorruptError`
- [x] 1.4 Create `task_manager.py` with `TaskManager` class skeleton

## 2. Core TaskManager Implementation

- [x] 2.1 Implement `TaskManager._get_tasks_dir()` to create and return `.anything-to-ai/tasks/` path
- [x] 2.2 Implement `TaskManager.create_task()` to create new task with JSON persistence
- [x] 2.3 Implement `TaskManager.load_task()` to load existing task from JSON file
- [x] 2.4 Implement `TaskManager.save_task()` with atomic write (temp file + rename)
- [x] 2.5 Implement `TaskManager.checkpoint()` to update `processed_pages` and persist immediately
- [x] 2.6 Implement `TaskManager.delete_task()` for explicit task removal

## 3. Auto-Cleanup Implementation

- [x] 3.1 Implement `TaskManager._cleanup_stale_tasks()` using TTL and file mtime
- [x] 3.2 Call `_cleanup_stale_tasks()` in `TaskManager.__init__()`

## 4. Error Handling and Validation

- [x] 4.1 Add JSON validation on load with descriptive error messages
- [x] 4.2 Handle `IOError`, `OSError` during file operations with context
- [x] 4.3 Add file locking via `fcntl` for write safety

## 5. Unit Tests

- [x] 5.1 Write tests for `TaskManager.create_task()` and JSON file creation
- [x] 5.2 Write tests for `TaskManager.load_task()` with valid JSON
- [x] 5.3 Write tests for `TaskManager.checkpoint()` and page tracking
- [x] 5.4 Write tests for `TaskManager.delete_task()`
- [x] 5.5 Write tests for TTL cleanup of stale tasks
- [x] 5.6 Write tests for error handling with corrupt JSON

## 6. Integration with routes/pdf.py

- [x] 6.1 Import `TaskManager` in `routes/pdf.py`
- [x] 6.2 Replace in-memory `pdf_tasks` dict with `TaskManager` instance
- [x] 6.3 Call `task_manager.checkpoint()` after each page is processed
- [x] 6.4 Load existing task on startup to resume from last checkpoint
