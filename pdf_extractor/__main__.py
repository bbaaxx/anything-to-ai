"""CLI entry point for python -m pdf_extractor."""
from .cli import main

if __name__ == "__main__":
    import sys
    sys.exit(main())
