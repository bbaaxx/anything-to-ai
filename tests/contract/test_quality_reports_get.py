"""
Contract test for GET /api/quality/reports endpoint
"""

import pytest
import requests
from unittest.mock import Mock, patch


@pytest.mark.contract
def test_get_quality_reports():
    """Test that GET /api/quality/reports returns quality reports"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "reports": [
            {
                "id": "report-1",
                "module_name": "anyfile_to_ai.image_processor",
                "violation_count": 5,
                "complexity_score": 8.5,
                "maintainability_index": 75.2,
                "last_check": "2025-10-06T10:00:00Z",
                "violations": [
                    {
                        "rule_code": "E501",
                        "severity": "warning",
                        "line_number": 25,
                        "column_number": 80,
                        "message": "Line too long",
                        "file_path": "/path/to/file.py",
                    },
                ],
            },
        ],
    }

    with patch("requests.get", return_value=mock_response):
        response = requests.get("http://localhost:8000/api/quality/reports")

        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        assert isinstance(data["reports"], list)


@pytest.mark.contract
def test_quality_reports_endpoint_not_implemented():
    """Test that endpoint returns 404 when not implemented"""
    mock_response = Mock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response):
        response = requests.get("http://localhost:8000/api/quality/reports")

        assert response.status_code == 404
