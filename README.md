# 📚 Personal Library Manager

A dependency-free, command-line manager for your personal book collection. Add, remove, search, browse and track your reading — with automatic, crash-safe persistence to **JSON** and a human-readable **TXT** export.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/Dependencies-none-success?style=for-the-badge" alt="No dependencies">
  <img src="https://img.shields.io/badge/Interface-CLI-4B8BBE?style=for-the-badge&logo=windowsterminal&logoColor=white" alt="CLI">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT License">
</p>

<p align="center">
  <img src="https://img.shields.io/pypi/v/personal-library-manager-cli-aui?label=PyPI&style=flat-square" alt="PyPI version">
  <img src="https://img.shields.io/pypi/pyversions/personal-library-manager-cli-aui?style=flat-square" alt="PyPI Python versions">
  <img src="https://img.shields.io/github/actions/workflow/status/afaqulislam/personal_library_manager/ci.yml?branch=main&label=tests&style=flat-square" alt="CI">
</p>

> **Package names**
>
> - **PyPI distribution:** `personal-library-manager-cli-aui`
> - **Python import:** `personal_library_manager`
> - **CLI command:** `personal_library_manager`
>
> The distribution name differs because the plain `personal-library-manager` name is already registered on PyPI by another project. The import package and command are exactly as expected.
>
> PyPI badges populate after the first release. This project has **not** been published to PyPI yet.

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [CLI Usage](#-cli-usage)
- [Where Your Data Lives](#-where-your-data-lives)
- [Data Format](#-data-format)
- [Python API](#-python-api)
- [Project Structure](#-project-structure)
- [Development Setup](#-development-setup)
- [Testing](#-testing)
- [Building Distributions](#-building-distributions)
- [Publishing (Maintainers)](#-publishing-maintainers)
- [Compatibility](#-compatibility)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)

---

## ✨ Overview

**Personal Library Manager** stores each book with its **title, author, publication year, genre and read status**, then lets you search, filter, and measure your reading progress from a simple numbered menu.

The project uses only the **Python Standard Library**, so installation is fast and there is nothing to compile. User data is written outside the installed package to a per-user data directory, which means your library survives upgrades and works on Windows, macOS and Linux.

---

## 🚀 Features

| Feature | Description |
|---|---|
| ➕ Add books | Store title, author, year, genre and read status |
| 🗑️ Remove books | Delete by title using case-insensitive matching |
| 🔎 Search | Case-insensitive substring search by **title** or **author** |
| 📖 Browse | Numbered, formatted list of every book |
| 📊 Statistics | Total books, books read, unread and completion percentage |
| 💾 Dual persistence | Writes `library.json` (data) and `library.txt` (readable export) |
| 🛡️ Crash-safe saves | Atomic writes via temporary file + rename |
| 🔁 Corrupt-file recovery | Broken JSON is backed up, never silently deleted |
| 📦 Legacy migration | Imports an existing `library.json` from the working directory |
| ✅ Validation | Rejects empty fields, non-numeric or non-positive years |
| 🧪 Tested | 98 automated tests covering models, storage, CLI and packaging |
| 🪶 Zero runtime dependencies | Standard library only |

---

## 📦 Installation

Requires **Python 3.9 or newer**.

### From PyPI (after publication)

```bash
pip install personal-library-manager-cli-aui
```

### Isolated install with pipx

```bash
pipx install personal-library-manager-cli-aui
```

### From source

```bash
git clone https://github.com/afaqulislam/personal_library_manager.git
cd personal_library_manager
python -m pip install .
```

For development (editable install with test tooling):

```bash
python -m pip install -e ".[dev]"
```

---

## ▶️ Quick Start

```bash
personal_library_manager
```

You can also run the module directly:

```bash
python -m personal_library_manager
```

Choose a custom data directory (useful for testing):

```bash
personal_library_manager --data-dir ./my-library
```

Check the installed version:

```bash
personal_library_manager --version
```

---

## 🖥️ CLI Usage

```text
📚 Welcome to your Personal Library Manager!
1. Add a book
2. Remove a book
3. Search for a book
4. Display all books
5. Display statistics
6. Exit
Enter your choice: 1
Enter the book title: Atomic Habits
Enter the author: James Clear
Enter the publication year: 2018
Enter the genre: Self-Help
Have you read this book? (yes/no): yes
✅ 'Atomic Habits' added successfully!

Enter your choice: 4

📚 Your Library:
1. Atomic Habits by James Clear (2018) - Self-Help - ✅ Read

Enter your choice: 5

📊 Library Statistics:
📚 Total books: 1
✅ Books read: 1
📖 Percentage read: 100.00%

Enter your choice: 6
💾 Library saved to:
   • C:\Users\<you>\AppData\Roaming\personal-library-manager\library.json
   • C:\Users\<you>\AppData\Roaming\personal-library-manager\library.txt
📌 Exiting... Goodbye!
```

### Menu reference

| Option | Action | Notes |
|---|---|---|
| `1` | Add a book | All fields required; year must be digits; `yes/y/true/1` = read |
| `2` | Remove a book | First case-insensitive title match |
| `3` | Search | Substring match by title or author |
| `4` | Display all books | Numbered list with read status |
| `5` | Statistics | Totals and percentage read |
| `6` | Exit | Saves before exiting |

### Saving behavior

- The library is saved when you choose **`6` (Exit)**.
- It is also saved if you press **Ctrl+C** or close standard input, so work is not lost.
- Saves are atomic: data is written to a temporary file and then renamed.

### Command-line options

| Option | Description |
|---|---|
| `--data-dir PATH` | Store `library.json`/`library.txt` in `PATH` |
| `--version` | Print the version and exit |
| `--help` | Show help and exit |

---

## 🗂️ Where Your Data Lives

User data is stored in a per-user directory, **not** inside the installed package:

| Platform | Default location |
|---|---|
| Windows | `%APPDATA%\personal-library-manager\` |
| macOS | `~/Library/Application Support/personal-library-manager/` |
| Linux | `$XDG_DATA_HOME/personal-library-manager/` (defaults to `~/.local/share/personal-library-manager/`) |

Override the location with:

```bash
# environment variable
PERSONAL_LIBRARY_MANAGER_HOME=/path/to/data personal_library_manager

# or the command-line flag
personal_library_manager --data-dir /path/to/data
```

**Legacy data:** if no library exists yet and a valid `library.json` is present in the current working directory, it is imported automatically on first run.

---

## 🗃️ Data Format

### `library.json`

```json
[
    {
        "title": "Atomic Habits",
        "author": "James Clear",
        "year": 2018,
        "genre": "Self-Help",
        "read": true
    }
]
```

| Key | Type | Description |
|---|---|---|
| `title` | string | Book title |
| `author` | string | Author name |
| `year` | integer | Positive publication year |
| `genre` | string | Genre / category |
| `read` | boolean | `true` = read, `false` = unread |

Invalid entries are skipped with a warning, and a corrupted file is renamed to `library.json.corrupt-<timestamp>` before the app starts with an empty library.

### `library.txt`

Regenerated on every save:

```text
Title: Atomic Habits | Author: James Clear | Year: 2018 | Genre: Self-Help | Read: Yes
```

---

## 🐍 Python API

The package can be used as a library:

```python
from personal_library_manager import Book, Library

library = Library()  # default user data directory
# library = Library(data_dir="./my-library")  # or a custom directory

library.add_book("Atomic Habits", "James Clear", 2018, "Self-Help", read=True)
library.add(Book("Deep Work", "Cal Newport", 2016, "Productivity", False))

print(len(library))                       # 2
print(library.statistics())
# {'total': 2, 'read': 1, 'unread': 1, 'percentage': 50.0}

for book in library.search("clear", field="author"):
    print(book.describe())

removed = library.remove_book("deep work")  # case-insensitive
json_path, text_path = library.save()
print(json_path, text_path)
```

### Public classes and methods

| API | Description |
|---|---|
| `Book(title, author, year, genre, read=False)` | Validated book model; `to_dict()`, `from_dict()`, `describe()` |
| `Library(data_dir=None)` | Loads existing data by default |
| `Library.add_book(...)` | Add and return a `Book` |
| `Library.add(book)` | Add a `Book` instance |
| `Library.remove_book(title)` | Remove first match; returns `Book` or `None` |
| `Library.search(keyword, field="title")` | `field` is `"title"` or `"author"` |
| `Library.statistics()` | Totals and percentage |
| `Library.save()` | Write JSON + TXT atomically; returns paths |
| `Library.load()` | Reload from disk; returns count |
| `Library.export_text()` | TXT representation as a string |
| `len(library)` / `library.books` / iteration | Collection access |

Invalid input raises `ValueError` with a descriptive message.

---

## 📁 Project Structure

```text
personal_library_manager/
├── src/
│   └── personal_library_manager/
│       ├── __init__.py      # Public API and version
│       ├── __main__.py      # python -m personal_library_manager
│       ├── cli.py           # Menu loop, prompts, argparse entry point
│       ├── library.py       # Collection logic + persistence
│       ├── models.py        # Book model and validation
│       └── paths.py         # Cross-platform data directory
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_library.py
│   ├── test_models.py
│   ├── test_package.py
│   └── test_storage.py
├── .github/workflows/       # CI and publishing workflows
├── CHANGELOG.md
├── LICENSE
├── MANIFEST.in
├── pyproject.toml
└── README.md
```

---

## 🛠️ Development Setup

```bash
git clone https://github.com/afaqulislam/personal_library_manager.git
cd personal_library_manager

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

---

## 🧪 Testing

The suite uses **pytest** and covers the data model, collection operations, JSON/TXT persistence, disaster recovery, the interactive CLI, module execution and installed metadata.

```bash
python -m pytest
```

Useful variants:

```bash
python -m pytest -q                 # quiet
python -m pytest tests/test_cli.py  # one module
python -m pytest -k storage         # keyword match
```

---

## 📦 Building Distributions

```bash
python -m pip install build twine
python -m build
python -m twine check dist/*
```

This produces:

- `dist/personal_library_manager_cli_aui-0.1.0-py3-none-any.whl`
- `dist/personal_library_manager_cli_aui-0.1.0.tar.gz`

Verify an artifact in a clean environment:

```bash
python -m venv /tmp/verify
/tmp/verify/bin/pip install dist/personal_library_manager_cli_aui-0.1.0-py3-none-any.whl
/tmp/verify/bin/personal_library_manager --version
```

---

## 🚢 Publishing (Maintainers)

> **Status:** not published. Publishing requires explicit approval.

### Option A — Trusted Publishing via GitHub Actions (recommended)

Workflows are included:

- `.github/workflows/publish-testpypi.yml` — manual **TestPyPI** publish
- `.github/workflows/publish-pypi.yml` — publish on a **GitHub Release**

One-time setup on PyPI / TestPyPI → **Your projects → Publishing → Add a pending publisher**:

| Field | TestPyPI | PyPI |
|---|---|---|
| PyPI project name | `personal-library-manager-cli-aui` | `personal-library-manager-cli-aui` |
| Owner | `afaqulislam` | `afaqulislam` |
| Repository | `personal_library_manager` | `personal_library_manager` |
| Workflow name | `publish-testpypi.yml` | `publish-pypi.yml` |
| Environment | `testpypi` | `pypi` |

No API tokens are stored in the repository; the workflows use OIDC.

After that:

1. Go to **Actions → Publish to TestPyPI → Run workflow** to validate.
2. Create a GitHub Release (tag e.g. `v0.1.0`) to publish to PyPI.

### Option B — Manual upload

TestPyPI:

```bash
python -m build
python -m twine upload --repository testpypi dist/*
```

Official PyPI:

```bash
python -m twine upload dist/*
```

When prompted, use `__token__` as the username and your API token as the password. Never commit tokens.

---

## 🧩 Compatibility

- **Python:** 3.9, 3.10, 3.11, 3.12, 3.13
- **Operating systems:** Windows, macOS, Linux
- **Runtime dependencies:** none
- **Development dependencies:** `pytest`, `build`, `twine`

---

## 🤝 Contributing

1. Fork the repository.
2. Create a branch: `git checkout -b feature/short-description`.
3. Make your change and add or update tests.
4. Run `python -m pytest` and confirm everything passes.
5. Commit with a clear message.
6. Push the branch and open a Pull Request.

Please keep the package free of runtime dependencies unless there is a strong justification.

---

## 📜 License

Released under the **MIT License**. See [LICENSE](LICENSE).

---

## 👨‍💻 Author

**Afaq Ul Islam**

- GitHub: [@afaqulislam](https://github.com/afaqulislam)
- LinkedIn: [in/afaqulislam](https://www.linkedin.com/in/afaqulislam)
- Portfolio: [afaqulislam.github.io](https://afaqulislam.github.io)
- Email: [afaqulislam707@gmail.com](mailto:afaqulislam707@gmail.com)

---

<p align="center">⭐ If this project helps you, consider starring the repository.</p>
