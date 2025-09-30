"""Contract tests for pre-commit configuration.

These tests verify that .pre-commit-config.yaml is correctly configured
with all required hooks and settings.
"""

import os
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def repo_root():
    """Return the repository root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def precommit_config(repo_root):
    """Load and return the pre-commit configuration."""
    config_path = repo_root / ".pre-commit-config.yaml"
    if not config_path.exists():
        pytest.fail(f"Pre-commit config file not found at {config_path}")
    with open(config_path) as f:
        return yaml.safe_load(f)


def test_precommit_config_file_exists(repo_root):
    """Verify .pre-commit-config.yaml exists at repository root."""
    config_path = repo_root / ".pre-commit-config.yaml"
    assert config_path.exists(), f"Pre-commit config file missing: {config_path}"
    assert config_path.is_file(), "Pre-commit config is not a file"


def test_precommit_config_is_valid_yaml(repo_root):
    """Verify .pre-commit-config.yaml is valid YAML."""
    config_path = repo_root / ".pre-commit-config.yaml"
    try:
        with open(config_path) as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        pytest.fail(f"Invalid YAML in pre-commit config: {e}")


def test_precommit_config_has_required_hooks(precommit_config):
    """Verify all required hooks are present in configuration."""
    required_hooks = {"ruff", "ruff-format", "trailing-whitespace"}
    repos = precommit_config.get("repos", [])
    found_hooks = set()

    for repo in repos:
        hooks = repo.get("hooks", [])
        for hook in hooks:
            hook_id = hook.get("id", "")
            found_hooks.add(hook_id)

    missing_hooks = required_hooks - found_hooks
    assert not missing_hooks, f"Missing required hooks: {missing_hooks}"


def test_precommit_config_python_version(precommit_config):
    """Verify default_language_version is set to python3.13."""
    lang_version = precommit_config.get("default_language_version", {})
    python_version = lang_version.get("python", "")
    assert python_version == "python3.13", f"Expected python3.13, got {python_version}"


def test_ruff_hook_has_fix_arg(precommit_config):
    """Verify ruff hook includes --fix argument."""
    repos = precommit_config.get("repos", [])
    ruff_hook = None

    for repo in repos:
        if "ruff-pre-commit" in repo.get("repo", ""):
            hooks = repo.get("hooks", [])
            for hook in hooks:
                if hook.get("id") == "ruff":
                    ruff_hook = hook
                    break

    assert ruff_hook is not None, "Ruff hook not found in configuration"
    args = ruff_hook.get("args", [])
    assert "--fix" in args, "Ruff hook missing --fix argument"


def test_ruff_runs_before_format(precommit_config):
    """Verify ruff hook runs before ruff-format hook."""
    repos = precommit_config.get("repos", [])
    hook_order = []

    for repo in repos:
        hooks = repo.get("hooks", [])
        for hook in hooks:
            hook_id = hook.get("id", "")
            if hook_id in ("ruff", "ruff-format"):
                hook_order.append(hook_id)

    assert len(hook_order) >= 2, "Both ruff and ruff-format hooks must be present"
    ruff_index = hook_order.index("ruff")
    format_index = hook_order.index("ruff-format")
    assert ruff_index < format_index, "ruff must run before ruff-format"