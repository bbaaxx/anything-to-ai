"""
Test Suite Service for managing test suites.
"""

import json
import subprocess
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from anyfile_to_ai.test_quality.models.test_result import TestResult
from anyfile_to_ai.test_quality.models.test_suite import TestSuite


class TestSuiteService:
    """Service for managing test suites and running tests."""

    def __init__(self, project_root: Path):
        """Initialize the test suite service.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.test_results_cache: dict[str, list[TestResult]] = {}

    async def create_test_suite(
        self,
        name: str,
        test_paths: list[str],
        description: str | None = None,
    ) -> TestSuite:
        """Create a new test suite.

        Args:
            name: Name of the test suite
            test_paths: List of test file/directory paths
            description: Optional description

        Returns:
            Created TestSuite instance
        """
        suite_id = f"suite_{name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"

        # Validate test paths exist
        valid_paths = []
        for path in test_paths:
            full_path = self.project_root / path
            if full_path.exists():
                valid_paths.append(path)
            else:
                pass

        return TestSuite(
            id=suite_id,
            name=name,
            test_paths=valid_paths,
            description=description,
        )

    async def run_test_suite(
        self,
        suite: TestSuite,
        verbose: bool = False,
        coverage: bool = False,
    ) -> tuple[bool, list[TestResult]]:
        """Run a test suite and return results.

        Args:
            suite: Test suite to run
            verbose: Enable verbose output
            coverage: Enable coverage measurement

        Returns:
            Tuple of (success, test_results)
        """
        results = []
        overall_success = True

        for test_path in suite.test_paths:
            success, test_results = await self._run_test_path(
                test_path,
                verbose,
                coverage,
            )
            results.extend(test_results)
            overall_success = overall_success and success

        # Update suite with latest results
        suite.last_run = datetime.now()
        suite.test_results = results
        suite.pass_rate = sum(1 for r in results if r.passed) / len(results) if results else 0.0

        # Cache results
        self.test_results_cache[suite.id] = results

        return overall_success, results

    async def _run_test_path(
        self,
        test_path: str,
        verbose: bool = False,
        coverage: bool = False,
    ) -> tuple[bool, list[TestResult]]:
        """Run tests for a specific path.

        Args:
            test_path: Path to test file or directory
            verbose: Enable verbose output
            coverage: Enable coverage measurement

        Returns:
            Tuple of (success, test_results)
        """
        cmd = ["python3", "-m", "pytest", test_path, "--json-report", "--json-report-file=/tmp/test_results.json"]

        if verbose:
            cmd.append("-v")

        if coverage:
            cmd.extend(["--cov=anyfile_to_ai", "--cov-report=json:/tmp/coverage.json"])

        try:
            # Run pytest
            result = subprocess.run(
                cmd,
                check=False,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            # Parse results
            test_results = await self._parse_test_results("/tmp/test_results.json")

            return result.returncode == 0, test_results

        except subprocess.TimeoutExpired:
            # Create timeout result
            timeout_result = TestResult(
                id=f"timeout_{test_path}_{int(datetime.now().timestamp())}",
                test_name=test_path,
                passed=False,
                duration=300.0,
                error_message="Test execution timed out after 5 minutes",
                severity="high",
            )
            return False, [timeout_result]

        except Exception as e:
            # Create error result
            error_result = TestResult(
                id=f"error_{test_path}_{int(datetime.now().timestamp())}",
                test_name=test_path,
                passed=False,
                duration=0.0,
                error_message=str(e),
                severity="high",
            )
            return False, [error_result]

    async def _parse_test_results(self, results_file: str) -> list[TestResult]:
        """Parse pytest JSON results.

        Args:
            results_file: Path to pytest JSON results file

        Returns:
            List of TestResult instances
        """
        results = []

        try:
            with open(results_file) as f:
                data = json.load(f)

            # Parse test results from pytest JSON report
            for test_name, test_info in data.get("tests", {}).items():
                result = TestResult(
                    id=f"test_{test_name}_{int(datetime.now().timestamp())}",
                    test_name=test_name,
                    passed=test_info.get("outcome") == "passed",
                    duration=test_info.get("duration", 0.0),
                    error_message=test_info.get("call", {}).get("longrepr", ""),
                    severity=self._determine_severity(test_info),
                )
                results.append(result)

        except FileNotFoundError:
            # No results file found
            pass
        except json.JSONDecodeError:
            # Invalid JSON
            pass

        return results

    def _determine_severity(self, test_info: dict) -> str:
        """Determine severity of test failure.

        Args:
            test_info: Test information from pytest

        Returns:
            Severity level (low, medium, high)
        """
        outcome = test_info.get("outcome", "unknown")
        if outcome == "passed":
            return "low"

        # Check for specific error patterns
        longrepr = test_info.get("call", {}).get("longrepr", "")

        if any(keyword in longrepr.lower() for keyword in ["import", "module", "syntax"]):
            return "high"
        if any(keyword in longrepr.lower() for keyword in ["assert", "expect"]):
            return "medium"
        return "medium"

    async def quarantine_flaky_tests(
        self,
        suite: TestSuite,
        max_retries: int = 3,
    ) -> list[TestResult]:
        """Identify and quarantine flaky tests.

        Args:
            suite: Test suite to analyze
            max_retries: Maximum number of retries for flaky detection

        Returns:
            List of quarantined test results
        """
        flaky_results = []

        for test_path in suite.test_paths:
            # Run test multiple times to detect flakiness
            results = []
            for _attempt in range(max_retries):
                _success, attempt_results = await self._run_test_path(test_path)
                results.extend(attempt_results)

            # Analyze results for flakiness
            flaky_results.extend(self._identify_flaky_tests(results))

        return flaky_results

    def _identify_flaky_tests(self, results: list[TestResult]) -> list[TestResult]:
        """Identify flaky tests from multiple runs.

        Args:
            results: Test results from multiple runs

        Returns:
            List of flaky test results
        """
        # Group results by test name
        test_groups = {}
        for result in results:
            if result.test_name not in test_groups:
                test_groups[result.test_name] = []
            test_groups[result.test_name].append(result)

        # Identify flaky tests (inconsistent results)
        flaky_results = []
        for test_name, test_results in test_groups.items():
            if len(test_results) > 1:
                outcomes = [r.passed for r in test_results]
                if len(set(outcomes)) > 1:  # Mixed pass/fail results
                    # Create a flaky test result
                    flaky_result = TestResult(
                        id=f"flaky_{test_name}_{int(datetime.now().timestamp())}",
                        test_name=test_name,
                        passed=False,
                        duration=sum(r.duration for r in test_results),
                        error_message=f"Flaky test detected: {sum(outcomes)}/{len(outcomes)} passes",
                        severity="medium",
                    )
                    flaky_results.append(flaky_result)

        return flaky_results

    def get_test_suite_health(self, suite: TestSuite) -> dict:
        """Get health metrics for a test suite.

        Args:
            suite: Test suite to analyze

        Returns:
            Health metrics dictionary
        """
        if not suite.test_results:
            return {
                "health_score": 0.0,
                "pass_rate": 0.0,
                "total_tests": 0,
                "failed_tests": 0,
                "flaky_tests": 0,
                "status": "no_results",
            }

        total_tests = len(suite.test_results)
        passed_tests = sum(1 for r in suite.test_results if r.passed)
        failed_tests = total_tests - passed_tests
        flaky_tests = sum(1 for r in suite.test_results if "flaky" in r.error_message.lower())

        # Calculate health score (0-100)
        health_score = (passed_tests / total_tests) * 100
        if flaky_tests > 0:
            health_score -= (flaky_tests / total_tests) * 20  # Penalty for flaky tests

        status = "healthy"
        if health_score < 50:
            status = "unhealthy"
        elif health_score < 80:
            status = "degraded"

        return {
            "health_score": max(0, health_score),
            "pass_rate": suite.pass_rate,
            "total_tests": total_tests,
            "failed_tests": failed_tests,
            "flaky_tests": flaky_tests,
            "status": status,
        }

    def save_test_suite(self, suite: TestSuite, file_path: Path) -> None:
        """Save test suite to file.

        Args:
            suite: Test suite to save
            file_path: Path to save file
        """
        suite_data = asdict(suite)
        # Convert datetime objects to strings for JSON serialization
        if suite_data.get("last_run"):
            suite_data["last_run"] = suite_data["last_run"].isoformat()

        with open(file_path, "w") as f:
            json.dump(suite_data, f, indent=2)

    def load_test_suite(self, file_path: Path) -> TestSuite:
        """Load test suite from file.

        Args:
            file_path: Path to load file from

        Returns:
            Loaded TestSuite instance
        """
        with open(file_path) as f:
            suite_data = json.load(f)

        # Convert string back to datetime
        if suite_data.get("last_run"):
            suite_data["last_run"] = datetime.fromisoformat(suite_data["last_run"])

        return TestSuite(**suite_data)
