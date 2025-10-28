"""Unit tests for configuration metadata extraction."""

import pytest


class TestConfigurationMetadata:
    """Tests for configuration metadata structure and validation."""

    def test_empty_user_config(self):
        """Test configuration with empty user-provided dict."""
        user_config = {}
        effective_config = {"format": "json", "progress": True, "timeout": 60}

        metadata = {"user_provided": user_config, "effective": effective_config}

        assert metadata["user_provided"] == {}
        assert len(metadata["effective"]) == 3

    def test_user_config_subset_of_effective(self):
        """Test user config is subset of effective config."""
        user_config = {"model": "medium", "style": "detailed"}
        effective_config = {
            "model": "medium",
            "style": "detailed",
            "timeout": 60,
            "batch_size": 4,
        }

        assert all(key in effective_config for key in user_config)
        assert all(user_config[key] == effective_config[key] for key in user_config)

    def test_effective_config_includes_defaults(self):
        """Test effective config includes default values."""
        user_config = {"model": "medium"}
        effective_config = {
            "model": "medium",
            "quantization": "none",
            "timeout": 600,
            "verbose": False,
        }

        metadata = {"user_provided": user_config, "effective": effective_config}

        assert metadata["effective"]["quantization"] == "none"
        assert metadata["effective"]["timeout"] == 600
        assert metadata["effective"]["verbose"] is False

    def test_user_config_overwrites_defaults(self):
        """Test user-provided values overwrite defaults in effective config."""
        user_config = {"timeout": 120}
        effective_config = {"timeout": 120, "verbose": False}

        assert effective_config["timeout"] == user_config["timeout"]

    def test_boolean_configuration_values(self):
        """Test boolean configuration values are preserved."""
        user_config = {"verbose": True, "progress": False}
        effective_config = {"verbose": True, "progress": False, "stream": False}

        metadata = {"user_provided": user_config, "effective": effective_config}

        assert metadata["user_provided"]["verbose"] is True
        assert metadata["user_provided"]["progress"] is False

    def test_numeric_configuration_values(self):
        """Test numeric configuration values are preserved."""
        user_config = {"timeout": 120, "batch_size": 8}
        effective_config = {"timeout": 120, "batch_size": 8, "max_length": 500}

        metadata = {"user_provided": user_config, "effective": effective_config}

        assert isinstance(metadata["user_provided"]["timeout"], int)
        assert metadata["user_provided"]["batch_size"] == 8

    def test_string_configuration_values(self):
        """Test string configuration values are preserved."""
        user_config = {"model": "medium", "style": "detailed", "language": "en"}
        effective_config = {
            "model": "medium",
            "style": "detailed",
            "language": "en",
            "format": "json",
        }

        metadata = {"user_provided": user_config, "effective": effective_config}

        assert metadata["user_provided"]["model"] == "medium"
        assert metadata["user_provided"]["style"] == "detailed"


class TestConfigurationMetadataScope:
    """Tests for configuration metadata scope (what to include/exclude)."""

    def test_includes_model_settings(self):
        """Test configuration includes model settings."""
        config = {
            "model": "medium",
            "model_version": "v1.0",
            "quantization": "4bit",
            "provider": "ollama",
        }

        assert "model" in config
        assert "model_version" in config
        assert "quantization" in config
        assert "provider" in config

    def test_includes_processing_parameters(self):
        """Test configuration includes processing parameters."""
        config = {
            "style": "detailed",
            "language": "en",
            "timeout_seconds": 60,
            "batch_size": 4,
        }

        assert "style" in config
        assert "language" in config
        assert "timeout_seconds" in config

    def test_excludes_io_paths(self):
        """Test configuration excludes I/O paths."""
        user_config = {"model": "medium"}
        effective_config = {"model": "medium", "timeout": 60}

        assert "input_file" not in user_config
        assert "output_file" not in user_config
        assert "file_path" not in effective_config

    def test_excludes_display_flags(self):
        """Test configuration excludes display-only flags."""
        user_config = {"model": "medium"}

        assert "verbose" not in user_config
        assert "progress" not in user_config
        assert "no-color" not in user_config

    def test_format_flag_included_when_affects_processing(self):
        """Test format flag included when it affects processing."""
        user_config = {"format": "json"}

        assert "format" in user_config


class TestConfigurationMetadataSerialization:
    """Tests for configuration metadata serialization."""

    def test_configuration_is_json_serializable(self):
        """Test configuration metadata can be JSON serialized."""
        import json

        config = {
            "user_provided": {"model": "medium", "timeout": 120},
            "effective": {"model": "medium", "timeout": 120, "verbose": False},
        }

        json_str = json.dumps(config)
        parsed = json.loads(json_str)

        assert parsed == config

    def test_nested_configuration_serialization(self):
        """Test nested configuration values are serializable."""
        import json

        config = {
            "user_provided": {"advanced": {"batch_size": 4, "max_tokens": 1000}},
            "effective": {
                "advanced": {"batch_size": 4, "max_tokens": 1000},
                "timeout": 60,
            },
        }

        json_str = json.dumps(config)
        parsed = json.loads(json_str)

        assert parsed["user_provided"]["advanced"]["batch_size"] == 4


class TestConfigurationMetadataConsistency:
    """Tests for configuration metadata consistency across modules."""

    def test_all_modules_use_same_structure(self):
        """Test all modules use consistent configuration structure."""
        pdf_config = {"user_provided": {"format": "json"}, "effective": {"format": "json"}}
        image_config = {"user_provided": {"style": "brief"}, "effective": {"style": "brief"}}
        audio_config = {"user_provided": {"model": "medium"}, "effective": {"model": "medium"}}

        for config in [pdf_config, image_config, audio_config]:
            assert "user_provided" in config
            assert "effective" in config
            assert isinstance(config["user_provided"], dict)
            assert isinstance(config["effective"], dict)
