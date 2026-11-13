"""Filesystem locations used by the Personal Library Manager.

User data is stored outside the installed package so that it survives
upgrades and is writable on every platform.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR_NAME = "personal-library-manager"
ENV_DATA_DIR = "PERSONAL_LIBRARY_MANAGER_HOME"


def default_data_dir() -> Path:
    """Return the default per-user data directory for the application.

    The location can be overridden with the ``PERSONAL_LIBRARY_MANAGER_HOME``
    environment variable or the ``--data-dir`` command-line option.
    """
    override = os.environ.get(ENV_DATA_DIR)
    if override:
        return Path(override).expanduser()

    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA")
        if base:
            return Path(base) / APP_DIR_NAME
        return Path.home() / "AppData" / "Roaming" / APP_DIR_NAME

    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_DIR_NAME

    base = os.environ.get("XDG_DATA_HOME")
    if base:
        return Path(base) / APP_DIR_NAME
    return Path.home() / ".local" / "share" / APP_DIR_NAME
