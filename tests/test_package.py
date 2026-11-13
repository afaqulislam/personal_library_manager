"""Package-level tests: public API, module execution and metadata."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import personal_library_manager
from personal_library_manager import Book, Library

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_module(*args, data_dir=None, inputs=None):
    env = os.environ.copy()
    python_path = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        str(PROJECT_ROOT / "src") if not python_path else str(PROJECT_ROOT / "src") + os.pathsep + python_path
    )
    command = [sys.executable, "-m", "personal_library_manager"]
    if data_dir is not None:
        command.extend(["--data-dir", str(data_dir)])
    command.extend(args)
    return subprocess.run(
        command,
        input=inputs,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        timeout=60,
    )


def test_public_api_exports():
    assert personal_library_manager.__version__ == "0.1.0"
    assert personal_library_manager.Book is Book
    assert personal_library_manager.Library is Library


def test_module_version_runs():
    result = run_module("--version")

    assert result.returncode == 0
    assert result.stdout.strip() == "personal_library_manager 0.1.0"


def test_module_help_runs():
    result = run_module("--help")

    assert result.returncode == 0
    assert "--data-dir" in result.stdout
    assert "--version" in result.stdout


def test_module_scripted_session(tmp_path):
    inputs = (
        "1\n"
        "The Pragmatic Programmer\n"
        "Andrew Hunt\n"
        "1999\n"
        "Software\n"
        "yes\n"
        "4\n"
        "5\n"
        "6\n"
    )

    result = run_module(data_dir=tmp_path, inputs=inputs)

    assert result.returncode == 0
    assert "added successfully" in result.stdout
    assert "The Pragmatic Programmer by Andrew Hunt (1999) - Software - \u2705 Read" in result.stdout
    assert "Total books: 1" in result.stdout

    payload = json.loads((tmp_path / "library.json").read_text(encoding="utf-8"))
    assert payload[0]["title"] == "The Pragmatic Programmer"
    assert (tmp_path / "library.txt").exists()


def test_module_handles_closed_stdin(tmp_path):
    result = run_module(data_dir=tmp_path, inputs="")

    assert result.returncode == 0
    assert (tmp_path / "library.json").exists()


def test_installed_metadata_matches_package_version():
    from importlib.metadata import PackageNotFoundError, version

    try:
        installed = version("personal-library-manager-cli-aui")
    except PackageNotFoundError:
        pytest.skip("Package is not installed in this environment.")

    assert installed == personal_library_manager.__version__
