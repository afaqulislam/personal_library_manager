"""Core library management and persistence logic."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from .models import Book
from .paths import default_data_dir

PathLike = Union[str, "os.PathLike[str]"]


class Library:
    """An in-memory book collection backed by JSON and plain-text files.

    The class is responsible for loading, validating, querying and saving the
    collection. It never stores user data inside the installed package.
    """

    JSON_FILENAME = "library.json"
    TEXT_FILENAME = "library.txt"

    def __init__(self, data_dir: Optional[PathLike] = None, auto_load: bool = True) -> None:
        self.data_dir: Path = Path(data_dir).expanduser() if data_dir is not None else default_data_dir()
        self._books: List[Book] = []
        self.last_error: Optional[str] = None
        self.migration_note: Optional[str] = None
        if auto_load:
            self.load()

    # ------------------------------------------------------------------
    # Container protocol
    # ------------------------------------------------------------------
    def __len__(self) -> int:
        return len(self._books)

    def __iter__(self) -> Iterator[Book]:
        return iter(self._books)

    @property
    def books(self) -> Tuple[Book, ...]:
        """A read-only snapshot of the collection."""
        return tuple(self._books)

    @property
    def json_path(self) -> Path:
        return self.data_dir / self.JSON_FILENAME

    @property
    def text_path(self) -> Path:
        return self.data_dir / self.TEXT_FILENAME

    # ------------------------------------------------------------------
    # Mutations
    # ------------------------------------------------------------------
    def add_book(self, title: Any, author: Any, year: Any, genre: Any, read: Any = False) -> Book:
        """Add one book and return the created ``Book``.

        Raises ``ValueError`` when any field is invalid.
        """
        book = Book(title=title, author=author, year=year, genre=genre, read=read)
        self._books.append(book)
        return book

    def add(self, book: Book) -> Book:
        """Add an existing ``Book`` instance."""
        if not isinstance(book, Book):
            raise TypeError("Expected a Book instance.")
        self._books.append(book)
        return book

    def remove_book(self, title: str) -> Optional[Book]:
        """Remove the first book whose title matches (case-insensitive).

        Returns the removed ``Book`` or ``None`` when nothing matched.
        """
        needle = str(title).strip().lower()
        for index, book in enumerate(self._books):
            if book.title.lower() == needle:
                return self._books.pop(index)
        return None

    def clear(self) -> None:
        """Remove every book from memory (does not touch the saved files)."""
        self._books = []

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------
    def search(self, keyword: str, field: str = "title") -> List[Book]:
        """Search by ``title`` or ``author`` using a case-insensitive substring."""
        field = str(field).strip().lower()
        if field not in {"title", "author"}:
            raise ValueError("Search field must be 'title' or 'author'.")

        needle = str(keyword).strip().lower()
        results: List[Book] = []
        for book in self._books:
            haystack = book.title.lower() if field == "title" else book.author.lower()
            if needle in haystack:
                results.append(book)
        return results

    def statistics(self) -> Dict[str, Any]:
        """Return totals and reading completion percentage."""
        total = len(self._books)
        read_books = sum(1 for book in self._books if book.read)
        percentage = (read_books / total * 100) if total else 0.0
        return {
            "total": total,
            "read": read_books,
            "unread": total - read_books,
            "percentage": round(percentage, 2),
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def load(self) -> int:
        """Load books from ``library.json`` and return the number loaded.

        Missing files simply produce an empty library. Corrupted files are
        moved aside to a timestamped backup before starting empty, so no user
        data is silently destroyed.
        """
        self._books = []
        self.last_error = None
        self.migration_note = None

        if not self.json_path.exists():
            self._migrate_legacy_file()

        if not self.json_path.exists():
            return 0

        try:
            with self.json_path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, ValueError) as exc:
            backup = self._backup_corrupt_file()
            message = "Could not read {0}: {1}.".format(self.json_path.name, exc)
            if backup is not None:
                message += " A backup was saved as {0}.".format(backup.name)
            self.last_error = message
            return 0

        if not isinstance(payload, list):
            backup = self._backup_corrupt_file()
            message = (
                "Invalid data in {0}: expected a list of books.".format(self.json_path.name)
            )
            if backup is not None:
                message += " A backup was saved as {0}.".format(backup.name)
            self.last_error = message
            return 0

        skipped = 0
        for entry in payload:
            try:
                self._books.append(Book.from_dict(entry))
            except (TypeError, ValueError):
                skipped += 1

        if skipped:
            noun = "entry" if skipped == 1 else "entries"
            self.last_error = "Skipped {count} invalid book {noun} in {name}.".format(
                count=skipped, noun=noun, name=self.json_path.name
            )
        return len(self._books)

    def save(self) -> Tuple[Path, Path]:
        """Write JSON and TXT files atomically and return their paths."""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        payload = [book.to_dict() for book in self._books]
        json_text = json.dumps(payload, indent=4, ensure_ascii=False) + "\n"
        self._write_atomic(self.json_path, json_text)
        self._write_atomic(self.text_path, self.export_text())
        return self.json_path, self.text_path

    def export_text(self) -> str:
        """Return the human-readable TXT representation of the library."""
        lines = [
            "Title: {title} | Author: {author} | Year: {year} | Genre: {genre} | Read: {read}\n".format(
                title=book.title,
                author=book.author,
                year=book.year,
                genre=book.genre,
                read="Yes" if book.read else "No",
            )
            for book in self._books
        ]
        return "".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _migrate_legacy_file(self) -> None:
        """Import a valid ``library.json`` from the current working directory.

        This keeps data created by the original single-file script working
        after the switch to a user data directory. Only valid JSON lists are
        imported.
        """
        legacy = Path.cwd() / self.JSON_FILENAME
        try:
            if not legacy.is_file() or legacy.resolve() == self.json_path.resolve():
                return
        except OSError:
            return

        try:
            with legacy.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, ValueError):
            return

        if not isinstance(payload, list):
            return

        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(legacy), str(self.json_path))
        except OSError:
            return

        self.migration_note = "Imported existing {0} from {1}.".format(self.JSON_FILENAME, legacy)

    def _backup_corrupt_file(self) -> Optional[Path]:
        """Move a broken JSON file aside and return the backup path."""
        if not self.json_path.exists():
            return None

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        target = self.json_path.with_name("{0}.corrupt-{1}".format(self.JSON_FILENAME, stamp))
        counter = 1
        while target.exists():
            target = self.json_path.with_name(
                "{0}.corrupt-{1}-{2}".format(self.JSON_FILENAME, stamp, counter)
            )
            counter += 1

        try:
            os.replace(str(self.json_path), str(target))
        except OSError:
            return None
        return target

    @staticmethod
    def _write_atomic(path: Path, content: str) -> None:
        """Write ``content`` to ``path`` using a temporary file and rename."""
        handle = tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=str(path.parent),
            prefix=".{0}.".format(path.name),
            suffix=".tmp",
            delete=False,
        )
        temp_name = handle.name
        try:
            with handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, str(path))
        except BaseException:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
            raise
