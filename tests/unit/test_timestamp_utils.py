"""Unit tests for ISO 8601 timestamp formatting utilities."""

from datetime import datetime, timezone, UTC

import pytest


class TestTimestampFormatting:
    """Tests for ISO 8601 timestamp formatting."""

    def test_iso8601_format_basic(self):
        """Test basic ISO 8601 timestamp format."""
        dt = datetime(2025, 10, 25, 14, 30, 0, tzinfo=UTC)
        timestamp = dt.isoformat()

        assert timestamp == "2025-10-25T14:30:00+00:00"

    def test_iso8601_format_with_microseconds(self):
        """Test ISO 8601 format preserves microseconds."""
        dt = datetime(2025, 10, 25, 14, 30, 0, 123456, tzinfo=UTC)
        timestamp = dt.isoformat()

        assert "2025-10-25T14:30:00.123456" in timestamp

    def test_iso8601_format_timezone_aware(self):
        """Test ISO 8601 format includes timezone."""
        dt = datetime.now(UTC)
        timestamp = dt.isoformat()

        assert "+00:00" in timestamp or "Z" in timestamp.replace("+00:00", "Z")

    def test_iso8601_roundtrip(self):
        """Test ISO 8601 timestamp can be parsed back."""
        original_dt = datetime(2025, 10, 25, 14, 30, 0, tzinfo=UTC)
        timestamp = original_dt.isoformat()

        parsed_dt = datetime.fromisoformat(timestamp)

        assert parsed_dt == original_dt
        assert parsed_dt.tzinfo == UTC

    def test_iso8601_format_consistency(self):
        """Test ISO 8601 format is consistent across calls."""
        dt = datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)

        timestamp1 = dt.isoformat()
        timestamp2 = dt.isoformat()

        assert timestamp1 == timestamp2

    def test_iso8601_format_different_times(self):
        """Test ISO 8601 format produces different strings for different times."""
        dt1 = datetime(2025, 10, 25, 14, 30, 0, tzinfo=UTC)
        dt2 = datetime(2025, 10, 25, 14, 31, 0, tzinfo=UTC)

        timestamp1 = dt1.isoformat()
        timestamp2 = dt2.isoformat()

        assert timestamp1 != timestamp2


class TestTimestampParsing:
    """Tests for parsing ISO 8601 timestamps."""

    def test_parse_iso8601_basic(self):
        """Test parsing basic ISO 8601 timestamp."""
        timestamp = "2025-10-25T14:30:00+00:00"
        dt = datetime.fromisoformat(timestamp)

        assert dt.year == 2025
        assert dt.month == 10
        assert dt.day == 25
        assert dt.hour == 14
        assert dt.minute == 30
        assert dt.second == 0

    def test_parse_iso8601_with_timezone(self):
        """Test parsing ISO 8601 timestamp preserves timezone."""
        timestamp = "2025-10-25T14:30:00+00:00"
        dt = datetime.fromisoformat(timestamp)

        assert dt.tzinfo == UTC

    def test_parse_iso8601_invalid_format(self):
        """Test parsing invalid ISO 8601 format raises error."""
        with pytest.raises(ValueError):
            datetime.fromisoformat("invalid_timestamp")

    def test_parse_iso8601_without_timezone(self):
        """Test parsing timestamp without timezone."""
        timestamp = "2025-10-25T14:30:00"
        dt = datetime.fromisoformat(timestamp)

        assert dt.tzinfo is None


class TestTimestampValidation:
    """Tests for timestamp validation."""

    def test_validate_timestamp_format(self):
        """Test timestamp format validation."""
        valid_timestamps = [
            "2025-10-25T14:30:00+00:00",
            "2025-01-01T00:00:00+00:00",
            "2025-12-31T23:59:59+00:00",
        ]

        for timestamp in valid_timestamps:
            dt = datetime.fromisoformat(timestamp)
            assert isinstance(dt, datetime)

    def test_timestamp_ordering(self):
        """Test timestamps can be ordered correctly."""
        dt1 = datetime(2025, 10, 25, 14, 30, 0, tzinfo=UTC)
        dt2 = datetime(2025, 10, 25, 14, 31, 0, tzinfo=UTC)

        assert dt1 < dt2

    def test_timestamp_equality(self):
        """Test timestamp equality comparison."""
        dt1 = datetime(2025, 10, 25, 14, 30, 0, tzinfo=UTC)
        dt2 = datetime(2025, 10, 25, 14, 30, 0, tzinfo=UTC)

        assert dt1 == dt2


class TestCurrentTimestamp:
    """Tests for current timestamp generation."""

    def test_current_timestamp_has_timezone(self):
        """Test current timestamp includes timezone."""
        dt = datetime.now(UTC)
        assert dt.tzinfo == UTC

    def test_current_timestamp_iso8601_format(self):
        """Test current timestamp can be formatted as ISO 8601."""
        dt = datetime.now(UTC)
        timestamp = dt.isoformat()

        assert "T" in timestamp
        assert "+" in timestamp or "Z" in timestamp.replace("+00:00", "Z")

    def test_current_timestamp_parseable(self):
        """Test current timestamp can be parsed back."""
        original_dt = datetime.now(UTC)
        timestamp = original_dt.isoformat()
        parsed_dt = datetime.fromisoformat(timestamp)

        time_diff = abs((parsed_dt - original_dt).total_seconds())
        assert time_diff < 1
