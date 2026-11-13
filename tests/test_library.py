"""Tests for collection operations (add, remove, search, statistics)."""

import pytest

from personal_library_manager import Book, Library


def test_add_book_appends_and_returns_book(library):
    book = library.add_book("Atomic Habits", "James Clear", 2018, "Self-Help", True)

    assert isinstance(book, Book)
    assert len(library) == 1
    assert library.books == (book,)


def test_add_book_allows_duplicate_titles(library):
    library.add_book("Dune", "Frank Herbert", 1965, "Sci-Fi")
    library.add_book("Dune", "Frank Herbert", 1965, "Sci-Fi")

    assert len(library) == 2


def test_add_rejects_invalid_book(library):
    with pytest.raises(ValueError):
        library.add_book("", "Author", 2020, "Genre")

    assert len(library) == 0


def test_add_requires_book_instance(library):
    with pytest.raises(TypeError):
        library.add({"title": "Dune"})


def test_remove_book_is_case_insensitive(library):
    library.add_book("Atomic Habits", "James Clear", 2018, "Self-Help")

    removed = library.remove_book("  atomic habits  ")

    assert removed is not None
    assert removed.title == "Atomic Habits"
    assert len(library) == 0


def test_remove_missing_book_returns_none(library):
    assert library.remove_book("Ghost Book") is None


def test_remove_only_removes_first_match(library):
    library.add_book("Dune", "Frank Herbert", 1965, "Sci-Fi")
    library.add_book("Dune", "Frank Herbert", 1965, "Sci-Fi")

    library.remove_book("Dune")

    assert len(library) == 1


def test_search_by_title_is_substring_and_case_insensitive(library):
    library.add_book("Atomic Habits", "James Clear", 2018, "Self-Help")
    library.add_book("Deep Work", "Cal Newport", 2016, "Productivity")

    results = library.search("ATOMIC")

    assert [book.title for book in results] == ["Atomic Habits"]


def test_search_by_author(library):
    library.add_book("Atomic Habits", "James Clear", 2018, "Self-Help")
    library.add_book("Deep Work", "Cal Newport", 2016, "Productivity")

    results = library.search("newport", field="author")

    assert [book.title for book in results] == ["Deep Work"]


def test_search_empty_keyword_returns_everything(library):
    library.add_book("Atomic Habits", "James Clear", 2018, "Self-Help")
    library.add_book("Deep Work", "Cal Newport", 2016, "Productivity")

    assert len(library.search("")) == 2


def test_search_rejects_unknown_field(library):
    with pytest.raises(ValueError):
        library.search("x", field="genre")


def test_statistics_for_empty_library(library):
    assert library.statistics() == {
        "total": 0,
        "read": 0,
        "unread": 0,
        "percentage": 0.0,
    }


def test_statistics_counts_and_percentage(populated_library):
    stats = populated_library.statistics()

    assert stats == {
        "total": 2,
        "read": 1,
        "unread": 1,
        "percentage": 50.0,
    }


def test_statistics_percentage_rounding(library):
    for index in range(3):
        library.add_book("Book {0}".format(index), "Author", 2000, "Genre", read=(index == 0))

    assert library.statistics()["percentage"] == 33.33


def test_iteration_and_books_snapshot(library):
    book = library.add_book("Dune", "Frank Herbert", 1965, "Sci-Fi")

    assert list(library) == [book]
    assert library.books == (book,)
    assert isinstance(library.books, tuple)


def test_clear_empties_memory(library):
    library.add_book("Dune", "Frank Herbert", 1965, "Sci-Fi")
    library.clear()

    assert len(library) == 0


def test_library_accepts_string_data_dir(tmp_path):
    lib = Library(data_dir=str(tmp_path), auto_load=False)

    assert lib.data_dir.name == tmp_path.name
    assert lib.json_path == tmp_path / "library.json"
    assert lib.text_path == tmp_path / "library.txt"
