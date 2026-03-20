"""PDF processing routes with persistent task state.

This module provides HTTP route handlers for PDF processing operations
with persistent task state management via TaskManager.
"""

from pathlib import Path
from typing import Any

from anyfile_to_ai.task_manager import TaskManager, TaskState, TaskNotFoundError


# Global TaskManager instance for persistent task state
# In production, this would be configured via dependency injection
_task_manager: TaskManager | None = None


def get_task_manager() -> TaskManager:
    """Get or create the global TaskManager instance.

    Returns:
        TaskManager instance
    """
    global _task_manager
    if _task_manager is None:
        # Default storage directory: .anything-to-ai/tasks/
        _task_manager = TaskManager(ttl_days=7)
    return _task_manager


def create_pdf_task(
    task_id: str,
    source_file: str,
    total_pages: int,
    metadata: dict[str, Any] | None = None,
) -> TaskState:
    """Create a new PDF processing task.

    Args:
        task_id: Unique task identifier
        source_file: Path to the PDF file
        total_pages: Total number of pages in the PDF
        metadata: Optional additional metadata

    Returns:
        Created TaskState instance

    Raises:
        TaskStateError: If task already exists
    """
    manager = get_task_manager()
    return manager.create_task(
        task_id=task_id,
        source_file=source_file,
        total_pages=total_pages,
        metadata=metadata,
    )


def get_pdf_task(task_id: str) -> TaskState:
    """Get the current state of a PDF processing task.

    Args:
        task_id: Unique task identifier

    Returns:
        TaskState instance

    Raises:
        TaskNotFoundError: If task doesn't exist
    """
    manager = get_task_manager()
    return manager.load_task(task_id)


def checkpoint_pdf_page(task_id: str, processed_page: int) -> TaskState:
    """Record a processed page and persist immediately.

    This is called after each page is successfully processed,
    enabling resume from the last checkpoint on failure.

    Args:
        task_id: Unique task identifier
        processed_page: Page number that was just processed

    Returns:
        Updated TaskState instance

    Raises:
        TaskNotFoundError: If task doesn't exist
    """
    manager = get_task_manager()
    return manager.checkpoint(task_id, processed_page)


def get_pdf_progress(task_id: str) -> dict[str, Any]:
    """Get progress information for a PDF processing task.

    Args:
        task_id: Unique task identifier

    Returns:
        Dictionary with progress information:
        - total_pages: Total pages to process
        - processed_pages: Number of pages processed
        - remaining_pages: Number of pages remaining
        - progress_percent: Progress as percentage
        - status: Current task status

    Raises:
        TaskNotFoundError: If task doesn't exist
    """
    manager = get_task_manager()
    return manager.get_task_progress(task_id)


def delete_pdf_task(task_id: str) -> None:
    """Delete a PDF processing task.

    Args:
        task_id: Unique task identifier

    Raises:
        TaskNotFoundError: If task doesn't exist
    """
    manager = get_task_manager()
    manager.delete_task(task_id)


def list_pdf_tasks() -> list[str]:
    """List all PDF processing task IDs.

    Returns:
        List of task IDs
    """
    manager = get_task_manager()
    return manager.list_tasks()


def resume_pdf_task(task_id: str) -> tuple[TaskState, list[int]]:
    """Resume a PDF processing task from its last checkpoint.

    This function loads an existing task and returns the state
    along with the list of pages that still need to be processed.

    Args:
        task_id: Unique task identifier

    Returns:
        Tuple of (TaskState, remaining_pages)

    Raises:
        TaskNotFoundError: If task doesn't exist
    """
    manager = get_task_manager()
    task = manager.load_task(task_id)

    # Calculate remaining pages
    all_pages = set(range(1, task.total_pages + 1))
    processed = set(task.processed_pages)
    remaining = sorted(all_pages - processed)

    return task, remaining


# Example integration with PDF processing workflow:
#
# def process_pdf(source_file: str, task_id: str) -> TaskState:
#     """Process a PDF file with persistent task state.
#
#     This demonstrates the integration pattern:
#     1. Create task with total pages
#     2. Process pages one by one
#     3. Checkpoint after each page
#     4. Resume from checkpoint on failure
#     """
#     total_pages = get_pdf_page_count(source_file)
#
#     # Create or resume task
#     try:
#         task = create_pdf_task(task_id, source_file, total_pages)
#         remaining_pages = list(range(1, total_pages + 1))
#     except TaskStateError:
#         # Task exists, resume from checkpoint
#         task, remaining_pages = resume_pdf_task(task_id)
#
#     # Process remaining pages
#     for page_num in remaining_pages:
#         try:
#             process_page(source_file, page_num)
#             task = checkpoint_pdf_page(task_id, page_num)
#         except Exception as e:
#             # Task state is persisted, can resume later
#             task.status = "failed"
#             task.error_message = str(e)
#             get_task_manager().save_task(task)
#             raise
#
#     return task
