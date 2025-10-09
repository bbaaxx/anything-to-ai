"""
API endpoints for quality reports management.
"""

from datetime import datetime
from pathlib import Path

from anyfile_to_ai.test_quality.services.quality_check_service import QualityCheckService
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anyfile_to_ai.test_quality.models.quality_report import QualityReport


class QualityReportsAPI:
    """API endpoints for quality reports management."""

    def __init__(self, project_root: Path):
        """Initialize the quality reports API.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.service = QualityCheckService(project_root)
        self.reports: dict[str, QualityReport] = {}

    async def check_quality(
        self,
        module_path: str,
        include_complexity: bool = True,
        include_maintainability: bool = True,
    ) -> dict:
        """Check quality of a specific module.

        Args:
            module_path: Path to the module to check
            include_complexity: Include complexity analysis
            include_maintainability: Include maintainability analysis

        Returns:
            API response with quality report
        """
        try:
            report = await self.service.check_quality(
                module_path,
                include_complexity,
                include_maintainability,
            )
            self.reports[report.id] = report

            # Prepare violations data
            violations_data = []
            for violation in report.violations:
                violations_data.append(
                    {
                        "id": violation.id,
                        "rule_code": violation.rule_code,
                        "severity": violation.severity,
                        "message": violation.message,
                        "file_path": violation.file_path,
                        "line_number": violation.line_number,
                        "column_number": violation.column_number,
                        "end_line_number": violation.end_line_number,
                        "end_column_number": violation.end_column_number,
                        "fix_available": violation.fix_available,
                        "priority": violation.priority,
                    },
                )

            return {
                "success": True,
                "data": {
                    "id": report.id,
                    "module_name": report.module_name,
                    "violation_count": report.violation_count,
                    "complexity_score": report.complexity_score,
                    "maintainability_index": report.maintainability_index,
                    "quality_grade": report.quality_grade,
                    "is_acceptable": report.is_acceptable,
                    "last_check": report.last_check.isoformat() if report.last_check else None,
                    "violations": violations_data,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "QUALITY_CHECK_FAILED",
            }

    async def get_report(self, report_id: str) -> dict:
        """Get a quality report by ID.

        Args:
            report_id: ID of the quality report

        Returns:
            API response with report data
        """
        if report_id not in self.reports:
            return {
                "success": False,
                "error": f"Quality report {report_id} not found",
                "error_code": "REPORT_NOT_FOUND",
            }

        report = self.reports[report_id]

        # Prepare violations data
        violations_data = []
        for violation in report.violations:
            violations_data.append(
                {
                    "id": violation.id,
                    "rule_code": violation.rule_code,
                    "severity": violation.severity,
                    "message": violation.message,
                    "file_path": violation.file_path,
                    "line_number": violation.line_number,
                    "column_number": violation.column_number,
                    "end_line_number": violation.end_line_number,
                    "end_column_number": violation.end_column_number,
                    "fix_available": violation.fix_available,
                    "priority": violation.priority,
                },
            )

        return {
            "success": True,
            "data": {
                "id": report.id,
                "module_name": report.module_name,
                "violation_count": report.violation_count,
                "complexity_score": report.complexity_score,
                "maintainability_index": report.maintainability_index,
                "quality_grade": report.quality_grade,
                "is_acceptable": report.is_acceptable,
                "last_check": report.last_check.isoformat() if report.last_check else None,
                "violations": violations_data,
            },
        }

    async def list_reports(self) -> dict:
        """List all quality reports.

        Returns:
            API response with list of reports
        """
        reports_data = []

        for report in self.reports.values():
            reports_data.append(
                {
                    "id": report.id,
                    "module_name": report.module_name,
                    "violation_count": report.violation_count,
                    "complexity_score": report.complexity_score,
                    "maintainability_index": report.maintainability_index,
                    "quality_grade": report.quality_grade,
                    "is_acceptable": report.is_acceptable,
                    "last_check": report.last_check.isoformat() if report.last_check else None,
                },
            )

        return {
            "success": True,
            "data": {
                "reports": reports_data,
                "total_count": len(reports_data),
            },
        }

    async def fix_quality_issues(
        self,
        module_path: str,
        auto_fix: bool = True,
        rule_selectors: list[str] | None = None,
    ) -> dict:
        """Attempt to fix quality issues automatically.

        Args:
            module_path: Path to module to fix
            auto_fix: Enable automatic fixing
            rule_selectors: Specific rules to fix (None for all)

        Returns:
            API response with fix results
        """
        try:
            unfixed_violations = await self.service.fix_quality_issues(
                module_path,
                auto_fix,
                rule_selectors,
            )

            # Prepare unfixed violations data
            unfixed_data = []
            for violation in unfixed_violations:
                unfixed_data.append(
                    {
                        "id": violation.id,
                        "rule_code": violation.rule_code,
                        "severity": violation.severity,
                        "message": violation.message,
                        "file_path": violation.file_path,
                        "line_number": violation.line_number,
                        "column_number": violation.column_number,
                        "fix_available": violation.fix_available,
                        "priority": violation.priority,
                    },
                )

            return {
                "success": True,
                "data": {
                    "module_path": module_path,
                    "auto_fix_enabled": auto_fix,
                    "rule_selectors": rule_selectors,
                    "unfixed_violations": unfixed_data,
                    "total_unfixed": len(unfixed_violations),
                    "fix_timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "FIX_QUALITY_FAILED",
            }

    async def get_quality_trend(
        self,
        module_path: str,
        days: int = 30,
    ) -> dict:
        """Get quality trend over time.

        Args:
            module_path: Path to module
            days: Number of days to look back

        Returns:
            API response with trend data
        """
        try:
            trend_data = self.service.get_quality_trend(module_path, days)

            return {
                "success": True,
                "data": {
                    "module_path": module_path,
                    "days_analyzed": days,
                    "trend": trend_data,
                    "generated_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "TREND_ANALYSIS_FAILED",
            }

    async def get_violations_by_severity(self, report_id: str) -> dict:
        """Get violations grouped by severity.

        Args:
            report_id: ID of the quality report

        Returns:
            API response with violations grouped by severity
        """
        if report_id not in self.reports:
            return {
                "success": False,
                "error": f"Quality report {report_id} not found",
                "error_code": "REPORT_NOT_FOUND",
            }

        try:
            report = self.reports[report_id]

            # Group violations by severity
            violations_by_severity = {
                "low": [],
                "medium": [],
                "high": [],
            }

            for violation in report.violations:
                violation_data = {
                    "id": violation.id,
                    "rule_code": violation.rule_code,
                    "message": violation.message,
                    "file_path": violation.file_path,
                    "line_number": violation.line_number,
                    "column_number": violation.column_number,
                    "fix_available": violation.fix_available,
                    "priority": violation.priority,
                }
                violations_by_severity[violation.severity].append(violation_data)

            return {
                "success": True,
                "data": {
                    "report_id": report_id,
                    "module_name": report.module_name,
                    "violations_by_severity": violations_by_severity,
                    "severity_counts": {
                        "low": len(violations_by_severity["low"]),
                        "medium": len(violations_by_severity["medium"]),
                        "high": len(violations_by_severity["high"]),
                    },
                    "total_violations": report.violation_count,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SEVERITY_GROUPING_FAILED",
            }

    async def get_violations_by_priority(self, report_id: str) -> dict:
        """Get violations grouped by priority.

        Args:
            report_id: ID of the quality report

        Returns:
            API response with violations grouped by priority
        """
        if report_id not in self.reports:
            return {
                "success": False,
                "error": f"Quality report {report_id} not found",
                "error_code": "REPORT_NOT_FOUND",
            }

        try:
            report = self.reports[report_id]

            # Group violations by priority
            violations_by_priority = {
                "low": [],
                "medium": [],
                "high": [],
            }

            for violation in report.violations:
                violation_data = {
                    "id": violation.id,
                    "rule_code": violation.rule_code,
                    "severity": violation.severity,
                    "message": violation.message,
                    "file_path": violation.file_path,
                    "line_number": violation.line_number,
                    "column_number": violation.column_number,
                    "fix_available": violation.fix_available,
                }
                violations_by_priority[violation.priority].append(violation_data)

            return {
                "success": True,
                "data": {
                    "report_id": report_id,
                    "module_name": report.module_name,
                    "violations_by_priority": violations_by_priority,
                    "priority_counts": {
                        "low": len(violations_by_priority["low"]),
                        "medium": len(violations_by_priority["medium"]),
                        "high": len(violations_by_priority["high"]),
                    },
                    "total_violations": report.violation_count,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "PRIORITY_GROUPING_FAILED",
            }

    def save_report(self, report_id: str, file_path: str) -> dict:
        """Save a quality report to file.

        Args:
            report_id: ID of the quality report to save
            file_path: Path to save file

        Returns:
            API response with save result
        """
        if report_id not in self.reports:
            return {
                "success": False,
                "error": f"Quality report {report_id} not found",
                "error_code": "REPORT_NOT_FOUND",
            }

        try:
            report = self.reports[report_id]
            self.service.save_quality_report(report, Path(file_path))

            return {
                "success": True,
                "data": {
                    "report_id": report_id,
                    "saved_to": file_path,
                    "saved_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SAVE_REPORT_FAILED",
            }

    def load_report(self, file_path: str) -> dict:
        """Load a quality report from file.

        Args:
            file_path: Path to load file from

        Returns:
            API response with loaded report
        """
        try:
            report = self.service.load_quality_report(Path(file_path))
            self.reports[report.id] = report

            # Prepare violations data
            violations_data = []
            for violation in report.violations:
                violations_data.append(
                    {
                        "id": violation.id,
                        "rule_code": violation.rule_code,
                        "severity": violation.severity,
                        "message": violation.message,
                        "file_path": violation.file_path,
                        "line_number": violation.line_number,
                        "column_number": violation.column_number,
                        "end_line_number": violation.end_line_number,
                        "end_column_number": violation.end_column_number,
                        "fix_available": violation.fix_available,
                        "priority": violation.priority,
                    },
                )

            return {
                "success": True,
                "data": {
                    "id": report.id,
                    "module_name": report.module_name,
                    "violation_count": report.violation_count,
                    "complexity_score": report.complexity_score,
                    "maintainability_index": report.maintainability_index,
                    "quality_grade": report.quality_grade,
                    "is_acceptable": report.is_acceptable,
                    "last_check": report.last_check.isoformat() if report.last_check else None,
                    "violations": violations_data,
                    "loaded_from": file_path,
                    "loaded_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "LOAD_REPORT_FAILED",
            }
