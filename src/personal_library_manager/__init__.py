"""Personal Library Manager - a CLI for organizing your book collection."""

from .library import Library
from .models import Book

__version__ = "0.1.0"

__all__ = ["Book", "Library", "__version__"]
