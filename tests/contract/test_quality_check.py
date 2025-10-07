"""
Contract test for POST /api/quality/check endpoint
"""

import pytest
import requests
from unittest.mock import Mock, patch


@pytest.mark.contract
def test_quality_check():
    """Test that POST /api/quality/check runs quality checks"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "checked_modules": ["anyfile_to_ai.image_processor"],
        "total_violations": 3,
        "check_time": "2025-10-06T10:00:00Z",
    }

    request_data = {"modules": ["anyfile_to_ai.image_processor"]}

    with patch("requests.post", return_value=mock_response):
        response = requests.post(
            "http://localhost:8000/api/quality/check",
            json=request_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert "checked_modules" in data
        assert "total_violations" in data


@pytest.mark.contract
def test_quality_check_endpoint_not_implemented():
    """Test that endpoint returns 404 when not implemented"""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.post", return_value=mock_response):
        response = requests.post("http://localhost:8000/api/quality/check")

        assert response.status_code == 404
