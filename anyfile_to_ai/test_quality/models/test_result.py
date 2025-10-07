"""
Test Result model for individual test outcomes.
"""

from dataclasses import dataclass, field
from typing import Literal
import uuid


@dataclass
class TestResult:
    """Represents the result of a single test execution."""

    test_name: str
    status: Literal["passed", "failed", "skipped", "error"]
    execution_time: float
    file_path: str
    line_number: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    failure_message: str | None = None
    is_flaky: bool = field(default=False)

    def __post_init__(self) -> None:
        """Validate test result data."""
        if not self.test_name:
            raise ValueError("Test name cannot be empty")
        if not self.file_path:
            raise ValueError("File path cannot be empty")
        if self.line_number < 1:
            raise ValueError("Line number must be positive")
        if self.execution_time < 0:
            raise ValueError("Execution time cannot be negative")
        if self.status not in ["passed", "failed", "skipped", "error"]:
            raise ValueError("Status must be passed, failed, skipped, or error")
        if self.status == "passed" and self.failure_message:
            raise ValueError("Passed tests cannot have failure messages")
        if self.status in ["failed", "error"] and not self.failure_message:
            self.failure_message = "Test failed without specific message"

    @property
    def is_successful(self) -> bool:
        """Check if test was successful."""
        return self.status == "passed"

    @property
    def is_problematic(self) -> bool:
        """Check if test has issues (failed, error, or flaky)."""
        return self.status in ["failed", "error"] or self.is_flaky

    @property
    def severity(self) -> Literal["low", "medium", "high"]:
        """Determine severity of test result."""
        if self.status == "error":
            return "high"
        if self.status == "failed" or self.is_flaky:
            return "medium"
        return "low"

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "test_name": self.test_name,
            "status": self.status,
            "execution_time": self.execution_time,
            "failure_message": self.failure_message,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "is_flaky": self.is_flaky,
        }
