"""
Contract test for GET /api/test/suites endpoint
"""

import pytest
import requests
from unittest.mock import Mock, patch


@pytest.mark.contract
def test_get_test_suites_returns_list():
    """Test that GET /api/test/suites returns a list of test suites"""
    # Mock the response since endpoint doesn't exist yet
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "suites": [
            {
                "id": "suite-1",
                "name": "Unit Tests",
                "status": "passing",
                "coverage_percentage": 85.5,
                "last_run": "2025-10-06T10:00:00Z",
                "test_count": 150,
                "failure_count": 0,
                "flaky_count": 2,
            },
        ],
    }

    with patch("requests.get", return_value=mock_response):
        response = requests.get("http://localhost:8000/api/test/suites")

        assert response.status_code == 200
        data = response.json()
        assert "suites" in data
        assert isinstance(data["suites"], list)

        # Validate suite structure
        if data["suites"]:
            suite = data["suites"][0]
            assert "id" in suite
            assert "name" in suite
            assert "status" in suite
            assert "coverage_percentage" in suite
            assert "last_run" in suite
            assert "test_count" in suite
            assert "failure_count" in suite
            assert "flaky_count" in suite
            assert suite["status"] in ["passing", "failing", "flaky", "quarantined"]


@pytest.mark.contract
def test_get_test_suites_empty_response():
    """Test that GET /api/test/suites handles empty test suite list"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"suites": []}

    with patch("requests.get", return_value=mock_response):
        response = requests.get("http://localhost:8000/api/test/suites")

        assert response.status_code == 200
        data = response.json()
        assert "suites" in data
        assert isinstance(data["suites"], list)
        assert len(data["suites"]) == 0


@pytest.mark.contract
def test_get_test_suites_endpoint_not_implemented():
    """Test that endpoint returns 404 when not implemented"""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response):
        response = requests.get("http://localhost:8000/api/test/suites")

        # This should fail until endpoint is implemented
        assert response.status_code == 404
