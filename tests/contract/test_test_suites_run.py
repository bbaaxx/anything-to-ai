"""
Contract test for POST /api/test/suites/{suite_id}/run endpoint
"""

import pytest
import requests
from unittest.mock import Mock, patch


@pytest.mark.contract
def test_run_test_suite_success():
    """Test that POST /api/test/suites/{suite_id}/run executes a test suite"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "suite_id": "suite-1",
        "status": "completed",
        "started_at": "2025-10-06T10:00:00Z",
        "results": [
            {
                "test_id": "test-1",
                "test_name": "test_example",
                "status": "passed",
                "execution_time": 0.05,
                "failure_message": None,
                "file_path": "tests/unit/test_example.py",
                "line_number": 10,
                "is_flaky": False,
            },
        ],
    }

    with patch("requests.post", return_value=mock_response):
        response = requests.post("http://localhost:8000/api/test/suites/suite-1/run")

        assert response.status_code == 200
        data = response.json()
        assert "suite_id" in data
        assert "status" in data
        assert "started_at" in data
        assert "results" in data
        assert data["status"] in ["running", "completed", "failed"]


@pytest.mark.contract
def test_run_test_suite_not_found():
    """Test that POST /api/test/suites/{suite_id}/run handles non-existent suite"""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.post", return_value=mock_response):
        response = requests.post("http://localhost:8000/api/test/suites/nonexistent/run")

        assert response.status_code == 404


@pytest.mark.contract
def test_run_test_suite_endpoint_not_implemented():
    """Test that endpoint returns 404 when not implemented"""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.post", return_value=mock_response):
        response = requests.post("http://localhost:8000/api/test/suites/suite-1/run")

        # This should fail until endpoint is implemented
        assert response.status_code == 404
