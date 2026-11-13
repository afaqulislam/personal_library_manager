"""Tests for JSON persistence, TXT export, recovery and migration."""

import json

import pytest

from personal_library_manager import Library


def test_save_creates_both_files(library):
    library.add_book("Atomic Habits", "James Clear", 2018, "Self-Help", True)

    json_path, text_path = library.save()

    assert json_path == library.json_path
    assert text_path == library.text_path
    assert json_path.exists()
    assert text_path.exists()


def test_saved_json_has_expected_schema(library):
    library.add_book("Atomic Habits", "James Clear", 2018, "Self-Help", True)
    library.save()

    payload = json.loads(library.json_path.read_text(encoding="utf-8"))

    assert payload == [
        {
            "title": "Atomic Habits",
            "author": "James Clear",
            "year": 2018,
            "genre": "Self-Help",
            "read": True,
        }
    ]


def test_saved_text_export_is_human_readable(library):
    library.add_book("Atomic Habits", "James Clear", 2018, "Self-Help", True)
    library.add_book("Deep Work", "Cal Newport", 2016, "Productivity", False)
    library.save()

    expected = (
        "Title: Atomic Habits | Author: James Clear | Year: 2018 | Genre: Self-Help | Read: Yes\n"
        "Title: Deep Work | Author: Cal Newport | Year: 2016 | Genre: Productivity | Read: No\n"
    )

    assert library.text_path.read_text(encoding="utf-8") == expected
    assert library.export_text() == expected


def test_roundtrip_preserves_everything(tmp_path):
    original = Library(data_dir=tmp_path, auto_load=False)
    original.add_book("Caf\u00e9 \U0001F4DA", "Jos\u00e9", 2021, "Essays", True)
    original.save()

    reloaded = Library(data_dir=tmp_path)

    assert reloaded.last_error is None
    assert len(reloaded) == 1
    assert reloaded.books[0] == original.books[0]


def test_missing_file_loads_empty_library(tmp_path):
    lib = Library(data_dir=tmp_path)

    assert len(lib) == 0
    assert lib.last_error is None


def test_load_is_idempotent(populated_library):
    assert len(populated_library) == 2
    populated_library.load()
    assert len(populated_library) == 2


def test_corrupted_json_is_backed_up(tmp_path):
    (tmp_path / "library.json").write_text("{ this is not json", encoding="utf-8")

    lib = Library(data_dir=tmp_path)

    assert len(lib) == 0
    assert lib.last_error is not None
    assert "Could not read" in lib.last_error
    assert not (tmp_path / "library.json").exists()
    assert len(list(tmp_path.glob("library.json.corrupt-*"))) == 1


def test_non_list_json_is_backed_up(tmp_path):
    (tmp_path / "library.json").write_text('{"title": "Dune"}', encoding="utf-8")

    lib = Library(data_dir=tmp_path)

    assert len(lib) == 0
    assert lib.last_error is not None
    assert "expected a list" in lib.last_error
    assert len(list(tmp_path.glob("library.json.corrupt-*"))) == 1


def test_invalid_entries_are_skipped(tmp_path):
    payload = [
        {"title": "Valid", "author": "Author", "year": 2020, "genre": "Genre", "read": False},
        {"title": "Missing fields"},
        "not even an object",
    ]
    (tmp_path / "library.json").write_text(json.dumps(payload), encoding="utf-8")

    lib = Library(data_dir=tmp_path)

    assert len(lib) == 1
    assert lib.books[0].title == "Valid"
    assert lib.last_error == "Skipped 2 invalid book entries in library.json."


def test_single_invalid_entry_uses_singular_message(tmp_path):
    payload = [
        {"title": "Valid", "author": "Author", "year": 2020, "genre": "Genre", "read": False},
        {"title": "Missing fields"},
    ]
    (tmp_path / "library.json").write_text(json.dumps(payload), encoding="utf-8")

    lib = Library(data_dir=tmp_path)

    assert lib.last_error == "Skipped 1 invalid book entry in library.json."


def test_legacy_file_is_migrated(tmp_path, monkeypatch):
    source = tmp_path / "legacy"
    source.mkdir()
    payload = [
        {"title": "Old Book", "author": "Old Author", "year": 1999, "genre": "Old", "read": True}
    ]
    (source / "library.json").write_text(json.dumps(payload), encoding="utf-8")
    target = tmp_path / "data"

    monkeypatch.chdir(source)
    lib = Library(data_dir=target)

    assert len(lib) == 1
    assert lib.books[0].title == "Old Book"
    assert lib.migration_note is not None
    assert "Imported" in lib.migration_note
    assert (target / "library.json").exists()


def test_invalid_legacy_file_is_not_migrated(tmp_path, monkeypatch):
    source = tmp_path / "legacy"
    source.mkdir()
    (source / "library.json").write_text("{broken", encoding="utf-8")
    target = tmp_path / "data"

    monkeypatch.chdir(source)
    lib = Library(data_dir=target)

    assert len(lib) == 0
    assert lib.migration_note is None
    assert not (target / "library.json").exists()


def test_save_creates_nested_data_directory(tmp_path):
    target = tmp_path / "nested" / "deeper"
    lib = Library(data_dir=target, auto_load=False)
    lib.add_book("Dune", "Frank Herbert", 1965, "Sci-Fi")

    lib.save()

    assert (target / "library.json").exists()
    assert (target / "library.txt").exists()


def test_save_overwrites_previous_content(library):
    library.add_book("First", "Author", 2000, "Genre")
    library.save()

    library.clear()
    library.add_book("Second", "Author", 2001, "Genre")
    library.save()

    payload = json.loads(library.json_path.read_text(encoding="utf-8"))

    assert [entry["title"] for entry in payload] == ["Second"]


def test_save_returns_path_objects(library):
    json_path, text_path = library.save()

    assert json_path.parent == library.data_dir
    assert text_path.parent == library.data_dir
