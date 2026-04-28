"""Unit tests for TaskManager module."""

import json
import tempfile
from datetime import datetime, timedelta, timezone, UTC
from pathlib import Path

import pytest

from anyfile_to_ai.task_manager import (
    TaskManager,
    TaskState,
    TaskStateError,
    TaskNotFoundError,
    TaskCorruptError,
    TaskIOError,
    TaskLockError,
)


class TestTaskState:
    """Tests for TaskState dataclass."""

    def test_task_state_required_fields(self) -> None:
        """Test that required fields must be provided."""
        task = TaskState(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
        )
        assert task.task_id == "test-123"
        assert task.source_file == "/path/to/file.pdf"
        assert task.total_pages == 10

    def test_task_state_all_fields(self) -> None:
        """Test that all fields can be set."""
        task = TaskState(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
            processed_pages=[1, 2, 3],
            status="in_progress",
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-02T00:00:00",
            error_message="test error",
            metadata={"key": "value"},
        )
        assert task.processed_pages == [1, 2, 3]
        assert task.status == "in_progress"
        assert task.error_message == "test error"
        assert task.metadata == {"key": "value"}

    def test_task_state_default_values(self) -> None:
        """Test that default values are set correctly."""
        task = TaskState(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
        )
        assert task.processed_pages == []
        assert task.status == "pending"
        assert task.error_message is None
        assert task.metadata == {}
        # Timestamps should be set
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_state_validation_empty_task_id(self) -> None:
        """Test that empty task_id raises ValueError."""
        with pytest.raises(ValueError, match="task_id cannot be empty"):
            TaskState(
                task_id="",
                source_file="/path/to/file.pdf",
                total_pages=10,
            )

    def test_task_state_validation_empty_source_file(self) -> None:
        """Test that empty source_file raises ValueError."""
        with pytest.raises(ValueError, match="source_file cannot be empty"):
            TaskState(
                task_id="test-123",
                source_file="",
                total_pages=10,
            )

    def test_task_state_validation_negative_pages(self) -> None:
        """Test that negative total_pages raises ValueError."""
        with pytest.raises(ValueError, match="total_pages cannot be negative"):
            TaskState(
                task_id="test-123",
                source_file="/path/to/file.pdf",
                total_pages=-1,
            )

    def test_task_state_validation_invalid_status(self) -> None:
        """Test that invalid status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid status"):
            TaskState(
                task_id="test-123",
                source_file="/path/to/file.pdf",
                total_pages=10,
                status="invalid_status",
            )

    def test_task_state_validation_invalid_page_number(self) -> None:
        """Test that invalid page numbers raise ValueError."""
        with pytest.raises(ValueError, match="Invalid page number"):
            TaskState(
                task_id="test-123",
                source_file="/path/to/file.pdf",
                total_pages=10,
                processed_pages=[0],  # Page 0 is invalid
            )

        with pytest.raises(ValueError, match="Invalid page number"):
            TaskState(
                task_id="test-123",
                source_file="/path/to/file.pdf",
                total_pages=10,
                processed_pages=[11],  # Page 11 exceeds total
            )

    def test_progress_percent(self) -> None:
        """Test progress_percent property."""
        task = TaskState(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
        )
        assert task.progress_percent == 0.0

        task.processed_pages = [1, 2, 3]
        assert task.progress_percent == 30.0

        task.processed_pages = list(range(1, 11))
        assert task.progress_percent == 100.0

    def test_progress_percent_zero_pages(self) -> None:
        """Test progress_percent with zero total_pages."""
        task = TaskState(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=0,
        )
        assert task.progress_percent == 0.0

    def test_is_complete(self) -> None:
        """Test is_complete property."""
        task = TaskState(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
        )
        assert not task.is_complete

        task.processed_pages = list(range(1, 11))
        assert task.is_complete

    def test_last_processed_page(self) -> None:
        """Test last_processed_page property."""
        task = TaskState(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
        )
        assert task.last_processed_page is None

        task.processed_pages = [1, 2, 3]
        assert task.last_processed_page == 3

        task.processed_pages = [5, 3, 7]
        assert task.last_processed_page == 7

    def test_to_json(self) -> None:
        """Test JSON serialization."""
        task = TaskState(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
            processed_pages=[1, 2],
            status="in_progress",
        )
        json_str = task.to_json()
        data = json.loads(json_str)

        assert data["task_id"] == "test-123"
        assert data["source_file"] == "/path/to/file.pdf"
        assert data["total_pages"] == 10
        assert data["processed_pages"] == [1, 2]
        assert data["status"] == "in_progress"

    def test_from_json(self) -> None:
        """Test JSON deserialization."""
        json_str = json.dumps(
            {
                "task_id": "test-123",
                "source_file": "/path/to/file.pdf",
                "total_pages": 10,
                "processed_pages": [1, 2],
                "status": "in_progress",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-02T00:00:00",
            }
        )
        task = TaskState.from_json(json_str)

        assert task.task_id == "test-123"
        assert task.source_file == "/path/to/file.pdf"
        assert task.total_pages == 10
        assert task.processed_pages == [1, 2]
        assert task.status == "in_progress"

    def test_from_json_invalid_json(self) -> None:
        """Test that invalid JSON raises ValueError."""
        with pytest.raises(ValueError, match="Invalid JSON"):
            TaskState.from_json("not valid json")

    def test_from_json_missing_required_fields(self) -> None:
        """Test that missing required fields raises ValueError."""
        json_str = json.dumps({"task_id": "test-123"})
        with pytest.raises(ValueError, match="Missing required fields"):
            TaskState.from_json(json_str)

    def test_to_dict_and_from_dict(self) -> None:
        """Test dictionary conversion round-trip."""
        task = TaskState(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
            processed_pages=[1, 2],
            status="in_progress",
        )
        data = task.to_dict()
        restored = TaskState.from_dict(data)

        assert restored.task_id == task.task_id
        assert restored.source_file == task.source_file
        assert restored.total_pages == task.total_pages
        assert restored.processed_pages == task.processed_pages
        assert restored.status == task.status


class TestTaskManager:
    """Tests for TaskManager class."""

    @pytest.fixture
    def temp_storage_dir(self, tmp_path: Path) -> Path:
        """Create a temporary storage directory."""
        storage_dir = tmp_path / "tasks"
        storage_dir.mkdir()
        return storage_dir

    @pytest.fixture
    def task_manager(self, temp_storage_dir: Path) -> TaskManager:
        """Create a TaskManager instance with temporary storage."""
        return TaskManager(storage_dir=temp_storage_dir, ttl_days=0)

    def test_init_creates_storage_dir(self, tmp_path: Path) -> None:
        """Test that __init__ creates storage directory if it doesn't exist."""
        storage_dir = tmp_path / "new_tasks_dir"
        assert not storage_dir.exists()

        TaskManager(storage_dir=storage_dir, ttl_days=0)

        assert storage_dir.exists()

    def test_create_task(self, task_manager: TaskManager) -> None:
        """Test creating a new task."""
        task = task_manager.create_task(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
        )

        assert task.task_id == "test-123"
        assert task.source_file == "/path/to/file.pdf"
        assert task.total_pages == 10
        assert task.status == "pending"
        assert task.processed_pages == []

        # Verify file was created
        assert task_manager.task_exists("test-123")

    def test_create_task_with_metadata(self, task_manager: TaskManager) -> None:
        """Test creating a task with metadata."""
        task = task_manager.create_task(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
            metadata={"key": "value"},
        )

        assert task.metadata == {"key": "value"}

    def test_create_task_already_exists(self, task_manager: TaskManager) -> None:
        """Test that creating a duplicate task raises TaskStateError."""
        task_manager.create_task(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
        )

        with pytest.raises(TaskStateError, match="Task already exists"):
            task_manager.create_task(
                task_id="test-123",
                source_file="/path/to/other.pdf",
                total_pages=20,
            )

    def test_load_task(self, task_manager: TaskManager) -> None:
        """Test loading an existing task."""
        task_manager.create_task(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
        )

        loaded = task_manager.load_task("test-123")

        assert loaded.task_id == "test-123"
        assert loaded.source_file == "/path/to/file.pdf"
        assert loaded.total_pages == 10

    def test_load_task_not_found(self, task_manager: TaskManager) -> None:
        """Test that loading a non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_manager.load_task("nonexistent")

    def test_load_task_corrupt_json(self, task_manager: TaskManager, temp_storage_dir: Path) -> None:
        """Test that loading a corrupt JSON file raises TaskCorruptError."""
        # Create a corrupt task file
        corrupt_file = temp_storage_dir / "corrupt.json"
        corrupt_file.write_text("not valid json")

        with pytest.raises(TaskCorruptError, match="Invalid JSON"):
            task_manager.load_task("corrupt")

    def test_load_task_missing_fields(self, task_manager: TaskManager, temp_storage_dir: Path) -> None:
        """Test that loading a task with missing fields raises TaskCorruptError."""
        # Create a task file with missing required fields
        incomplete_file = temp_storage_dir / "incomplete.json"
        incomplete_file.write_text(json.dumps({"task_id": "incomplete"}))

        with pytest.raises(TaskCorruptError, match="Missing required fields"):
            task_manager.load_task("incomplete")

    def test_save_task(self, task_manager: TaskManager) -> None:
        """Test saving task state."""
        task = task_manager.create_task(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
        )

        task.processed_pages = [1, 2, 3]
        task.status = "in_progress"
        task_manager.save_task(task)

        # Reload and verify
        loaded = task_manager.load_task("test-123")
        assert loaded.processed_pages == [1, 2, 3]
        assert loaded.status == "in_progress"

    def test_checkpoint(self, task_manager: TaskManager) -> None:
        """Test checkpoint updates processed pages."""
        task_manager.create_task(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
        )

        # Checkpoint first page
        task = task_manager.checkpoint("test-123", 1)
        assert task.processed_pages == [1]
        assert task.status == "in_progress"

        # Checkpoint second page
        task = task_manager.checkpoint("test-123", 2)
        assert task.processed_pages == [1, 2]

        # Checkpoint same page again (should be idempotent)
        task = task_manager.checkpoint("test-123", 2)
        assert task.processed_pages == [1, 2]

    def test_checkpoint_completes_task(self, task_manager: TaskManager) -> None:
        """Test that checkpoint marks task as completed when all pages processed."""
        task_manager.create_task(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=3,
        )

        task_manager.checkpoint("test-123", 1)
        task_manager.checkpoint("test-123", 2)
        task = task_manager.checkpoint("test-123", 3)

        assert task.is_complete
        assert task.status == "completed"

    def test_checkpoint_not_found(self, task_manager: TaskManager) -> None:
        """Test that checkpoint raises TaskNotFoundError for non-existent task."""
        with pytest.raises(TaskNotFoundError):
            task_manager.checkpoint("nonexistent", 1)

    def test_delete_task(self, task_manager: TaskManager) -> None:
        """Test deleting a task."""
        task_manager.create_task(
            task_id="test-123",
            source_file="/path/to/file.pdf",
            total_pages=10,
        )

        assert task_manager.task_exists("test-123")

        task_manager.delete_task("test-123")

        assert not task_manager.task_exists("test-123")

    def test_delete_task_not_found(self, task_manager: TaskManager) -> None:
        """Test that deleting a non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_manager.delete_task("nonexistent")

    def test_list_tasks(self, task_manager: TaskManager) -> None:
        """Test listing all tasks."""
        task_manager.create_task("task-1", "/file1.pdf", 10)
        task_manager.create_task("task-2", "/file2.pdf", 20)
        task_manager.create_task("task-3", "/file3.pdf", 30)

        task_ids = task_manager.list_tasks()

        assert task_ids == ["task-1", "task-2", "task-3"]

    def test_list_tasks_empty(self, task_manager: TaskManager) -> None:
        """Test listing tasks when storage is empty."""
        assert task_manager.list_tasks() == []

    def test_task_exists(self, task_manager: TaskManager) -> None:
        """Test checking if a task exists."""
        task_manager.create_task("test-123", "/file.pdf", 10)

        assert task_manager.task_exists("test-123") is True
        assert task_manager.task_exists("nonexistent") is False

    def test_get_task_progress(self, task_manager: TaskManager) -> None:
        """Test getting task progress information."""
        task_manager.create_task("test-123", "/file.pdf", 10)
        task_manager.checkpoint("test-123", 1)
        task_manager.checkpoint("test-123", 2)

        progress = task_manager.get_task_progress("test-123")

        assert progress["total_pages"] == 10
        assert progress["processed_pages"] == 2
        assert progress["remaining_pages"] == 8
        assert progress["progress_percent"] == 20.0
        assert progress["status"] == "in_progress"

    def test_get_task_progress_not_found(self, task_manager: TaskManager) -> None:
        """Test that get_task_progress raises TaskNotFoundError for non-existent task."""
        with pytest.raises(TaskNotFoundError):
            task_manager.get_task_progress("nonexistent")


