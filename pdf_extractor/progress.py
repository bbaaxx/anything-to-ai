"""Progress tracking functionality."""
from dataclasses import dataclass


@dataclass
class ProgressInfo:
    """Tracks processing progress and status."""

    pages_processed: int
    total_pages: int
    percentage: float
    current_page: int
    estimated_remaining: float

    def __post_init__(self):
        """Validate ProgressInfo fields."""
        if self.pages_processed > self.total_pages:
            raise ValueError("pages_processed must be <= total_pages")
        if not (0.0 <= self.percentage <= 100.0):
            raise ValueError("percentage must be between 0.0 and 100.0")
        if self.current_page < 0:
            raise ValueError("current_page must be non-negative")
        if self.estimated_remaining < 0:
            raise ValueError("estimated_remaining must be non-negative")

    @classmethod
    def create_started(cls, total_pages: int) -> "ProgressInfo":
        """Create ProgressInfo for started state."""
        return cls(
            pages_processed=0,
            total_pages=total_pages,
            percentage=0.0,
            current_page=0,
            estimated_remaining=0.0,
        )

    @classmethod
    def create_in_progress(
        cls, pages_processed: int, total_pages: int, current_page: int,
        estimated_remaining: float
    ) -> "ProgressInfo":
        """Create ProgressInfo for in-progress state."""
        percentage = (pages_processed / total_pages) * 100.0 if total_pages > 0 else 0.0
        return cls(
            pages_processed=pages_processed,
            total_pages=total_pages,
            percentage=percentage,
            current_page=current_page,
            estimated_remaining=estimated_remaining,
        )

    @classmethod
    def create_complete(cls, total_pages: int) -> "ProgressInfo":
        """Create ProgressInfo for complete state."""
        return cls(
            pages_processed=total_pages,
            total_pages=total_pages,
            percentage=100.0,
            current_page=total_pages,
            estimated_remaining=0.0,
        )
