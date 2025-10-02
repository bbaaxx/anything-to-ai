"""
Progress tracking for text summarization.

This module provides progress tracking integration with the unified
progress_tracker system.
"""

try:
    from progress_tracker import ProgressEmitter, CLIProgressConsumer, CallbackProgressConsumer

    _PROGRESS_AVAILABLE = True
except ImportError:
    _PROGRESS_AVAILABLE = False
    ProgressEmitter = None
    CLIProgressConsumer = None
    CallbackProgressConsumer = None


__all__ = ["ProgressEmitter", "CLIProgressConsumer", "CallbackProgressConsumer"]
