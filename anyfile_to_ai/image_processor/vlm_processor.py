"""VLM processor for single and batch image processing."""

from typing import Any
import time

from .vlm_models import ModelConfiguration
from .model_registry import get_global_registry, LoadedModel
from .vlm_model_impl import create_vlm_model
from .vlm_exceptions import VLMProcessingError, VLMTimeoutError
from .config import VLMConfig


def _convert_config(config) -> ModelConfiguration:
    """Convert VLMConfig to ModelConfiguration if needed."""
    if isinstance(config, VLMConfig):
        return ModelConfiguration(
            model_name=config.model_name,
            timeout_seconds=config.timeout_seconds,
            timeout_behavior=config.timeout_behavior,
            auto_download=config.auto_download,
            validation_enabled=config.validate_before_load,
            cache_dir=config.cache_dir,
        )
    return config


class VLMProcessor:
    """Main VLM processing interface for single and batch operations."""

    def __init__(self):
        self.registry = get_global_registry()
        self._current_model = None

    def process_image_with_vlm(self, image_path: str, prompt: str, config) -> dict[str, Any]:
        """
        Process single image with VLM.

        Args:
            image_path: Path to image file
            prompt: VLM prompt text
            config: VLM configuration

        Returns:
            Dict containing VLM processing results

        Raises:
            VLMProcessingError: If VLM processing fails
            VLMTimeoutError: If processing exceeds timeout
        """
        try:
            # Convert config if needed
            config = _convert_config(config)

            # Ensure model is loaded
            loaded_model = self._ensure_model_loaded(config)

            # Create VLM model instance if needed
            if self._current_model is None or self._current_model.model_name != config.model_name:
                self._current_model = create_vlm_model(config.model_name)
                # Pre-load the model WITHOUT timeout to allow for downloading
                self._current_model._ensure_model_loaded()

            # Process with timeout handling (only for actual inference)
            start_time = time.time()

            try:
                result = self._process_with_timeout(self._current_model, image_path, prompt, config.timeout_seconds)

                processing_time = time.time() - start_time

                return {"description": result["description"], "confidence_score": result.get("confidence_score"), "processing_time": processing_time, "model_info": loaded_model.model_info}

            except VLMTimeoutError:
                processing_time = time.time() - start_time

                # Handle timeout based on configuration
                if config.timeout_behavior == "error":
                    raise VLMTimeoutError(f"VLM processing timed out after {config.timeout_seconds} seconds", timeout_seconds=config.timeout_seconds, actual_time=processing_time, image_path=image_path, model_name=config.model_name)
                if config.timeout_behavior == "fallback":
                    return self._create_fallback_result(image_path, loaded_model, processing_time)
                # continue
                return self._create_timeout_result(image_path, loaded_model, processing_time)

        except Exception as e:
            if isinstance(e, (VLMProcessingError, VLMTimeoutError)):
                raise
            raise VLMProcessingError(f"VLM processing failed: {e!s}", image_path=image_path, model_name=config.model_name, error_details=str(e))

    def process_batch_with_vlm(self, image_paths: list[str], prompts: list[str], config) -> list[dict[str, Any]]:
        """
        Process batch of images with VLM.

        Args:
            image_paths: List of image file paths
            prompts: List of VLM prompts
            config: VLM configuration

        Returns:
            List[Dict]: VLM results for each image

        Raises:
            VLMProcessingError: If batch processing fails
        """
        if len(image_paths) != len(prompts):
            raise VLMProcessingError("Number of image paths must match number of prompts", error_details=f"Images: {len(image_paths)}, Prompts: {len(prompts)}")

        results = []
        successful = 0
        failed = 0

        try:
            # Convert config if needed
            config = _convert_config(config)

            # Ensure model is loaded once for the batch
            self._ensure_model_loaded(config)

            for image_path, prompt in zip(image_paths, prompts, strict=False):
                try:
                    result = self.process_image_with_vlm(image_path, prompt, config)
                    results.append(result)
                    successful += 1

                except Exception as e:
                    # For batch processing, continue with other images on individual failures
                    error_result = {"description": f"Error processing {image_path}: {e!s}", "confidence_score": None, "processing_time": 0.0, "model_info": {"name": config.model_name, "version": "unknown"}, "error": str(e)}
                    results.append(error_result)
                    failed += 1

            # Cleanup after batch processing
            self._cleanup_batch_resources()

            return results

        except Exception as e:
            raise VLMProcessingError(f"Batch VLM processing failed: {e!s}", model_name=config.model_name, error_details=f"Processed {successful}/{len(image_paths)} images successfully")

    def _ensure_model_loaded(self, config: ModelConfiguration) -> LoadedModel:
        """Ensure VLM model is loaded and ready."""
        if not self.registry.is_model_loaded(config.model_name):
            return self.registry.load_model(config)
        return self.registry.get_current_model()

    def _process_with_timeout(self, model, image_path: str, prompt: str, timeout_seconds: int) -> dict[str, Any]:
        """Process image with timeout handling."""
        import signal

        def timeout_handler(signum, frame):
            raise VLMTimeoutError(f"Processing timed out after {timeout_seconds} seconds")

        # Set up timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)

        try:
            result = model.process_image(image_path, prompt)
            signal.alarm(0)  # Cancel timeout
            return result

        except VLMTimeoutError:
            raise
        except Exception as e:
            signal.alarm(0)  # Cancel timeout
            raise e
        finally:
            signal.signal(signal.SIGALRM, old_handler)

    def _create_fallback_result(self, image_path: str, loaded_model: LoadedModel, processing_time: float) -> dict[str, Any]:
        """Create fallback result when VLM times out."""
        import os

        filename = os.path.basename(image_path)

        return {"description": f"Timeout fallback description for {filename}", "confidence_score": None, "processing_time": processing_time, "model_info": loaded_model.model_info}

    def _create_timeout_result(self, image_path: str, loaded_model: LoadedModel, processing_time: float) -> dict[str, Any]:
        """Create partial result when VLM times out but should continue."""
        import os

        filename = os.path.basename(image_path)

        return {"description": f"Partial description for {filename} (processing interrupted)", "confidence_score": None, "processing_time": processing_time, "model_info": loaded_model.model_info}

    def _cleanup_batch_resources(self):
        """Clean up resources after batch processing."""
        # For now, just cleanup the current model
        if self._current_model is not None:
            self._current_model.cleanup()

        # Registry cleanup for memory management
        self.registry.cleanup_models()

    def cleanup(self):
        """Clean up processor resources."""
        if self._current_model is not None:
            self._current_model.cleanup()
            self._current_model = None

        self.registry.cleanup_models()


# Global processor instance
_global_processor = None


def get_global_vlm_processor() -> VLMProcessor:
    """Get or create global VLM processor instance."""
    global _global_processor

    if _global_processor is None:
        _global_processor = VLMProcessor()

    return _global_processor
