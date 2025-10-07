"""Unit tests for import structure."""


def test_main_package_import():
    """Test that main package can be imported."""
    import anything_to_ai

    assert anything_to_ai is not None


def test_submodules_importable():
    """Test that submodules can be imported."""
    # Test that submodules exist and can be imported
    submodules = [
        "anything_to_ai.pdf_extractor",
        "anything_to_ai.image_processor",
        "anything_to_ai.audio_processor",
        "anything_to_ai.text_summarizer",
        "anything_to_ai.llm_client",
        "anything_to_ai.progress_tracker",
    ]

    for module_name in submodules:
        try:
            __import__(module_name)
        except ImportError as e:
            # Import might fail due to missing optional dependencies
            # but the module structure should exist
            assert "No module named" not in str(e) or "anything_to_ai" not in str(e), f"Module {module_name} should be importable or fail due to dependencies, not structure"


def test_cli_modules_importable():
    """Test that CLI main modules are importable."""
    cli_modules = [
        "anything_to_ai.pdf_extractor.__main__",
        "anything_to_ai.image_processor.__main__",
        "anything_to_ai.audio_processor.__main__",
        "anything_to_ai.text_summarizer.__main__",
    ]

    for module_name in cli_modules:
        try:
            __import__(module_name)
        except ImportError as e:
            # Import might fail due to missing optional dependencies
            # but the module structure should exist
            assert "No module named" not in str(e) or "anything_to_ai" not in str(e), f"CLI module {module_name} should be importable or fail due to dependencies, not structure"


def test_package_has_version():
    """Test that package has version information."""
    import anything_to_ai

    assert hasattr(anything_to_ai, "__version__")
    assert isinstance(anything_to_ai.__version__, str)
    assert len(anything_to_ai.__version__) > 0


def test_package_has_metadata():
    """Test that package has metadata information."""
    import anything_to_ai

    assert hasattr(anything_to_ai, "__author__")
    assert hasattr(anything_to_ai, "__email__")
    assert isinstance(anything_to_ai.__author__, str)
    assert isinstance(anything_to_ai.__email__, str)
