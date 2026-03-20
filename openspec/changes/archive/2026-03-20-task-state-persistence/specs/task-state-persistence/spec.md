## ADDED Requirements

### Requirement: TaskManager provides persistent task state storage

The system SHALL provide a `TaskManager` class that persists task state to JSON files in the `.anything-to-ai/tasks/` directory. Each task SHALL be stored in a separate file named `{task_id}.json`.

#### Scenario: Task creation and initial save
- **WHEN** a new task is created via `TaskManager.create_task()`
- **THEN** a JSON file is created at `.anything-to-ai/tasks/{task_id}.json`
- **AND** the file contains all task metadata including `pdf_path`, `thumbnails`, `extracted_images`, `processed_pages`, `content_type`, `subcategory`, `complexity`, `batch_index`, `created_at`, `total_pages`

#### Scenario: Existing task is loaded
- **WHEN** `TaskManager.load_task(task_id)` is called for an existing task
- **THEN** the system SHALL return a `TaskState` object matching the saved JSON
- **AND** the task can continue processing from its saved checkpoint

### Requirement: Checkpoint-based page/image tracking

The system SHALL track which pages and images have been successfully processed at a granular level.

#### Scenario: Individual page checkpoint
- **WHEN** a page is successfully processed
- **THEN** `processed_pages[page_number]` SHALL be updated in the task state
- **AND** the checkpoint SHALL be persisted to disk immediately

#### Scenario: Resume from last checkpoint
- **WHEN** a task is resumed after interruption
- **THEN** only unprocessed pages/images SHALL be processed
- **AND** already processed entries in `processed_pages` SHALL be skipped

### Requirement: Atomic writes to prevent corruption

The system SHALL use atomic write operations to prevent corruption from partial writes.

#### Scenario: Write failure handling
- **WHEN** a write operation fails mid-way
- **THEN** the original file SHALL remain unchanged
- **AND** an appropriate error SHALL be raised with context

### Requirement: Auto-cleanup of stale tasks

The system SHALL automatically remove task files older than the configured TTL (default: 7 days).

#### Scenario: TTL cleanup on manager initialization
- **WHEN** `TaskManager()` is instantiated
- **THEN** task files older than TTL SHALL be removed from `.anything-to-ai/tasks/`

#### Scenario: Custom TTL configuration
- **WHEN** `TaskManager(ttl_days=14)` is instantiated
- **THEN** only task files older than 14 days SHALL be removed

### Requirement: Task deletion capability

The system SHALL allow explicit deletion of task state files.

#### Scenario: Delete specific task
- **WHEN** `TaskManager.delete_task(task_id)` is called
- **THEN** the corresponding JSON file SHALL be removed from disk
- **AND** no error SHALL be raised if the file does not exist

### Requirement: JSON schema validation

The system SHALL validate task state JSON structure on load and raise clear errors for corrupt data.

#### Scenario: Load corrupt JSON
- **WHEN** `load_task()` is called with a corrupt JSON file
- **THEN** a `TaskStateError` SHALL be raised with a descriptive message
- **AND** the corrupt file SHALL NOT be modified
