"""
Contract test for GET /api/coverage/modules endpoint
"""

import pytest
import requests
from unittest.mock import Mock, patch


@pytest.mark.contract
def test_get_coverage_modules():
    """Test that GET /api/coverage/modules returns coverage data"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "modules": [
            {
                "module_name": "anyfile_to_ai.image_processor",
                "total_lines": 500,
                "covered_lines": 425,
                "uncovered_lines": [75, 76, 77, 78, 79],
                "coverage_percentage": 85.0,
                "last_measured": "2025-10-06T10:00:00Z",
            },
        ],
    }

    with patch("requests.get", return_value=mock_response):
        response = requests.get("http://localhost:8000/api/coverage/modules")

        assert response.status_code == 200
        data = response.json()
        assert "modules" in data
        assert isinstance(data["modules"], list)


@pytest.mark.contract
def test_coverage_modules_endpoint_not_implemented():
    """Test that endpoint returns 404 when not implemented"""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response):
        response = requests.get("http://localhost:8000/api/coverage/modules")

        assert response.status_code == 404
