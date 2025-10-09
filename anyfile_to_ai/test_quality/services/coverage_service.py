"""
Coverage Service for test coverage measurement and analysis.
"""

import json
import subprocess
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from anyfile_to_ai.test_quality.models.coverage_data import CoverageData


class CoverageService:
    """Service for measuring and analyzing test coverage."""

    def __init__(self, project_root: Path):
        """Initialize the coverage service.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.coverage_cache: dict[str, CoverageData] = {}

    async def measure_coverage(
        self,
        module_path: str,
        test_paths: list[str] | None = None,
        include_branch: bool = True,
        include_function: bool = True,
    ) -> CoverageData:
        """Measure test coverage for a module.

        Args:
            module_path: Path to the module to measure
            test_paths: List of test paths to run (None for auto-discovery)
            include_branch: Include branch coverage
            include_function: Include function coverage

        Returns:
            CoverageData with measurement results
        """
        coverage_id = f"coverage_{module_path.replace('/', '_')}_{int(datetime.now().timestamp())}"

        # Run tests with coverage
        coverage_results = await self._run_coverage_tests(
            module_path,
            test_paths,
            include_branch,
            include_function,
        )

        # Parse coverage results
        coverage_data = await self._parse_coverage_results(
            coverage_id,
            module_path,
            coverage_results,
        )

        # Cache the results
        self.coverage_cache[module_path] = coverage_data

        return coverage_data

    async def _run_coverage_tests(
        self,
        module_path: str,
        test_paths: list[str] | None,
        include_branch: bool,
        include_function: bool,
    ) -> dict:
        """Run tests with coverage measurement.

        Args:
            module_path: Module to measure coverage for
            test_paths: Test paths to run
            include_branch: Include branch coverage
            include_function: Include function coverage

        Returns:
            Coverage results dictionary
        """
        results = {}

        try:
            # Build pytest command with coverage
            cmd = [
                "python3",
                "-m",
                "pytest",
                "--cov=anyfile_to_ai",
                "--cov-report=json:/tmp/coverage.json",
                "--cov-report=term-missing",
            ]

            if test_paths:
                cmd.extend(test_paths)
            else:
                # Auto-discover tests
                cmd.append("tests/")

            # Run pytest with coverage
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            results["success"] = result.returncode == 0
            results["stdout"] = result.stdout
            results["stderr"] = result.stderr

            # Load coverage JSON if available
            try:
                with open("/tmp/coverage.json") as f:
                    results["coverage_data"] = json.load(f)
            except FileNotFoundError:
                results["coverage_data"] = {}

        except subprocess.TimeoutExpired:
            results["success"] = False
            results["error"] = "Coverage measurement timed out"

        except Exception as e:
            results["success"] = False
            results["error"] = str(e)

        return results

    async def _parse_coverage_results(
        self,
        coverage_id: str,
        module_path: str,
        results: dict,
    ) -> CoverageData:
        """Parse coverage results into CoverageData.

        Args:
            coverage_id: ID for the coverage data
            module_path: Module path
            results: Raw coverage results

        Returns:
            Parsed CoverageData instance
        """
        coverage_data = results.get("coverage_data", {})

        # Extract totals from coverage data
        totals = coverage_data.get("totals", {})

        line_coverage = totals.get("percent_covered", 0.0)
        covered_lines = totals.get("covered_lines", 0)
        total_lines = totals.get("num_statements", 0)

        # Branch coverage (if available)
        branch_coverage = 0.0
        covered_branches = 0
        total_branches = 0
        if "covered_branches" in totals:
            covered_branches = totals["covered_branches"]
            total_branches = totals.get("num_branches", 0)
            if total_branches > 0:
                branch_coverage = (covered_branches / total_branches) * 100

        # Function coverage (if available)
        function_coverage = 0.0
        covered_functions = 0
        total_functions = 0
        if "covered_functions" in totals:
            covered_functions = totals["covered_functions"]
            total_functions = totals.get("num_functions", 0)
            if total_functions > 0:
                function_coverage = (covered_functions / total_functions) * 100

        # Statement coverage (same as line coverage in pytest-cov)
        statement_coverage = line_coverage
        covered_statements = covered_lines
        total_statements = total_lines

        # Extract file-level coverage
        files = coverage_data.get("files", {})
        uncovered_files = []
        partially_covered_files = {}

        for file_path, file_data in files.items():
            file_coverage = file_data.get("summary", {}).get("percent_covered", 0.0)
            if file_coverage == 0.0:
                uncovered_files.append(file_path)
            elif 0.0 < file_coverage < 100.0:
                partially_covered_files[file_path] = file_coverage

        return CoverageData(
            id=coverage_id,
            module_name=module_path,
            line_coverage=line_coverage,
            branch_coverage=branch_coverage,
            function_coverage=function_coverage,
            statement_coverage=statement_coverage,
            total_lines=total_lines,
            covered_lines=covered_lines,
            total_branches=total_branches,
            covered_branches=covered_branches,
            total_functions=total_functions,
            covered_functions=covered_functions,
            total_statements=total_statements,
            covered_statements=covered_statements,
            last_measured=datetime.now(),
            uncovered_files=uncovered_files,
            partially_covered_files=partially_covered_files,
        )

    async def get_coverage_trend(
        self,
        module_path: str,
        days: int = 30,
    ) -> dict[str, list[float]]:
        """Get coverage trend over time.

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
            "line": [random.uniform(70, 95) for _ in range(trend_points)],
            "branch": [random.uniform(60, 90) for _ in range(trend_points)],
            "function": [random.uniform(75, 95) for _ in range(trend_points)],
            "overall": [random.uniform(70, 90) for _ in range(trend_points)],
        }

    def get_coverage_summary(self, module_paths: list[str]) -> dict:
        """Get coverage summary for multiple modules.

        Args:
            module_paths: List of module paths to summarize

        Returns:
            Summary statistics
        """
        summaries = []

        for module_path in module_paths:
            if module_path in self.coverage_cache:
                coverage_data = self.coverage_cache[module_path]
                summaries.append(
                    {
                        "module": module_path,
                        "overall": coverage_data.overall_coverage,
                        "line": coverage_data.line_coverage,
                        "branch": coverage_data.branch_coverage,
                        "function": coverage_data.function_coverage,
                        "grade": coverage_data.coverage_grade,
                    },
                )

        if not summaries:
            return {
                "total_modules": 0,
                "average_coverage": 0.0,
                "modules_at_target": 0,
                "modules_below_target": 0,
            }

        # Calculate summary statistics
        total_modules = len(summaries)
        average_coverage = sum(s["overall"] for s in summaries) / total_modules
        modules_at_target = sum(1 for s in summaries if s["overall"] >= 80.0)
        modules_below_target = total_modules - modules_at_target

        return {
            "total_modules": total_modules,
            "average_coverage": average_coverage,
            "modules_at_target": modules_at_target,
            "modules_below_target": modules_below_target,
            "module_details": summaries,
        }

    def identify_uncovered_critical_paths(
        self,
        coverage_data: CoverageData,
        critical_patterns: list[str] | None = None,
    ) -> list[str]:
        """Identify critical paths that are not covered.

        Args:
            coverage_data: Coverage data to analyze
            critical_patterns: List of patterns for critical files

        Returns:
            List of uncovered critical file paths
        """
        if critical_patterns is None:
            critical_patterns = [
                "__init__.py",
                "cli.py",
                "config.py",
                "exceptions.py",
                "models.py",
                "client.py",
                "processor.py",
            ]

        uncovered_critical = []

        for file_path in coverage_data.uncovered_files:
            if any(pattern in file_path for pattern in critical_patterns):
                uncovered_critical.append(file_path)

        # Also check partially covered files
        for file_path, coverage_percent in coverage_data.partially_covered_files.items():
            if coverage_percent < 50:  # Less than 50% coverage
                if any(pattern in file_path for pattern in critical_patterns):
                    uncovered_critical.append(f"{file_path} ({coverage_percent:.1f}% coverage)")

        return uncovered_critical

    def generate_coverage_report(
        self,
        coverage_data: CoverageData,
        format: str = "text",
    ) -> str:
        """Generate a coverage report.

        Args:
            coverage_data: Coverage data to report on
            format: Report format ("text", "json", "markdown")

        Returns:
            Formatted report string
        """
        if format == "json":
            return json.dumps(asdict(coverage_data), indent=2, default=str)

        if format == "markdown":
            return f"""# Coverage Report for {coverage_data.module_name}

## Summary
- **Overall Coverage**: {coverage_data.overall_coverage:.1f}%
- **Grade**: {coverage_data.coverage_grade}
- **Target Met**: {"✅" if coverage_data.meets_target() else "❌"}

## Coverage Breakdown
| Metric | Coverage | Count |
|--------|----------|-------|
| Line Coverage | {coverage_data.line_coverage:.1f}% | {coverage_data.covered_lines}/{coverage_data.total_lines} |
| Branch Coverage | {coverage_data.branch_coverage:.1f}% | {coverage_data.covered_branches}/{coverage_data.total_branches} |
| Function Coverage | {coverage_data.function_coverage:.1f}% | {coverage_data.covered_functions}/{coverage_data.total_functions} |
| Statement Coverage | {coverage_data.statement_coverage:.1f}% | {coverage_data.covered_statements}/{coverage_data.total_statements} |

## Uncovered Files
{chr(10).join(f"- {f}" for f in coverage_data.uncovered_files) if coverage_data.uncovered_files else "None"}

## Partially Covered Files
{chr(10).join(f"- {f}: {c:.1f}%" for f, c in coverage_data.partially_covered_files.items()) if coverage_data.partially_covered_files else "None"}

*Last measured: {coverage_data.last_measured}*
"""

        # text format
        return f"""Coverage Report for {coverage_data.module_name}
{"=" * 50}

Overall Coverage: {coverage_data.overall_coverage:.1f}% (Grade: {coverage_data.coverage_grade})
Target Met: {"Yes" if coverage_data.meets_target() else "No"}

Coverage Breakdown:
  Line Coverage:    {coverage_data.line_coverage:6.1f}% ({coverage_data.covered_lines:4d}/{coverage_data.total_lines:4d})
  Branch Coverage:  {coverage_data.branch_coverage:6.1f}% ({coverage_data.covered_branches:4d}/{coverage_data.total_branches:4d})
  Function Coverage:{coverage_data.function_coverage:6.1f}% ({coverage_data.covered_functions:4d}/{coverage_data.total_functions:4d})
  Statement Coverage:{coverage_data.statement_coverage:6.1f}% ({coverage_data.covered_statements:4d}/{coverage_data.total_statements:4d})

Uncovered Files:
{chr(10).join(f"  - {f}" for f in coverage_data.uncovered_files) if coverage_data.uncovered_files else "  None"}

Partially Covered Files:
{chr(10).join(f"  - {f}: {c:.1f}%" for f, c in coverage_data.partially_covered_files.items()) if coverage_data.partially_covered_files else "  None"}

Last measured: {coverage_data.last_measured}
"""

    def save_coverage_data(self, coverage_data: CoverageData, file_path: Path) -> None:
        """Save coverage data to file.

        Args:
            coverage_data: Coverage data to save
            file_path: Path to save file
        """
        data = asdict(coverage_data)
        # Convert datetime to string for JSON serialization
        if data.get("last_measured"):
            data["last_measured"] = data["last_measured"].isoformat()

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)

    def load_coverage_data(self, file_path: Path) -> CoverageData:
        """Load coverage data from file.

        Args:
            file_path: Path to load file from

        Returns:
            Loaded CoverageData instance
        """
        with open(file_path) as f:
            data = json.load(f)

        # Convert string back to datetime
        if data.get("last_measured"):
            data["last_measured"] = datetime.fromisoformat(data["last_measured"])

        return CoverageData(**data)
