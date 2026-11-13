"""Tests for the Book model and validation helpers."""

import pytest

from personal_library_manager import Book
from personal_library_manager.models import normalize_read, normalize_year


def make_book(**overrides):
    data = {
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "genre": "Science Fiction",
        "read": False,
    }
    data.update(overrides)
    return Book(**data)


def test_book_normalizes_whitespace_and_year():
    book = make_book(title="  Dune  ", author=" Frank Herbert ", year="1965", read="yes")

    assert book.title == "Dune"
    assert book.author == "Frank Herbert"
    assert book.year == 1965
    assert book.read is True


def test_book_describe_and_status():
    read_book = make_book(read=True)
    unread_book = make_book(read=False)

    assert read_book.status == "\u2705 Read"
    assert unread_book.status == "\U0001F4D6 Unread"
    assert read_book.describe() == "Dune by Frank Herbert (1965) - Science Fiction - \u2705 Read"


@pytest.mark.parametrize("field", ["title", "author", "genre"])
@pytest.mark.parametrize("value", ["", "   ", None])
def test_required_text_fields_reject_empty_values(field, value):
    with pytest.raises(ValueError):
        make_book(**{field: value})


@pytest.mark.parametrize("year", ["abc", "", "  ", -1, 0, 2020.5, None, True, False])
def test_invalid_years_are_rejected(year):
    with pytest.raises(ValueError):
        make_book(year=year)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("yes", True),
        ("YES", True),
        ("y", True),
        ("true", True),
        ("1", True),
        ("read", True),
        ("no", False),
        ("", False),
        ("maybe", False),
        (True, True),
        (False, False),
        (1, True),
        (0, False),
    ],
)
def test_read_status_normalization(value, expected):
    assert normalize_read(value) is expected


def test_year_normalization_accepts_numeric_strings():
    assert normalize_year("1999") == 1999
    assert normalize_year(1999) == 1999


def test_to_dict_roundtrip():
    book = make_book(read=True)
    restored = Book.from_dict(book.to_dict())

    assert restored == book
    assert restored.to_dict() == {
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "genre": "Science Fiction",
        "read": True,
    }


def test_from_dict_accepts_legacy_read_values():
    book = Book.from_dict(
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "year": "1965",
            "genre": "Science Fiction",
            "read": "yes",
        }
    )

    assert book.year == 1965
    assert book.read is True


def test_from_dict_missing_field_reports_field_name():
    with pytest.raises(ValueError, match="Missing required field: author"):
        Book.from_dict({"title": "Dune", "year": 1965, "genre": "Sci-Fi"})


@pytest.mark.parametrize("payload", ["not a mapping", 42, ["title"]])
def test_from_dict_rejects_non_mapping(payload):
    with pytest.raises(ValueError):
        Book.from_dict(payload)


@pytest.mark.parametrize("field", ["title", "author", "genre"])
def test_from_dict_rejects_non_string_text_fields(field):
    payload = {
        "title": "Dune",
        "author": "Frank Herbert",
        "year": 1965,
        "genre": "Science Fiction",
    }
    payload[field] = 123

    with pytest.raises(ValueError, match="must be a string"):
        Book.from_dict(payload)
