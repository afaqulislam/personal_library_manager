"""Interactive command-line interface for the Personal Library Manager."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from . import __version__
from .library import Library

YES_VALUES = {"yes", "y", "true", "1", "read"}


def _configure_stdio() -> None:
    """Make emoji output safe when stdout/stderr are redirected on Windows."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):
            pass


def display_menu() -> None:
    """Print the main menu."""
    print("\n\U0001F4DA Welcome to your Personal Library Manager!")
    print("1. Add a book")
    print("2. Remove a book")
    print("3. Search for a book")
    print("4. Display all books")
    print("5. Display statistics")
    print("6. Exit")


def add_book(library: Library) -> None:
    """Prompt for a new book and add it to the library."""
    title = input("Enter the book title: ").strip()
    author = input("Enter the author: ").strip()
    year = input("Enter the publication year: ").strip()
    genre = input("Enter the genre: ").strip()
    read_status = input("Have you read this book? (yes/no): ").strip().lower()

    if not title or not author or not year or not genre:
        print("\u26A0\uFE0F All fields are required!")
        return

    if not year.isdigit():
        print("\u26A0\uFE0F Publication year must be a number!")
        return

    try:
        book = library.add_book(
            title=title,
            author=author,
            year=int(year),
            genre=genre,
            read=read_status in YES_VALUES,
        )
    except ValueError as exc:
        print("\u26A0\uFE0F {0}".format(exc))
        return

    print("\u2705 '{0}' added successfully!".format(book.title))


def remove_book(library: Library) -> None:
    """Prompt for a title and remove the matching book."""
    title = input("Enter the title of the book to remove: ").strip()
    removed = library.remove_book(title)
    if removed is None:
        print("\u274C Book '{0}' not found!".format(title))
    else:
        print("\u2705 '{0}' removed successfully!".format(removed.title))


def search_book(library: Library) -> None:
    """Prompt for a search mode and keyword, then print matches."""
    print("\nSearch by:")
    print("1. Title")
    print("2. Author")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice == "1":
        keyword = input("Enter the book title: ").strip()
        results = library.search(keyword, field="title")
    elif choice == "2":
        keyword = input("Enter the author's name: ").strip()
        results = library.search(keyword, field="author")
    else:
        print("\u274C Invalid choice!")
        return

    if not results:
        print("\u274C No matching books found!")
        return

    print("\n\U0001F50E Matching Books:")
    for index, book in enumerate(results, start=1):
        print("{0}. {1}".format(index, book.describe()))


def display_books(library: Library) -> None:
    """Print every book in the library."""
    if not len(library):
        print("\U0001F4D6 Your library is empty!")
        return

    print("\n\U0001F4DA Your Library:")
    for index, book in enumerate(library, start=1):
        print("{0}. {1}".format(index, book.describe()))


def display_statistics(library: Library) -> None:
    """Print collection totals and reading completion."""
    stats = library.statistics()
    if stats["total"] == 0:
        print("\U0001F4CA Your library is empty! Add some books first.")
        return

    print("\n\U0001F4CA Library Statistics:")
    print("\U0001F4DA Total books: {0}".format(stats["total"]))
    print("\u2705 Books read: {0}".format(stats["read"]))
    print("\U0001F4D6 Percentage read: {0:.2f}%".format(stats["percentage"]))


def save_library(library: Library) -> bool:
    """Save the library and report the resulting paths."""
    try:
        json_path, text_path = library.save()
    except OSError as exc:
        print("\u274C Could not save the library: {0}".format(exc))
        return False

    print("\U0001F4BE Library saved to:")
    print("   \u2022 {0}".format(json_path))
    print("   \u2022 {0}".format(text_path))
    return True


def run_menu(library: Library) -> None:
    """Run the interactive menu loop until the user chooses Exit."""
    actions = {
        "1": add_book,
        "2": remove_book,
        "3": search_book,
        "4": display_books,
        "5": display_statistics,
    }

    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()
        if choice == "6":
            save_library(library)
            print("\U0001F4CC Exiting... Goodbye!")
            return
        action = actions.get(choice)
        if action is None:
            print("\u274C Invalid choice! Please enter a number between 1 and 6.")
            continue
        action(library)


def build_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="personal_library_manager",
        description=(
            "Manage your personal book collection from the terminal. "
            "Add, remove, search, browse and track reading progress."
        ),
    )
    parser.add_argument(
        "--data-dir",
        metavar="PATH",
        default=None,
        help="Directory used to store library.json and library.txt.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {0}".format(__version__),
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """CLI entry point. Returns a process exit code."""
    _configure_stdio()
    args = build_parser().parse_args(argv)

    library = Library(data_dir=args.data_dir)

    if library.migration_note:
        print("\U0001F4E6 {0}".format(library.migration_note))
    if library.last_error:
        print("\u26A0\uFE0F {0}".format(library.last_error))
    elif library.json_path.exists():
        print("\U0001F4C2 Library loaded from {0} successfully!".format(library.json_path))

    try:
        run_menu(library)
    except (KeyboardInterrupt, EOFError):
        print("")
        save_library(library)
        print("\U0001F4CC Exiting... Goodbye!")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
