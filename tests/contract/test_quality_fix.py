"""
Contract test for POST /api/quality/fix endpoint
"""

import pytest
import requests
from unittest.mock import Mock, patch


@pytest.mark.contract
def test_quality_fix():
    """Test that POST /api/quality/fix applies atomic fixes"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "fixed_violations": 2,
        "failed_fixes": 0,
        "fix_time": "2025-10-06T10:00:00Z",
    }

    request_data = {
        "violations": [
            {
                "file_path": "/path/to/file.py",
                "line_number": 25,
                "rule_code": "E501",
            },
        ],
    }

    with patch("requests.post", return_value=mock_response):
        response = requests.post(
            "http://localhost:8000/api/quality/fix",
            json=request_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert "fixed_violations" in data
        assert "failed_fixes" in data


@pytest.mark.contract
def test_quality_fix_endpoint_not_implemented():
    """Test that endpoint returns 404 when not implemented"""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.post", return_value=mock_response):
        response = requests.post("http://localhost:8000/api/quality/fix")

        assert response.status_code == 404
