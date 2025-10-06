"""
Data models for audio processing module.
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Callable


@dataclass
class AudioDocument:
    """
    Represents a validated audio file with extracted metadata.

    Created after validating an audio file but before processing.
    All fields are required and validated according to spec constraints.
    """
    file_path: str
    format: str  # mp3, wav, m4a
    duration: float  # seconds
    sample_rate: int  # Hz
    file_size: int  # bytes
    channels: int  # 1=mono, 2=stereo


@dataclass
class TranscriptionResult:
    """
    Contains transcription output with quality metrics and metadata.

    Represents the result of transcribing a single audio file.
    success=True indicates successful transcription, False indicates failure.
    """
    audio_path: str
    text: str
    confidence_score: Optional[float]  # 0.0-1.0
    processing_time: float  # seconds
    model_used: str  # e.g., "medium"
    quantization: str  # none, 4bit, 8bit
    detected_language: Optional[str]  # ISO 639-1 code (e.g., "en")
    success: bool
    error_message: Optional[str]


@dataclass
class TranscriptionConfig:
    """
    Configuration parameters for transcription process.

    Encapsulates all transcription settings in a single validated object.
    Use create_config() factory function to instantiate with validation.
    """
    model: str = "medium"
    quantization: str = "none"  # Changed from "4bit" due to MLX compatibility
    batch_size: int = 12
    language: Optional[str] = None  # ISO 639-1 code, None for auto-detect
    output_format: str = "plain"  # plain or json
    timeout_seconds: int = 600
    progress_callback: Optional[Callable[[int, int], None]] = None
    verbose: bool = False
    max_duration_seconds: int = 7200  # 2 hours


@dataclass
class ProcessingResult:
    """
    Aggregate results from batch transcription operations.

    Stores results of processing multiple audio files with statistics.
    success=True if at least one file succeeded.
    """
    success: bool
    results: List[TranscriptionResult]
    total_files: int
    successful_count: int
    failed_count: int
    total_processing_time: float  # seconds
    average_processing_time: float  # seconds
    error_summary: Optional[Dict[str, int]]  # error type -> count
