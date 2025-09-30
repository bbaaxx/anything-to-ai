"""
Whisper model loading and caching.
"""

from typing import Optional
from audio_processor.exceptions import ModelLoadError


class WhisperModelLoader:
    """
    Manages Whisper model loading and caching.

    Uses lazy loading and singleton pattern to reuse models across transcriptions.
    Models are automatically downloaded by lightning-whisper-mlx on first use.
    """

    def __init__(self):
        self._model = None
        self._current_model_name = None
        self._current_quantization = None
        self._current_batch_size = None

    def load_model(self, model_name: str, quantization: str, batch_size: int):
        """
        Load or retrieve cached Whisper model.

        Args:
            model_name: Model identifier (e.g., "medium")
            quantization: Quantization level ("none", "4bit", "8bit")
            batch_size: Decoder batch size

        Returns:
            LightningWhisperMLX: Loaded model instance

        Raises:
            ModelLoadError: If model loading fails
        """
        # Check if we already have the right model loaded
        if (self._model is not None and
                self._current_model_name == model_name and
                self._current_quantization == quantization and
                self._current_batch_size == batch_size):
            return self._model

        try:
            from lightning_whisper_mlx import LightningWhisperMLX

            # Convert quantization format
            quant = None if quantization == "none" else quantization

            # Load model
            self._model = LightningWhisperMLX(
                model=model_name,
                batch_size=batch_size,
                quant=quant
            )

            # Cache model parameters
            self._current_model_name = model_name
            self._current_quantization = quantization
            self._current_batch_size = batch_size

            return self._model

        except Exception as e:
            raise ModelLoadError(
                f"Failed to load Whisper model '{model_name}': {str(e)}",
                model_name=model_name
            )

    def clear_cache(self):
        """Clear cached model to free memory."""
        self._model = None
        self._current_model_name = None
        self._current_quantization = None
        self._current_batch_size = None


# Global model loader instance (singleton pattern)
_model_loader = WhisperModelLoader()


def get_model_loader() -> WhisperModelLoader:
    """Get the global model loader instance."""
    return _model_loader