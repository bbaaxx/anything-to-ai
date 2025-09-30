"""
Contract tests for audio_processor module API.
Tests FR-019, FR-020: Public API functions and configuration factory.
"""

import inspect


class TestAudioModuleAPIContract:
    """Test that module exports required API functions with correct signatures."""

    def test_process_audio_function_exists(self):
        """Test that process_audio function is available."""
        import audio_processor
        assert hasattr(audio_processor, 'process_audio')
        assert callable(audio_processor.process_audio)

    def test_process_audio_signature(self):
        """Test process_audio has correct signature."""
        import audio_processor
        sig = inspect.signature(audio_processor.process_audio)
        params = list(sig.parameters.keys())
        assert 'file_path' in params
        assert 'config' in params
        # config should have default value
        assert sig.parameters['config'].default is not inspect.Parameter.empty or sig.parameters['config'].default is None

    def test_process_audio_batch_function_exists(self):
        """Test that process_audio_batch function is available."""
        import audio_processor
        assert hasattr(audio_processor, 'process_audio_batch')
        assert callable(audio_processor.process_audio_batch)

    def test_process_audio_batch_signature(self):
        """Test process_audio_batch has correct signature."""
        import audio_processor
        sig = inspect.signature(audio_processor.process_audio_batch)
        params = list(sig.parameters.keys())
        assert 'file_paths' in params
        assert 'config' in params

    def test_validate_audio_function_exists(self):
        """Test that validate_audio function is available."""
        import audio_processor
        assert hasattr(audio_processor, 'validate_audio')
        assert callable(audio_processor.validate_audio)

    def test_validate_audio_signature(self):
        """Test validate_audio has correct signature."""
        import audio_processor
        sig = inspect.signature(audio_processor.validate_audio)
        params = list(sig.parameters.keys())
        assert 'file_path' in params

    def test_create_config_function_exists(self):
        """Test that create_config function is available."""
        import audio_processor
        assert hasattr(audio_processor, 'create_config')
        assert callable(audio_processor.create_config)

    def test_create_config_signature(self):
        """Test create_config has correct signature."""
        import audio_processor
        sig = inspect.signature(audio_processor.create_config)
        params = list(sig.parameters.keys())
        # All parameters should have defaults
        assert all(p.default is not inspect.Parameter.empty for p in sig.parameters.values())

    def test_create_config_parameters(self):
        """Test create_config has expected parameters."""
        import audio_processor
        sig = inspect.signature(audio_processor.create_config)
        params = list(sig.parameters.keys())
        expected = ['model', 'quantization', 'batch_size', 'language',
                   'output_format', 'timeout_seconds', 'progress_callback',
                   'verbose', 'max_duration_seconds']
        for param in expected:
            assert param in params, f"Expected parameter '{param}' not found"

    def test_get_supported_formats_function_exists(self):
        """Test that get_supported_formats function is available."""
        import audio_processor
        assert hasattr(audio_processor, 'get_supported_formats')
        assert callable(audio_processor.get_supported_formats)

    def test_get_supported_formats_signature(self):
        """Test get_supported_formats has no required parameters."""
        import audio_processor
        sig = inspect.signature(audio_processor.get_supported_formats)
        required_params = [p for p in sig.parameters.values()
                          if p.default is inspect.Parameter.empty]
        assert len(required_params) == 0

    def test_get_audio_info_function_exists(self):
        """Test that get_audio_info function is available."""
        import audio_processor
        assert hasattr(audio_processor, 'get_audio_info')
        assert callable(audio_processor.get_audio_info)

    def test_get_audio_info_signature(self):
        """Test get_audio_info has correct signature."""
        import audio_processor
        sig = inspect.signature(audio_processor.get_audio_info)
        params = list(sig.parameters.keys())
        assert 'file_path' in params
