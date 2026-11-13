"""Data models for the Personal Library Manager."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping

READ_BADGE = "\u2705 Read"
UNREAD_BADGE = "\U0001F4D6 Unread"


def _clean_text(value: Any, field: str) -> str:
    """Validate and normalize a required text field."""
    if value is None:
        raise ValueError("{0} is required.".format(field.capitalize()))
    text = str(value).strip()
    if not text:
        raise ValueError("{0} is required.".format(field.capitalize()))
    return text


def normalize_year(value: Any) -> int:
    """Coerce a publication year to a positive integer."""
    if isinstance(value, bool):
        raise ValueError("Publication year must be a number.")

    if isinstance(value, int):
        year = value
    elif isinstance(value, str) and value.strip().isdigit():
        year = int(value.strip())
    else:
        raise ValueError("Publication year must be a number.")

    if year <= 0:
        raise ValueError("Publication year must be a positive number.")
    return year


def normalize_read(value: Any) -> bool:
    """Interpret the many ways a read status may be represented."""
    if isinstance(value, str):
        return value.strip().lower() in {"yes", "y", "true", "1", "read"}
    return bool(value)


@dataclass
class Book:
    """A single book in the library.

    All values are validated on construction, so a ``Book`` instance is always
    safe to serialize and display.
    """

    title: str
    author: str
    year: int
    genre: str
    read: bool = False

    def __post_init__(self) -> None:
        self.title = _clean_text(self.title, "title")
        self.author = _clean_text(self.author, "author")
        self.genre = _clean_text(self.genre, "genre")
        self.year = normalize_year(self.year)
        self.read = normalize_read(self.read)

    @property
    def status(self) -> str:
        """Human readable read status badge."""
        return READ_BADGE if self.read else UNREAD_BADGE

    def describe(self) -> str:
        """Return the single-line representation used by the CLI."""
        return "{title} by {author} ({year}) - {genre} - {status}".format(
            title=self.title,
            author=self.author,
            year=self.year,
            genre=self.genre,
            status=self.status,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the book to the on-disk JSON representation."""
        return {
            "title": self.title,
            "author": self.author,
            "year": self.year,
            "genre": self.genre,
            "read": self.read,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Book":
        """Build a book from a JSON object, validating every field."""
        if not isinstance(data, Mapping):
            raise ValueError("A book entry must be a JSON object.")

        missing = [key for key in ("title", "author", "year", "genre") if key not in data]
        if missing:
            raise ValueError("Missing required field: {0}".format(missing[0]))

        for key in ("title", "author", "genre"):
            if not isinstance(data[key], str):
                raise ValueError("{0} must be a string.".format(key.capitalize()))

        return cls(
            title=data["title"],
            author=data["author"],
            year=data["year"],
            genre=data["genre"],
            read=data.get("read", False),
        )
