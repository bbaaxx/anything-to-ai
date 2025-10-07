"""
Test Quality Models

Data models for test suites, quality reports, and coverage data.
"""

from .test_suite import TestSuite
from .quality_report import QualityReport
from .quality_violation import QualityViolation
from .test_result import TestResult
from .coverage_data import CoverageData

__all__ = [
    "CoverageData",
    "QualityReport",
    "QualityViolation",
    "TestResult",
    "TestSuite",
]
