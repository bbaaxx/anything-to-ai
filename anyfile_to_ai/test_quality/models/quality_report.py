"""
Quality Report model for code quality tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime

from .quality_violation import QualityViolation


@dataclass
class QualityReport:
    """Represents a quality report for a module."""

    id: str
    module_name: str
    violation_count: int = field(default=0)
    complexity_score: float = field(default=0.0)
    maintainability_index: float = field(default=0.0)
    last_check: datetime | None = None
    violations: list[QualityViolation] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate quality report data."""
        if not self.id:
            raise ValueError("Quality report ID cannot be empty")
        if not self.module_name:
            raise ValueError("Module name cannot be empty")
        if self.violation_count < 0:
            raise ValueError("Violation count cannot be negative")
        if not 0 <= self.complexity_score <= 20:  # McCain complexity typically 0-20
            raise ValueError("Complexity score must be between 0 and 20")
        if not 0 <= self.maintainability_index <= 100:
            raise ValueError("Maintainability index must be between 0 and 100")
        if len(self.violations) != self.violation_count:
            self.violation_count = len(self.violations)

    @property
    def quality_grade(self) -> str:
        """Calculate quality grade based on metrics."""
        if self.maintainability_index >= 85 and self.complexity_score <= 5:
            return "A"
        if self.maintainability_index >= 70 and self.complexity_score <= 10:
            return "B"
        if self.maintainability_index >= 50 and self.complexity_score <= 15:
            return "C"
        return "D"

    @property
    def is_acceptable(self) -> bool:
        """Check if quality meets minimum standards."""
        return self.maintainability_index >= 70.0 and self.complexity_score <= 10.0

    def add_violation(self, violation: QualityViolation) -> None:
        """Add a quality violation."""
        self.violations.append(violation)
        self.violation_count = len(self.violations)

    def remove_violation(self, violation_id: str) -> bool:
        """Remove a violation by ID."""
        for i, violation in enumerate(self.violations):
            if violation.id == violation_id:
                del self.violations[i]
                self.violation_count = len(self.violations)
                return True
        return False
