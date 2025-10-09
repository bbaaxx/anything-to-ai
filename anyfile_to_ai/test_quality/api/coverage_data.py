"""
API endpoints for coverage data management.
"""

from datetime import datetime
from pathlib import Path

from anyfile_to_ai.test_quality.services.coverage_service import CoverageService
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from anyfile_to_ai.test_quality.models.coverage_data import CoverageData


class CoverageDataAPI:
    """API endpoints for coverage data management."""

    def __init__(self, project_root: Path):
        """Initialize the coverage data API.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.service = CoverageService(project_root)
        self.coverage_data: dict[str, CoverageData] = {}

    async def measure_coverage(
        self,
        module_path: str,
        test_paths: list[str] | None = None,
        include_branch: bool = True,
        include_function: bool = True,
    ) -> dict:
        """Measure test coverage for a module.

        Args:
            module_path: Path to the module to measure
            test_paths: List of test paths to run (None for auto-discovery)
            include_branch: Include branch coverage
            include_function: Include function coverage

        Returns:
            API response with coverage data
        """
        try:
            coverage = await self.service.measure_coverage(
                module_path,
                test_paths,
                include_branch,
                include_function,
            )
            self.coverage_data[coverage.id] = coverage

            return {
                "success": True,
                "data": {
                    "id": coverage.id,
                    "module_name": coverage.module_name,
                    "line_coverage": coverage.line_coverage,
                    "branch_coverage": coverage.branch_coverage,
                    "function_coverage": coverage.function_coverage,
                    "statement_coverage": coverage.statement_coverage,
                    "overall_coverage": coverage.overall_coverage,
                    "coverage_grade": coverage.coverage_grade,
                    "meets_target": coverage.meets_target(),
                    "total_lines": coverage.total_lines,
                    "covered_lines": coverage.covered_lines,
                    "total_branches": coverage.total_branches,
                    "covered_branches": coverage.covered_branches,
                    "total_functions": coverage.total_functions,
                    "covered_functions": coverage.covered_functions,
                    "total_statements": coverage.total_statements,
                    "covered_statements": coverage.covered_statements,
                    "last_measured": coverage.last_measured.isoformat() if coverage.last_measured else None,
                    "uncovered_files": coverage.uncovered_files,
                    "partially_covered_files": coverage.partially_covered_files,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "COVERAGE_MEASUREMENT_FAILED",
            }

    async def get_coverage(self, coverage_id: str) -> dict:
        """Get coverage data by ID.

        Args:
            coverage_id: ID of the coverage data

        Returns:
            API response with coverage data
        """
        if coverage_id not in self.coverage_data:
            return {
                "success": False,
                "error": f"Coverage data {coverage_id} not found",
                "error_code": "COVERAGE_NOT_FOUND",
            }

        coverage = self.coverage_data[coverage_id]

        return {
            "success": True,
            "data": {
                "id": coverage.id,
                "module_name": coverage.module_name,
                "line_coverage": coverage.line_coverage,
                "branch_coverage": coverage.branch_coverage,
                "function_coverage": coverage.function_coverage,
                "statement_coverage": coverage.statement_coverage,
                "overall_coverage": coverage.overall_coverage,
                "coverage_grade": coverage.coverage_grade,
                "meets_target": coverage.meets_target(),
                "total_lines": coverage.total_lines,
                "covered_lines": coverage.covered_lines,
                "total_branches": coverage.total_branches,
                "covered_branches": coverage.covered_branches,
                "total_functions": coverage.total_functions,
                "covered_functions": coverage.covered_functions,
                "total_statements": coverage.total_statements,
                "covered_statements": coverage.covered_statements,
                "last_measured": coverage.last_measured.isoformat() if coverage.last_measured else None,
                "uncovered_files": coverage.uncovered_files,
                "partially_covered_files": coverage.partially_covered_files,
            },
        }

    async def list_coverage_data(self) -> dict:
        """List all coverage data.

        Returns:
            API response with list of coverage data
        """
        coverage_list = []

        for coverage in self.coverage_data.values():
            coverage_list.append(
                {
                    "id": coverage.id,
                    "module_name": coverage.module_name,
                    "overall_coverage": coverage.overall_coverage,
                    "coverage_grade": coverage.coverage_grade,
                    "meets_target": coverage.meets_target(),
                    "last_measured": coverage.last_measured.isoformat() if coverage.last_measured else None,
                },
            )

        return {
            "success": True,
            "data": {
                "coverage_data": coverage_list,
                "total_count": len(coverage_list),
            },
        }

    async def get_coverage_summary(self, module_paths: list[str]) -> dict:
        """Get coverage summary for multiple modules.

        Args:
            module_paths: List of module paths to summarize

        Returns:
            API response with summary statistics
        """
        try:
            summary = self.service.get_coverage_summary(module_paths)

            return {
                "success": True,
                "data": {
                    "summary": summary,
                    "generated_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "COVERAGE_SUMMARY_FAILED",
            }

    async def get_coverage_trend(
        self,
        module_path: str,
        days: int = 30,
    ) -> dict:
        """Get coverage trend over time.

        Args:
            module_path: Path to module
            days: Number of days to look back

        Returns:
            API response with trend data
        """
        try:
            trend_data = self.service.get_coverage_trend(module_path, days)

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
                "error_code": "COVERAGE_TREND_FAILED",
            }

    async def identify_uncovered_critical_paths(
        self,
        coverage_id: str,
        critical_patterns: list[str] | None = None,
    ) -> dict:
        """Identify critical paths that are not covered.

        Args:
            coverage_id: ID of the coverage data
            critical_patterns: List of patterns for critical files

        Returns:
            API response with uncovered critical paths
        """
        if coverage_id not in self.coverage_data:
            return {
                "success": False,
                "error": f"Coverage data {coverage_id} not found",
                "error_code": "COVERAGE_NOT_FOUND",
            }

        try:
            coverage = self.coverage_data[coverage_id]
            uncovered_critical = self.service.identify_uncovered_critical_paths(
                coverage,
                critical_patterns,
            )

            return {
                "success": True,
                "data": {
                    "coverage_id": coverage_id,
                    "module_name": coverage.module_name,
                    "critical_patterns": critical_patterns or [],
                    "uncovered_critical_paths": uncovered_critical,
                    "total_uncovered_critical": len(uncovered_critical),
                    "analyzed_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "CRITICAL_PATHS_ANALYSIS_FAILED",
            }

    async def generate_coverage_report(
        self,
        coverage_id: str,
        format: str = "text",
    ) -> dict:
        """Generate a coverage report.

        Args:
            coverage_id: ID of the coverage data
            format: Report format ("text", "json", "markdown")

        Returns:
            API response with formatted report
        """
        if coverage_id not in self.coverage_data:
            return {
                "success": False,
                "error": f"Coverage data {coverage_id} not found",
                "error_code": "COVERAGE_NOT_FOUND",
            }

        try:
            coverage = self.coverage_data[coverage_id]
            report = self.service.generate_coverage_report(coverage, format)

            return {
                "success": True,
                "data": {
                    "coverage_id": coverage_id,
                    "module_name": coverage.module_name,
                    "format": format,
                    "report": report,
                    "generated_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "REPORT_GENERATION_FAILED",
            }

    async def get_modules_below_target(self, target: float = 80.0) -> dict:
        """Get modules that are below coverage target.

        Args:
            target: Coverage target percentage

        Returns:
            API response with modules below target
        """
        try:
            modules_below_target = []

            for coverage in self.coverage_data.values():
                if not coverage.meets_target(target):
                    modules_below_target.append(
                        {
                            "id": coverage.id,
                            "module_name": coverage.module_name,
                            "overall_coverage": coverage.overall_coverage,
                            "coverage_grade": coverage.coverage_grade,
                            "gap": target - coverage.overall_coverage,
                            "last_measured": coverage.last_measured.isoformat() if coverage.last_measured else None,
                        },
                    )

            # Sort by coverage gap (largest gap first)
            modules_below_target.sort(key=lambda x: x["gap"], reverse=True)

            return {
                "success": True,
                "data": {
                    "target_percentage": target,
                    "modules_below_target": modules_below_target,
                    "total_modules_below_target": len(modules_below_target),
                    "analyzed_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "TARGET_ANALYSIS_FAILED",
            }

    async def get_coverage_metrics(self) -> dict:
        """Get overall coverage metrics across all modules.

        Returns:
            API response with overall metrics
        """
        try:
            if not self.coverage_data:
                return {
                    "success": True,
                    "data": {
                        "total_modules": 0,
                        "average_coverage": 0.0,
                        "modules_at_target": 0,
                        "modules_below_target": 0,
                        "highest_coverage": 0.0,
                        "lowest_coverage": 0.0,
                        "grade_distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
                    },
                }

            coverages = list(self.coverage_data.values())
            total_modules = len(coverages)

            # Calculate metrics
            overall_coverages = [c.overall_coverage for c in coverages]
            average_coverage = sum(overall_coverages) / total_modules
            modules_at_target = sum(1 for c in coverages if c.meets_target())
            modules_below_target = total_modules - modules_at_target
            highest_coverage = max(overall_coverages)
            lowest_coverage = min(overall_coverages)

            # Grade distribution
            grade_distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
            for coverage in coverages:
                grade_distribution[coverage.coverage_grade] += 1

            return {
                "success": True,
                "data": {
                    "total_modules": total_modules,
                    "average_coverage": average_coverage,
                    "modules_at_target": modules_at_target,
                    "modules_below_target": modules_below_target,
                    "highest_coverage": highest_coverage,
                    "lowest_coverage": lowest_coverage,
                    "grade_distribution": grade_distribution,
                    "analyzed_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "METRICS_CALCULATION_FAILED",
            }

    def save_coverage_data(self, coverage_id: str, file_path: str) -> dict:
        """Save coverage data to file.

        Args:
            coverage_id: ID of the coverage data to save
            file_path: Path to save file

        Returns:
            API response with save result
        """
        if coverage_id not in self.coverage_data:
            return {
                "success": False,
                "error": f"Coverage data {coverage_id} not found",
                "error_code": "COVERAGE_NOT_FOUND",
            }

        try:
            coverage = self.coverage_data[coverage_id]
            self.service.save_coverage_data(coverage, Path(file_path))

            return {
                "success": True,
                "data": {
                    "coverage_id": coverage_id,
                    "saved_to": file_path,
                    "saved_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SAVE_COVERAGE_FAILED",
            }

    def load_coverage_data(self, file_path: str) -> dict:
        """Load coverage data from file.

        Args:
            file_path: Path to load file from

        Returns:
            API response with loaded coverage data
        """
        try:
            coverage = self.service.load_coverage_data(Path(file_path))
            self.coverage_data[coverage.id] = coverage

            return {
                "success": True,
                "data": {
                    "id": coverage.id,
                    "module_name": coverage.module_name,
                    "overall_coverage": coverage.overall_coverage,
                    "coverage_grade": coverage.coverage_grade,
                    "meets_target": coverage.meets_target(),
                    "last_measured": coverage.last_measured.isoformat() if coverage.last_measured else None,
                    "loaded_from": file_path,
                    "loaded_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "LOAD_COVERAGE_FAILED",
            }
