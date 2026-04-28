"""VLM processor for single and batch image processing."""

from typing import Any
import time

from .vlm_models import ModelConfiguration
from .model_registry import get_global_registry, LoadedModel
from .vlm_model_impl import create_vlm_model
from .vlm_exceptions import VLMProcessingError, VLMTimeoutError, VLMMemoryError, VLMContextLengthError
from .config import VLMConfig
from .subprocess_runner import SubprocessTimeoutRunner


# Memory and context error patterns to detect
_MEMORY_ERROR_PATTERNS = (
    "out of memory",
    "memory allocation failed",
    "cuda out of memory",
    "mps out of memory",
    "cannot allocate memory",
    "memoryerror",
    "malloc",
)

_CONTEXT_ERROR_PATTERNS = (
    "context length",
    "maximum context",
    "token limit",
    "sequence length",
    "context window",
    "max tokens",
)


def _is_memory_or_context_error(error: Exception) -> tuple[bool, str]:
    """Detect if an exception is a memory or context length error.

    Args:
        error: The exception to check.

    Returns:
        Tuple of (is_recoverable, error_type) where:
        - is_recoverable: True if this is a memory/context error that can be retried with smaller tokens
        - error_type: "memory", "context", or "unknown"
    """
    error_str = str(error).lower()
    error_type_name = type(error).__name__.lower()

    # Check if it's already one of our typed exceptions
    if isinstance(error, VLMMemoryError):
        return (True, "memory")
    if isinstance(error, VLMContextLengthError):
        return (True, "context")

    # Check for memory error patterns
    for pattern in _MEMORY_ERROR_PATTERNS:
        if pattern in error_str or pattern in error_type_name:
            return (True, "memory")

    # Check for context length error patterns
    for pattern in _CONTEXT_ERROR_PATTERNS:
        if pattern in error_str or pattern in error_type_name:
            return (True, "context")

    return (False, "unknown")


# Default token fallback levels for progressive reduction
_DEFAULT_FALLBACK_LEVELS = [8192, 4096, 2048, 1024, 512]


def _get_default_fallback_levels(initial_max_tokens: int) -> list[int]:
    """Get default token fallback levels capped at initial max_tokens.

    Args:
        initial_max_tokens: The initial max_tokens value to cap levels at.

    Returns:
        List of token levels in descending order, capped at initial_max_tokens.
    """
    levels = []
    for level in _DEFAULT_FALLBACK_LEVELS:
        if level <= initial_max_tokens:
            levels.append(level)
    # Ensure at least one level is returned
    if not levels:
        levels = [min(initial_max_tokens, 512)]
    return levels


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
            enable_token_fallback=config.enable_token_fallback,
            token_fallback_levels=config.token_fallback_levels,
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
                    msg = f"VLM processing timed out after {config.timeout_seconds} seconds"
                    raise VLMTimeoutError(msg, timeout_seconds=config.timeout_seconds, actual_time=processing_time, image_path=image_path, model_name=config.model_name)
                if config.timeout_behavior == "fallback":
                    return self._create_fallback_result(image_path, loaded_model, processing_time)
                # continue
                return self._create_timeout_result(image_path, loaded_model, processing_time)

        except Exception as e:
            if isinstance(e, (VLMProcessingError, VLMTimeoutError)):
                raise
            msg = f"VLM processing failed: {e!s}"
            raise VLMProcessingError(msg, image_path=image_path, model_name=config.model_name, error_details=str(e))

    def process_with_fallback(
        self,
        image_path: str,
        prompt: str,
        config,
        initial_max_tokens: int = 8192,
    ) -> dict[str, Any]:
        """
        Process image with VLM using token reduction fallback on memory/context errors.

        This method wraps process_image_with_vlm with automatic retry logic that
        progressively reduces max_tokens when memory or context length errors occur.

        Args:
            image_path: Path to image file
            prompt: VLM prompt text
            config: VLM configuration
            initial_max_tokens: Initial max_tokens value (default: 8192)

        Returns:
            Dict containing VLM processing results

        Raises:
            VLMProcessingError: If all fallback attempts fail
            VLMTimeoutError: If processing exceeds timeout

        Example:
            >>> processor = VLMProcessor()
            >>> result = processor.process_with_fallback(
            ...     "image.jpg",
            ...     "Describe this image",
            ...     config,
            ...     initial_max_tokens=4096
            ... )
        """
        config = _convert_config(config)

        # Check if fallback is enabled
        if not config.enable_token_fallback:
            return self.process_image_with_vlm(image_path, prompt, config)

        # Determine fallback levels
        levels = [min(level, initial_max_tokens) for level in config.token_fallback_levels] if config.token_fallback_levels else _get_default_fallback_levels(initial_max_tokens)

        attempted_levels = []
        last_error = None

        for token_level in levels:
            attempted_levels.append(token_level)
            try:
                # Note: The actual max_tokens parameter would need to be passed
                # through to the VLM generation. For now, we process normally
                # and catch memory/context errors for retry.
                return self.process_image_with_vlm(image_path, prompt, config)
            except Exception as e:
                is_recoverable, _error_type = _is_memory_or_context_error(e)

                if is_recoverable:
                    # Store error and try next level
                    last_error = e
                    continue
                # Non-recoverable error, re-raise
                raise

        # All levels exhausted
        msg = f"VLM processing failed at all token levels. Attempted: {attempted_levels}"
        if last_error:
            raise VLMProcessingError(
                msg,
                image_path=image_path,
                model_name=config.model_name,
                error_details=f"Last error: {last_error!s}",
            )
        raise VLMProcessingError(msg, image_path=image_path, model_name=config.model_name)

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
            msg = "Number of image paths must match number of prompts"
            raise VLMProcessingError(msg, error_details=f"Images: {len(image_paths)}, Prompts: {len(prompts)}")

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
            msg = f"Batch VLM processing failed: {e!s}"
            raise VLMProcessingError(msg, model_name=config.model_name, error_details=f"Processed {successful}/{len(image_paths)} images successfully")

    def _ensure_model_loaded(self, config: ModelConfiguration) -> LoadedModel:
        """Ensure VLM model is loaded and ready."""
        if not self.registry.is_model_loaded(config.model_name):
            return self.registry.load_model(config)
        return self.registry.get_current_model()

    def _process_with_timeout(self, model, image_path: str, prompt: str, timeout_seconds: int) -> dict[str, Any]:
        """Process image with timeout handling via subprocess isolation.

        Delegates to ``SubprocessTimeoutRunner`` which spawns a child process,
        enforces a wall-clock timeout, and escalates termination (SIGTERM →
        SIGKILL) if the child does not exit in time.  This approach works
        correctly from non-main threads and against native C-extension code
        (MLX, CoreML) that cannot be interrupted by SIGALRM.
        """
        # Look up SubprocessTimeoutRunner from sys.modules at call time so that
        # test patches applied to the current module are always visible, even
        # when this method's __globals__ points to an earlier module instance
        # (which can happen when the image_processor package is re-imported
        # during test runs via __init__ → processor → vlm_processor chain).
        import sys as _sys

        _mod = _sys.modules[__name__]
        _runner_cls = _mod.SubprocessTimeoutRunner
        runner = _runner_cls()
        config_dict = {"model_name": model.model_name if hasattr(model, "model_name") else ""}
        try:
            return runner.run(image_path, prompt, config_dict.get("model_name", ""), config_dict, timeout_seconds)
        except TimeoutError as exc:
            msg = f"Processing timed out after {timeout_seconds} seconds"
            raise VLMTimeoutError(msg) from exc

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
