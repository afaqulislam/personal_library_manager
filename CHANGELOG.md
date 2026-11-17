# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.1] - 2026-11-17

### Changed

- Refreshed `README.md` for the published PyPI release, including current
  installation instructions, release status, project links and maintainer steps.
- Added `ruff` to the documented development dependencies.
- Aligned the `v0.1.0` GitHub release notes with `CHANGELOG.md`.
- Documentation-only release; no functional or API changes.

## [0.1.0] - 2026-11-14

### Added

- Installable Python package under `src/personal_library_manager`.
- `personal_library_manager` console command and `python -m personal_library_manager` support.
- `Book` data model with validation and JSON (de)serialization.
- `Library` API for adding, removing, searching, browsing and statistics.
- Atomic JSON and TXT persistence.
- Per-user data directory on Windows, macOS and Linux, with
  `PERSONAL_LIBRARY_MANAGER_HOME` and `--data-dir` overrides.
- Automatic migration of a legacy `library.json` from the working directory.
- Corrupt-file recovery: broken JSON is backed up instead of discarded.
- Graceful saving on exit, Ctrl+C and EOF.
- 98 automated tests covering models, storage, CLI, module execution and metadata.
- GitHub Actions CI and Trusted Publishing workflows.
- Full documentation in `README.md`.

### Changed

- Converted the original single-file script into a maintainable package.
- Improved input validation and error messages.
- TXT and JSON files are now UTF-8 and written atomically.

### Fixed

- Data loss when the application crashed before the manual save step.
- Silent failures on corrupted or malformed `library.json`.
- Import-time side effects; the CLI now lives behind an entry point.
