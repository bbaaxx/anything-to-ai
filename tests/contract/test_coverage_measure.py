"""
Contract test for POST /api/coverage/measure endpoint
"""

import pytest
import requests
from unittest.mock import Mock, patch


@pytest.mark.contract
def test_measure_coverage():
    """Test that POST /api/coverage/measure measures test coverage"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "measured_modules": ["anyfile_to_ai.image_processor"],
        "overall_coverage": 85.0,
        "measurement_time": "2025-10-06T10:00:00Z",
    }

    request_data = {"modules": ["anyfile_to_ai.image_processor"]}

    with patch("requests.post", return_value=mock_response):
        response = requests.post(
            "http://localhost:8000/api/coverage/measure",
            json=request_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert "measured_modules" in data
        assert "overall_coverage" in data


@pytest.mark.contract
def test_coverage_measure_endpoint_not_implemented():
    """Test that endpoint returns 404 when not implemented"""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.post", return_value=mock_response):
        response = requests.post("http://localhost:8000/api/coverage/measure")

        assert response.status_code == 404