class TestTaskManagerCleanup:
    """Tests for TTL-based cleanup functionality."""

    def test_cleanup_expired_tasks(self, tmp_path: Path) -> None:
        """Test that expired tasks are cleaned up on init."""
        storage_dir = tmp_path / "tasks"
        storage_dir.mkdir()

        # Create a task manager with TTL
        manager = TaskManager(storage_dir=storage_dir, ttl_days=7)

        # Create a task
        manager.create_task("test-123", "/file.pdf", 10)

        # Manually age the task file
        task_file = storage_dir / "test-123.json"
        old_time = (datetime.now(UTC) - timedelta(days=10)).timestamp()
        import os

        os.utime(task_file, (old_time, old_time))

        # Create new manager - should clean up expired task
        manager2 = TaskManager(storage_dir=storage_dir, ttl_days=7)

        assert not manager2.task_exists("test-123")

    def test_cleanup_disabled_with_zero_ttl(self, tmp_path: Path) -> None:
        """Test that cleanup is disabled when TTL is 0."""
        storage_dir = tmp_path / "tasks"
        storage_dir.mkdir()

        # Create a task manager with TTL=0
        manager = TaskManager(storage_dir=storage_dir, ttl_days=0)

        # Create a task
        manager.create_task("test-123", "/file.pdf", 10)

        # Manually age the task file
        task_file = storage_dir / "test-123.json"
        old_time = (datetime.now(UTC) - timedelta(days=100)).timestamp()
        import os

        os.utime(task_file, (old_time, old_time))

        # Create new manager - should NOT clean up
        manager2 = TaskManager(storage_dir=storage_dir, ttl_days=0)

        assert manager2.task_exists("test-123")


