"""
Quality Check Service for code quality validation.
"""

import json
import subprocess
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from anyfile_to_ai.test_quality.models.quality_report import QualityReport
from anyfile_to_ai.test_quality.models.quality_violation import QualityViolation


class QualityCheckService:
    """Service for checking and enforcing code quality."""

    def __init__(self, project_root: Path):
        """Initialize the quality check service.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.quality_cache: dict[str, QualityReport] = {}

    async def check_quality(
        self,
        module_path: str,
        include_complexity: bool = True,
        include_maintainability: bool = True,
    ) -> QualityReport:
        """Check quality of a specific module.

        Args:
            module_path: Path to the module to check
            include_complexity: Include complexity analysis
            include_maintainability: Include maintainability analysis

        Returns:
            QualityReport with analysis results
        """
        report_id = f"quality_{module_path.replace('/', '_')}_{int(datetime.now().timestamp())}"

        violations = []
        complexity_score = 0.0
        maintainability_index = 100.0

        # Run ruff for linting violations
        ruff_violations = await self._run_ruff_check(module_path)
        violations.extend(ruff_violations)

        # Run complexity analysis if requested
        if include_complexity:
            complexity_score = await self._analyze_complexity(module_path)

        # Run maintainability analysis if requested
        if include_maintainability:
            maintainability_index = await self._analyze_maintainability(module_path)

        # Create quality report
        report = QualityReport(
            id=report_id,
            module_name=module_path,
            violation_count=len(violations),
            complexity_score=complexity_score,
            maintainability_index=maintainability_index,
            last_check=datetime.now(),
            violations=violations,
        )

        # Cache the report
        self.quality_cache[module_path] = report

        return report

    async def _run_ruff_check(self, module_path: str) -> list[QualityViolation]:
        """Run ruff linter and parse violations.

        Args:
            module_path: Path to module to check

        Returns:
            List of QualityViolation instances
        """
        violations = []

        try:
            # Run ruff with JSON output
            cmd = ["ruff", "check", module_path, "--format=json"]
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.stdout:
                try:
                    ruff_data = json.loads(result.stdout)
                    for violation_data in ruff_data:
                        violation = QualityViolation(
                            id=f"ruff_{module_path}_{violation_data.get('row', 0)}_{violation_data.get('col', 0)}_{int(datetime.now().timestamp())}",
                            rule_code=violation_data.get("code", "UNKNOWN"),
                            severity=self._map_ruff_severity(violation_data.get("fix", {}).get("availability")),
                            message=violation_data.get("message", ""),
                            file_path=violation_data.get("filename", module_path),
                            line_number=violation_data.get("row", 0),
                            column_number=violation_data.get("col", 0),
                            end_line_number=violation_data.get("end_row"),
                            end_column_number=violation_data.get("end_col"),
                            fix_available=violation_data.get("fix", {}).get("availability") is not None,
                        )
                        violations.append(violation)

                except json.JSONDecodeError:
                    # Invalid JSON output
                    pass

        except subprocess.TimeoutExpired:
            # Create timeout violation
            timeout_violation = QualityViolation(
                id=f"timeout_{module_path}_{int(datetime.now().timestamp())}",
                rule_code="TIMEOUT",
                severity="medium",
                message="Quality check timed out",
                file_path=module_path,
                line_number=0,
                column_number=0,
            )
            violations.append(timeout_violation)

        except Exception as e:
            # Create error violation
            error_violation = QualityViolation(
                id=f"error_{module_path}_{int(datetime.now().timestamp())}",
                rule_code="ERROR",
                severity="high",
                message=f"Quality check failed: {e!s}",
                file_path=module_path,
                line_number=0,
                column_number=0,
            )
            violations.append(error_violation)

        return violations

    def _map_ruff_severity(self, fix_availability: str | None) -> str:
        """Map ruff fix availability to severity.

        Args:
            fix_availability: Ruff fix availability status

        Returns:
            Severity level (low, medium, high)
        """
        if fix_availability is not None:
            return "low"  # Auto-fixable issues are low severity
        return "medium"  # Manual fixes are medium severity

    async def _analyze_complexity(self, module_path: str) -> float:
        """Analyze cyclomatic complexity of a module.

        Args:
            module_path: Path to module to analyze

        Returns:
            Complexity score (0-20, higher is more complex)
        """
        try:
            # Use radon for complexity analysis if available
            cmd = ["radon", "cc", module_path, "--json"]
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                try:
                    radon_data = json.loads(result.stdout)
                    max_complexity = 0.0

                    for file_data in radon_data.values():
                        for item in file_data:
                            complexity = item.get("complexity", 0)
                            max_complexity = max(max_complexity, complexity)

                    return min(max_complexity, 20.0)  # Cap at 20

                except json.JSONDecodeError:
                    pass

            # Fallback: use ruff's complexity rules
            cmd = ["ruff", "check", module_path, "--select=C901"]
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Count complexity violations as a proxy
            complexity_violations = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            return min(complexity_violations * 2.0, 20.0)  # Scale to 0-20

        except Exception:
            # Default to moderate complexity if analysis fails
            return 10.0

    async def _analyze_maintainability(self, module_path: str) -> float:
        """Analyze maintainability index of a module.

        Args:
            module_path: Path to module to analyze

        Returns:
            Maintainability index (0-100, higher is more maintainable)
        """
        try:
            # Use radon for maintainability analysis if available
            cmd = ["radon", "mi", module_path, "--json"]
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.stdout:
                try:
                    radon_data = json.loads(result.stdout)
                    maintainability_scores = []

                    for file_data in radon_data.values():
                        for item in file_data:
                            mi = item.get("mi", 0)
                            maintainability_scores.append(mi)

                    if maintainability_scores:
                        return sum(maintainability_scores) / len(maintainability_scores)

                except json.JSONDecodeError:
                    pass

            # Fallback: calculate based on violations and complexity
            quality_report = await self.check_quality(module_path, include_complexity=True, include_maintainability=False)

            # Base score of 100, subtract penalties
            score = 100.0

            # Penalty for violations
            score -= len(quality_report.violations) * 2

            # Penalty for complexity
            score -= quality_report.complexity_score * 3

            return max(0.0, min(score, 100.0))

        except Exception:
            # Default to moderate maintainability if analysis fails
            return 70.0

    async def fix_quality_issues(
        self,
        module_path: str,
        auto_fix: bool = True,
        rule_selectors: list[str] | None = None,
    ) -> list[QualityViolation]:
        """Attempt to fix quality issues automatically.

        Args:
            module_path: Path to module to fix
            auto_fix: Enable automatic fixing
            rule_selectors: Specific rules to fix (None for all)

        Returns:
            List of violations that could not be fixed
        """
        unfixed_violations = []

        if not auto_fix:
            # Get current violations and return all as unfixed
            report = await self.check_quality(module_path)
            return report.violations

        try:
            # Run ruff with --fix option
            cmd = ["ruff", "check", module_path, "--fix"]
            if rule_selectors:
                cmd.extend(["--select", ",".join(rule_selectors)])

            subprocess.run(
                cmd,
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Re-check to see what violations remain
            report = await self.check_quality(module_path)
            unfixed_violations = report.violations

        except Exception as e:
            # Create error violation for the fix failure
            error_violation = QualityViolation(
                id=f"fix_error_{module_path}_{int(datetime.now().timestamp())}",
                rule_code="FIX_ERROR",
                severity="high",
                message=f"Auto-fix failed: {e!s}",
                file_path=module_path,
                line_number=0,
                column_number=0,
            )
            unfixed_violations.append(error_violation)

        return unfixed_violations

    def get_quality_trend(
        self,
        module_path: str,
        days: int = 30,
    ) -> dict[str, list[float]]:
        """Get quality trend over time.

        Args:
            module_path: Path to module
            days: Number of days to look back

        Returns:
            Dictionary with trend data
        """
        # This would typically load historical data from a database
        # For now, return mock trend data
        import random

        trend_points = max(1, days // 7)  # Weekly points
        return {
            "maintainability": [random.uniform(60, 90) for _ in range(trend_points)],
            "complexity": [random.uniform(5, 15) for _ in range(trend_points)],
            "violations": [random.randint(0, 20) for _ in range(trend_points)],
        }

    def save_quality_report(self, report: QualityReport, file_path: Path) -> None:
        """Save quality report to file.

        Args:
            report: Quality report to save
            file_path: Path to save file
        """
        report_data = asdict(report)
        # Convert datetime objects to strings for JSON serialization
        if report_data.get("last_check"):
            report_data["last_check"] = report_data["last_check"].isoformat()

        # Convert violations to dicts
        if report_data.get("violations"):
            report_data["violations"] = [asdict(v) for v in report_data["violations"]]

        with open(file_path, "w") as f:
            json.dump(report_data, f, indent=2)

    def load_quality_report(self, file_path: Path) -> QualityReport:
        """Load quality report from file.

        Args:
            file_path: Path to load file from

        Returns:
            Loaded QualityReport instance
        """
        with open(file_path) as f:
            report_data = json.load(f)

        # Convert string back to datetime
        if report_data.get("last_check"):
            report_data["last_check"] = datetime.fromisoformat(report_data["last_check"])

        # Convert violations back to QualityViolation objects
        if report_data.get("violations"):
            violations = []
            for violation_data in report_data["violations"]:
                violations.append(QualityViolation(**violation_data))
            report_data["violations"] = violations

        return QualityReport(**report_data)
