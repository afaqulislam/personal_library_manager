"""Shared pytest fixtures."""

import pytest

from personal_library_manager import Book, Library


@pytest.fixture
def library(tmp_path):
    """An empty library backed by a temporary directory."""
    return Library(data_dir=tmp_path)


@pytest.fixture
def sample_books():
    """A representative pair of books (one read, one unread)."""
    return [
        Book("Atomic Habits", "James Clear", 2018, "Self-Help", True),
        Book("Deep Work", "Cal Newport", 2016, "Productivity", False),
    ]


@pytest.fixture
def populated_library(tmp_path, sample_books):
    """A library pre-filled with books and saved to disk."""
    lib = Library(data_dir=tmp_path, auto_load=False)
    for book in sample_books:
        lib.add(book)
    lib.save()
    return lib
