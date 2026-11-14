"""Tests for the interactive CLI and its entry point."""

import builtins
import json

import pytest

from personal_library_manager import Library, __version__
from personal_library_manager.cli import main


def feed(monkeypatch, values):
    """Replace input() with a scripted sequence that raises EOF when exhausted."""
    answers = iter(values)

    def fake_input(_prompt=""):
        try:
            return next(answers)
        except StopIteration:
            raise EOFError

    monkeypatch.setattr(builtins, "input", fake_input)


def run(monkeypatch, data_dir, values):
    feed(monkeypatch, values)
    return main(["--data-dir", str(data_dir)])


def test_add_book_and_persist(monkeypatch, tmp_path, capsys):
    code = run(
        monkeypatch,
        tmp_path,
        ["1", "Atomic Habits", "James Clear", "2018", "Self-Help", "yes", "4", "6"],
    )

    out = capsys.readouterr().out
    assert code == 0
    assert "'Atomic Habits' added successfully!" in out
    assert "1. Atomic Habits by James Clear (2018) - Self-Help - \u2705 Read" in out
    assert "Library saved to:" in out

    payload = json.loads((tmp_path / "library.json").read_text(encoding="utf-8"))
    assert payload == [
        {
            "title": "Atomic Habits",
            "author": "James Clear",
            "year": 2018,
            "genre": "Self-Help",
            "read": True,
        }
    ]
    text = (tmp_path / "library.txt").read_text(encoding="utf-8")
    assert text == (
        "Title: Atomic Habits | Author: James Clear | Year: 2018 | "
        "Genre: Self-Help | Read: Yes\n"
    )


def test_add_requires_all_fields(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, ["1", "", "Author", "2020", "Genre", "no", "6"])

    out = capsys.readouterr().out
    assert "All fields are required!" in out
    assert json.loads((tmp_path / "library.json").read_text(encoding="utf-8")) == []


def test_add_rejects_non_numeric_year(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, ["1", "Book", "Author", "20xx", "Genre", "no", "6"])

    assert "Publication year must be a number!" in capsys.readouterr().out


def test_add_rejects_zero_year(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, ["1", "Book", "Author", "0", "Genre", "no", "6"])

    assert "Publication year must be a positive number." in capsys.readouterr().out


def test_remove_existing_and_missing_book(monkeypatch, tmp_path, capsys):
    seeded = Library(data_dir=tmp_path, auto_load=False)
    seeded.add_book("Atomic Habits", "James Clear", 2018, "Self-Help")
    seeded.save()

    run(monkeypatch, tmp_path, ["2", "atomic habits", "2", "Ghost", "6"])

    out = capsys.readouterr().out
    assert "'Atomic Habits' removed successfully!" in out
    assert "Book 'Ghost' not found!" in out
    assert json.loads((tmp_path / "library.json").read_text(encoding="utf-8")) == []


def test_search_by_title(monkeypatch, tmp_path, capsys):
    seeded = Library(data_dir=tmp_path, auto_load=False)
    seeded.add_book("Atomic Habits", "James Clear", 2018, "Self-Help")
    seeded.add_book("Deep Work", "Cal Newport", 2016, "Productivity")
    seeded.save()

    run(monkeypatch, tmp_path, ["3", "1", "atomic", "6"])

    out = capsys.readouterr().out
    assert "Matching Books:" in out
    assert "Atomic Habits by James Clear" in out


def test_search_by_author(monkeypatch, tmp_path, capsys):
    seeded = Library(data_dir=tmp_path, auto_load=False)
    seeded.add_book("Atomic Habits", "James Clear", 2018, "Self-Help")
    seeded.add_book("Deep Work", "Cal Newport", 2016, "Productivity")
    seeded.save()

    run(monkeypatch, tmp_path, ["3", "2", "newport", "6"])

    out = capsys.readouterr().out
    assert "Deep Work by Cal Newport" in out


def test_search_without_matches(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, ["3", "1", "nothing", "6"])

    assert "No matching books found!" in capsys.readouterr().out


def test_search_invalid_choice(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, ["3", "9", "6"])

    assert "Invalid choice!" in capsys.readouterr().out


def test_empty_library_messages(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, ["4", "5", "6"])

    out = capsys.readouterr().out
    assert "Your library is empty!" in out
    assert "Your library is empty! Add some books first." in out


def test_statistics_output(monkeypatch, tmp_path, capsys):
    seeded = Library(data_dir=tmp_path, auto_load=False)
    seeded.add_book("Read Book", "A", 2000, "G", True)
    seeded.add_book("Unread Book", "B", 2001, "G", False)
    seeded.save()

    run(monkeypatch, tmp_path, ["5", "6"])

    out = capsys.readouterr().out
    assert "Total books: 2" in out
    assert "Books read: 1" in out
    assert "Percentage read: 50.00%" in out


def test_invalid_menu_choice(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, ["42", "6"])

    assert "Invalid choice! Please enter a number between 1 and 6." in capsys.readouterr().out


def test_eof_saves_before_exit(monkeypatch, tmp_path, capsys):
    run(monkeypatch, tmp_path, ["1", "Saved Book", "Author", "2020", "Genre", "no"])

    out = capsys.readouterr().out
    assert "Library saved to:" in out
    payload = json.loads((tmp_path / "library.json").read_text(encoding="utf-8"))
    assert payload[0]["title"] == "Saved Book"


def test_keyboard_interrupt_saves_before_exit(monkeypatch, tmp_path, capsys):
    seeded = Library(data_dir=tmp_path, auto_load=False)
    seeded.add_book("Saved Book", "Author", 2020, "Genre")
    seeded.save()

    def interrupt(_prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr(builtins, "input", interrupt)
    code = main(["--data-dir", str(tmp_path)])

    out = capsys.readouterr().out
    assert code == 0
    assert "Library saved to:" in out


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])

    assert excinfo.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_help_lists_data_dir(capsys):
    with pytest.raises(SystemExit) as excinfo:
        main(["--help"])

    assert excinfo.value.code == 0
    assert "--data-dir" in capsys.readouterr().out


def test_corrupted_data_warning_is_shown(monkeypatch, tmp_path, capsys):
    (tmp_path / "library.json").write_text("{broken", encoding="utf-8")

    run(monkeypatch, tmp_path, ["6"])

    out = capsys.readouterr().out
    assert "Could not read library.json" in out
    assert "A backup was saved as" in out
