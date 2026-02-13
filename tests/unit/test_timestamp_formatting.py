"""Unit tests for audio timestamp formatting utilities."""

import re

import pytest

from anyfile_to_ai.audio_processor.markdown_formatter import (
    format_segments_csv,
    format_segments_markdown,
    format_timestamp,
)
from anyfile_to_ai.output_formatter.markdown import format_audio_timestamp
from anyfile_to_ai.audio_processor.models import TranscriptionSegment


def test_format_timestamp_edge_cases():
    """Validate format_timestamp edge behavior and boundaries."""
    assert format_timestamp(0.0) == "00:00:00.00"
    assert format_timestamp(7199.99) == "01:59:59.99"

    rounded = format_timestamp(59.999)
    assert re.match(r"^\d{2}:\d{2}:\d{2}\.\d{2}$", rounded)

    with pytest.raises(ValueError):
        format_timestamp(-0.01)

    with pytest.raises(ValueError):
        format_timestamp(7200.01)


def test_format_segments_markdown():
    """Validate markdown rendering of timestamped segments."""
    segments = [
        TranscriptionSegment(start=0.0, end=5.23, text="First segment."),
        TranscriptionSegment(start=5.23, end=12.45, text="Second segment."),
    ]

    output = format_segments_markdown(segments)
    lines = output.splitlines()

    assert len(lines) == 2
    assert lines[0] == "[00:00:00.00] First segment."
    assert lines[1] == "[00:00:05.23] Second segment."

    timestamps_only = format_segments_markdown(segments, include_text=False)
    assert timestamps_only.splitlines() == ["[00:00:00.00]", "[00:00:05.23]"]
    assert format_segments_markdown([]) == ""


def test_format_csv_with_timestamps():
    """Validate CSV output with timestamped segments."""
    segments = [
        TranscriptionSegment(start=0.0, end=5.23, text='First "quoted" segment'),
        TranscriptionSegment(start=5.23, end=12.45, text="Second segment"),
    ]

    output = format_segments_csv(segments)
    lines = output.strip().splitlines()

    assert lines[0] == "start,end,text"
    assert lines[1] == '0.00,5.23,"First ""quoted"" segment"'
    assert lines[2] == "5.23,12.45,Second segment"


def test_shared_timestamp_formatter_parity():
    assert format_audio_timestamp(0.0) == format_timestamp(0.0)
    assert format_audio_timestamp(65.45) == format_timestamp(65.45)
