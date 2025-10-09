"""
Quality Violation model for tracking code quality issues.
"""

from dataclasses import dataclass, field
from typing import Literal
import uuid


@dataclass
class QualityViolation:
    """Represents a quality rule violation."""

    rule_code: str
    severity: Literal["error", "warning", "info"]
    line_number: int
    column_number: int
    message: str
    file_path: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def __post_init__(self) -> None:
        """Validate quality violation data."""
        if not self.rule_code:
            msg = "Rule code cannot be empty"
            raise ValueError(msg)
        if not self.message:
            msg = "Message cannot be empty"
            raise ValueError(msg)
        if not self.file_path:
            msg = "File path cannot be empty"
            raise ValueError(msg)
        if self.line_number < 1:
            msg = "Line number must be positive"
            raise ValueError(msg)
        if self.column_number < 1:
            msg = "Column number must be positive"
            raise ValueError(msg)
        if self.severity not in ["error", "warning", "info"]:
            msg = "Severity must be error, warning, or info"
            raise ValueError(msg)

    @property
    def is_blocking(self) -> bool:
        """Check if violation blocks deployment."""
        return self.severity == "error"

    @property
    def priority_score(self) -> int:
        """Calculate priority score for fixing."""
        severity_scores = {"error": 3, "warning": 2, "info": 1}
        return severity_scores[self.severity]

    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "rule_code": self.rule_code,
            "severity": self.severity,
            "line_number": self.line_number,
            "column_number": self.column_number,
            "message": self.message,
            "file_path": self.file_path,
        }