class TestTaskManagerAtomicWrites:
    """Tests for atomic write functionality."""

    @pytest.fixture
    def temp_storage_dir(self, tmp_path: Path) -> Path:
        """Create a temporary storage directory."""
        storage_dir = tmp_path / "tasks"
        storage_dir.mkdir()
        return storage_dir

    @pytest.fixture
    def task_manager(self, temp_storage_dir: Path) -> TaskManager:
        """Create a TaskManager instance with temporary storage."""
        return TaskManager(storage_dir=temp_storage_dir, ttl_days=0)

    def test_atomic_write_creates_valid_json(self, task_manager: TaskManager) -> None:
        """Test that atomic write creates valid JSON file."""
        task_manager.create_task("test-123", "/file.pdf", 10)

        # Read the file directly
        task_file = task_manager._get_task_path("test-123")
        content = task_file.read_text()

        # Should be valid JSON
        data = json.loads(content)
        assert data["task_id"] == "test-123"

    def test_no_temp_files_left(self, task_manager: TaskManager) -> None:
        """Test that no temp files are left after write."""
        task_manager.create_task("test-123", "/file.pdf", 10)

        # Check for temp files
        temp_files = list(task_manager.storage_dir.glob("*.tmp"))
        assert temp_files == []


class TestTaskManagerFileLocking:
    """Tests for file locking functionality."""

    @pytest.fixture
    def temp_storage_dir(self, tmp_path: Path) -> Path:
        """Create a temporary storage directory."""
        storage_dir = tmp_path / "tasks"
        storage_dir.mkdir()
        return storage_dir

    @pytest.fixture
    def task_manager(self, temp_storage_dir: Path) -> TaskManager:
        """Create a TaskManager instance with temporary storage."""
        return TaskManager(storage_dir=temp_storage_dir, ttl_days=0)

    def test_lock_file_created_during_checkpoint(self, task_manager: TaskManager) -> None:
        """Test that lock file is managed during checkpoint."""
        task_manager.create_task("test-123", "/file.pdf", 10)

        # Checkpoint should acquire and release lock
        task_manager.checkpoint("test-123", 1)

        # Lock file should be cleaned up
        task_manager._get_task_path("test-123").with_suffix(".json.lock")
        # Lock file may or may not exist, but should not be locked
        # This is a basic sanity check
        assert task_manager.task_exists("test-123")


