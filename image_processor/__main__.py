"""CLI entry point for python -m image_processor."""
from .cli import main

if __name__ == "__main__":
    import sys
    sys.exit(main())