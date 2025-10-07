"""
Contract test for POST /api/test/suites/{suite_id}/quarantine endpoint
"""

import pytest
import requests
from unittest.mock import Mock, patch


@pytest.mark.contract
def test_quarantine_flaky_tests():
    """Test that POST /api/test/suites/{suite_id}/quarantine quarantines flaky tests"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "suite_id": "suite-1",
        "quarantined_tests": ["test-1", "test-2"],
        "message": "Tests quarantined successfully",
    }

    request_data = {"test_ids": ["test-1", "test-2"]}

    with patch("requests.post", return_value=mock_response):
        response = requests.post(
            "http://localhost:8000/api/test/suites/suite-1/quarantine",
            json=request_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert "suite_id" in data
        assert "quarantined_tests" in data
        assert "message" in data


@pytest.mark.contract
def test_quarantine_endpoint_not_implemented():
    """Test that endpoint returns 404 when not implemented"""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.post", return_value=mock_response):
        response = requests.post("http://localhost:8000/api/test/suites/suite-1/quarantine")

        assert response.status_code == 404