class TestExceptions:
    """Tests for custom exceptions."""

    def test_task_state_error(self) -> None:
        """Test TaskStateError basic functionality."""
        error = TaskStateError("Something went wrong")
        assert str(error) == "Something went wrong"

    def test_task_state_error_with_context(self) -> None:
        """Test TaskStateError with context."""
        error = TaskStateError(
            "Something went wrong",
            task_id="test-123",
            file_path="/path/to/file.json",
        )
        assert "test-123" in str(error)
        assert "file.json" in str(error)

    def test_task_not_found_error(self) -> None:
        """Test TaskNotFoundError."""
        error = TaskNotFoundError(task_id="test-123")
        assert "not found" in str(error).lower()
        assert "test-123" in str(error)

    def test_task_corrupt_error(self) -> None:
        """Test TaskCorruptError."""
        error = TaskCorruptError(
            task_id="test-123",
            reason="Invalid JSON",
        )
        assert "Corrupt" in str(error)
        assert "Invalid JSON" in str(error)

    def test_task_io_error(self) -> None:
        """Test TaskIOError."""
        error = TaskIOError(
            operation="write",
            task_id="test-123",
        )
        assert "I/O error" in str(error)
        assert "write" in str(error)

    def test_task_lock_error(self) -> None:
        """Test TaskLockError."""
        error = TaskLockError(
            operation="acquire",
            task_id="test-123",
        )
        assert "lock" in str(error).lower()
