"""
API endpoints for test suite management.
"""

from datetime import datetime
from pathlib import Path

from anyfile_to_ai.test_quality.models.test_suite import TestSuite
from anyfile_to_ai.test_quality.services.test_suite_service import TestSuiteService


class TestSuitesAPI:
    """API endpoints for test suite management."""

    def __init__(self, project_root: Path):
        """Initialize the test suites API.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.service = TestSuiteService(project_root)
        self.suites: dict[str, TestSuite] = {}

    async def create_suite(
        self,
        name: str,
        test_paths: list[str],
        description: str | None = None,
    ) -> dict:
        """Create a new test suite.

        Args:
            name: Name of the test suite
            test_paths: List of test file/directory paths
            description: Optional description

        Returns:
            API response with created suite data
        """
        try:
            suite = await self.service.create_test_suite(name, test_paths, description)
            self.suites[suite.id] = suite

            return {
                "success": True,
                "data": {
                    "id": suite.id,
                    "name": suite.name,
                    "test_paths": suite.test_paths,
                    "description": suite.description,
                    "created_at": suite.created_at.isoformat() if suite.created_at else None,
                    "last_run": suite.last_run.isoformat() if suite.last_run else None,
                    "pass_rate": suite.pass_rate,
                },
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "CREATE_SUITE_FAILED",
            }

    async def get_suite(self, suite_id: str) -> dict:
        """Get a test suite by ID.

        Args:
            suite_id: ID of the test suite

        Returns:
            API response with suite data
        """
        if suite_id not in self.suites:
            return {
                "success": False,
                "error": f"Test suite {suite_id} not found",
                "error_code": "SUITE_NOT_FOUND",
            }

        suite = self.suites[suite_id]
        health = self.service.get_test_suite_health(suite)

        return {
            "success": True,
            "data": {
                "id": suite.id,
                "name": suite.name,
                "test_paths": suite.test_paths,
                "description": suite.description,
                "created_at": suite.created_at.isoformat() if suite.created_at else None,
                "last_run": suite.last_run.isoformat() if suite.last_run else None,
                "pass_rate": suite.pass_rate,
                "health": health,
                "test_results_count": len(suite.test_results),
            },
        }

    async def list_suites(self) -> dict:
        """List all test suites.

        Returns:
            API response with list of suites
        """
        suites_data = []

        for suite in self.suites.values():
            health = self.service.get_test_suite_health(suite)
            suites_data.append(
                {
                    "id": suite.id,
                    "name": suite.name,
                    "test_paths": suite.test_paths,
                    "description": suite.description,
                    "created_at": suite.created_at.isoformat() if suite.created_at else None,
                    "last_run": suite.last_run.isoformat() if suite.last_run else None,
                    "pass_rate": suite.pass_rate,
                    "health": health,
                    "test_results_count": len(suite.test_results),
                },
            )

        return {
            "success": True,
            "data": {
                "suites": suites_data,
                "total_count": len(suites_data),
            },
        }

    async def run_suite(
        self,
        suite_id: str,
        verbose: bool = False,
        coverage: bool = False,
    ) -> dict:
        """Run a test suite.

        Args:
            suite_id: ID of the test suite to run
            verbose: Enable verbose output
            coverage: Enable coverage measurement

        Returns:
            API response with run results
        """
        if suite_id not in self.suites:
            return {
                "success": False,
                "error": f"Test suite {suite_id} not found",
                "error_code": "SUITE_NOT_FOUND",
            }

        try:
            suite = self.suites[suite_id]
            success, results = await self.service.run_test_suite(suite, verbose, coverage)

            # Update suite with results
            self.suites[suite_id] = suite

            # Prepare results data
            results_data = []
            for result in results:
                results_data.append(
                    {
                        "id": result.id,
                        "test_name": result.test_name,
                        "passed": result.passed,
                        "duration": result.duration,
                        "error_message": result.error_message,
                        "severity": result.severity,
                        "timestamp": result.timestamp.isoformat() if result.timestamp else None,
                    },
                )

            return {
                "success": success,
                "data": {
                    "suite_id": suite_id,
                    "suite_name": suite.name,
                    "run_timestamp": suite.last_run.isoformat() if suite.last_run else None,
                    "overall_success": success,
                    "pass_rate": suite.pass_rate,
                    "total_tests": len(results),
                    "passed_tests": sum(1 for r in results if r.passed),
                    "failed_tests": sum(1 for r in results if not r.passed),
                    "results": results_data,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "RUN_SUITE_FAILED",
            }

    async def quarantine_flaky_tests(
        self,
        suite_id: str,
        max_retries: int = 3,
    ) -> dict:
        """Quarantine flaky tests in a suite.

        Args:
            suite_id: ID of the test suite
            max_retries: Maximum number of retries for flaky detection

        Returns:
            API response with quarantined tests
        """
        if suite_id not in self.suites:
            return {
                "success": False,
                "error": f"Test suite {suite_id} not found",
                "error_code": "SUITE_NOT_FOUND",
            }

        try:
            suite = self.suites[suite_id]
            flaky_results = await self.service.quarantine_flaky_tests(suite, max_retries)

            # Prepare flaky results data
            flaky_data = []
            for result in flaky_results:
                flaky_data.append(
                    {
                        "id": result.id,
                        "test_name": result.test_name,
                        "duration": result.duration,
                        "error_message": result.error_message,
                        "severity": result.severity,
                        "timestamp": result.timestamp.isoformat() if result.timestamp else None,
                    },
                )

            return {
                "success": True,
                "data": {
                    "suite_id": suite_id,
                    "suite_name": suite.name,
                    "quarantined_tests": flaky_data,
                    "total_quarantined": len(flaky_data),
                    "quarantine_timestamp": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "QUARANTINE_FAILED",
            }

    async def delete_suite(self, suite_id: str) -> dict:
        """Delete a test suite.

        Args:
            suite_id: ID of the test suite to delete

        Returns:
            API response with deletion result
        """
        if suite_id not in self.suites:
            return {
                "success": False,
                "error": f"Test suite {suite_id} not found",
                "error_code": "SUITE_NOT_FOUND",
            }

        try:
            suite_name = self.suites[suite_id].name
            del self.suites[suite_id]

            return {
                "success": True,
                "data": {
                    "deleted_suite_id": suite_id,
                    "deleted_suite_name": suite_name,
                    "deleted_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "DELETE_SUITE_FAILED",
            }

    async def get_suite_health(self, suite_id: str) -> dict:
        """Get health metrics for a test suite.

        Args:
            suite_id: ID of the test suite

        Returns:
            API response with health metrics
        """
        if suite_id not in self.suites:
            return {
                "success": False,
                "error": f"Test suite {suite_id} not found",
                "error_code": "SUITE_NOT_FOUND",
            }

        try:
            suite = self.suites[suite_id]
            health = self.service.get_test_suite_health(suite)

            return {
                "success": True,
                "data": {
                    "suite_id": suite_id,
                    "suite_name": suite.name,
                    "health_metrics": health,
                    "assessed_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "HEALTH_CHECK_FAILED",
            }

    def save_suite(self, suite_id: str, file_path: str) -> dict:
        """Save a test suite to file.

        Args:
            suite_id: ID of the test suite to save
            file_path: Path to save file

        Returns:
            API response with save result
        """
        if suite_id not in self.suites:
            return {
                "success": False,
                "error": f"Test suite {suite_id} not found",
                "error_code": "SUITE_NOT_FOUND",
            }

        try:
            suite = self.suites[suite_id]
            self.service.save_test_suite(suite, Path(file_path))

            return {
                "success": True,
                "data": {
                    "suite_id": suite_id,
                    "saved_to": file_path,
                    "saved_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "SAVE_SUITE_FAILED",
            }

    def load_suite(self, file_path: str) -> dict:
        """Load a test suite from file.

        Args:
            file_path: Path to load file from

        Returns:
            API response with loaded suite
        """
        try:
            suite = self.service.load_test_suite(Path(file_path))
            self.suites[suite.id] = suite

            return {
                "success": True,
                "data": {
                    "id": suite.id,
                    "name": suite.name,
                    "test_paths": suite.test_paths,
                    "description": suite.description,
                    "created_at": suite.created_at.isoformat() if suite.created_at else None,
                    "last_run": suite.last_run.isoformat() if suite.last_run else None,
                    "pass_rate": suite.pass_rate,
                    "loaded_from": file_path,
                    "loaded_at": datetime.now().isoformat(),
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_code": "LOAD_SUITE_FAILED",
            }
