"""
Coverage Data model for test coverage tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CoverageData:
    """Represents coverage data for a module."""

    id: str
    module_name: str
    line_coverage: float = field(default=0.0)
    branch_coverage: float = field(default=0.0)
    function_coverage: float = field(default=0.0)
    statement_coverage: float = field(default=0.0)
    total_lines: int = field(default=0)
    covered_lines: int = field(default=0)
    total_branches: int = field(default=0)
    covered_branches: int = field(default=0)
    total_functions: int = field(default=0)
    covered_functions: int = field(default=0)
    total_statements: int = field(default=0)
    covered_statements: int = field(default=0)
    last_measured: datetime | None = None
    uncovered_files: list[str] = field(default_factory=list)
    partially_covered_files: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate coverage data."""
        if not self.id:
            raise ValueError("Coverage data ID cannot be empty")
        if not self.module_name:
            raise ValueError("Module name cannot be empty")
        if not 0 <= self.line_coverage <= 100:
            raise ValueError("Line coverage must be between 0 and 100")
        if not 0 <= self.branch_coverage <= 100:
            raise ValueError("Branch coverage must be between 0 and 100")
        if not 0 <= self.function_coverage <= 100:
            raise ValueError("Function coverage must be between 0 and 100")
        if not 0 <= self.statement_coverage <= 100:
            raise ValueError("Statement coverage must be between 0 and 100")
        if any(x < 0 for x in [self.total_lines, self.covered_lines, self.total_branches, self.covered_branches, self.total_functions, self.covered_functions, self.total_statements, self.covered_statements]):
            raise ValueError("Coverage counts cannot be negative")
        if self.covered_lines > self.total_lines:
            raise ValueError("Covered lines cannot exceed total lines")
        if self.covered_branches > self.total_branches:
            raise ValueError("Covered branches cannot exceed total branches")
        if self.covered_functions > self.total_functions:
            raise ValueError("Covered functions cannot exceed total functions")
        if self.covered_statements > self.total_statements:
            raise ValueError("Covered statements cannot exceed total statements")

    @property
    def overall_coverage(self) -> float:
        """Calculate overall coverage as weighted average."""
        weights = {
            "line": 0.4,
            "branch": 0.3,
            "function": 0.2,
            "statement": 0.1,
        }
        return self.line_coverage * weights["line"] + self.branch_coverage * weights["branch"] + self.function_coverage * weights["function"] + self.statement_coverage * weights["statement"]

    @property
    def meets_target(self, target: float = 80.0) -> bool:
        """Check if coverage meets target percentage."""
        return self.overall_coverage >= target

    @property
    def coverage_grade(self) -> str:
        """Calculate coverage grade."""
        coverage = self.overall_coverage
        if coverage >= 90:
            return "A"
        if coverage >= 80:
            return "B"
        if coverage >= 70:
            return "C"
        if coverage >= 60:
            return "D"
        return "F"

    def add_uncovered_file(self, file_path: str) -> None:
        """Add an uncovered file."""
        if file_path not in self.uncovered_files:
            self.uncovered_files.append(file_path)

    def add_partially_covered_file(self, file_path: str, coverage_percent: float) -> None:
        """Add a partially covered file with its coverage percentage."""
        if not 0 <= coverage_percent <= 100:
            raise ValueError("Coverage percentage must be between 0 and 100")
        self.partially_covered_files[file_path] = coverage_percent

    def get_coverage_summary(self) -> dict[str, float]:
        """Get summary of all coverage metrics."""
        return {
            "overall": self.overall_coverage,
            "line": self.line_coverage,
            "branch": self.branch_coverage,
            "function": self.function_coverage,
            "statement": self.statement_coverage,
        }
