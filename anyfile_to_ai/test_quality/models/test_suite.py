"""
Test Suite model for test quality management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal


@dataclass
class TestSuite:
    """Represents a test suite with quality metrics."""

    id: str
    name: str
    status: Literal["passing", "failing", "flaky", "quarantined"]
    coverage_percentage: float = field(default=0.0)
    last_run: datetime | None = None
    test_count: int = field(default=0)
    failure_count: int = field(default=0)
    flaky_count: int = field(default=0)

    def __post_init__(self) -> None:
        """Validate test suite data."""
        if not self.id:
            raise ValueError("Test suite ID cannot be empty")
        if not self.name:
            raise ValueError("Test suite name cannot be empty")
        if not 0 <= self.coverage_percentage <= 100:
            raise ValueError("Coverage percentage must be between 0 and 100")
        if self.test_count < 0:
            raise ValueError("Test count cannot be negative")
        if self.failure_count < 0:
            raise ValueError("Failure count cannot be negative")
        if self.flaky_count < 0:
            raise ValueError("Flaky count cannot be negative")
        if self.failure_count > self.test_count:
            raise ValueError("Failure count cannot exceed test count")
        if self.flaky_count > self.test_count:
            raise ValueError("Flaky count cannot exceed test count")

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.test_count == 0:
            return 0.0
        return ((self.test_count - self.failure_count) / self.test_count) * 100

    @property
    def is_healthy(self) -> bool:
        """Check if test suite is healthy."""
        return self.status == "passing" and self.coverage_percentage >= 80.0 and self.flaky_count == 0

    def update_status(self) -> None:
        """Update status based on current metrics."""
        if self.flaky_count > 0:
            self.status = "flaky"
        elif self.failure_count > 0:
            self.status = "failing"
        elif self.coverage_percentage >= 80.0:
            self.status = "passing"
        else:
            self.status = "failing"  # Low coverage is considered failing
